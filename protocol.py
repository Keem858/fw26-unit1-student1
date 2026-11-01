import json
import io
from io import BytesIO
import struct

"""
JSON Formatting Examples:
{
    "action": "PUT",
    "key": "name",
    "value": "Alice"
}

{
    "action": "GET",
    "key": "name"
}

{
    "action": "ENQUEUE",
    "value": "task1"
}

{
    "action": DEQUEUE
}
"""


"""
The below three helper functions handle sending a byte stream
between sockets.
"""


# AI Assisted Function
# Desc: Receives exactly size bytes from a socket, handling partial reads.
def recv_exact(sock, size):
    data = bytearray()
    while len(data) < size:
        chunk = sock.recv(size - len(data))
        if not chunk:
            raise EOFError(
                "Connection closed before all bytes were received.")
        data.extend(chunk)
    return bytes(data)


# AI Assisted Function
# Desc: Sends a dict as a length-prefixed JSON message
def send_message(sock, message):
    payload = json.dumps(message).encode("utf-8")
    header = struct.pack("!I", len(payload))
    sock.sendall(header + payload)


# AI Assisted Function
# Desc: Turns a byte-stream into a JSON message
def recv_message(sock):
    header = recv_exact(sock, 4)
    payload_size = struct.unpack("!I", header)[0]

    payload = recv_exact(sock, payload_size)
    message = json.loads(payload.decode("utf-8"))
    if not isinstance(message, dict):
        raise ValueError("Message must be a JSON object")
    return message
