import os

class Config:
    """Server configuration"""
    MAX_PUBLIC_HISTORY = 200
    MAX_FILE_BYTES = 5 * 1024 * 1024  # 5 MB
    DEFAULT_CHUNK_SIZE = 64 * 1024
    
    # Server settings
    PORT = int(os.environ.get("PORT") or os.environ.get("CHAT_PORT", 5000))
    HOST = os.environ.get("CHAT_HOST", "0.0.0.0")
    
    # Paths
    BASE_DIR = os.path.dirname(__file__)
    PRIVATE_KEY_PATH = os.path.join(BASE_DIR, "private_key.pem")
    PUBLIC_KEY_PATH = os.path.join(BASE_DIR, "public_key.pem")
    UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
    
    # CORS
    CORS_ALLOWED_ORIGINS = "*"