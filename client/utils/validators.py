from pathlib import Path
from typing import Optional, Dict, Any
import mimetypes
import base64


MAX_FILE_BYTES = 5 * 1024 * 1024


class FileValidator:
    """Validates file operations."""
    
    @staticmethod
    def normalize_file_path(file_url: str) -> Optional[Path]:
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
    
    @staticmethod
    def validate_and_prepare_file(file_path: Path) -> Optional[Dict[str, Any]]:
        """Validate file and prepare payload."""
        try:
            resolved = file_path.resolve(strict=True)
        except (OSError, RuntimeError):
            return None
        
        if not resolved.is_file():
            return None
        
        try:
            size = resolved.stat().st_size
        except OSError:
            return None
        
        if size <= 0 or size > MAX_FILE_BYTES:
            return None
        
        try:
            raw = resolved.read_bytes()
        except OSError:
            return None
        
        encoded = base64.b64encode(raw).decode("ascii")
        mime, _ = mimetypes.guess_type(str(resolved))
        mime = mime or "application/octet-stream"
        
        return {
            "name": resolved.name,
            "size": size,
            "mime": mime,
            "data": encoded,
        }
