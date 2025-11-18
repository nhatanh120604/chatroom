from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from enum import Enum


class MessageStatus(Enum):
    """Message delivery status."""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    SEEN = "seen"
    FAILED = "failed"


@dataclass
class FilePayload:
    """File attachment data."""
    name: str
    size: int
    mime: str
    data: str  # base64 encoded
    transfer_id: Optional[str] = None
    is_private: bool = False
    recipient: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Optional['FilePayload']:
        """Create FilePayload from dictionary."""
        if not isinstance(data, dict):
            return None
        
        if not all(k in data for k in ['name', 'size', 'mime', 'data']):
            return None
        
        return cls(
            name=data['name'],
            size=int(data['size']),
            mime=data['mime'],
            data=data['data'],
            transfer_id=data.get('transfer_id'),
            is_private=bool(data.get('is_private', False)),
            recipient=data.get('recipient')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {
            'name': self.name,
            'size': self.size,
            'mime': self.mime,
            'data': self.data,
        }
        if self.transfer_id:
            result['transfer_id'] = self.transfer_id
        if self.is_private:
            result['is_private'] = self.is_private
        if self.recipient:
            result['recipient'] = self.recipient
        return result


@dataclass
class Message:
    """Represents a chat message."""
    username: str
    text: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    is_private: bool = False
    is_outgoing: bool = False
    message_id: int = 0
    status: MessageStatus = MessageStatus.SENT
    file: Optional[FilePayload] = None
    recipient: Optional[str] = None
    
    @property
    def display_context(self) -> str:
        """Get display context for UI."""
        if self.is_private:
            if self.is_outgoing:
                return "You"
            return f"{self.username} • private"
        return self.username
    
    @property
    def has_file(self) -> bool:
        """Check if message has file attachment."""
        return self.file is not None and bool(self.file.name)
    
    @property
    def has_text(self) -> bool:
        """Check if message has text content."""
        return bool(self.text)
    
    @classmethod
    def from_server_data(cls, data: Dict[str, Any], is_private: bool = False) -> 'Message':
        """Create Message from server data."""
        # Parse timestamp
        timestamp_str = data.get('timestamp', '')
        try:
            timestamp = datetime.fromisoformat(timestamp_str) if timestamp_str else datetime.now(timezone.utc)
        except (ValueError, AttributeError):
            timestamp = datetime.now(timezone.utc)
        
        # Parse file
        file_data = data.get('file')
        file_payload = FilePayload.from_dict(file_data) if file_data else None
        
        # Parse status
        status_str = data.get('status', 'sent')
        try:
            status = MessageStatus(status_str.lower())
        except (ValueError, AttributeError):
            status = MessageStatus.SENT
        
        return cls(
            username=data.get('username', 'Unknown'),
            text=data.get('message', ''),
            timestamp=timestamp,
            is_private=is_private,
            is_outgoing=False,  # Server data is always incoming
            message_id=int(data.get('message_id', 0)),
            status=status,
            file=file_payload,
            recipient=data.get('recipient')
        )
    
    def to_qml_dict(self) -> Dict[str, Any]:
        """Convert to QML-friendly dictionary."""
        return {
            'user': self.username,
            'text': self.text,
            'timestamp': self.timestamp.strftime('%I:%M %p'),
            'isPrivate': self.is_private,
            'isOutgoing': self.is_outgoing,
            'messageId': self.message_id,
            'status': self.status.value,
            'displayContext': self.display_context,
            'readNotified': self.is_outgoing,
            'fileName': self.file.name if self.file else '',
            'fileMime': self.file.mime if self.file else '',
            'fileData': self.file.data if self.file else '',
            'fileSize': self.file.size if self.file else 0,
        }


@dataclass
class User:
    """Represents a user in the chat."""
    username: str
    avatar: Optional[Dict[str, Any]] = None
    is_typing_public: bool = False
    is_typing_private: Dict[str, bool] = field(default_factory=dict)
    
    @property
    def has_avatar(self) -> bool:
        """Check if user has avatar."""
        return self.avatar is not None and bool(self.avatar.get('data'))
    
    @property
    def avatar_source(self) -> str:
        """Get avatar data URI."""
        if not self.has_avatar:
            return ''
        
        mime = self.avatar.get('mime', 'image/png')
        data = self.avatar.get('data', '')
        return f"data:{mime};base64,{data}"
    
    def to_qml_dict(self) -> Dict[str, Any]:
        """Convert to QML-friendly dictionary."""
        return {
            'name': self.username,
            'hasAvatar': self.has_avatar,
            'avatarSource': self.avatar_source,
        }


@dataclass
class FileTransfer:
    """Represents an active file transfer."""
    transfer_id: str
    filename: str
    total_chunks: int
    received_chunks: int = 0
    total_size: int = 0
    is_private: bool = False
    recipient: Optional[str] = None
    sender: Optional[str] = None
    
    @property
    def progress(self) -> float:
        """Get transfer progress (0.0 to 1.0)."""
        if self.total_chunks == 0:
            return 0.0
        return min(1.0, self.received_chunks / self.total_chunks)
    
    @property
    def is_complete(self) -> bool:
        """Check if transfer is complete."""
        return self.received_chunks >= self.total_chunks and self.total_chunks > 0
    
    def to_qml_dict(self) -> Dict[str, Any]:
        """Convert to QML-friendly dictionary."""
        return {
            'transferId': self.transfer_id,
            'filename': self.filename,
            'progress': self.progress,
            'current': self.received_chunks,
            'total': self.total_chunks,
            'isComplete': self.is_complete,
        }