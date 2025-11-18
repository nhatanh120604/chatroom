import logging


class TypingHandler:
    """Handles typing indicators"""
    
    def __init__(self, sio, user_service):
        self.sio = sio
        self.user_service = user_service
    
    def on_typing(self, sid, data):
        """Handle typing indicator."""
        username = self.user_service.get_username(sid)
        
        if username == "Unknown":
            logging.warning(f"Typing event from unknown SID: {sid}")
            return
        
        context = data.get("context")
        is_typing = bool(data.get("is_typing"))
        
        if context == "public":
            self.sio.emit(
                "public_typing",
                {"username": username, "is_typing": is_typing},
                skip_sid=sid
            )
        elif context == "private":
            recipient_username = data.get("recipient")
            if not recipient_username:
                return
            
            recipient_sid = self.user_service.find_user_sid(recipient_username)
            if recipient_sid:
                self.sio.emit(
                    "private_typing",
                    {"username": username, "is_typing": is_typing},
                    to=recipient_sid
                )