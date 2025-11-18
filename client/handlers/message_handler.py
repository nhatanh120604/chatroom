from typing import Optional, Dict, List
import base64
from PySide6.QtCore import QObject, Signal
from datetime import datetime, timezone


class MessageHandler(QObject):
    """Handles message sending and receiving."""
    
    messageReceived = Signal(str, str, object)  # username, message, file
    messageReceivedEx = Signal(str, str, object, str)  # + timestamp
    privateMessageReceived = Signal(str, str, str, int, str, object)
    privateMessageReceivedEx = Signal(str, str, str, int, str, object, str)
    privateMessageSent = Signal(str, str, str, int, str, object)
    privateMessageSentEx = Signal(str, str, str, int, str, object, str)
    privateMessageRead = Signal(int)
    generalHistoryReceived = Signal(object)
    
    def __init__(self, session_manager, emit_callback):
        super().__init__()
        self._session_manager = session_manager
        self._emit = emit_callback
    
    def send_public_message(self, text: str, file_payload: Optional[Dict] = None):
        """Send encrypted public message."""
        try:
            from ..network.encryption import aes_encrypt
            
            if not self._session_manager.session_key:
                raise ValueError("Session key not established")
            
            ciphertext, iv = aes_encrypt(
                text.encode("utf-8"),
                self._session_manager.session_key
            )
            
            payload = {
                "enc": True,
                "ciphertext": base64.b64encode(ciphertext).decode("utf-8"),
                "iv": base64.b64encode(iv).decode("utf-8"),
            }
            
            if file_payload:
                payload["file"] = file_payload
            
            self._emit("message", payload)
            
        except Exception as e:
            print(f"[MessageHandler] Failed to send message: {e}")
            raise
    
    def send_private_message(
        self,
        recipient: str,
        text: str,
        file_payload: Optional[Dict] = None
    ):
        """Send encrypted private message."""
        try:
            from ..network.encryption import aes_encrypt
            
            if not self._session_manager.session_key:
                raise ValueError("Session key not established")
            
            ciphertext, iv = aes_encrypt(
                text.encode("utf-8"),
                self._session_manager.session_key
            )
            
            payload = {
                "recipient": recipient,
                "enc": True,
                "ciphertext": base64.b64encode(ciphertext).decode("utf-8"),
                "iv": base64.b64encode(iv).decode("utf-8"),
            }
            
            if file_payload:
                payload["file"] = file_payload
            
            self._emit("private_message", payload)
            
        except Exception as e:
            print(f"[MessageHandler] Failed to send private message: {e}")
            raise
    
    def mark_messages_read(self, recipient: str, message_ids: List[int]):
        """Mark private messages as read."""
        if not recipient or not message_ids:
            return
        
        sanitized = [int(mid) for mid in message_ids if isinstance(mid, (int, str))]
        if not sanitized:
            return
        
        payload = {"recipient": recipient, "message_ids": sanitized}
        self._emit("private_message_read", payload)
    
    def request_history(self):
        """Request public chat history."""
        self._emit("request_history", {})