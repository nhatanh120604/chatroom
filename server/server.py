import socketio
from flask import Flask, request
import eventlet

class ChatServer():
    def __init__(self, test=False):
        self.sio = socketio.Server(cors_allowed_origins='*')
        self.app = Flask(__name__)
        self.app.wsgi_app = socketio.WSGIApp(self.sio, self.app.wsgi_app)
        self.clients = {}
        self.test = test

        self.register_events()

    def register_events(self):

        @self.sio.event
        def connect(sid, environ):
            print(f"Client connected: {sid}")
            

        @self.sio.event
        def disconnect(sid):
            print(f"Client disconnected: {sid}")
            username = self.clients.pop(sid, None)
            if username:
                # Notify remaining clients that a user has left
                self.sio.emit('user_left', {'username': username})
                print(f"User left: {username}")


        @self.sio.event
        def register(sid, data):
            username = data.get('username')
            if username:
                self.clients[sid] = username
                # Notify other clients that a new user has joined
                self.sio.emit('user_joined', {'username': username}, skip_sid=sid)
                # Send the full user list to the newly registered client
                self.sio.emit('update_user_list', {'users': list(self.clients.values())}, to=sid)
                print(f"User registered: {username}")

        @self.sio.event
        def message(sid, data):
            """Handle incoming messages from a client and broadcast them."""
            sender_username = self.clients.get(sid, 'Unknown')
            
            # The data from the test client is the entire payload.
            # We need to add the sender's username and broadcast it.
            if data and 'message' in data:
                # Prepare the payload to be sent to all clients
                broadcast_data = {
                    'username': sender_username,
                    'message': data.get('message'),
                    'timestamp': data.get('timestamp') # Forward the timestamp for latency calculation
                }
                # Emit to all clients, including the listener.
                # `skip_sid=sid` is optional but good practice to not send the message back to the original sender.
                self.sio.emit('message', broadcast_data, skip_sid=sid)

if __name__ == '__main__':
    server = ChatServer()
    #server.app.run(port=5000, debug=True)
    eventlet.wsgi.server(eventlet.listen(('localhost', 5000)), server.app)