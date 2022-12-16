#!/usr/bin/env python3

import sys
import socket
import selectors
import types
from constants import *
import argparse
import logging

parser = argparse.ArgumentParser()
parser.add_argument( '-log',
                     '--loglevel',
                     default='warning',
                     help='Provide logging level. Example --loglevel debug, default=warning' )

args = parser.parse_args()
logging.basicConfig( level=args.loglevel.upper() )
log = logging.getLogger('server')

sel = selectors.DefaultSelector()

def accept_wrapper(sock):
    conn, addr = sock.accept()
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=0, outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)


def service_connection(key, mask):
    sock = key.fileobj
    local_data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(BUFFER_SIZE)
        # print(f"received connection to {local_data.addr}, {len(recv_data)}")
        if recv_data:
            local_data.outb = b"n"
            local_data.inb += len(recv_data)
            if (local_data.inb // BUFFER_SIZE) % 100 == 0:
                print(f"connection to {local_data.addr}, {local_data.inb}")
            if local_data.inb == len(transfer_data):
                local_data.outb = b"a"

        else:
            print(f"Closing connection to {local_data.addr}")
            # print("received", len(local_data.inb))
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        # print(f"send to {local_data.addr}, {local_data.outb}")
        if local_data.outb:
            sent = sock.send(local_data.outb) 
            local_data.outb = local_data.outb[sent:]
            # _ = sock.send(b'a') 
            # local_data.outb = b""


def get_socket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, port))
    sock.listen()
    log.info(f'serving: {(host, port)}')
    sock.setblocking(False)
    return sock

def main():
    server = get_socket()
    sel.register(server, selectors.EVENT_READ, data=None)
    try:
        while True:
            events = sel.select(timeout=None)
            for key, mask in events:
                if key.data is None:
                    accept_wrapper(key.fileobj)
                else:
                    service_connection(key, mask)
    except KeyboardInterrupt:
        print("Caught keyboard interrupt, exiting")
    finally:
        sel.close()

if __name__ == "__main__":
    main()