import socket
import struct
import threading
from packet import *
from constants import *
import sys
import time
import math
import argparse
import logging

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

total_length = len(data)
total_frames = math.ceil(total_length / FRAME_DATA_SIZE) + 1

lock = threading.Lock()
times = []

def handle_data(server: socket):
    current_frame = 1
    last_transmitted_frame = 0
    frames_transmitted = 0

    try:
        while frames_transmitted != total_frames:
            current_frame = last_transmitted_frame + 1

            data_packet = packet(DATA_PACKET_FORMAT)
            last_trans_data_loc = last_transmitted_frame * FRAME_DATA_SIZE
            packet_args = (current_frame, data_packet.size(), total_frames, data[last_trans_data_loc: last_trans_data_loc + FRAME_DATA_SIZE].encode('ascii'), 0)
            data_packet.set_args(*packet_args)

            try:
                packet_bytes = data_packet.pack()
            except struct.error as e:
                log.error(f'packing error {last_transmitted_frame}')

            sent = server.send(packet_bytes)
            if sent == 0:
                log.warning(f'sent 0 bytes: {last_transmitted_frame}')

            ack_packet = server.recv(BUFFER_SIZE)
            try:
                ack, last_transmitted_frame = packet(ACK_PACKET_FORMAT).unpack(ack_packet)
            except struct.error as e:
                log.error(f'unpacking error {len(ack_packet)}, {ack_packet[:10]}, {last_transmitted_frame}')

            if ack == ACK:
                frames_transmitted += 1

            if ack == NACK:
                # do nothing coz the loop retries based on the last transmitted frame
                pass
        
        log.info(f'Server: {server.getpeername()} Frames: {frames_transmitted} Msg len: {total_length}')
    except ConnectionResetError:
        if last_transmitted_frame == total_frames - 1:
            log.warning('gracefully ignoring last packet')
        else:
            log.error(f'connection', exc_info=True)
    except socket.error as e:
        log.error(f'socket error', exc_info=True)
    finally:
        server.close()

def client():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(TIME_OUT)
            sock.connect((host, port))
            log.info(f'Sock: {sock.getsockname()}, Data/Frame: {FRAME_DATA_SIZE}, Frames: {total_frames}')

            start = time.time()
            handle_data(sock)
            end = time.time()

            # locking makes update sequential but it should not impact because handle_data(sock)
            # is finshed and end time is captured
            # it may impact total time
            lock.acquire()
            times.append(end - start)
            lock.release()

    except OSError:
        log.error(f'os error', exc_info=False)
    except UnboundLocalError:
        log.error('reference error', exc_info=False)
    except Exception as e:
        log.error(f'Unknown error', exc_info=True)

if __name__ == "__main__":
    start = time.time()
    all_threads = []

    for i in range(no_of_clients):
        thread = threading.Thread(target=client, args=())
        thread.start()
        all_threads.append(thread)

    for t in all_threads:
        t.join()
    end = time.time()

    log.critical(f'Avg = {sum(times)/len(times)}, Max:{max(times)}, Min:{min(times)}, Total: {end - start}')
    