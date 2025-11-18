import uuid
import base64
import threading
import time
import tempfile
from pathlib import Path
from typing import Optional, Dict, List, Any
from PySide6.QtCore import QObject, Signal, QUrl


MAX_FILE_BYTES = 5 * 1024 * 1024  # 5 MB


class FileHandler(QObject):
    """Handles file transfers (send/receive/reassembly)."""
    
    fileTransferProgress = Signal(str, int, int)  # transfer_id, current, total
    fileTransferComplete = Signal(str, str)  # transfer_id, filename
    fileTransferError = Signal(str, str)  # transfer_id, error
    errorNotification = Signal(str)  # error message
    
    def __init__(self, session_manager, emit_callback):
        super().__init__()
        self._session_manager = session_manager
        self._emit = emit_callback
        
        # Transfer tracking
        self._active_transfers = {}  # transfer_id -> metadata
        self._received_chunks = {}  # transfer_id -> {chunk_index: data}
        self._transfer_lock = threading.Lock()
        self._download_threads = {}  # transfer_id -> thread
    
    def send_file_chunks(
        self,
        file_data: bytes,
        filename: str,
        recipient: Optional[str] = None
    ) -> Optional[str]:
        """Send file in encrypted chunks."""
        try:
            if not isinstance(file_data, bytes):
                print(f"[FileHandler] Invalid file_data type: {type(file_data)}")
                self.errorNotification.emit("Invalid file data.")
                return None
            
            if not filename or not isinstance(filename, str):
                print(f"[FileHandler] Invalid filename: {filename}")
                self.errorNotification.emit("Invalid filename.")
                return None
            
            from ..network.encryption import aes_encrypt
            
            if not self._session_manager.session_key:
                self.errorNotification.emit(
                    "Session key not established; cannot send file securely."
                )
                return None
            
            # Encrypt entire file
            ciphertext, iv = aes_encrypt(file_data, self._session_manager.session_key)
            iv_b64 = base64.b64encode(iv).decode("utf-8")
            
            # Chunk ciphertext
            chunk_size = 64 * 1024
            chunks = [
                ciphertext[i : i + chunk_size]
                for i in range(0, len(ciphertext), chunk_size)
            ]
            total_chunks = len(chunks)
            transfer_id = uuid.uuid4().hex
            
            # First chunk with metadata
            first_chunk = {
                "transfer_id": transfer_id,
                "chunk_index": 0,
                "chunk_data": base64.b64encode(chunks[0]).decode("utf-8"),
                "is_last_chunk": total_chunks == 1,
                "metadata": {
                    "filename": filename,
                    "total_size": len(file_data),
                    "total_chunks": total_chunks,
                    "chunk_size": chunk_size,
                    "iv": iv_b64,
                },
            }
            
            if recipient:
                first_chunk["recipient"] = recipient
                self._emit("private_file_chunk", first_chunk)
            else:
                self._emit("public_file_chunk", first_chunk)
            
            # Send remaining chunks
            for i, chunk_data in enumerate(chunks[1:], 1):
                chunk = {
                    "transfer_id": transfer_id,
                    "chunk_index": i,
                    "chunk_data": base64.b64encode(chunk_data).decode("utf-8"),
                    "is_last_chunk": i == total_chunks - 1,
                }
                
                if recipient:
                    chunk["recipient"] = recipient
                    self._emit("private_file_chunk", chunk)
                else:
                    self._emit("public_file_chunk", chunk)
                
                time.sleep(0.01)  # Prevent overwhelming server
            
            return transfer_id
            
        except Exception as e:
            print(f"[FileHandler] Secure transfer failed: {e}")
            self.errorNotification.emit("File transfer failed. Please try again.")
            return None
    
    def handle_file_chunk(self, data: Dict[str, Any]):
        """Handle incoming file chunks."""
        transfer_id = data.get("transfer_id")
        chunk_index = data.get("chunk_index")
        chunk_data = data.get("chunk_data")
        is_last_chunk = data.get("is_last_chunk", False)
        metadata = data.get("metadata")
        
        if not all([transfer_id, chunk_index is not None, chunk_data]):
            self.errorNotification.emit("Invalid file chunk received")
            return
        
        should_reassemble = False
        
        with self._transfer_lock:
            # Initialize chunk storage
            if transfer_id not in self._received_chunks:
                self._received_chunks[transfer_id] = {}
            
            # Store chunk
            try:
                self._received_chunks[transfer_id][chunk_index] = base64.b64decode(
                    chunk_data
                )
            except Exception as e:
                print(f"[FileHandler] Failed to decode chunk {chunk_index}: {e}")
                return
            
            # Store metadata from first chunk
            if metadata and chunk_index == 0:
                self._active_transfers[transfer_id] = metadata
            
            # Check if all chunks received
            stored_meta = self._active_transfers.get(transfer_id, {})
            expected_chunks = stored_meta.get("total_chunks", 0)
            
            if expected_chunks == 0 and is_last_chunk:
                expected_chunks = chunk_index + 1
            
            received_count = len(self._received_chunks[transfer_id])
            
            # Emit progress
            self.fileTransferProgress.emit(transfer_id, received_count, expected_chunks)
            
            # Check if ready to reassemble
            if received_count >= expected_chunks and expected_chunks > 0:
                should_reassemble = True
        
        # Start background reassembly
        if should_reassemble:
            thread = threading.Thread(
                target=self._reassemble_file_background,
                args=(transfer_id,),
                daemon=True,
            )
            with self._transfer_lock:
                self._download_threads[transfer_id] = thread
            thread.start()
    
    def _reassemble_file_background(self, transfer_id: str):
        """Reassemble file in background thread."""
        try:
            # Get data from locked section
            with self._transfer_lock:
                if transfer_id not in self._active_transfers:
                    return
                if transfer_id not in self._received_chunks:
                    return
                
                metadata = dict(self._active_transfers[transfer_id])
                chunks_dict = dict(self._received_chunks[transfer_id])
            
            # Reassemble
            sorted_indices = sorted(chunks_dict.keys())
            data_bytes = b"".join(chunks_dict[i] for i in sorted_indices)
            
            filename = metadata.get("filename", "received_file")
            
            # Emit completion
            self.fileTransferComplete.emit(transfer_id, filename)
            
            # Cleanup
            with self._transfer_lock:
                self._active_transfers.pop(transfer_id, None)
                self._received_chunks.pop(transfer_id, None)
                self._download_threads.pop(transfer_id, None)
        
        except Exception as e:
            print(f"[FileHandler] Error reassembling {transfer_id}: {e}")
            self.fileTransferError.emit(transfer_id, f"Reassembly failed: {str(e)}")
            
            with self._transfer_lock:
                self._active_transfers.pop(transfer_id, None)
                self._received_chunks.pop(transfer_id, None)
                self._download_threads.pop(transfer_id, None)
    
    def save_file_to_temp(self, filename: str, data: str, mime: str) -> str:
        """Save file to temp directory."""
        safe_name = Path(filename or "attachment").name
        if not data:
            return ""
        
        try:
            binary = base64.b64decode(data)
        except (ValueError, TypeError):
            return ""
        
        suffix = Path(safe_name).suffix
        unique_name = f"chatroom_{uuid.uuid4().hex}{suffix}"
        target = Path(tempfile.gettempdir()) / unique_name
        
        try:
            target.write_bytes(binary)
        except OSError as exc:
            print(f"[FileHandler] Failed to save file: {exc}")
            return ""
        
        return QUrl.fromLocalFile(str(target)).toString()
    
    def save_file_to_downloads(self, filename: str, data: str, mime: str) -> str:
        """Save file to Downloads directory."""
        from PySide6.QtCore import QStandardPaths
        
        safe_name = Path(filename or "download").name
        if not data:
            return ""
        
        try:
            binary = base64.b64decode(data)
        except (ValueError, TypeError):
            return ""
        
        downloads_path = QStandardPaths.writableLocation(
            QStandardPaths.DownloadLocation
        )
        downloads = (
            Path(downloads_path) if downloads_path else (Path.home() / "Downloads")
        )
        
        try:
            downloads.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass
        
        target = downloads / safe_name
        
        # Ensure unique filename
        if target.exists():
            base = target.stem
            ext = target.suffix
            counter = 1
            while True:
                candidate = downloads / f"{base} ({counter}){ext}"
                if not candidate.exists():
                    target = candidate
                    break
                counter += 1
        
        try:
            target.write_bytes(binary)
        except OSError as exc:
            print(f"[FileHandler] Failed to save file: {exc}")
            return ""
        
        return QUrl.fromLocalFile(str(target)).toString()