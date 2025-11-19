import os
import logging
import socketio
from flask import Flask
from config import Config
from services.encryption_service import EncryptionService
from services.user_service import UserService
from services.history_service import HistoryService
from services.message_service import MessageService
from services.file_transfer_service import FileTransferService
from handlers.connection_handler import ConnectionHandler
from handlers.message_handler import MessageHandler
from handlers.typing_handler import TypingHandler
from handlers.file_handler import FileHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


class ChatServer:
    """Main chat server application"""
    
    def __init__(self, test=False):
        self.test = test
        
        # Initialize Socket.IO server
        self.sio = socketio.Server(
            cors_allowed_origins=Config.CORS_ALLOWED_ORIGINS,
            max_http_buffer_size=Config.MAX_FILE_BYTES * 2,
        )
        
        # Initialize Flask app
        self.app = Flask(__name__)
        self.app.wsgi_app = socketio.WSGIApp(self.sio, self.app.wsgi_app)
        
        # Initialize services
        self.encryption_service = EncryptionService()
        self.user_service = UserService()
        self.history_service = HistoryService()
        self.message_service = MessageService()
        self.file_transfer_service = FileTransferService(self.encryption_service)
        
        # Initialize handlers
        self.connection_handler = ConnectionHandler(
            self.sio, self.user_service, self.history_service, self.file_transfer_service
        )
        self.message_handler = MessageHandler(
            self.sio, self.user_service, self.message_service,
            self.history_service, self.encryption_service
        )
        self.typing_handler = TypingHandler(self.sio, self.user_service)
        self.file_handler = FileHandler(
            self.sio, self.user_service, self.file_transfer_service,
            self.encryption_service
        )
        
        # Register all events
        self._register_events()
        self._register_http_routes()
    
    def _register_events(self):
        """Register all Socket.IO event handlers"""
        
        # Connection events
        @self.sio.event
        def connect(sid, environ):
            self.connection_handler.on_connect(sid, environ)
        
        @self.sio.event
        def disconnect(sid):
            self.connection_handler.on_disconnect(sid)
        
        @self.sio.event
        def register(sid, data):
            self.connection_handler.on_register(sid, data)
        
        @self.sio.event
        def request_history(sid, data=None):
            self.connection_handler.on_request_history(sid, data)
        
        # Message events
        @self.sio.event
        def session_key(sid, data):
            self.message_handler.on_session_key(sid, data)
        
        @self.sio.event
        def message(sid, data):
            self.message_handler.on_message(sid, data)
        
        @self.sio.event
        def private_message(sid, data):
            self.message_handler.on_private_message(sid, data)
        
        @self.sio.event
        def private_message_read(sid, data):
            self.message_handler.on_private_message_read(sid, data)
        
        # Typing events
        @self.sio.event
        def typing(sid, data):
            self.typing_handler.on_typing(sid, data)
        
        # File transfer events
        @self.sio.event
        def public_file_chunk(sid, data):
            self.file_handler.on_public_file_chunk(sid, data)
        
        @self.sio.event
        def private_file_chunk(sid, data):
            self.file_handler.on_private_file_chunk(sid, data)
        
        @self.sio.event
        def file_transfer_ack(sid, data):
            self.file_handler.on_file_transfer_ack(sid, data)
    
    def _register_http_routes(self):
        """Register HTTP routes"""
        
        @self.app.route("/")
        def index():
            return """
            <html>
            <head><title>FUV Chat Backend</title></head>
            <body style="font-family: Arial, sans-serif; text-align: center; margin-top: 50px;">
                <h1>🟢 FUV Chat Backend Running</h1>
                <p>The chat server is online and ready to accept connections.</p>
                <hr>
                <p><a href="/health">Health Check</a> | <a href="/public_key">Public Key</a></p>
            </body>
            </html>
            """, 200
        
        @self.app.route("/health")
        def health():
            return "ok", 200
        
        @self.app.route("/public_key")
        def public_key():
            try:
                pub = self.encryption_service.get_public_key_pem()
                return pub, 200, {"Content-Type": "application/x-pem-file"}
            except Exception:
                return "unavailable", 500


# Global server instance for WSGI servers (gunicorn, etc.)
_chat_server_instance = None


def get_app():
    """Get or create server instance for WSGI servers."""
    global _chat_server_instance
    if _chat_server_instance is None:
        _chat_server_instance = ChatServer()
    return _chat_server_instance.app


if __name__ == "__main__":
    import signal
    import sys
    
    server = ChatServer()
    http_server = None
    
    def signal_handler(sig, frame):
        """Handle graceful shutdown on Ctrl+C."""
        logging.info("Shutdown signal received, closing connections...")
        
        # Disconnect all clients
        try:
            if hasattr(server.sio, 'manager') and hasattr(server.sio.manager, 'rooms'):
                rooms = server.sio.manager.rooms.get('/', {})
                if rooms:
                    for sid in list(rooms.keys()):
                        try:
                            server.sio.disconnect(sid)
                        except Exception as e:
                            logging.debug(f"Error disconnecting {sid}: {e}")
                    logging.info(f"Disconnected {len(rooms)} clients")
                else:
                    logging.info("No clients connected")
            else:
                logging.info("No clients connected")
        except Exception as e:
            logging.debug(f"Error accessing client list: {e}")
        
        # Stop HTTP server if available
        if http_server:
            try:
                if hasattr(http_server, 'stop'):
                    http_server.stop()
                elif hasattr(http_server, 'shutdown'):
                    http_server.shutdown()
            except Exception as e:
                logging.debug(f"Error stopping HTTP server: {e}")
        
        logging.info("Server shutdown complete")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    logging.info(f"Starting server on {Config.HOST}:{Config.PORT}")
    
    # Try different WSGI servers in order of preference
    try:
        import eventlet
        import eventlet.wsgi
        
        logging.info("Using eventlet WSGI server (recommended for Socket.IO)")
        eventlet.wsgi.server(eventlet.listen((Config.HOST, Config.PORT)), server.app)
    except ImportError:
        try:
            from gevent import pywsgi
            from geventwebsocket.handler import WebSocketHandler
            
            logging.info("Using gevent WSGI server with WebSocket support")
            http_server = pywsgi.WSGIServer(
                (Config.HOST, Config.PORT),
                server.app,
                handler_class=WebSocketHandler
            )
            http_server.serve_forever()
        except ImportError:
            # Fallback to Flask dev server (not recommended for production)
            logging.warning("eventlet/gevent not available, using Flask dev server")
            server.app.run(host=Config.HOST, port=Config.PORT, debug=False, use_reloader=False)