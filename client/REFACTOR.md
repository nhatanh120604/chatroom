client/
├── __init__.py
├── main.py                      # Application entry point
├── core/
│   ├── __init__.py
│   ├── client.py                # Main ChatClient (orchestrator)
│   ├── connection_manager.py   # Connection/reconnection logic
│   ├── session_manager.py      # Session key management
│   └── state_manager.py         # Client state (users, avatars, etc.)
├── handlers/
│   ├── __init__.py
│   ├── message_handler.py      # Message receive/send logic
│   ├── file_handler.py         # File transfer logic
│   ├── typing_handler.py       # Typing indicators
│   └── avatar_handler.py       # Avatar management
├── network/
│   ├── __init__.py
│   ├── socket_manager.py       # SocketIO setup and events
│   └── encryption.py           # Encryption utilities
├── models/
│   ├── __init__.py
│   └── message.py              # Data classes for messages
├── utils/
│   ├── __init__.py
│   ├── file_utils.py           # File operations
│   └── validators.py           # Input validation
└── qml/
    ├── Main.qml                 # Root window
    ├── components/
    │   ├── Header.qml           # Header card
    │   ├── ConversationTabs.qml # Tab bar
    │   ├── PublicChat.qml       # Public conversation
    │   ├── PrivateChat.qml      # Private conversation
    │   ├── UserList.qml         # Concierge panel
    │   ├── MessageBubble.qml    # Message delegate
    │   ├── UserCard.qml         # User delegate
    │   ├── FileAttachment.qml   # File display
    │   ├── Composer.qml         # Message input
    │   └── Toast.qml            # Notifications
    ├── dialogs/
    │   └── FileDialog.qml       # File picker
    └── styles/
        ├── Theme.qml            # Color palette
        └── Animations.qml       # Reusable animations