import threading
import time
import socketio
import statistics
import argparse

# --- Configuration ---
SERVER_URL = "http://localhost:5000"

# --- Shared Data for Metrics ---
# These will be accessed by multiple threads
latencies = []
successful_connections = 0
failed_connections = 0
messages_sent = 0
lock = threading.Lock()

def run_chat_client(client_id, messages_to_send, listener_ready_event):
    """Simulates a single client's behavior: connect, register, send messages."""
    global successful_connections, failed_connections, messages_sent

    sio = socketio.Client()
    try:
        sio.connect(SERVER_URL)
        with lock:
            successful_connections += 1
    except Exception as e:
        with lock:
            failed_connections += 1
        # print(f"Client {client_id} connection failed: {e}")
        return

    # Register with a unique username
    sio.emit('register', {'username': f'test_user_{client_id}'})

    # Wait until the listener client is ready to ensure we measure all messages
    listener_ready_event.wait()

    # Send messages with timestamps
    for i in range(messages_to_send):
        payload = {
            'message': f'Hello from {client_id}, message {i}',
            'timestamp': time.time()
        }
        sio.emit('message', payload)
        with lock:
            messages_sent += 1
        time.sleep(0.05) # Stagger messages slightly

    sio.disconnect()

def listener_client(num_total_messages, listener_ready_event):
    """A dedicated client to listen for all messages and calculate latency."""
    sio = socketio.Client()
    
    @sio.on('message')
    def on_message(data):
        if 'timestamp' in data:
            latency = time.time() - data['timestamp']
            with lock:
                latencies.append(latency)

    try:
        sio.connect(SERVER_URL)
        sio.emit('register', {'username': 'listener'})
        listener_ready_event.set() # Signal that the listener is ready
    except Exception as e:
        print(f"Listener client failed to connect: {e}")
        listener_ready_event.set() # Unblock other threads even if listener fails
        return

    # Keep the listener alive until all expected messages are received or timeout
    start_time = time.time()
    timeout = 60  # 60-second timeout
    while len(latencies) < num_total_messages and time.time() - start_time < timeout:
        sio.sleep(0.1)

    sio.disconnect()

def main(num_clients, messages_per_client):
    threads = []
    listener_ready_event = threading.Event()
    total_messages = num_clients * messages_per_client

    print(f"Starting load test with {num_clients} clients, {messages_per_client} messages each...")
    start_time = time.time()

    # Start the listener client
    listener_thread = threading.Thread(target=listener_client, args=(total_messages, listener_ready_event))
    threads.append(listener_thread)
    listener_thread.start()

    # Start the sender clients
    for i in range(num_clients):
        thread = threading.Thread(target=run_chat_client, args=(i, messages_per_client, listener_ready_event))
        threads.append(thread)
        thread.start()
        time.sleep(0.01) # Stagger connections slightly

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    end_time = time.time()
    duration = end_time - start_time

    # --- Print Results ---
    print("\n--- Load Test Results ---")
    print(f"Test duration: {duration:.2f} seconds")
    print(f"Successful connections: {successful_connections}/{num_clients}")
    print(f"Failed connections: {failed_connections}")
    print(f"Total messages sent: {messages_sent}")
    print(f"Total messages received: {len(latencies)}")

    if latencies:
        avg_latency = statistics.mean(latencies) * 1000
        max_latency = max(latencies) * 1000
        min_latency = min(latencies) * 1000
        throughput = len(latencies) / duration if duration > 0 else 0

        print(f"\nMessage Latency (ms):")
        print(f"  - Average: {avg_latency:.2f} ms")
        print(f"  - Min:     {min_latency:.2f} ms")
        print(f"  - Max:     {max_latency:.2f} ms")
        print(f"Server Throughput: {throughput:.2f} messages/sec")
    else:
        print("\nNo latencies recorded. Did the listener receive any messages?")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Chat Server Load Tester")
    parser.add_argument("-c", "--clients", type=int, default=50, help="Number of concurrent clients to simulate.")
    parser.add_argument("-m", "--messages", type=int, default=10, help="Number of messages each client will send.")
    args = parser.parse_args()
    print(f"Parsed arguments: {args}")
    main(args.clients, args.messages)
