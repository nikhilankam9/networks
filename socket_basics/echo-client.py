import socket
import time

HOST = "127.0.0.1"
PORT = 8989 

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b"Hello, world")
    time.sleep(2)
    data = s.recv(1024)

print(f"Received {data!r}")

