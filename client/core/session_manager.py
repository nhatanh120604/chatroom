import base64
from typing import Optional, Tuple, List
from PySide6.QtCore import QObject, Signal
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend


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
            from ..network.encryption import generate_aes_key, rsa_encrypt_with_server_public_key
            
            self._session_aes_key = generate_aes_key()
            encrypted = rsa_encrypt_with_server_public_key(
                self._session_aes_key, server_url
            )
            return encrypted
        except Exception as e:
            print(f"[SessionManager] Key exchange failed: {e}")
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