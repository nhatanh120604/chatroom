import socketio
import logging
from typing import Callable, Dict, Any
from PySide6.QtCore import QObject

logger = logging.getLogger(__name__)


class SocketManager(QObject):
    """Manages SocketIO event handlers."""
    
    def __init__(self):
        super().__init__()
        self._sio = socketio.Client()
        self._handlers: Dict[str, Callable] = {}
        self._emitting_events = set()  # Track events being emitted to prevent recursion
    
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
        # Prevent recursive emission of the same event
        if event in self._emitting_events:
            logger.debug(f"[SocketManager] Recursive emit detected for '{event}', skipping")
            return
        
        try:
            self._emitting_events.add(event)
            logger.debug(f"[SocketManager] Emitting '{event}'")
            self._sio.emit(event, data)
        except Exception as e:
            logger.error(f"[SocketManager] Failed to emit '{event}': {e}", exc_info=True)
            # Don't re-raise to avoid recursion loops
        finally:
            self._emitting_events.discard(event)
    
    def connect(self, url: str):
        """Connect to server."""
        self._sio.connect(url)
    
    def disconnect(self):
        """Disconnect from server."""
        if self._sio.connected:
            self._sio.disconnect()