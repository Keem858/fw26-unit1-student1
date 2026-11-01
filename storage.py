# storage.py
import threading
from collections import deque


class Storage:
    # constructor
    def __init__(self):
        self._data = {}
        self._queue = deque()
        """
        threading.Lock() vs threading.Condition()
        Lock controls access while Condition waits for some condition to become True.
        """
        self._lock = threading.Lock()
        self._condition = threading.Condition()

    # methods
    # Desc 1: Puts a item into the shared datastructure.
    # Desc 2: Lock attribute resolves issue of concurrent processes modifying the datastructure.
    def put(self, key, value):
        with self._lock:
            self._data[key] = value

    # Desc: Retrieves data for the data structure.
    def get(self, key):
        with self._lock:
            return self._data[key]

    # Desc: Enqueue's string unto queue.
    def enqueue(self, data):
        with self._condition:
            self._queue.append(data)
            self._condition.notify()

    # Desc: Dequeue's string from top of queue.
    def dequeue(self):
        with self._condition:
            while not self._queue:
                self._condition.wait()
            return self._queue.popleft()

    # AI Assisted Method
    # Desc: Returns a string of data for printing.
    def print_data(self):
        with self._lock:
            map_snap = self._data.copy()

        with self._condition:
            queue_snap = list(self._queue)

        return f"Map: {map_snap} \n Queue: {queue_snap}"
