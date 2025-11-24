import base64
import logging
from typing import Optional, Tuple, List
from PySide6.QtCore import QObject, Signal
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend

logger = logging.getLogger(__name__)

# Import encryption with error handling
try:
    from ..handlers.encryption import generate_aes_key, rsa_encrypt_with_server_public_key
    logger.debug("[SessionManager] Successfully imported encryption functions")
except ImportError as e:
    logger.error(f"[SessionManager] Failed to import encryption functions: {e}")
    raise           


class SessionManager(QObject):
    """Manages encryption session key exchange."""
    
    sessionReady = Signal()
    sessionError = Signal(str)
    
    def __init__(self):
        super().__init__()
        self._session_aes_key: Optional[bytes] = None
        self._session_ready = False
        self._post_key_queue: List[Tuple[str, dict]] = []
    
    @property
    def session_key(self) -> Optional[bytes]:
        return self._session_aes_key
    
    @property
    def is_ready(self) -> bool:
        return self._session_ready
    
    def generate_and_exchange(self, server_url: str) -> Optional[str]:
        """Generate AES key and encrypt with server's public key."""
        try:
            logger.debug("[SessionManager] Starting key generation")
            try:
                self._session_aes_key = generate_aes_key()
                logger.debug("[SessionManager] AES key generated successfully")
            except Exception as e:
                logger.error(f"[SessionManager] Failed to generate AES key: {e}", exc_info=True)
                raise
            
            try:
                encrypted = rsa_encrypt_with_server_public_key(
                    self._session_aes_key, server_url
                )
                logger.debug("[SessionManager] RSA encryption successful")
                return encrypted
            except Exception as e:
                logger.error(f"[SessionManager] Failed to encrypt with server public key: {e}", exc_info=True)
                raise
        except Exception as e:
            logger.error(f"[SessionManager] Key exchange failed: {e}", exc_info=True)
            self.sessionError.emit(str(e))
            return None
    
    def on_session_ack(self):
        """Called when server acknowledges session key."""
        self._session_ready = True
        self.sessionReady.emit()
    
    def queue_event(self, event: str, payload: dict):
        """Queue event until session is ready."""
        self._post_key_queue.append((event, payload))
    
    def flush_queue(self) -> List[Tuple[str, dict]]:
        """Get and clear queued events."""
        queued = list(self._post_key_queue)
        self._post_key_queue.clear()
        return queued
    
    def reset(self):
        """Reset session state."""
        self._session_aes_key = None
        self._session_ready = False
        self._post_key_queue.clear()