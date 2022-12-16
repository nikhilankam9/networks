#!/usr/bin/env python3

import socket
import selectors
import types
import time
import argparse
import logging
from constants import *

parser = argparse.ArgumentParser()
parser.add_argument( '-log',
                     '--loglevel',
                     default='warning',
                     help='Provide logging level. Example --loglevel debug, default=warning' )
parser.add_argument('-n',
                     default=100,
                     help='Provide no of clients (default 100)')

args = parser.parse_args()
logging.basicConfig( level=args.loglevel.upper() )
log = logging.getLogger('client')

no_of_clients = int(args.n)

sel = selectors.DefaultSelector()
messages = []
for i in range(0, len(transfer_data), BUFFER_SIZE):
    messages.append(str.encode(transfer_data[i: i + BUFFER_SIZE]))

times = {}

def start_connections(host, port, num_conns):
    server_addr = (host, port)
    for i in range(0, num_conns):
        connid = i + 1
        times[connid] = [time.time(), time.time()]
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.connect_ex(server_addr)
        # sock.connect((host, port))
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        data = types.SimpleNamespace(
            connid=connid,
            msg_total=sum(len(m) for m in messages),
            # msg_total=len(messages),
            recv_total=0,
            messages=messages.copy(),
            outb=b"",
        )
        sel.register(sock, events, data=data)


def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(BUFFER_SIZE)
        if recv_data:
            times[data.connid][1] = time.time()
            # data.recv_total += len(recv_data)
            # print("got", recv_data, recv_data.decode('ascii'))
            # data.recv_total += int(recv_data.decode('ascii'))
            # print(data.recv_total)
        if not recv_data or 'a' in recv_data.decode('ascii'):
            sel.unregister(sock)
            sock.close()


        # recv_data = sock.recv(BUFFER_SIZE)
        # if recv_data:
        #     times[data.connid][1] = time.time()
        #     data.recv_total += len(recv_data.decode('ascii').rstrip('\x00'))
        # if data.recv_total == data.msg_total:
        #     sel.unregister(sock)
        #     sock.close()
    if mask & selectors.EVENT_WRITE:
        if not data.outb and data.messages:
            data.outb = data.messages.pop(0)
        if data.outb:
            sent = sock.send(data.outb) 
            # print("sent", len(data.outb), len(data.messages), sent)
            data.outb = data.outb[sent:]

start_connections(host, port, no_of_clients)

try:
    while True:
        events = sel.select(timeout=1)
        if events:
            for key, mask in events:
                service_connection(key, mask)
        # Check for a socket being monitored to continue.
        if not sel.get_map():
            break

except KeyboardInterrupt:
    print("Caught keyboard interrupt, exiting")
finally:
    sel.close()

res = []
for t in times.values():
    res.append(t[1] - t[0])
# print(sum(res)/len(res))
print(f'Avg = {round(sum(res)/len(res), 3)}, \
        Max:{round(max(res), 3)}, \
        Min:{round(min(res), 3)}')