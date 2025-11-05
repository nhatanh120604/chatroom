# Chat Application README

This is a real-time chat application with end-to-end encryption, file transfer, and private messaging features.

## 🚀 Quick Start

### Deployed Server

The backend is deployed and running at: **https://fuv-chatapp-server.onrender.com**

Visit the URL to see the status page.

### Running the Client

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Connect to deployed server:**
   ```bash
   # Set environment variable
   $env:CHAT_SERVER_URL="https://fuv-chatapp-server.onrender.com"

   # Run the client
   python client/client.py
   ```

   Or create `client/.env` file:
   ```
   CHAT_SERVER_URL=https://fuv-chatapp-server.onrender.com
   ```

3. **For local development:**
   - Start server: `python server/server.py`
   - Client will default to `http://localhost:5000`

### Docker Deployment

#### Using Docker Compose (Recommended)

1. **Build and run everything:**
   ```bash
   docker-compose up --build
   ```

2. **Run in detached mode:**
   ```bash
   docker-compose up -d
   ```

3. **View logs:**
   ```bash
   docker-compose logs -f
   ```

4. **Stop services:**
   ```bash
   docker-compose down
   ```

#### Individual Docker Containers

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

**Note:** The client requires X11 forwarding or a virtual display for GUI. For headless environments, use VNC or Xvfb.

### Features

- ✅ Real-time public and private messaging
- ✅ End-to-end encryption (RSA + AES)
- ✅ File transfer with progress tracking
- ✅ Typing indicators
- ✅ Read receipts for private messages
- ✅ Thread-safe server implementation
- ✅ Automatic key exchange


