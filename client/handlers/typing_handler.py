from typing import Optional, Dict, List, Any
from PySide6.QtCore import QObject, Signal


class TypingHandler(QObject):
    """Handles typing indicators."""
    
    publicTypingReceived = Signal(str, bool)  # username, is_typing
    privateTypingReceived = Signal(str, bool)  # username, is_typing
    
    def __init__(self, emit_callback):
        super().__init__()
        self._emit = emit_callback
        self._public_typing_flag = False
        self._private_typing_flags: Dict[str, bool] = {}
    
    def indicate_public_typing(self, is_typing: bool):
        """Send public typing indicator."""
        state = bool(is_typing)
        if self._public_typing_flag == state:
            return
        
        self._public_typing_flag = state
        self._send_typing_state("public", state)
    
    def indicate_private_typing(self, recipient: str, is_typing: bool):
        """Send private typing indicator."""
        recip = (recipient or "").strip()
        if not recip:
            return
        
        state = bool(is_typing)
        previous = self._private_typing_flags.get(recip)
        if previous == state:
            return
        
        if state:
            self._private_typing_flags[recip] = True
        else:
            self._private_typing_flags.pop(recip, None)
        
        self._send_typing_state("private", state, recip)
    
    def _send_typing_state(
        self,
        context: str,
        is_typing: bool,
        recipient: Optional[str] = None
    ):
        """Send typing state to server."""
        payload = {"context": context, "is_typing": bool(is_typing)}
        if recipient:
            payload["recipient"] = recipient
        self._emit("typing", payload)
    
    def reset(self):
        """Reset typing state."""
        self._public_typing_flag = False
        self._private_typing_flags.clear()