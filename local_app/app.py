import socket
import webhooks

HOST = '127.0.0.1'  # Localhost
PORT = 8080        # Arbitrary non-privileged port


# Create a TCP/IP socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sckt:
    sckt.bind((HOST, PORT))        # Bind to localhost on port 8080
    sckt.listen()                  # Start listening for incoming connections
    print(f"Listening on {HOST}:{PORT}...")

    while True:
        conn, addr = sckt.accept()  # Accept new connection
        with conn:
            print(f"\nConnected by {addr}")
            buffer = conn.recv(8192)  # Receive data (in bytes)
            if buffer:
                data_str = buffer.decode('utf-8')
                hook = webhooks.parse_webhook(data_str)
                webhooks.handle_webhook(hook)
            conn.close()  # Close connection when finished
