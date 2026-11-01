# server.py
import socket
from concurrent.futures import ThreadPoolExecutor
import queue
import threading
from protocol import *
from storage import Storage

HOST = "127.0.0.1"
PORT = 9090
MAX_WORKERS = 10

'''
# Creating thread pool
"""
ThreadPoolExecutor documentation: https://superfastpython.com/threadpoolexecutor-in-python/
1. create -> pool = ThreadPoolExecutor(max_workers=MAX_WORKERS)
2. submit -> pool.submit(client_handler, client_socket, client_addr)
3. wait ->
4. shutdown ->
* ThreadPoolExecutor has a built in Queue and manager.
"""
pool = ThreadPoolExecutor(max_workers=MAX_WORKERS)
'''


# Pool class
class Pool:
    # constructor
    def __init__(self, max_workers):
        self.tasks = queue.Queue()
        self.threads = []
        for i in range(max_workers):
            worker = threading.Thread(
                target=self.worker,
                name=f"worker-{i + 1}",
                daemon=True
            )
            worker.start()
            self.threads.append(worker)

    # methods
    def submit(self, function, *args, **kwargs):
        # Queue the callable and its arguments for an available worker.
        self.tasks.put((function, args, kwargs))

    def worker(self):
        while True:
            task = self.tasks.get()
            try:
                if task is None:
                    return

                function, args, kwargs = task
                function(*args, **kwargs)
            except Exception as exec:
                print(f"Worker error: {exec}")
            finally:
                self.tasks.task_done()

    def shutdown(self, wait=True):
        # One shutdown signal per worker
        for _ in self.threads:
            self.tasks.put(None)

        if wait:
            for worker in self.threads:
                worker.join()


# Routine for handling client connections
def client_handler(client_socket, client_addr, storage):
    print(f"New connection from {client_addr}")

    # Management of worker thread <--> client connection
    with client_socket:
        try:
            while True:
                data = recv_message(client_socket)  # Defined in protocol
                # Storage manipulation
                if data["action"] == "PUT":
                    storage.put(data["key"], data["value"])
                    response = {"status": "OK"}
                elif data["action"] == "GET":
                    try:
                        value = storage.get(data["key"])
                        response = {"status": "OK", "value": value}
                    except KeyError:
                        response = {
                            "status": "ERROR",
                            "message": "Key not found"
                        }
                elif data["action"] == "ENQUEUE":
                    storage.enqueue(data["value"])
                    response = {"status": "OK"}
                elif data["action"] == "DEQUEUE":
                    response = {"status": "OK", "value": storage.dequeue()}
                else:
                    response = {
                        "status": "ERROR",
                        "message": "Unknown action"
                    }
                send_message(client_socket, response)

        except EOFError:
            print(f"Connection closed by {client_addr}")
        except (OSError, ValueError, KeyError) as exc:
            print(f"Request error with {client_addr}: {exc}")


# Instantiating worker pool
pool = Pool(MAX_WORKERS)


# Instantiating storage
storage = Storage()


# Establishing connection to socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()


# Iterative socket listening & handling (Dispatcher Thread)
try:
    while True:
        client_socket, client_addr = server_socket.accept()

        # Dispatching thread from pool
        pool.submit(client_handler, client_socket, client_addr, storage)

except KeyboardInterrupt:
    # Listens for "ctrl+c" keystroke and stops the server when it is pressed.
    print("\nShutting down server...")

finally:
    server_socket.close()
    pool.shutdown()
    print("Final storage: ", storage.print_data())
