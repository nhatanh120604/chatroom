import logging
from datetime import datetime, timezone


class ConnectionHandler:
    """Handles client connection/disconnection events"""
    
    def __init__(self, sio, user_service, history_service):
        self.sio = sio
        self.user_service = user_service
        self.history_service = history_service
    
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
            # Notify remaining clients
            self.sio.emit("update_user_list", {"users": users_list})
            
            # Send system message
            server_ts = datetime.now(timezone.utc).isoformat()
            
            # Stream file in chunks
            try: 
                with open(file_path, "rb") as f:
                    for chunk_idx in range(total_chunks):
                        chunk_data = f.read(chunk_size)
                        if not chunk_data:
                            break
                        
                        payload = {
                            "transfer_id": transfer_id,
                            "chunk_index": chunk_idx,
                            "chunk_data": base64.b64encode(chunk_data).decode("utf-8"),
                            "is_last_chunk": chunk_idx == total_chunks - 1,
                        }
                        
                        # Include metadata in first chunk
                        if chunk_idx == 0:
                            payload["metadata"] = {
                                "filename": os.path.basename(filename),
                                "total_size": file_size,
                                "total_chunks": total_chunks,
                                "chunk_size": chunk_size,
                                "username": sender_username,
                                "timestamp": server_ts,
                                "is_private": bool(transfer["is_private"]),
                                "recipient": transfer["recipient"] if transfer["is_private"] else "",
                            }
                        
                        # Emit to target or broadcast
                        if target_sid:
                            self.sio.emit("file_chunk", payload, to=target_sid)
                        else:
                            self.sio.emit("file_chunk", payload)
                
                logging.info(f"File broadcast complete: {transfer_id} ({total_chunks} chunks)")
            
            except Exception as e:
                logging.error(f"Failed to broadcast file: {e}")
                self.sio.emit(
                    "error",
                    {"message": f"Server streaming error: {e}"},
                    to=transfer["sender_sid"]
                )
            finally:
                # Cleanup
                self.file_transfer_service.cleanup_transfer(transfer_id)
                try:
                    os.remove(file_path)
                except OSError:
                    pass
    
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