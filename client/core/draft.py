def sendMessageWithAttachment(self, message: str, file_url: str):
        """Send public message with optional file."""
        text = (message or "").strip()
        file_url = (file_url or "").strip()
        
        if file_url:
            try:
                file_path = FileValidator.normalize_file_path(file_url)
                if not file_path:
                    self.errorReceived.emit("Invalid file selection.")
                    return
                
                # Resolve and validate file exists
                resolved = file_path.resolve(strict=True)
                if not resolved.is_file():
                    self.errorReceived.emit("Selection is not a file.")
                    return
                
                # Read file
                file_data = resolved.read_bytes()
                filename = resolved.name
                
                if text:
                    self._message_handler.send_public_message(text)
                
                self._file_handler.send_file_chunks(file_data, filename)
            except FileNotFoundError:
                print(f"[ChatClient] File not found: {file_url}")
                self.errorReceived.emit("File not found.")
            except PermissionError:
                print(f"[ChatClient] Permission denied reading file: {file_url}")
                self.errorReceived.emit("Permission denied reading file.")
            except Exception as e:
                print(f"[ChatClient] Failed to read file: {e}")
                self.errorReceived.emit("Failed to read file.")
        else:
            if not text:
                self.errorReceived.emit("Cannot send an empty message.")
                return
            self._message_handler.send_public_message(text)