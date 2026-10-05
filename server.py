# server.py
import socket
from concurrent.futures import ThreadPoolExecutor
from client_stress_test import Client
import queue
import threading

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
def client_handler(client_socket, client_addr):
    print(f"New connection from {client_addr}")

    # Management of worker thread <--> client connection
    with client_socket:
        try:
            while True:
                data = client_socket.recv(1024)
                if data:
                    print(
                        f"Received: {data.decode('utf-8', errors='replace')}")
                    client_socket.sendall(data)  # Echo to the client
                if not data:
                    return

        except OSError as exc:
            print(f"Connection error with {client_addr}: {exc}")


# Instantiating worker pool
pool = Pool(MAX_WORKERS)


# Establishing connection to socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()


# Iterative socket listening & handling
try:
    while True:
        client_socket, client_addr = server_socket.accept()

        # Dispatching thread from pool
        pool.submit(client_handler, client_socket, client_addr)

except:
    print("\nShutting down server...")

finally:
    server_socket.close()
    pool.shutdown()
