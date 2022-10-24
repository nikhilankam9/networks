import socket
import sys

host = 'localhost'
port = 8989

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, port))
    print(f'Started TCP server Host:{host} Port:{port}')
    sock.listen(5)
    sock.setblocking(False)

    connections = []
    try:
        while True:
            try:
                conn, info = sock.accept()
                conn.setblocking(False)
                print('Client connected: {info}')
                connections.append(conn)
            except BlockingIOError:
                pass

            for conn in connections:
                try:
                    data = conn.recv(1024)
                    while data:
                        print(data)
                        data = conn.recv(1024) 
                except BlockingIOError:
                    pass
    except KeyboardInterrupt:
        print('Closing server')

