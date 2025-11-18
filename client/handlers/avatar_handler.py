import base64
import mimetypes
from pathlib import Path
from typing import Optional
from PySide6.QtCore import QObject, Signal


MAX_AVATAR_BYTES = 128 * 1024  # 128 KB


class AvatarHandler(QObject):
    """Handles avatar uploads."""
    
    errorNotification = Signal(str)
    
    def __init__(self, emit_callback):
        super().__init__()
        self._emit = emit_callback
    
    def set_avatar(self, file_url: str):
        """Upload avatar image."""
        path = self._normalize_file_path(file_url)
        if not path:
            self.errorNotification.emit("Invalid avatar selection.")
            return
        
        try:
            resolved = path.resolve(strict=True)
        except (OSError, RuntimeError):
            self.errorNotification.emit("Avatar file could not be accessed.")
            return
        
        if not resolved.is_file():
            self.errorNotification.emit("Avatar must be a regular image file.")
            return
        
        try:
            raw = resolved.read_bytes()
        except OSError:
            self.errorNotification.emit("Failed to read avatar file.")
            return
        
        if not raw or len(raw) > MAX_AVATAR_BYTES:
            self.errorNotification.emit("Avatar must be under 128 KB.")
            return
        
        mime, _ = mimetypes.guess_type(str(resolved))
        mime = mime or "image/png"
        
        if not mime.startswith("image/"):
            self.errorNotification.emit("Avatar must be an image.")
            return
        
        payload = {
            "mime": mime,
            "data": base64.b64encode(raw).decode("ascii"),
        }
        
        self._emit("set_avatar", payload)
    
    def _normalize_file_path(self, file_url: str) -> Optional[Path]:
        """Convert file URL to Path."""
        from PySide6.QtCore import QUrl
        
        candidate = (file_url or "").strip()
        if not candidate:
            return None
        
        qurl = QUrl(candidate)
        if qurl.isValid() and qurl.scheme().lower() == "file":
            if qurl.isLocalFile():
                candidate = qurl.toLocalFile()
            else:
                return None
        
        return Path(candidate)