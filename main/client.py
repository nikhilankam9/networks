import socket
import sys

host = 'ec2-18-237-37-212.us-west-2.compute.amazonaws.com'
host = 'localhost'
port = 8989

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect((host, port))
    print(f'Connected to server Host:{host} Port:{port}')

    data = 'foobar\n' if len(sys.argv) == 1 else sys.argv[1]
    data = data * 10 * 1024 * 1024  # 70 MB of data
    assert sock.send(str.encode(data)) == len(data)