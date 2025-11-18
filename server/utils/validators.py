import logging
from config import Config

def sanitize_file_payload(data):
    """Validate and clamp incoming file payloads."""
    if not isinstance(data, dict):
        return None

    name = str(data.get("name", ""))[:255]
    mime = str(data.get("mime", "application/octet-stream"))[:255]
    size = data.get("size", 0)
    
    try:
        size = int(size)
    except (TypeError, ValueError):
        size = 0

    b64_data = data.get("data")
    if not isinstance(b64_data, str) or not b64_data:
        return None

    if size > Config.MAX_FILE_BYTES:
        logging.warning("Rejected file '%s' exceeding size cap", name)
        return None

    if len(b64_data) > (Config.MAX_FILE_BYTES * 4) // 3 + 8:
        logging.warning("Rejected file '%s' due to encoded length", name)
        return None

    return {
        "name": name,
        "mime": mime,
        "size": size,
        "data": b64_data,
    }


def validate_username(username):
    """Validate username format."""
    if not username or not isinstance(username, str):
        return False, "A valid username is required."
    
    username = username.strip()
    if not username:
        return False, "Username cannot be empty."
    
    if len(username) > 50:
        return False, "Username too long (max 50 characters)."
    
    return True, username


def validate_message(message, file_payload=None):
    """Validate message content."""
    if isinstance(message, str):
        message = message.strip()
    else:
        message = ""
    
    if not message and not file_payload:
        return False, "Cannot send an empty message."
    
    return True, message
