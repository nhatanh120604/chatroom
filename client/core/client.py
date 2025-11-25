import os
import json
from typing import Optional
from PySide6.QtCore import QObject, Signal, Slot, Property
from .connection_manager import ConnectionManager
from .session_manager import SessionManager
from .state_manager import StateManager
from ..handlers.message_handler import MessageHandler
from ..handlers.file_handler import FileHandler
from ..handlers.typing_handler import TypingHandler
from ..handlers.avatar_handler import AvatarHandler
from ..handlers.socket_manager import SocketManager
from ..utils.validators import FileValidator


class ChatClient(QObject):
    """Main chat client orchestrator - coordinates all components."""
    
    # Forward signals from components
    messageReceived = Signal(str, str, "QVariant")  # username, message, file payload
    messageReceivedEx = Signal(str, str, "QVariant", str)  # username, message, file payload, timestamp
    privateMessageReceived = Signal(str, str, str, int, str, "QVariant")  # sender, recipient, message, message_id, status, file payload
    privateMessageReceivedEx = Signal(str, str, str, int, str, "QVariant", str)  # + timestamp
    privateMessageSent = Signal(str, str, str, int, str, "QVariant")  # sender, recipient, message, message_id, status, file payload
    privateMessageSentEx = Signal(str, str, str, int, str, "QVariant", str)  # + timestamp
    privateMessageRead = Signal(int)
    publicTypingReceived = Signal(str, bool)
    privateTypingReceived = Signal(str, bool)
    usersUpdated = Signal(list)  # Explicitly list type for QML compatibility
    avatarsUpdated = Signal(dict)  # Explicitly dict type for QML compatibility
    avatarUpdated = Signal(str, "QVariant")
    disconnected = Signal(bool)
    reconnecting = Signal(int)
    reconnected = Signal()
    errorReceived = Signal(str)
    usernameChanged = Signal(str)
    generalHistoryReceived = Signal("QVariant")
    fileTransferProgress = Signal(str, int, int)
    fileTransferComplete = Signal(str, str)
    fileTransferError = Signal(str, str)
    connectionStateChanged = Signal(str)
    
    def __init__(self, url: Optional[str] = None):
        super().__init__()
        
        # Resolve server URL
        self._url = self._resolve_server_url(url)
        self._username = ""
        self._desired_username = ""
        
        # Initialize components
        self._socket_manager = SocketManager()
        self._connection_manager = ConnectionManager(
            self._socket_manager.sio, self._url
        )
        self._session_manager = SessionManager()
        self._state_manager = StateManager()
        
        # Initialize handlers
        self._message_handler = MessageHandler(
            self._session_manager,
            self._emit_when_connected
        )
        self._file_handler = FileHandler(
            self._session_manager,
            self._emit_when_connected
        )
        self._typing_handler = TypingHandler(self._emit_when_connected)
        self._avatar_handler = AvatarHandler(self._emit_when_connected)
        
        # Connect component signals to our signals
        self._connect_signals()
        
        # Setup socket event handlers
        self._setup_socket_handlers()
        
        # Pending events queue
        self._pending_events = []
    
    def _resolve_server_url(self, url: Optional[str]) -> str:
        """Resolve server URL from environment or parameter."""
        try:
            from dotenv import load_dotenv
            client_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            env_path = os.path.join(client_dir, ".env")
            load_dotenv(env_path)
        except Exception:
            pass
        
        return url or os.environ.get("CHAT_SERVER_URL") or "http://localhost:5000"
    
    def _convert_dict_for_qml(self, obj):
        """Convert Python dict to QML-compatible format via JSON serialization."""
        if obj is None:
            return None
        if isinstance(obj, dict):
            try:
                # Convert to JSON and back to ensure QML compatibility
                json_str = json.dumps(obj)
                result = json.loads(json_str)
                print(f"[ChatClient] Converted dict for QML: {result}")
                return result
            except Exception as e:
                print(f"[ChatClient] Failed to convert dict for QML: {e}")
                return obj
        return obj
    
    def _connect_signals(self):
        """Connect component signals to main signals."""
        # Connection manager
        self._connection_manager.reconnecting.connect(self.reconnecting)
        self._connection_manager.reconnected.connect(self.reconnected)
        self._connection_manager.disconnected.connect(self._on_disconnected)
        self._connection_manager.connectionStateChanged.connect(
            self.connectionStateChanged
        )
        
        # Message handler
        self._message_handler.messageReceived.connect(self.messageReceived)
        self._message_handler.messageReceivedEx.connect(self.messageReceivedEx)
        self._message_handler.privateMessageReceived.connect(
            self.privateMessageReceived
        )
        self._message_handler.privateMessageReceivedEx.connect(
            self.privateMessageReceivedEx
        )
        self._message_handler.privateMessageSent.connect(self.privateMessageSent)
        self._message_handler.privateMessageSentEx.connect(self.privateMessageSentEx)
        self._message_handler.privateMessageRead.connect(self.privateMessageRead)
        self._message_handler.generalHistoryReceived.connect(
            self.generalHistoryReceived
        )
        
        # File handler
        self._file_handler.fileTransferProgress.connect(self.fileTransferProgress)
        self._file_handler.fileTransferComplete.connect(self.fileTransferComplete)
        self._file_handler.fileTransferError.connect(self.fileTransferError)
        self._file_handler.errorNotification.connect(self.errorReceived)
        
        # Typing handler
        self._typing_handler.publicTypingReceived.connect(self.publicTypingReceived)
        self._typing_handler.privateTypingReceived.connect(self.privateTypingReceived)
        
        # Avatar handler
        self._avatar_handler.errorNotification.connect(self.errorReceived)
        
        # State manager
        try:
            self._state_manager.usersUpdated.connect(self.usersUpdated)
            print("[ChatClient] Connected usersUpdated signal")
        except Exception as e:
            print(f"[ChatClient] Failed to connect usersUpdated: {e}")
        
        try:
            self._state_manager.avatarsUpdated.connect(self.avatarsUpdated)
            print("[ChatClient] Connected avatarsUpdated signal")
        except Exception as e:
            print(f"[ChatClient] Failed to connect avatarsUpdated: {e}")
        
        try:
            self._state_manager.avatarUpdated.connect(self.avatarUpdated)
            print("[ChatClient] Connected avatarUpdated signal")
        except Exception as e:
            print(f"[ChatClient] Failed to connect avatarUpdated: {e}")
    
    def _setup_socket_handlers(self):
        """Setup SocketIO event handlers."""
        sio = self._socket_manager.sio
        
        @sio.event
        def connect():
            print("[ChatClient] Connected to server")
            self._connection_manager.on_connected()
            
            # Exchange session key
            encrypted = self._session_manager.generate_and_exchange(self._url)
            if encrypted:
                sio.emit("session_key", {"encrypted_aes_key": encrypted})
            
            # Send pending events
            self._flush_pending_events()
        
        @sio.on("session_key_ok")
        def on_session_key_ok(data):
            print("[ChatClient] Session key acknowledged")
            self._session_manager.on_session_ack()
            
            # Flush events waiting for session
            for event, payload in self._session_manager.flush_queue():
                try:
                    sio.emit(event, payload)
                except Exception as e:
                    print(f"[ChatClient] Failed to emit queued '{event}': {e}")
        
        @sio.event
        def disconnect():
            print("[ChatClient] Disconnected from server")
            self._connection_manager.on_disconnected()
        
        @sio.on("message")
        def on_message(data):
            # Log raw data received from server
            print(f"[CLIENT] on_message RAW data type: {type(data)}")
            print(f"[CLIENT] on_message RAW data keys: {list(data.keys()) if isinstance(data, dict) else 'N/A'}")
            print(f"[CLIENT] on_message RAW data: {data}")
            
            username = data.get("username", "Unknown")
            message = data.get("message", "")
            timestamp = data.get("timestamp", "")
            
            # Log file payload extraction
            raw_file = data.get("file")
            print(f"[CLIENT] on_message raw_file type: {type(raw_file)}")
            print(f"[CLIENT] on_message raw_file value: {raw_file}")
            if isinstance(raw_file, dict):
                print(f"[CLIENT] on_message raw_file keys: {list(raw_file.keys())}")
                print(f"[CLIENT] on_message raw_file length: {len(raw_file)}")
            
            # Extract file payload - pass it through even if empty dict
            file_payload = data.get("file")
            if isinstance(file_payload, dict) and len(file_payload) == 0:
                print(f"[CLIENT] on_message converting empty dict to None")
                file_payload = None
            
            print(f"[CLIENT] on_message final file_payload: {file_payload}")
            print(f"[CLIENT] on_message emitting: username={username}, msg_len={len(message)}, file={file_payload is not None}")
            
            # Convert dict to QML-compatible format via JSON serialization
            file_payload = self._convert_dict_for_qml(file_payload)
            
            self.messageReceived.emit(username, message, file_payload)
            self.messageReceivedEx.emit(username, message, file_payload, timestamp)
        
        @sio.on("private_message_received")
        def on_private_message_received(data):
            # Log raw data
            print(f"[CLIENT] on_private_message_received RAW data: {data}")
            print(f"[CLIENT] on_private_message_received RAW data keys: {list(data.keys())}")
            
            raw_file = data.get("file")
            print(f"[CLIENT] on_private_message_received raw_file type: {type(raw_file)}")
            print(f"[CLIENT] on_private_message_received raw_file value: {raw_file}")
            if isinstance(raw_file, dict):
                print(f"[CLIENT] on_private_message_received raw_file keys: {list(raw_file.keys())}")
            
            file_payload = data.get("file")
            if isinstance(file_payload, dict) and len(file_payload) == 0:
                print(f"[CLIENT] on_private_message_received converting empty dict to None")
                file_payload = None
            
            print(f"[CLIENT] on_private_message_received final file_payload: {file_payload}")
            
            # Convert dict to QML-compatible format
            if file_payload is not None and isinstance(file_payload, dict):
                file_payload = dict(file_payload)
                print(f"[CLIENT] on_private_message_received converted file_payload for QML: {file_payload}")
            
            self._message_handler.privateMessageReceivedEx.emit(
                data.get("sender", "Unknown"),
                data.get("recipient", "Unknown"),
                data.get("message", ""),
                int(data.get("message_id", 0)),
                data.get("status", ""),
                file_payload,
                data.get("timestamp", "")
            )
        
        @sio.on("private_message_sent")
        def on_private_message_sent(data):
            # Log raw data
            print(f"[CLIENT] on_private_message_sent RAW data: {data}")
            print(f"[CLIENT] on_private_message_sent RAW data keys: {list(data.keys())}")
            
            raw_file = data.get("file")
            print(f"[CLIENT] on_private_message_sent raw_file type: {type(raw_file)}")
            print(f"[CLIENT] on_private_message_sent raw_file value: {raw_file}")
            if isinstance(raw_file, dict):
                print(f"[CLIENT] on_private_message_sent raw_file keys: {list(raw_file.keys())}")
            
            file_payload = data.get("file")
            if isinstance(file_payload, dict) and len(file_payload) == 0:
                print(f"[CLIENT] on_private_message_sent converting empty dict to None")
                file_payload = None
            
            print(f"[CLIENT] on_private_message_sent final file_payload: {file_payload}")
            
            # Convert dict to QML-compatible format
            if file_payload is not None and isinstance(file_payload, dict):
                file_payload = dict(file_payload)
                print(f"[CLIENT] on_private_message_sent converted file_payload for QML: {file_payload}")
            
            self._message_handler.privateMessageSentEx.emit(
                data.get("sender", "Unknown"),
                data.get("recipient", "Unknown"),
                data.get("message", ""),
                int(data.get("message_id", 0)),
                data.get("status", ""),
                file_payload,
                data.get("timestamp", "")
            )
        
        @sio.on("private_message_read")
        def on_private_message_read(data):
            try:
                message_id = int(data.get("message_id", 0))
                if message_id > 0:
                    self.privateMessageRead.emit(message_id)
            except (TypeError, ValueError):
                pass
        
        @sio.on("public_typing")
        def on_public_typing(data):
            username = data.get("username")
            is_typing = bool(data.get("is_typing"))
            if username:
                self.publicTypingReceived.emit(username, is_typing)
        
        @sio.on("private_typing")
        def on_private_typing(data):
            username = data.get("username")
            is_typing = bool(data.get("is_typing"))
            if username:
                self.privateTypingReceived.emit(username, is_typing)
        
        @sio.on("update_user_list")
        def on_update_user_list(data):
            try:
                users = data.get("users", [])
                avatars = data.get("avatars", {})
                
                print(f"[ChatClient] on_update_user_list: users type={type(users)}, count={len(users) if users else 0}")
                self._state_manager.update_users(users)
                self._state_manager.update_avatars(avatars)
                
                # Update username if in list
                if self._desired_username and self._desired_username in users:
                    self._set_username(self._desired_username)
                elif self._username and self._username not in users:
                    self._set_username("")
            except Exception as e:
                print(f"[ChatClient] Error in on_update_user_list: {e}")
                import traceback
                traceback.print_exc()
        
        @sio.on("avatar_update")
        def on_avatar_update(data):
            username = data.get("username")
            avatar = data.get("avatar")
            if username:
                self._state_manager.update_avatar(username, avatar)
        
        @sio.on("chat_history")
        def on_chat_history(data):
            messages = data.get("messages", [])
            self.generalHistoryReceived.emit(messages)
        
        @sio.on("file_chunk")
        def on_file_chunk(data):
            self._file_handler.handle_file_chunk(data)
        
        @sio.on("error")
        def on_error(data):
            message = data.get("message", "An unknown error occurred.")
            self.errorReceived.emit(message)
            
            # Handle username errors
            lowered = message.lower()
            if "username" in lowered or "name" in lowered:
                if self._desired_username and self._desired_username == self._username:
                    self._set_username("")
                self._desired_username = ""
    
    def _emit_when_connected(self, event: str, data: dict):
        """Emit event when connected, otherwise queue."""
        if self._connection_manager.connected:
            try:
                self._socket_manager.emit(event, data)
            except Exception as e:
                print(f"[ChatClient] Failed to emit '{event}': {e}")
                # Don't emit error for typing events as they're not critical
                if event != "typing":
                    self.errorReceived.emit(
                        "Unable to send message. Please check your connection."
                    )
        else:
            self._pending_events.append((event, data))
            self._connection_manager.connect_async(
                on_error=lambda err: self.errorReceived.emit(
                    "Unable to connect to server. Please check your network."
                )
            )
    
    def _flush_pending_events(self):
        """Flush queued events after connection."""
        if self._desired_username:
            has_register = any(evt == "register" for evt, _ in self._pending_events)
            if not has_register:
                self._pending_events.insert(
                    0, ("register", {"username": self._desired_username})
                )
        
        # Send all pending
        for event, payload in self._pending_events:
            try:
                self._socket_manager.emit(event, payload)
            except Exception as e:
                print(f"[ChatClient] Failed to send pending '{event}': {e}")
        
        self._pending_events.clear()
    
    def _on_disconnected(self, user_requested: bool):
        """Handle disconnection."""
        self._state_manager.clear()
    
    def _set_username(self, value: str):
        """Update username and notify UI."""
        value = value or ""
        if self._username != value:
            self._username = value
            self.usernameChanged.emit(self._username)
            if self._username:
                self._message_handler.request_history()
    
    # ========================================================================
    # PUBLIC API - QML-exposed slots
    # ========================================================================
    
    @Slot(str)
    def register(self, username: str):
        """Register username with server."""
        desired = (username or "").strip()
        if not desired:
            self.errorReceived.emit("Username cannot be empty.")
            return
        
        self._desired_username = desired
        self._emit_when_connected("register", {"username": desired})
    
    @Slot(str, str)
    def sendMessageWithAttachment(self, message: str, file_url: str):
        """Send public message with optional file."""
        text = (message or "").strip()
        file_url = (file_url or "").strip()
        
        if file_url:
            try:
                print(f"[ChatClient] sendMessageWithAttachment: file_url={file_url}")
                file_path = FileValidator.normalize_file_path(file_url)
                if not file_path:
                    print(f"[ChatClient] Failed to normalize file path from: {file_url}")
                    self.errorReceived.emit("Invalid file selection.")
                    return
                
                print(f"[ChatClient] Normalized file path: {file_path}")
                
                # Resolve and validate file exists
                resolved = file_path.resolve(strict=True)
                if not resolved.is_file():
                    print(f"[ChatClient] Path is not a file: {resolved}")
                    self.errorReceived.emit("Selection is not a file.")
                    return
                
                # Read file
                file_data = resolved.read_bytes()
                filename = resolved.name
                
                print(f"[ChatClient] File loaded: filename={filename}, size={len(file_data)} bytes")
                
                # Send file chunks first to get transfer_id
                transfer_id = self._file_handler.send_file_chunks(file_data, filename)
                print(f"[ChatClient] File transfer started: transfer_id={transfer_id}")
                
                # Create file payload for message
                file_payload = {
                    "transfer_id": transfer_id,
                    "filename": filename,
                    "size": len(file_data),
                }
                print(f"[ChatClient] File payload for message: {file_payload}")
                
                # Send message with file metadata
                if text or transfer_id:
                    self._message_handler.send_public_message(text, file_payload)
                    print(f"[ChatClient] Message sent with file metadata")
            except FileNotFoundError:
                print(f"[ChatClient] File not found: {file_url}")
                self.errorReceived.emit("File not found.")
            except PermissionError:
                print(f"[ChatClient] Permission denied reading file: {file_url}")
                self.errorReceived.emit("Permission denied reading file.")
            except Exception as e:
                print(f"[ChatClient] Failed to read file: {e}")
                import traceback
                traceback.print_exc()
                self.errorReceived.emit("Failed to read file.")
        else:
            if not text:
                self.errorReceived.emit("Cannot send an empty message.")
                return
            self._message_handler.send_public_message(text)
    
    @Slot(str, str, str)
    def sendPrivateMessageWithAttachment(
        self, recipient: str, message: str, file_url: str
    ):
        """Send private message with optional file."""
        recip = (recipient or "").strip()
        text = (message or "").strip()
        file_url = (file_url or "").strip()
        
        if not recip:
            self.errorReceived.emit("Recipient is required for private messages.")
            return
        
        if file_url:
            try:
                print(f"[ChatClient] sendPrivateMessageWithAttachment: file_url={file_url}, recipient={recip}")
                file_path = FileValidator.normalize_file_path(file_url)
                if not file_path:
                    print(f"[ChatClient] Failed to normalize file path from: {file_url}")
                    self.errorReceived.emit("Invalid file selection.")
                    return
                
                print(f"[ChatClient] Normalized file path: {file_path}")
                
                # Resolve and validate file exists
                resolved = file_path.resolve(strict=True)
                if not resolved.is_file():
                    print(f"[ChatClient] Path is not a file: {resolved}")
                    self.errorReceived.emit("Selection is not a file.")
                    return
                
                # Read file
                file_data = resolved.read_bytes()
                filename = resolved.name
                
                print(f"[ChatClient] File loaded: filename={filename}, size={len(file_data)} bytes")
                
                # Send file chunks first to get transfer_id
                transfer_id = self._file_handler.send_file_chunks(file_data, filename, recip)
                print(f"[ChatClient] File transfer started: transfer_id={transfer_id}")
                
                # Create file payload for message
                file_payload = {
                    "transfer_id": transfer_id,
                    "filename": filename,
                    "size": len(file_data),
                }
                print(f"[ChatClient] File payload for message: {file_payload}")
                
                # Send message with file metadata
                if text or transfer_id:
                    self._message_handler.send_private_message(recip, text, file_payload)
                    print(f"[ChatClient] Private message sent with file metadata")
            except FileNotFoundError:
                print(f"[ChatClient] File not found: {file_url}")
                self.errorReceived.emit("File not found.")
            except PermissionError:
                print(f"[ChatClient] Permission denied reading file: {file_url}")
                self.errorReceived.emit("Permission denied reading file.")
            except Exception as e:
                print(f"[ChatClient] Failed to read file: {e}")
                import traceback
                traceback.print_exc()
                self.errorReceived.emit("Failed to read file.")
        else:
            if not text:
                self.errorReceived.emit("Cannot send an empty message.")
                return
            self._message_handler.send_private_message(recip, text)
    
    @Slot(str, result=dict)
    def inspectFile(self, file_url: str):
        """Inspect file and return metadata without reading content."""
        try:
            print(f"[ChatClient] inspectFile called with: {file_url}")
            
            file_path = FileValidator.normalize_file_path(file_url)
            if not file_path:
                print(f"[ChatClient] Failed to normalize file path from: {file_url}")
                self.errorReceived.emit("Invalid file selection.")
                print(f"[ChatClient] Returning empty dict")
                return {}
            
            print(f"[ChatClient] Normalized file path: {file_path}")
            
            # Only validate file exists and get metadata, don't read content
            try:
                resolved = file_path.resolve(strict=True)
            except (OSError, RuntimeError) as e:
                print(f"[ChatClient] Failed to resolve file path: {e}")
                self.errorReceived.emit("File not found.")
                print(f"[ChatClient] Returning empty dict")
                return {}
            
            print(f"[ChatClient] Resolved file path: {resolved}")
            
            if not resolved.is_file():
                print(f"[ChatClient] Path is not a file: {resolved}")
                self.errorReceived.emit("Selection is not a file.")
                print(f"[ChatClient] Returning empty dict")
                return {}
            
            try:
                size = resolved.stat().st_size
            except OSError as e:
                print(f"[ChatClient] Cannot access file stats: {e}")
                self.errorReceived.emit("Cannot access file.")
                print(f"[ChatClient] Returning empty dict")
                return {}
            
            print(f"[ChatClient] File size: {size} bytes")
            
            if size <= 0 or size > 5 * 1024 * 1024:  # 5 MB limit
                print(f"[ChatClient] File size out of range: {size}")
                self.errorReceived.emit("File must be between 1 byte and 5 MB.")
                print(f"[ChatClient] Returning empty dict")
                return {}
            
            import mimetypes
            mime, _ = mimetypes.guess_type(str(resolved))
            mime = mime or "application/octet-stream"
            
            result = {
                "path": str(resolved),
                "name": resolved.name,
                "size": size,
                "mime": mime,
            }
            print(f"[ChatClient] inspectFile result: {result}")
            print(f"[ChatClient] Returning result dict with keys: {list(result.keys())}")
            return result
        except Exception as e:
            print(f"[ChatClient] Error inspecting file: {e}")
            import traceback
            traceback.print_exc()
            self.errorReceived.emit("Error inspecting file.")
            print(f"[ChatClient] Returning empty dict due to exception")
            return {}

    @Slot(bool)
    def indicatePublicTyping(self, is_typing: bool):
        """Send public typing indicator."""
        self._typing_handler.indicate_public_typing(is_typing)
    
    @Slot(str, bool)
    def indicatePrivateTyping(self, recipient: str, is_typing: bool):
        """Send private typing indicator."""
        self._typing_handler.indicate_private_typing(recipient, is_typing)
    
    @Slot(str, object)
    def markPrivateMessagesRead(self, recipient: str, message_ids):
        """Mark private messages as read."""
        self._message_handler.mark_messages_read(recipient, list(message_ids))
    
    @Slot(str)
    def setAvatar(self, file_url: str):
        """Upload avatar image."""
        self._avatar_handler.set_avatar(file_url)
    
    @Slot(str, str, str, result=str)
    def saveFileToTemp(self, filename: str, data: str, mime: str) -> str:
        """Save file to temp directory."""
        return self._file_handler.save_file_to_temp(filename, data, mime)
    
    @Slot(str, str, str, result=str)
    def saveFileToDownloads(self, filename: str, data: str, mime: str) -> str:
        """Save file to Downloads directory (for inline/base64 data)."""
        return self._file_handler.save_file_to_downloads(filename, data, mime)
    
    @Slot(str, str, result=str)
    def downloadReceivedFile(self, transfer_id: str, filename: str) -> str:
        """Download a received file (chunked transfer) to Downloads directory."""
        return self._file_handler.download_received_file(transfer_id, filename)
    
    @Slot()
    def disconnect(self):
        """Disconnect from server (user-requested)."""
        print("[ChatClient] User requested disconnect")
        self._desired_username = ""
        self._connection_manager.disconnect(user_requested=True)
    
    @Slot(str)
    def copyToClipboard(self, text: str):
        """Copy text to system clipboard."""
        try:
            from PySide6.QtGui import QGuiApplication
            clipboard = QGuiApplication.clipboard()
            if clipboard:
                clipboard.setText(text)
                print(f"[ChatClient] Copied to clipboard: {text[:50]}...")
        except Exception as e:
            print(f"[ChatClient] Failed to copy to clipboard: {e}")
    
    # Properties
    @Property(str, notify=usernameChanged)
    def username(self):
        return self._username
    
    @Property(str, notify=connectionStateChanged)
    def connectionState(self):
        return self._connection_manager.connection_state