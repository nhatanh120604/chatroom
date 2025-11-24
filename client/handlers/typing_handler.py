import logging
from typing import Optional, Dict, List, Any
from PySide6.QtCore import QObject, Signal

logger = logging.getLogger(__name__)


class TypingHandler(QObject):
    """Handles typing indicators."""
    
    publicTypingReceived = Signal(str, bool)  # username, is_typing
    privateTypingReceived = Signal(str, bool)  # username, is_typing
    
    def __init__(self, emit_callback):
        super().__init__()
        self._emit = emit_callback
        self._public_typing_flag = False
        self._private_typing_flags: Dict[str, bool] = {}
        self._sending_typing = False  # Flag to prevent recursion
    
    def indicate_public_typing(self, is_typing: bool):
        """Send public typing indicator."""
        try:
            state = bool(is_typing)
            if self._public_typing_flag == state:
                return
            
            self._public_typing_flag = state
            self._send_typing_state("public", state)
        except Exception as e:
            logger.error(f"[TypingHandler] Error in indicate_public_typing: {e}", exc_info=True)
    
    def indicate_private_typing(self, recipient: str, is_typing: bool):
        """Send private typing indicator."""
        try:
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
        except Exception as e:
            logger.error(f"[TypingHandler] Error in indicate_private_typing: {e}", exc_info=True)
    
    def _send_typing_state(
        self,
        context: str,
        is_typing: bool,
        recipient: Optional[str] = None
    ):
        """Send typing state to server."""
        # Prevent recursion by checking if we're already sending
        if self._sending_typing:
            logger.debug(f"[TypingHandler] Already sending typing state, skipping")
            return
        
        try:
            self._sending_typing = True
            payload = {"context": context, "is_typing": bool(is_typing)}
            if recipient:
                payload["recipient"] = recipient
            
            logger.debug(f"[TypingHandler] Sending typing: context={context}, is_typing={is_typing}, recipient={recipient}")
            self._emit("typing", payload)
        except Exception as e:
            logger.error(f"[TypingHandler] Error sending typing state: {e}", exc_info=True)
        finally:
            self._sending_typing = False
    
    def reset(self):
        """Reset typing state."""
        self._public_typing_flag = False
        self._private_typing_flags.clear()