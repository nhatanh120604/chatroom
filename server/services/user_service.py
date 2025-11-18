import threading
import logging
from utils.validators import validate_username


class UserService:
    """Manages user registrations and sessions"""
    
    def __init__(self):
        self.clients = {}  # sid -> username
        self.session_keys = {}  # sid -> AES key
        self.lock = threading.Lock()
    
    def register_user(self, sid, username):
        """Register a new user. Returns (success, message, users_list)."""
        is_valid, result = validate_username(username)
        if not is_valid:
            return False, result, None
        
        username = result
        
        with self.lock:
            # Check for duplicate username (case-insensitive)
            if any((name or "").lower() == username.lower() 
                   for name in self.clients.values()):
                return False, f"Username '{username}' is already taken.", None
            
            self.clients[sid] = username
            users_list = list(self.clients.values())
        
        logging.info(f"User registered: {username} with SID: {sid}")
        return True, "", users_list
    
    def unregister_user(self, sid):
        """Remove user and return username if existed."""
        with self.lock:
            username = self.clients.pop(sid, None)
            self.session_keys.pop(sid, None)
            users_list = list(self.clients.values()) if username else None
        
        if username:
            logging.info(f"User unregistered: {username}")
        
        return username, users_list
    
    def get_username(self, sid):
        """Get username for a session ID."""
        with self.lock:
            return self.clients.get(sid, "Unknown")
    
    def get_users_list(self):
        """Get list of all connected users."""
        with self.lock:
            return list(self.clients.values())
    
    def find_user_sid(self, username):
        """Find session ID for a username."""
        with self.lock:
            for sid, name in self.clients.items():
                if name == username:
                    return sid
        return None
    
    def store_session_key(self, sid, key):
        """Store AES session key for a user."""
        with self.lock:
            self.session_keys[sid] = key
        logging.info(f"Stored session key for {sid}")
    
    def get_session_key(self, sid):
        """Retrieve AES session key for a user."""
        with self.lock:
            return self.session_keys.get(sid)