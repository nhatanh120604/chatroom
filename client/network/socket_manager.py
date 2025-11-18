import socketio
from typing import Callable, Dict, Any
from PySide6.QtCore import QObject


class SocketManager(QObject):
    """Manages SocketIO event handlers."""
    
    def __init__(self):
        super().__init__()
        self._sio = socketio.Client()
        self._handlers: Dict[str, Callable] = {}
    
    @property
    def sio(self):
        return self._sio
    
    @property
    def connected(self) -> bool:
        return self._sio.connected
    
    def register_handler(self, event: str, handler: Callable):
        """Register event handler."""
        self._handlers[event] = handler
        self._sio.on(event)(handler)
    
    def emit(self, event: str, data: Any = None):
        """Emit event to server."""
        try:
            self._sio.emit(event, data)
        except Exception as e:
            print(f"[SocketManager] Failed to emit '{event}': {e}")
            raise
    
    def connect(self, url: str):
        """Connect to server."""
        self._sio.connect(url)
    
    def disconnect(self):
        """Disconnect from server."""
        if self._sio.connected:
            self._sio.disconnect()