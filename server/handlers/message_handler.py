import base64
import logging
from datetime import datetime, timezone
from utils.validators import validate_message, sanitize_file_payload


class MessageHandler:
    """Handles message sending and receiving"""
    
    def __init__(self, sio, user_service, message_service, 
                 history_service, encryption_service):
        self.sio = sio
        self.user_service = user_service
        self.message_service = message_service
        self.history_service = history_service
        self.encryption_service = encryption_service
    
    def on_session_key(self, sid, data):
        """Handle session key establishment."""
        enc_key_b64 = data.get("encrypted_aes_key")
        if not enc_key_b64:
            self.sio.emit("error", {"message": "Missing encrypted AES key."}, to=sid)
            return
        
        try:
            aes_key = self.encryption_service.decrypt_session_key(enc_key_b64)
            self.user_service.store_session_key(sid, aes_key)
            self.sio.emit("session_key_ok", {"ok": True}, to=sid)
        except Exception as e:
            logging.error(f"Failed to decrypt session key from {sid}: {e}")
            self.sio.emit("error", {"message": "Invalid session key."}, to=sid)
    
    def on_message(self, sid, data):
        """Handle public message."""
        sender_username = self.user_service.get_username(sid)
        
        # Debug: Log incoming data
        logging.info(f"[MESSAGE] on_message received data keys: {list(data.keys())}")
        logging.info(f"[MESSAGE] on_message data['file'] value: {data.get('file')}")
        
        # Decrypt if encrypted
        file_payload = None
        if data.get("enc"):
            message_text = self._decrypt_message(sid, data)
            if message_text is None:
                return
            # Extract file payload from encrypted message
            logging.info(f"[MESSAGE] Before sanitize: data.get('file') = {data.get('file')}")
            file_payload = sanitize_file_payload(data.get("file"))
            logging.info(f"[MESSAGE] After sanitize: file_payload = {file_payload}")
            if file_payload:
                logging.info(f"[MESSAGE] Public message with file from {sender_username}: {file_payload}")
        else:
            message_text = data.get("message")
            file_payload = sanitize_file_payload(data.get("file"))
            if file_payload:
                logging.info(f"[MESSAGE] Public message with file from {sender_username}: {file_payload}")
        
        # Validate message
        is_valid, result = validate_message(message_text, file_payload)
        if not is_valid:
            logging.warning(f"Invalid message from {sender_username} ({sid})")
            return
        
        message_text = result
        
        # Prepare broadcast data
        server_ts = data.get("timestamp") or datetime.now(timezone.utc).isoformat()
        broadcast_data = {
            "username": sender_username,
            "message": message_text,
            "timestamp": server_ts,
        }
        if file_payload is not None:
            broadcast_data["file"] = file_payload
            logging.info(f"[MESSAGE] Broadcasting public message with file: {file_payload}")
        
        # Debug: Log what's being emitted
        logging.info(f"[MESSAGE] broadcast_data keys: {list(broadcast_data.keys())}")
        logging.info(f"[MESSAGE] broadcast_data['file'] before emit: {broadcast_data.get('file')}")
        
        # Add to history and broadcast
        self.history_service.add_message(broadcast_data)
        self.sio.emit("message", broadcast_data)
        
        # Debug: Log after emit
        logging.info(f"[MESSAGE] Emitted message event with file: {broadcast_data.get('file')}")
    
    def on_private_message(self, sid, data):
        """Handle private message."""
        sender_username = self.user_service.get_username(sid)
        recipient_username = data.get("recipient")
        
        # Validate recipient
        if not recipient_username or not isinstance(recipient_username, str):
            self.sio.emit("error", {"message": "A valid recipient is required."}, to=sid)
            return
        
        recipient_username = recipient_username.strip()
        
        # Prevent self-messaging
        if sender_username == recipient_username:
            self.sio.emit(
                "error",
                {"message": "You cannot send a private message to yourself."},
                to=sid
            )
            return
        
        # Decrypt if encrypted
        file_payload = None
        if data.get("enc"):
            message = self._decrypt_message(sid, data)
            if message is None:
                return
            # Extract file payload from encrypted message
            file_payload = sanitize_file_payload(data.get("file"))
            if file_payload:
                logging.info(f"[MESSAGE] Private message with file from {sender_username} to {recipient_username}: {file_payload}")
        else:
            message = data.get("message")
            file_payload = sanitize_file_payload(data.get("file"))
            if file_payload:
                logging.info(f"[MESSAGE] Private message with file from {sender_username} to {recipient_username}: {file_payload}")
        
        # Validate message
        is_valid, result = validate_message(message, file_payload)
        if not is_valid:
            self.sio.emit("error", {"message": result}, to=sid)
            return
        
        message = result
        
        # Find recipient
        recipient_sid = self.user_service.find_user_sid(recipient_username)
        if not recipient_sid:
            self.sio.emit(
                "error",
                {"message": f"User '{recipient_username}' not found or offline."},
                to=sid
            )
            logging.warning(
                f"Private message failed: {recipient_username} not found"
            )
            return
        
        # Create message record
        server_ts = data.get("timestamp") or datetime.now(timezone.utc).isoformat()
        message_id = self.message_service.create_private_message(sid, recipient_sid)
        
        # Prepare payloads
        base_payload = {
            "sender": sender_username,
            "recipient": recipient_username,
            "message": message,
            "timestamp": server_ts,
            "message_id": message_id,
        }
        
        recipient_payload = dict(base_payload, status="delivered")
        sender_payload = dict(base_payload, status="sent")
        
        if file_payload is not None:
            recipient_payload["file"] = file_payload
            sender_payload["file"] = file_payload
            logging.info(f"[MESSAGE] Broadcasting private message with file to {recipient_username}")
        
        # Send to both parties
        self.sio.emit("private_message_received", recipient_payload, to=recipient_sid)
        self.sio.emit("private_message_sent", sender_payload, to=sid)
        
        logging.info(f"Private message from {sender_username} to {recipient_username}")
    
    def on_private_message_read(self, sid, data):
        """Handle private message read receipts."""
        message_ids = data.get("message_ids")
        if message_ids is None:
            return
        
        acknowledgements = self.message_service.mark_messages_as_read(sid, message_ids)
        
        # Notify senders
        for sender_sid, message_id in acknowledgements:
            if sender_sid:
                self.sio.emit(
                    "private_message_read",
                    {"message_id": message_id},
                    to=sender_sid
                )
    
    def _decrypt_message(self, sid, data):
        """Decrypt encrypted message payload."""
        try:
            key = self.user_service.get_session_key(sid)
            if not key:
                self.sio.emit("error", {"message": "Session key not found."}, to=sid)
                return None
            
            ciphertext = base64.b64decode(data.get("ciphertext", ""))
            iv = base64.b64decode(data.get("iv", ""))
            plaintext = self.encryption_service.aes_decrypt(ciphertext, key, iv)
            return plaintext.decode("utf-8", errors="replace")
        except Exception as e:
            self.sio.emit("error", {"message": f"Decrypt failed: {e}"}, to=sid)
            return None
