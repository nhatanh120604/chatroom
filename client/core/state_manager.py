import logging
from typing import List, Dict, Any
from PySide6.QtCore import QObject, Signal

logger = logging.getLogger(__name__)


class StateManager(QObject):
    """Manages application state (users, avatars, etc.)."""
    
    usersUpdated = Signal(list)  # list of usernames - explicitly list type
    avatarsUpdated = Signal(dict)  # dict of avatars - explicitly dict type
    avatarUpdated = Signal(str, object)  # username, avatar
    
    def __init__(self):
        super().__init__()
        self._users: List[str] = []
        self._avatars: Dict[str, Dict[str, Any]] = {}
    
    @property
    def users(self) -> List[str]:
        return self._users.copy()
    
    @property
    def avatars(self) -> Dict[str, Dict[str, Any]]:
        return self._avatars.copy()
    
    def update_users(self, users: List[str]):
        """Update user list."""
        try:
            self._users = users if isinstance(users, list) else list(users) if users else []
            user_list = self._users.copy()
            logger.debug(f"[StateManager] Emitting usersUpdated with {len(user_list)} users: {user_list}")
            self.usersUpdated.emit(user_list)
        except Exception as e:
            logger.error(f"[StateManager] Error in update_users: {e}", exc_info=True)
            self.usersUpdated.emit([])
    
    def update_avatars(self, avatars: Dict[str, Dict[str, Any]]):
        """Update all avatars."""
        snapshot = {}
        for name, info in avatars.items():
            if isinstance(info, dict) and info.get("data"):
                snapshot[name] = info
        self._avatars = snapshot
        self.avatarsUpdated.emit(snapshot.copy())
    
    def update_avatar(self, username: str, avatar: Dict[str, Any]):
        """Update single avatar."""
        if not isinstance(username, str) or not username:
            return
        
        payload = avatar if isinstance(avatar, dict) else {}
        if payload.get("data"):
            self._avatars[username] = payload
        else:
            self._avatars.pop(username, None)
        
        self.avatarUpdated.emit(username, payload)
        self.avatarsUpdated.emit(self._avatars.copy())
    
    def clear(self):
        """Clear all state."""
        self._users.clear()
        self._avatars.clear()
        self.usersUpdated.emit([])
        self.avatarsUpdated.emit({})