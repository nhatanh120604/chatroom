# Aurora Chat - Secure Real-Time Chatroom

A secure, multi-user real-time chatroom application built with Python and Qt/QML, featuring robust encryption, public/private messaging, file sharing, emoji support, and a modern Aurora-themed GUI.

---

## Table of Contents

1. 🌟 [Features & Functional Requirements](#features--functional-requirements)
2. 🏗️ [Architecture Overview](#architecture-overview)
3. 💾 [Installation](#installation)
4. 💬 [Usage](#usage)
5. ⚖️ [Strengths & Limitations](#strengths--limitations)
6. 🔮 [Future Work](#future-work)
7. 🎓 [Acknowledgements & References](#acknowledgements--references)

---

## Features & Functional Requirements

The application delivers all essential capabilities for a secure, modern chatroom:

| #  | Feature                  | Description                                                                                 |
|----|--|----|
| 1  | 🔐 User Authentication   | Prompts for a unique username; enforces uniqueness across all connected users.              |
| 2  | 🌐 Public Messaging      | Broadcasts encrypted messages to all users in real time.                                   |
| 3  | 🤝 Private Messaging     | Enables sending encrypted messages to selected users only.                                  |
| 4  | 🧑‍🤝‍🧑 Active User List  | Displays a live list of all currently connected users.                                      |
| 5  | 🖥️ GUI Interface         | Provides an intuitive, modern Aurora-themed chat interface with status and error displays.                |
| 6  | 🧵 Concurrent Connections| Server supports multiple simultaneous users via threading.                                  |
| 7  | 📎 File Sharing          | Allows sending and receiving files with confirmation dialogs and progress indicators.        |
| 8  | 😄 Emoji Support         | Lets users add emojis using a visual picker or shortcode commands (e.g., `:smile:`).        |
| 9  | ⏰ Message Timestamps    | Shows the time of each message in `HH:MM AP` format.                                       |
| 10 | 🛡️ Message Encryption    | Encrypts all messages and files using AES-256 symmetric encryption.                        |
| 11 | ✅ Graceful Exit & Errors| Handles disconnects, invalid input, and network failures with user-friendly feedback.       |
| 12 | 📊 Typing Indicators     | Shows when other users are typing in real time.                                             |
| 13 | ✔️ Read Receipts         | Displays delivery and read status for private messages.                                     |

### Detailed Feature Descriptions

#### 1. 🔐 User Authentication
- Prompt for a unique username at startup
- Server maintains list of active usernames and enforces uniqueness
- Duplicate usernames are rejected with error notifications
- Users can register and join the chatroom with a single click

#### 2. 🌐 Public Messaging
- Messages are sent by clients and broadcast to all users by the server
- All public messages are encrypted, timestamped, and displayed in the chat history
- Messages show sender name, timestamp, and content
- System messages notify users of joins/leaves and connection changes

#### 3. 🤝 Private Messaging
- Users can click on any user in the active user list to open a private conversation
- Private messages are encrypted end-to-end and routed only to the selected recipient
- Each private conversation maintains its own message history
- Users can have multiple concurrent private conversations

#### 4. 🧑‍🤝‍🧑 Active User List
- GUI displays all connected users in a live sidebar
- User list updates automatically when users join or leave
- Click any user to initiate a private conversation
- Shows total number of active guests in the lounge

#### 5. 🖥️ GUI Interface (Aurora Theme)
- Modern, responsive Qt/QML interface with animated aurora gradient background
- Scrollable message window with smooth animations
- User list with avatar support and hover effects
- Input composer with file attachment and emoji picker
- Toast notifications for system messages and errors
- Responsive design that adapts to different screen sizes

#### 6. 🧵 Concurrent Connections
- Server uses threading to handle multiple simultaneous client connections
- Each client connection is handled independently
- Thread-safe message routing and user management
- Supports unlimited concurrent users (limited by system resources)

#### 7. 📎 File Sharing
- Users can attach files to messages using the file picker
- Files are sent in encrypted chunks with integrity verification
- Recipients see file metadata (name, size) and can download
- Progress indicators show upload/download status
- SHA-256 hashing ensures file integrity
- Supports files up to 20MB

#### 8. 😄 Emoji Support
- Visual emoji picker integrated into the composer
- Users can click emojis to insert them directly
- Shortcode support (e.g., `:smile:`, `:heart:`) for quick insertion
- Comprehensive emoji library with common expressions and symbols
- Emojis are preserved through encryption/decryption

#### 9. ⏰ Message Timestamps
- Each message is automatically timestamped when sent
- Timestamps are displayed in `HH:MM AP` format (e.g., "02:45 PM")
- Timestamps are preserved through encryption and decryption
- System messages also include timestamps for audit trail

#### 10. 🛡️ Message Encryption
- Hybrid cryptography: RSA key exchange + AES-256 session encryption
- Initial RSA handshake secures a unique AES-256 key per session
- All messages and files are encrypted before transmission
- Keys are never logged or exposed in plaintext
- Transparent encryption/decryption for user experience

#### 11. ✅ Graceful Exit & Errors
- On exit, clients notify server and are removed from user list
- Server notifies all clients when users disconnect
- Network failures trigger automatic reconnection attempts
- All exceptions are handled with user-friendly error messages
- Toast notifications provide real-time feedback

#### 12. 📊 Typing Indicators
- Shows when other users are typing in real time
- Typing status updates automatically as users type
- Indicators appear in both public and private conversations
- Typing status clears when message is sent or typing stops

#### 13. ✔️ Read Receipts
- Private messages show delivery status (Sent, Delivered, Seen)
- Read receipts are sent when recipient views a message
- Status indicators appear next to each private message
- Helps users know if their message was received and read

---

## Architecture Overview

### Technology Stack

- **Client:** Qt/QML GUI application with Python backend (`client/main.py`). Handles all user interaction, sends/receives messages and files, and manages encryption/decryption.
- **Server:** Python Flask server (`server/server.py`) using Flask-SocketIO for event-driven communication, user management, message/file routing, and server-side encryption.
- **Encryption:** Hybrid cryptography: Initial RSA key exchange secures a per-session AES-256 key, which is then used for all data encryption/decryption.
- **Logging:** Event and error logging with console output and file logging for debugging.
- **UI Framework:** Qt 5.15+ with QML for modern, responsive interface design.

### Project Structure

```
chat_app2/
├── client/
│   ├── main.py                 # Client entry point
│   ├── qml/
│   │   ├── Main.qml            # Orchestration file
│   │   ├── Main_1.qml          # Main application window
│   │   ├── components/         # Reusable UI components
│   │   │   ├── MessageBubble.qml
│   │   │   ├── Composer.qml
│   │   │   ├── FileAttachment.qml
│   │   │   ├── Header.qml
│   │   │   ├── Avatar.qml
│   │   │   ├── Toast.qml
│   │   │   └── ...
│   │   ├── pages/              # Full page views
│   │   │   ├── PublicChatPage.qml
│   │   │   └── PrivateChatPage.qml
│   │   ├── styles/
│   │   │   └── Theme.qml       # Global theme (singleton)
│   │   └── assets/             # Images, sounds, fonts
│   ├── handlers/
│   │   └── file_handler.py     # File transfer logic
│   └── requirements.txt
├── server/
│   ├── server.py               # Flask-SocketIO server
│   ├── handlers/
│   │   └── file_handler.py     # Server-side file handling
│   ├── services/
│   │   └── file_transfer_service.py
│   ├── crypto_utils.py         # Encryption utilities
│   ├── private_key.pem         # Server's RSA private key
│   └── public_key.pem          # Server's RSA public key
├── requirements.txt
├── README.md
└── docker-compose.yml
```

### Component Architecture

#### Client-Side Components

**GUI (Qt/QML)**
- Modern Aurora-themed interface with animated gradients
- Responsive layout with message history, user list, and composer
- Toast notifications for system messages
- File picker and emoji picker dialogs
- Avatar display with fallback gradients

**Encryption (AES, RSA)**
- On first connect, client generates a unique AES-256 key
- AES key is encrypted with server's RSA public key and exchanged securely
- All chat and file data are encrypted/decrypted transparently

**Messaging Logic**
- Outgoing messages are timestamped, encrypted, and routed via Socket.IO
- Incoming messages are decrypted and displayed in real time
- Typing indicators and read receipts are handled automatically

**File Sharing**
- Files are split into chunks, base64-encoded, and sent with integrity hashes
- Progress bars provide user feedback during transfer
- Download dialog allows users to accept/reject files

#### Server-Side Components

**Socket.IO Event Server**
- Manages client connections, user sessions, and event-driven communication
- Uses threads for concurrent handling of multiple clients

**Authentication & Session Management**
- Validates and enforces unique usernames
- Maintains up-to-date user list and broadcasts join/leave events

**Message Routing & Encryption**
- Receives encrypted messages, decrypts them, and re-encrypts for each recipient
- Ensures only intended clients can read their messages
- Handles both public broadcasts and private routing

**File Handling**
- Receives file chunks, reconstructs and verifies files
- Includes SHA-256 hashing for end-to-end data integrity
- Serves files to recipients on demand

**Graceful Disconnection**
- Updates user list and informs all clients on disconnect
- Handles network failures with automatic reconnection

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/chat_app2.git
cd chat_app2
```

### 2. Install Python Dependencies

Make sure you have Python 3.8+ installed.

```bash
pip install -r requirements.txt
```

### 3. Generate RSA Keys (First Time Only)

To enable secure encryption, generate RSA key pairs for the server:

```bash
python -c "from cryptography.hazmat.primitives.asymmetric import rsa; from cryptography.hazmat.primitives import serialization; from cryptography.hazmat.backends import default_backend; private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend()); public_key = private_key.public_key(); open('server/private_key.pem', 'wb').write(private_key.private_bytes(encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.PKCS8, encryption_algorithm=serialization.NoEncryption())); open('server/public_key.pem', 'wb').write(public_key.public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo()));"
```

Or use a key generator script if provided.

### 4. Start the Server

```bash
cd server
python server.py
```

The server will start and listen for connections on `http://localhost:5000`.

### 5. Start the Client

Open a new terminal and run:

```bash
cd client
python main.py
```

The client will launch with the Aurora-themed GUI. You can run multiple clients to test the chat functionality.

### 6. Docker Deployment (Optional)

#### Using Docker Compose

```bash
docker-compose up --build
```

#### Individual Containers

**Server only:**
```bash
docker build -t chat-server .
docker run -p 5000:5000 chat-server
```

**Client only:**
```bash
docker build -f client/Dockerfile -t chat-client .
docker run -e CHAT_SERVER_URL=http://localhost:5000 chat-client
```

---

## Usage

### Login & Registration
- Enter a unique username when prompted
- Click "Enter the lounge" to join
- Duplicate usernames are rejected with an error message

### Sending Messages
- **Public messages:** Type in the message composer and press Enter
- **Private messages:** Click on a user in the user list to open a private conversation, then type and send

### File Sharing
- Click the 📎 attachment button in the composer
- Select a file from your computer
- The file will be sent with the next message
- Recipients see the file and can download it

### Using Emojis
- Click the 😊 emoji button to open the picker
- Select an emoji to insert it into your message
- Or type shortcodes like `:smile:` directly in your message

### Managing Conversations
- Click any user in the user list to start a private conversation
- Close a private conversation by clicking the X on its tab
- Switch between public and private conversations using the tabs

### Connection Status
- Check the connection indicator in the header
- Green dot = Connected
- Yellow dot = Reconnecting
- Red dot = Offline

### Sound Notifications
- Click the 🔔 bell icon to toggle sound notifications
- Notifications play when you receive messages

---

## Strengths & Limitations

### Strengths

- ✅ Complete core functionality for a modern secure chatroom
- ✅ Strong encryption for all communications (RSA + AES-256)
- ✅ Intuitive, modern GUI with Aurora theme and animations
- ✅ Emoji support and rich message formatting
- ✅ Robust error handling and user-friendly feedback
- ✅ Real-time typing indicators and read receipts
- ✅ File sharing with progress tracking
- ✅ Thread-safe server implementation
- ✅ Modular QML component architecture

### Limitations

- **Scalability:** Designed for small/medium groups; threading model not suitable for large-scale use (100+ concurrent users)
- **File sharing:** Limited to 20MB per file; no compression or resumable uploads
- **Persistence:** No message history persistence; messages are lost on server restart
- **Encryption:** Introduces minor latency for large files
- **Platform:** Client requires Qt 5.15+ and may need platform-specific setup

---

## Future Work

- Refactor to support async/multi-process models for higher scalability
- Add message history persistence with database backend
- Transition to cloud hosting for broader accessibility
- Expand file sharing: support compression, resumable uploads, and more file types
- Enhance GUI: dark mode, customizable themes, accessibility features
- Optimize encryption routines for lower latency
- Add voice/video calling capabilities
- Implement message search and filtering
- Add user profiles and custom avatars
- Support for message reactions and threading

---

## Acknowledgements & References

This project was developed as part of the Independent Study in Computer Networks at FUV - Summer 2025, built on the foundations of Kurose & Ross's *Computer Networking: A Top-Down Approach*.

### References

- Miguel Grinberg, [Flask-SocketIO Documentation](https://flask-socketio.readthedocs.io/)
- Kurose & Ross, *Computer Networking: A Top-Down Approach*, Pearson, 8th edition
- [Python Cryptography Authority](https://cryptography.io/en/latest/)
- [Qt Documentation](https://doc.qt.io/)
- [QML Documentation](https://doc.qt.io/qt-5/qmlreference.html)


