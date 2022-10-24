import socket
import sys

host = 'localhost'
port = 8989

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.bind((host, port))
    print(f'Started TCP server Host:{host} Port:{port}')
    sock.listen(5)

    try:
        while True:
            conn, info = sock.accept()
            print('Client connected: {info}')
            with conn:
                data = conn.recv(1024)
                while data:
                    print(data.decode('ascii'))
                    data = conn.recv(1024)
    except KeyboardInterrupt:
        sock.close