# client.py
import socket
from protocol import *
import random
from concurrent.futures import ThreadPoolExecutor

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
    def send(self, message: dict) -> dict:
        send_message(self.socket, message)
        return recv_message(self.socket)

    def close(self):
        self.socket.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


"""
# TEST CASE 1: 1 client connection
if __name__ == "__main__":
    request = {
        "action": "PUT",
        "key": "name",
        "value": "Alice"
    }

    with Client(id=0) as client:
        response = client.send(request)
        print(response)
"""


# AI Assisted
# TEST CASE 2: 20 CONCURRENT client connections
def client_worker(client_id):
    key = f"client_{client_id}"
    value = random.randint(1, 1000)

    with Client(id=client_id) as client:
        client.socket.settimeout(5)

        if random.random() > 0.5:
            # Store a value in the map.
            response = client.send({
                "action": "PUT",
                "key": key,
                "value": value
            })
            assert response == {"status": "OK"}, response

            # Retrieve and verify that value.
            response = client.send({
                "action": "GET",
                "key": key
            })
            assert response == {
                "status": "OK",
                "value": value
            }, response

            print(f"Client {client_id}: PUT and GET verified")

        else:
            # Add a task to the shared queue.
            task = f"Client {client_id}: process value {value}"

            response = client.send({
                "action": "ENQUEUE",
                "value": task
            })
            assert response == {"status": "OK"}, response

            print(f"Client {client_id}: ENQUEUE acknowledged")


if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=20) as executor:
        results = list(executor.map(client_worker, range(20)))

    print("PASS: All 20 clients completed successfully")


"""
# AI Assisted
# TEST CASE 3: 10 client connections. Storage DEQUEUE and GET operations.
def test_case_3():
    expected_tasks = {f"test3_task_{i}" for i in range(10)}

    # Seed storage before starting the consumers.
    with Client(id="setup") as client:
        client.socket.settimeout(5)

        for i in range(10):
            response = client.send({
                "action": "PUT",
                "key": f"test3_key_{i}",
                "value": i
            })
            assert response == {"status": "OK"}, response

            response = client.send({
                "action": "ENQUEUE",
                "value": f"test3_task_{i}"
            })
            assert response == {"status": "OK"}, response

    def worker(client_id):
        with Client(id=client_id) as client:
            client.socket.settimeout(5)

            response = client.send({
                "action": "GET",
                "key": f"test3_key_{client_id}"
            })
            assert response == {
                "status": "OK",
                "value": client_id
            }, response

            response = client.send({"action": "DEQUEUE"})
            assert response.get("status") == "OK", response
            task = response["value"]
            assert task in expected_tasks, response

            print(f"Client {client_id}: GET and DEQUEUE verified")
            return task

    with ThreadPoolExecutor(max_workers=10) as executor:
        received_tasks = list(executor.map(worker, range(10)))

    # Every seeded task must be removed exactly once.
    assert len(received_tasks) == 10
    assert set(received_tasks) == expected_tasks, received_tasks

    print("PASS: All 10 clients verified GET and DEQUEUE")


if __name__ == "__main__":
    test_case_3()
"""
