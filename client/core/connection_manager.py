import threading
import time
from typing import Callable, Optional
from PySide6.QtCore import QObject, Signal


class ConnectionManager(QObject):
    """Manages socket connection and reconnection logic."""
    
    reconnecting = Signal(int)  # attempt number
    reconnected = Signal()
    disconnected = Signal(bool)  # user_requested
    connectionStateChanged = Signal(str)  # "connected", "reconnecting", "offline"
    
    def __init__(self, sio, url: str):
        super().__init__()
        self._sio = sio
        self._url = url
        self._connected = False
        self._connecting = False
        self._connect_lock = threading.Lock()
        
        # Reconnection settings
        self._reconnect_attempts = 0
        self._max_reconnect_attempts = 10
        self._reconnect_delay = 1.0
        self._max_reconnect_delay = 30.0
        self._should_reconnect = True
        self._reconnect_thread = None
        self._user_requested_disconnect = False
        self._connection_state = "offline"
        
    @property
    def connected(self) -> bool:
        return self._connected
    
    @property
    def connection_state(self) -> str:
        return self._connection_state
    
    def set_connection_state(self, state: str):
        if self._connection_state != state:
            self._connection_state = state
            self.connectionStateChanged.emit(state)
    
    def connect_async(self, on_error: Optional[Callable] = None):
        """Attempt connection in background thread."""
        with self._connect_lock:
            if self._connected or self._connecting:
                return
            self._connecting = True
        
        def _connect():
            try:
                self._sio.connect(self._url)
            except Exception as e:
                print(f"[ConnectionManager] Connection error: {e}")
                with self._connect_lock:
                    self._connecting = False
                if on_error:
                    on_error(str(e))
        
        t = threading.Thread(target=_connect, daemon=True)
        t.start()
    
    def on_connected(self):
        """Called when connection is established."""
        self._connected = True
        self._connecting = False
        self.set_connection_state("connected")
        
        # Reset reconnection state
        was_reconnecting = self._reconnect_attempts > 0
        self._reconnect_attempts = 0
        self._reconnect_delay = 1.0
        
        if was_reconnecting:
            print("[ConnectionManager] Successfully reconnected")
            self.reconnected.emit()
    
    def on_disconnected(self):
        """Called when connection is lost."""
        self._connected = False
        self._connecting = False
        self.set_connection_state("offline")
        
        self.disconnected.emit(self._user_requested_disconnect)
        
        # Start automatic reconnection if not user-requested
        if self._should_reconnect and not self._user_requested_disconnect:
            print("[ConnectionManager] Connection lost, attempting reconnection...")
            self._start_reconnection()
    
    def disconnect(self, user_requested: bool = False):
        """Disconnect from server."""
        self._user_requested_disconnect = user_requested
        self._should_reconnect = False
        
        try:
            if self._sio.connected:
                self._sio.disconnect()
        except Exception as e:
            print(f"[ConnectionManager] Error during disconnect: {e}")
        finally:
            self._connected = False
            self._connecting = False
    
    def _start_reconnection(self):
        """Start reconnection loop in background thread."""
        if self._reconnect_thread and self._reconnect_thread.is_alive():
            return
        
        self._reconnect_thread = threading.Thread(
            target=self._reconnection_loop, daemon=True
        )
        self._reconnect_thread.start()
    
    def _reconnection_loop(self):
        """Attempt to reconnect with exponential backoff."""
        while self._should_reconnect and not self._connected:
            self._reconnect_attempts += 1
            
            if self._reconnect_attempts > self._max_reconnect_attempts:
                print(f"[ConnectionManager] Max attempts reached. Giving up.")
                break
            
            print(f"[ConnectionManager] Reconnection attempt {self._reconnect_attempts}")
            self.set_connection_state("reconnecting")
            self.reconnecting.emit(self._reconnect_attempts)
            
            try:
                with self._connect_lock:
                    self._connecting = True
                
                self._sio.connect(self._url)
                return  # Success
                
            except Exception as e:
                print(f"[ConnectionManager] Attempt {self._reconnect_attempts} failed: {e}")
                with self._connect_lock:
                    self._connecting = False
                
                # Exponential backoff
                delay = min(
                    self._reconnect_delay * (2 ** (self._reconnect_attempts - 1)),
                    self._max_reconnect_delay
                )
                time.sleep(delay)
        
        # Reset if loop exits without success
        if not self._connected:
            with self._connect_lock:
                self._connecting = False