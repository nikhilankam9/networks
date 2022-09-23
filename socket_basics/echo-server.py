import socket

HOST = "127.0.0.1" 
PORT = 8989

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.settimeout(600)
    print(s.getsockname(), s.getblocking())
    s.bind((HOST, PORT))
    s.listen()
    while True:
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                conn.sendall(data)
                #what is time_wait in netstat -an? and why are sockets not closed immediately
