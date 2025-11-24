import logging
from config import Config

def sanitize_file_payload(data):
    """Validate and clamp incoming file payloads."""
    logging.debug(f"[SANITIZE] Input data: type={type(data)}, value={data}")
    
    if not isinstance(data, dict):
        logging.debug(f"[SANITIZE] Not a dict, returning None")
        return None

    # Support both old format (with base64 data) and new format (with transfer_id)
    transfer_id = data.get("transfer_id")
    filename = str(data.get("filename", ""))[:255]
    size = data.get("size", 0)
    
    logging.debug(f"[SANITIZE] Extracted: transfer_id={transfer_id}, filename={filename}, size={size}")
    
    try:
        size = int(size)
    except (TypeError, ValueError):
        size = 0

    # New format: transfer_id, filename, size (for chunked file transfers)
    if transfer_id:
        logging.debug(f"[SANITIZE] Has transfer_id, validating...")
        if not filename:
            logging.warning("Rejected file payload: missing filename")
            return None
        
        if size <= 0 or size > Config.MAX_FILE_BYTES:
            logging.warning("Rejected file '%s' with invalid size: %d", filename, size)
            return None
        
        result = {
            "transfer_id": transfer_id,
            "filename": filename,
            "size": size,
        }
        logging.debug(f"[SANITIZE] Returning sanitized payload: {result}")
        return result
    
    # Old format: name, mime, data (for inline file data)
    name = str(data.get("name", ""))[:255]
    mime = str(data.get("mime", "application/octet-stream"))[:255]
    b64_data = data.get("data")
    
    if not isinstance(b64_data, str) or not b64_data:
        logging.debug("File payload has no data or transfer_id")
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
