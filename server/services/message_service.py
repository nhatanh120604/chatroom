import threading
import logging


class MessageService:
    """Manages private messages and their states"""
    
    def __init__(self):
        self.private_messages = {}  # message_id -> metadata
        self.message_counter = 0
        self.lock = threading.Lock()
    
    def create_private_message(self, sender_sid, recipient_sid):
        """Create a new private message and return its ID."""
        with self.lock:
            self.message_counter += 1
            message_id = self.message_counter
            self.private_messages[message_id] = {
                "sender_sid": sender_sid,
                "recipient_sid": recipient_sid,
                "status": "sent",
            }
        return message_id
    
    def mark_messages_as_read(self, reader_sid, message_ids):
        """Mark messages as read. Returns list of (sender_sid, message_id) to notify."""
        if not isinstance(message_ids, list):
            message_ids = [message_ids]
        
        acknowledgements = []
        
        with self.lock:
            for raw_id in message_ids:
                try:
                    message_id = int(raw_id)
                except (TypeError, ValueError):
                    continue
                
                message_meta = self.private_messages.get(message_id)
                if not message_meta:
                    continue
                
                if message_meta.get("recipient_sid") != reader_sid:
                    continue
                
                if message_meta.get("status") == "seen":
                    continue
                
                message_meta["status"] = "seen"
                acknowledgements.append(
                    (message_meta.get("sender_sid"), message_id)
                )
        
        return acknowledgements