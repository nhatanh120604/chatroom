import logging
import os
import base64
from datetime import datetime, timezone


class ConnectionHandler:
    """Handles client connection/disconnection events"""
    
    def __init__(self, sio, user_service, history_service, file_transfer_service=None):
        self.sio = sio
        self.user_service = user_service
        self.history_service = history_service
        self.file_transfer_service = file_transfer_service
    
    def on_connect(self, sid, environ):
        """Handle client connection."""
        logging.info(f"Client connected: {sid}")
        
        # Send chat history to new client
        history = self.history_service.get_history()
        if history:
            self.sio.emit("chat_history", {"messages": history}, to=sid)
    
    def on_disconnect(self, sid):
        """Handle client disconnection."""
        logging.info(f"Client disconnected: {sid}")
        
        username, users_list = self.user_service.unregister_user(sid)
        
        if username:
            # Notify remaining clients of user list update
            self.sio.emit("update_user_list", {"users": users_list})
            
            # Send system message that user left the chat
            server_ts = datetime.now(timezone.utc).isoformat()
            system_message = {
                "username": "System",
                "message": f"{username} has left the chat",
                "timestamp": server_ts,
            }
            self.sio.emit("message", system_message)
    
    def on_file_transfer_ack(self, sid, data):
        """Handle file transfer acknowledgment."""
        transfer_id = data.get("transfer_id")
        success = data.get("success", False)
        error_msg = data.get("error", "")
        
        transfer = self.file_transfer_service.get_transfer_info(transfer_id)
        if transfer and transfer.get("sender_sid"):
            self.sio.emit(
                "file_transfer_ack",
                {
                    "transfer_id": transfer_id,
                    "success": success,
                    "error": error_msg,
                },
                to=transfer["sender_sid"]
            )
        
        self.file_transfer_service.cleanup_transfer(transfer_id)

    def on_register(self, sid, data):
        """Handle user registration."""
        username = data.get("username")
        
        success, message, users_list = self.user_service.register_user(sid, username)
        
        if not success:
            self.sio.emit("error", {"message": message}, to=sid)
            logging.warning(f"Registration failed for {sid}: {message}")
            return
        
        # Notify all clients with updated user list
        self.sio.emit("update_user_list", {"users": users_list})
        
        # Send history to new user
        history = self.history_service.get_history()
        if history:
            self.sio.emit("chat_history", {"messages": history}, to=sid)
    
    def on_request_history(self, sid, data=None):
        """Handle history request."""
        history = self.history_service.get_history()
        self.sio.emit("chat_history", {"messages": history}, to=sid)