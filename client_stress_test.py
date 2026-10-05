# client.py
import socket

# Startup
"""
HOST = "127.0.0.1"
PORT = 9090
message = "Hello from the client!"
with socket.create_connection((HOST, PORT)) as client_socket:
    client_socket.sendall(message.encode("utf-8"))
    echo = client_socket.recv(1024)
    print(f"Server echo'd: {echo.decode('utf-8', errors='replace')}")
"""


class Client:
    # attributes
    id = None

    # contructor
    def __init__(self, id=0000, host="127.0.0.1", port=9090):
        self.id = id
        self.socket = socket.create_connection((host, port))

    # methods
    def send(self, message: str) -> str:
        self.socket.sendall(message.encode("utf-8"))
        echo = self.socket.recv(1024)
        return echo.decode("utf-8", errors="replace")

    def close(self):
        self.socket.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


if __name__ == "__main__":
    # client list
    clients = []

    try:
        # create clients
        for _ in range(12):
            client = Client(id=_)
            clients.append(client)

        # handle client behavior
        for client in clients:
            try:
                echo = client.send(f"Hello from client: " + str(client.id))
                print(f"Server echode: {echo}")
            finally:
                # close connection to server
                client.close()

    finally:
        for client in clients:
            client.close()
