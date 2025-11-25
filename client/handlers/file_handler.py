import uuid
import base64
import threading
import time
import tempfile
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from PySide6.QtCore import QObject, Signal, QUrl

logger = logging.getLogger(__name__)

# Import encryption with error handling
try:
    from .encryption import aes_encrypt
    logger.debug("[FileHandler] Successfully imported aes_encrypt")
except ImportError as e:
    logger.error(f"[FileHandler] Failed to import aes_encrypt: {e}")
    raise

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
        self._reassembled_files = {}  # transfer_id -> {filename, data, size}
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
            # logger.info(f"Preparing to send file: {filename}, size: {len(file_data)} bytes")
            print(f"[FILE HANDLER] Preparing to send file: {filename}, size: {len(file_data)} bytes")
            
            if not filename or not isinstance(filename, str):
                print(f"[FILE HANDLER] ERROR: Invalid filename: {filename}")
                self.errorNotification.emit("Invalid filename.")
                return None

            session_key = self._session_manager.session_key
            if not session_key:
                print("[FILE HANDLER] Session key not established")
                self.errorNotification.emit(
                    "Session key not established; cannot send file securely."
                )
                return None
            
            # Validate session key type
            if not isinstance(session_key, bytes):
                print(f"[FILE HANDLER] Invalid session key type: {type(session_key)}, expected bytes")
                self.errorNotification.emit("Invalid session key type")
                return None
            
            print(f"[FILE HANDLER] START: file={filename}, size={len(file_data)} bytes, "
                  f"type={'private' if recipient else 'public'}, key_size={len(session_key)}")
            
            # Encrypt entire file
            try:
                ciphertext, iv = aes_encrypt(file_data, session_key)
                iv_b64 = base64.b64encode(iv).decode("utf-8")
            except Exception as e:
                print(f"[FILE HANDLER] Encryption failed: {e}", exc_info=True)
                self.errorNotification.emit(f"Encryption failed: {str(e)}")
                return None
            
            print(f"[FILE HANDLER] ENCRYPTED: ciphertext_size={len(ciphertext)} bytes")
            
            # Chunk ciphertext
            chunk_size = 64 * 1024
            chunks = [
                ciphertext[i : i + chunk_size]
                for i in range(0, len(ciphertext), chunk_size)
            ]
            total_chunks = len(chunks)
            transfer_id = uuid.uuid4().hex
            
            #logger.info(f"[CLIENT FILE] CHUNKS: transfer_id={transfer_id}, total_chunks={total_chunks}")
            print(f"[FILE HANDLER] CHUNKS: transfer_id={transfer_id}, total_chunks={total_chunks}")
            
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
                print(f"[FILE HANDLER] SENDING: chunk 0 (private to {recipient})")
                self._emit("private_file_chunk", first_chunk)
            else:
                print(f"[FILE HANDLER] SENDING: chunk 0 (public)")
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
                    print(f"[FILE HANDLER] SENDING: chunk {i}/{total_chunks} (private to {recipient})")
                    self._emit("private_file_chunk", chunk)
                else:
                    print(f"[FILE HANDLER] SENDING: chunk {i}/{total_chunks} (public)")
                    self._emit("public_file_chunk", chunk)
                
                time.sleep(0.01)  # Prevent overwhelming server
            
            print(f"[FILE HANDLER] COMPLETE: transfer_id={transfer_id}, all {total_chunks} chunks sent")
            return transfer_id
            
        except Exception as e:
            print(f"[FILE HANDLER] ERROR: Secure transfer failed: {e}")
            import traceback
            traceback.print_exc()
            self.errorNotification.emit("File transfer failed. Please try again.")
            return None
    
    def handle_file_chunk(self, data: Dict[str, Any]):
        """Handle incoming file chunks."""
        try:
            transfer_id = data.get("transfer_id")
            chunk_index = data.get("chunk_index")
            chunk_data = data.get("chunk_data")
            is_last_chunk = data.get("is_last_chunk", False)
            metadata = data.get("metadata")
            
            print(f"[FileHandler] Received chunk: transfer_id={transfer_id}, index={chunk_index}, is_last={is_last_chunk}")
            
            if not all([transfer_id, chunk_index is not None, chunk_data]):
                print(f"[FileHandler] Invalid file chunk: missing required fields")
                self.errorNotification.emit("Invalid file chunk received")
                return
            
            should_reassemble = False
            
            with self._transfer_lock:
                # Initialize chunk storage
                if transfer_id not in self._received_chunks:
                    self._received_chunks[transfer_id] = {}
                    print(f"[FileHandler] Initialized chunk storage for transfer {transfer_id}")
                
                # Store chunk
                try:
                    self._received_chunks[transfer_id][chunk_index] = base64.b64decode(
                        chunk_data
                    )
                    print(f"[FileHandler] Stored chunk {chunk_index} for transfer {transfer_id}")
                except Exception as e:
                    print(f"[FileHandler] Failed to decode chunk {chunk_index}: {e}", exc_info=True)
                    return
                
                # Store metadata from first chunk
                if metadata and chunk_index == 0:
                    self._active_transfers[transfer_id] = metadata
                    print(f"[FileHandler] Transfer metadata stored: filename={metadata.get('filename')}, total_chunks={metadata.get('total_chunks')}")
                
                # Check if all chunks received
                stored_meta = self._active_transfers.get(transfer_id, {})
                expected_chunks = stored_meta.get("total_chunks", 0)
                
                if expected_chunks == 0 and is_last_chunk:
                    expected_chunks = chunk_index + 1
                
                received_count = len(self._received_chunks[transfer_id])
                print(f"[FileHandler] Progress: {received_count}/{expected_chunks} chunks")
                
                # Emit progress
                try:
                    self.fileTransferProgress.emit(transfer_id, received_count, expected_chunks)
                except Exception as e:
                    print(f"[FileHandler] Failed to emit progress: {e}", exc_info=True)
                
                # Check if ready to reassemble
                if received_count >= expected_chunks and expected_chunks > 0:
                    should_reassemble = True
                    print(f"[FileHandler] All chunks received, starting reassembly for transfer {transfer_id}")
            
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
        except Exception as e:
            print(f"[FileHandler] Error in handle_file_chunk: {e}", exc_info=True)
            self.errorNotification.emit("Error processing file chunk")
    
    def _reassemble_file_background(self, transfer_id: str):
        """Reassemble file in background thread."""
        try:
            logger.info(f"[FileHandler] Starting reassembly for transfer {transfer_id}")
            
            # Get data from locked section
            with self._transfer_lock:
                if transfer_id not in self._active_transfers:
                    logger.warning(f"[FileHandler] No metadata for transfer {transfer_id}")
                    return
                if transfer_id not in self._received_chunks:
                    logger.warning(f"[FileHandler] No chunks for transfer {transfer_id}")
                    return
                
                metadata = dict(self._active_transfers[transfer_id])
                chunks_dict = dict(self._received_chunks[transfer_id])
            
            logger.debug(f"[FileHandler] Reassembling {len(chunks_dict)} chunks")
            
            # Reassemble
            sorted_indices = sorted(chunks_dict.keys())
            data_bytes = b"".join(chunks_dict[i] for i in sorted_indices)
            
            filename = metadata.get("filename", "received_file")
            logger.info(f"[FileHandler] Reassembly complete: {filename}, size={len(data_bytes)} bytes")
            
            # Store the reassembled file data for later download (don't save automatically)
            # Store in a temporary location or memory for the user to download
            self._reassembled_files[transfer_id] = {
                "filename": filename,
                "data": data_bytes,
                "size": len(data_bytes)
            }
            print(f"[FileHandler] Stored reassembled file in memory: transfer_id={transfer_id}, filename={filename}, size={len(data_bytes)}")
            
            # Emit completion signal (file is ready to download, not yet saved)
            try:
                self.fileTransferComplete.emit(transfer_id, filename)
                logger.debug(f"[FileHandler] Emitted fileTransferComplete for {transfer_id}, filename={filename}")
            except Exception as e:
                logger.error(f"[FileHandler] Failed to emit completion: {e}", exc_info=True)
            
            # Cleanup
            with self._transfer_lock:
                self._active_transfers.pop(transfer_id, None)
                self._received_chunks.pop(transfer_id, None)
                self._download_threads.pop(transfer_id, None)
                logger.debug(f"[FileHandler] Cleaned up transfer {transfer_id}")
        
        except Exception as e:
            logger.error(f"[FileHandler] Error reassembling {transfer_id}: {e}", exc_info=True)
            try:
                self.fileTransferError.emit(transfer_id, f"Reassembly failed: {str(e)}")
            except Exception as emit_err:
                logger.error(f"[FileHandler] Failed to emit error: {emit_err}", exc_info=True)
            
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
    
    def _save_received_file_to_downloads(self, filename: str, data_bytes: bytes) -> str:
        """Save received file bytes to Downloads directory."""
        from PySide6.QtCore import QStandardPaths
        
        safe_name = Path(filename or "download").name
        print(f"[FileHandler] _save_received_file_to_downloads: filename={filename}, safe_name={safe_name}, data_size={len(data_bytes) if data_bytes else 0}")
        
        if not data_bytes:
            logger.warning(f"[FileHandler] No data to save for {filename}")
            print(f"[FileHandler] No data to save for {filename}")
            return ""
        
        downloads_path = QStandardPaths.writableLocation(
            QStandardPaths.DownloadLocation
        )
        print(f"[FileHandler] downloads_path from QStandardPaths: {downloads_path}")
        
        downloads = (
            Path(downloads_path) if downloads_path else (Path.home() / "Downloads")
        )
        print(f"[FileHandler] Using downloads folder: {downloads}")
        
        try:
            downloads.mkdir(parents=True, exist_ok=True)
            print(f"[FileHandler] Downloads folder created/verified")
        except OSError as exc:
            logger.error(f"[FileHandler] Failed to create Downloads directory: {exc}")
            print(f"[FileHandler] Failed to create Downloads directory: {exc}")
            pass
        
        target = downloads / safe_name
        print(f"[FileHandler] Target file path: {target}")
        
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
            print(f"[FileHandler] File exists, using unique name: {target}")
        
        try:
            target.write_bytes(data_bytes)
            file_url = QUrl.fromLocalFile(str(target)).toString()
            logger.info(f"[FileHandler] File saved to Downloads: {target}")
            print(f"[FileHandler] File saved successfully!")
            print(f"[FileHandler] Returning file URL: {file_url}")
            return file_url
        except OSError as exc:
            logger.error(f"[FileHandler] Failed to save file: {exc}")
            print(f"[FileHandler] Failed to save file: {exc}")
            return ""
    
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
            logger.error(f"[FileHandler] Failed to save file: {exc}")
            print(f"[FileHandler] Failed to save file: {exc}")
            return ""
        
        return QUrl.fromLocalFile(str(target)).toString()

    def download_received_file(self, transfer_id: str, filename: str) -> str:
        """Download a received (reassembled) file to Downloads directory."""
        print(f"[FileHandler] download_received_file: transfer_id={transfer_id}, filename={filename}")
        
        # Get the reassembled file data from memory
        if transfer_id not in self._reassembled_files:
            print(f"[FileHandler] File not found in memory: {transfer_id}")
            return ""
        
        file_info = self._reassembled_files[transfer_id]
        data_bytes = file_info.get("data", b"")
        
        if not data_bytes:
            print(f"[FileHandler] No data for transfer_id: {transfer_id}")
            return ""
        
        # Save to Downloads
        file_path = self._save_received_file_to_downloads(filename, data_bytes)
        
        # Clean up from memory after saving
        del self._reassembled_files[transfer_id]
        print(f"[FileHandler] Cleaned up reassembled file from memory: {transfer_id}")
        
        return file_path

    