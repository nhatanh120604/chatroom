import threading
from config import Config


class HistoryService:
    """Manages message history"""
    
    def __init__(self):
        self.public_history = []
        self.lock = threading.Lock()
    
    def add_message(self, message_data):
        """Add message to public history."""
        with self.lock:
            self.public_history.append(message_data)
            if len(self.public_history) > Config.MAX_PUBLIC_HISTORY:
                self.public_history.pop(0)
    
    def get_history(self):
        """Get snapshot of public message history."""
        with self.lock:
            return list(self.public_history)