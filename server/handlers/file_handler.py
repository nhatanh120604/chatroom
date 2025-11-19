import os
import base64
import logging
from datetime import datetime, timezone
from config import Config


class FileHandler:
    """Handles file transfer operations"""
    
    def __init__(self, sio, user_service, file_transfer_service, encryption_service):
        self.sio = sio
        self.user_service = user_service
        self.file_transfer_service = file_transfer_service
        self.encryption_service = encryption_service
    
    def on_public_file_chunk(self, sid, data):
        """Handle public file chunk."""
        self._handle_file_chunk(sid, data, is_private=False)
    
    def on_private_file_chunk(self, sid, data):
        """Handle private file chunk."""
        self._handle_file_chunk(sid, data, is_private=True)
    
    def _handle_file_chunk(self, sid, data, is_private):
        """Process incoming file chunk."""
        sender_username = self.user_service.get_username(sid)
        transfer_id = data.get("transfer_id")
        chunk_index = data.get("chunk_index")
        is_last_chunk = data.get("is_last_chunk", False)
        metadata = data.get("metadata")
        
        # Log chunk reception
        if metadata:
            total_chunks = metadata.get("total_chunks", "?")
            filename = metadata.get("filename", "unknown")
            logging.info(f"[FILE TRANSFER] START: transfer_id={transfer_id}, file={filename}, "
                        f"total_chunks={total_chunks}, type={'private' if is_private else 'public'}")
        else:
            logging.debug(f"[FILE TRANSFER] CHUNK: transfer_id={transfer_id}, "
                         f"chunk_index={chunk_index}, is_last={is_last_chunk}")
        
        # Get session key for decryption
        session_key = self.user_service.get_session_key(sid)
        if not session_key:
            error_msg = "Session key not established"
            logging.error(f"[FILE TRANSFER] ERROR: {error_msg} for {sender_username}")
            self.sio.emit("error", {"message": error_msg}, to=sid)
            return
        
        # Handle chunk
        success, error, is_complete, file_path = \
            self.file_transfer_service.handle_chunk(
                sid, sender_username, data, session_key, is_private
            )
        
        if not success:
            logging.error(f"[FILE TRANSFER] ERROR: transfer_id={transfer_id}, error={error}")
            self.sio.emit("error", {"message": error}, to=sid)
            return
        
        if not is_complete:
            logging.debug(f"[FILE TRANSFER] WAITING: transfer_id={transfer_id}, "
                         f"chunk_index={chunk_index}")
            return  # Wait for more chunks
        
        # File complete - broadcast to recipients
        logging.info(f"[FILE TRANSFER] COMPLETE: transfer_id={transfer_id}, "
                    f"file_path={file_path}, ready to broadcast")
        self._broadcast_file(transfer_id, file_path, sender_username)
    
    def _broadcast_file(self, transfer_id, file_path, sender_username):
        """Broadcast decrypted file to recipients."""
        transfer = self.file_transfer_service.get_transfer_info(transfer_id)
        if not transfer:
            logging.warning(f"Transfer info not found for {transfer_id}")
            return
        
        try:
            # Get file metadata
            chunk_size = transfer["metadata"].get("chunk_size", Config.DEFAULT_CHUNK_SIZE)
            filename = transfer["metadata"].get("filename", "file")
            
            # Calculate file details
            file_size = os.path.getsize(file_path)
            total_chunks = max(1, (file_size + chunk_size - 1) // chunk_size)
            
            # Determine target recipient(s)
            target_sid = None
            if transfer["is_private"] and transfer["recipient"]:
                target_sid = self.user_service.find_user_sid(transfer["recipient"])
                if not target_sid:
                    self.sio.emit(
                        "error",
                        {"message": f"Recipient '{transfer['recipient']}' not found"},
                        to=transfer["sender_sid"]
                    )
                    self._cleanup_file_and_transfer(transfer_id, file_path)
                    return
            
            server_ts = datetime.now(timezone.utc).isoformat()
            
            # Stream file to recipient(s) in chunks
            logging.info(f"Broadcasting file {transfer_id}: {filename} ({total_chunks} chunks)")
            
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
                    
                    # Emit to target recipient or broadcast to all
                    if target_sid:
                        self.sio.emit("file_chunk", payload, to=target_sid)
                    else:
                        self.sio.emit("file_chunk", payload)
            
            logging.info(f"File broadcast complete: {transfer_id} ({total_chunks} chunks)")
            
        except OSError as e:
            logging.error(f"Failed to broadcast file {transfer_id}: {e}")
            self.sio.emit(
                "error",
                {"message": f"Server streaming error: {e}"},
                to=transfer["sender_sid"]
            )
        except Exception as e:
            logging.error(f"Unexpected error broadcasting file {transfer_id}: {e}")
            self.sio.emit(
                "error",
                {"message": f"Server error: {e}"},
                to=transfer["sender_sid"]
            )
        finally:
            # Always cleanup
            self._cleanup_file_and_transfer(transfer_id, file_path)
    
    def _cleanup_file_and_transfer(self, transfer_id, file_path):
        """Clean up transfer tracking and temporary file."""
        self.file_transfer_service.cleanup_transfer(transfer_id)
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
                logging.debug(f"Removed temporary file: {file_path}")
        except OSError as e:
            logging.warning(f"Failed to remove temporary file {file_path}: {e}")
    
    def on_file_transfer_ack(self, sid, data):
        """Handle file transfer acknowledgment from client."""
        transfer_id = data.get("transfer_id")
        success = data.get("success", False)
        error_msg = data.get("error", "")
        
        if not transfer_id:
            logging.warning(f"File transfer ack missing transfer_id from {sid}")
            return
        
        transfer = self.file_transfer_service.get_transfer_info(transfer_id)
        
        if transfer and transfer.get("sender_sid"):
            # Forward acknowledgment to the sender
            self.sio.emit(
                "file_transfer_ack",
                {
                    "transfer_id": transfer_id,
                    "success": success,
                    "error": error_msg,
                },
                to=transfer["sender_sid"]
            )
            
            if success:
                logging.info(f"File transfer {transfer_id} acknowledged successfully")
            else:
                logging.warning(f"File transfer {transfer_id} failed: {error_msg}")
        
        # Clean up transfer tracking
        self.file_transfer_service.cleanup_transfer(transfer_id)