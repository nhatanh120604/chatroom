from typing import List, Dict, Any
from PySide6.QtCore import QObject, Signal


class StateManager(QObject):
    """Manages application state (users, avatars, etc.)."""
    
    usersUpdated = Signal(object)  # list of usernames
    avatarsUpdated = Signal(object)  # dict of avatars
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
        self._users = users
        self.usersUpdated.emit(self._users.copy())
    
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