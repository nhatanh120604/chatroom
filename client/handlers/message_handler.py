from typing import Optional, Dict, List
import base64
import logging
from PySide6.QtCore import QObject, Signal
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# Import encryption with error handling
try:
    from .encryption import aes_encrypt
    logger.debug("[MessageHandler] Successfully imported aes_encrypt")
except ImportError as e:
    logger.error(f"[MessageHandler] Failed to import aes_encrypt: {e}")
    raise


class MessageHandler(QObject):
    """Handles message sending and receiving."""
    
    messageReceived = Signal(str, str, "QVariant")  # username, message, file
    messageReceivedEx = Signal(str, str, "QVariant", str)  # + timestamp
    privateMessageReceived = Signal(str, str, str, int, str, "QVariant")
    privateMessageReceivedEx = Signal(str, str, str, int, str, "QVariant", str)
    privateMessageSent = Signal(str, str, str, int, str, "QVariant")
    privateMessageSentEx = Signal(str, str, str, int, str, "QVariant", str)
    privateMessageRead = Signal(int)
    generalHistoryReceived = Signal("QVariant")
    
    def __init__(self, session_manager, emit_callback):
        super().__init__()
        self._session_manager = session_manager
        self._emit = emit_callback
    
    def send_public_message(self, text: str, file_payload: Optional[Dict] = None):
        """Send encrypted public message."""
        try:
            
            session_key = self._session_manager.session_key
            if not session_key:
                raise ValueError("Session key not established")
            
            # Validate session key type
            if not isinstance(session_key, bytes):
                logger.error(f"[MessageHandler] Invalid session key type: {type(session_key)}, expected bytes")
                raise TypeError(f"Session key must be bytes, got {type(session_key).__name__}")
            
            logger.debug(f"[MessageHandler] Using session key of length {len(session_key)} bytes")
            
            try:
                ciphertext, iv = aes_encrypt(
                    text.encode("utf-8"),
                    session_key
                )
            except Exception as e:
                logger.error(f"[MessageHandler] Encryption failed in send_public_message: {e}", exc_info=True)
                raise
            
            payload = {
                "enc": True,
                "ciphertext": base64.b64encode(ciphertext).decode("utf-8"),
                "iv": base64.b64encode(iv).decode("utf-8"),
            }
            
            if file_payload is not None:
                payload["file"] = file_payload
                logger.debug(f"[MessageHandler] Adding file payload to message: {file_payload}")
            
            logger.debug(f"[MessageHandler] Sending message payload with keys: {list(payload.keys())}")
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
            session_key = self._session_manager.session_key
            if not session_key:
                raise ValueError("Session key not established")
            
            # Validate session key type
            if not isinstance(session_key, bytes):
                logger.error(f"[MessageHandler] Invalid session key type: {type(session_key)}, expected bytes")
                raise TypeError(f"Session key must be bytes, got {type(session_key).__name__}")
            
            logger.debug(f"[MessageHandler] Using session key of length {len(session_key)} bytes")
            
            try:
                ciphertext, iv = aes_encrypt(
                    text.encode("utf-8"),
                    session_key
                )
            except Exception as e:
                logger.error(f"[MessageHandler] Encryption failed in send_private_message: {e}", exc_info=True)
                raise
            
            payload = {
                "recipient": recipient,
                "enc": True,
                "ciphertext": base64.b64encode(ciphertext).decode("utf-8"),
                "iv": base64.b64encode(iv).decode("utf-8"),
            }
            
            if file_payload is not None:
                payload["file"] = file_payload
                logger.debug(f"[MessageHandler] Adding file payload to private message: {file_payload}")
            
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