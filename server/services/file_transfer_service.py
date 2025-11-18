import os
import base64
import threading
import logging
from datetime import datetime, timezone
from config import Config


class FileTransferService:
    """Manages file transfers with encryption/decryption"""
    
    def __init__(self, encryption_service):
        self.encryption_service = encryption_service
        self.active_transfers = {}  # transfer_id -> transfer_info
        self.lock = threading.Lock()
        self._ensure_upload_dir()
    
    def _ensure_upload_dir(self):
        """Create uploads directory if it doesn't exist."""
        try:
            os.makedirs(Config.UPLOAD_DIR, exist_ok=True)
        except OSError as e:
            logging.error(f"Failed to create upload directory: {e}")
    
    def handle_chunk(self, sid, sender_username, data, is_private=False):
        """
        Handle incoming file chunk.
        Returns (success, error_message, is_complete, decrypted_path)
        """
        transfer_id = data.get("transfer_id")
        chunk_index = data.get("chunk_index")
        chunk_data = data.get("chunk_data")
        metadata = data.get("metadata")
        recipient = data.get("recipient") if is_private else None
        
        if not all([transfer_id, chunk_index is not None, chunk_data]):
            return False, "Invalid file chunk", False, None
        
        with self.lock:
            # Initialize transfer if new
            if transfer_id not in self.active_transfers:
                self.active_transfers[transfer_id] = {
                    "sender_sid": sid,
                    "sender_username": sender_username,
                    "recipient": recipient,
                    "is_private": is_private,
                    "total_chunks": 0,
                    "received_chunks": 0,
                    "metadata": None,
                    "encrypted_chunks": {},
                }
            
            transfer = self.active_transfers[transfer_id]
            
            # Store metadata from first chunk
            if metadata and chunk_index == 0:
                transfer["metadata"] = metadata
                transfer["total_chunks"] = metadata.get("total_chunks", 0)
                transfer["iv"] = metadata.get("iv")
            
            transfer["received_chunks"] += 1
            transfer["encrypted_chunks"][chunk_index] = base64.b64decode(chunk_data)
            
            # Check if transfer is complete
            is_complete = (
                transfer["received_chunks"] >= transfer["total_chunks"]
                and transfer["total_chunks"] > 0
            )
            
            if not is_complete:
                return True, "", False, None
            
            # Decrypt and save file
            try:
                decrypted_path = self._decrypt_and_save(transfer_id, transfer, sid)
                return True, "", True, decrypted_path
            except Exception as e:
                logging.error(f"File decryption failed: {e}")
                self.cleanup_transfer(transfer_id)
                return False, str(e), False, None
    
    def _decrypt_and_save(self, transfer_id, transfer, sender_sid):
        """Decrypt file and save to disk."""
        from services.encryption_service import EncryptionService
        
        # Get session key
        # Note: This needs access to session keys - passed through or refactored
        # For now, assume it's available through encryption service
        
        iv_b64 = transfer.get("iv", "")
        iv = base64.b64decode(iv_b64)
        
        # Reassemble ciphertext
        chunks_dict = transfer["encrypted_chunks"]
        ciphertext = b"".join(chunks_dict[i] for i in sorted(chunks_dict.keys()))
        
        # This needs the session key - should be passed in or refactored
        # For now, placeholder:
        # plaintext = EncryptionService.aes_decrypt(ciphertext, key, iv)
        # We'll need to refactor to pass the key
        
        # Save to disk
        filename = transfer["metadata"].get("filename", "file")
        safe_name = os.path.basename(filename) or "file"
        out_path = os.path.join(Config.UPLOAD_DIR, f"{transfer_id}_{safe_name}")
        
        # Placeholder - actual decryption needs session key
        # with open(out_path, "wb") as f:
        #     f.write(plaintext)
        
        return out_path
    
    def get_transfer_info(self, transfer_id):
        """Get transfer information."""
        with self.lock:
            return self.active_transfers.get(transfer_id)
    
    def cleanup_transfer(self, transfer_id):
        """Remove transfer from tracking."""
        with self.lock:
            if transfer_id in self.active_transfers:
                del self.active_transfers[transfer_id]