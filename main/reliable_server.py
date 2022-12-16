from random import randint
import socket
import struct
from packet import *
from constants import *
import threading
import argparse
import logging
import time

parser = argparse.ArgumentParser()
parser.add_argument( '-log',
                     '--loglevel',
                     default='warning',
                     help='Provide logging level. Example --loglevel debug, default=warning' )

args = parser.parse_args()
logging.basicConfig( level=args.loglevel.upper() )
log = logging.getLogger('server')

lock = threading.Lock()
received = 0
handled = 0

def get_socket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # socket family(ipv4 address family) and socket type(tcp)

    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # level(current socket itself), reuse = True(1)

    sock.bind((host, port))
    sock.listen() # backlog(# of unaccepted conn in queue before refusing)
    log.info(f'serving: {(host, port)}')

    return sock

def handle_client(c :socket):
    frames_received = 0
    last_received_frame = 0
    message = ""
    total_frames = 0

    try:
        while True:
            data_packet = c.recv(BUFFER_SIZE)
            if len(data_packet) > 0:
                #TODO: what if these values are corrupted?
                frame_no, frame_size, total_frames, data_piece, checksum = \
                    packet(DATA_PACKET_FORMAT).unpack(data_packet)
                ack = None
                if not ack and frame_no <= last_received_frame:
                    ack = ACK #gracefully ignoring if a duplicate packet is sent

                if not ack and frame_size == len(data_packet): # validating if the whole packet is received
                    ack = NACK
                
                #TODO: Add checksum validation
                if not ack and frame_no == last_received_frame + 1:
                    last_received_frame += 1
                    frames_received += 1
                    # message += data_piece.decode('ascii').rstrip('\x00')
                    if frame_no % 1000 == 0:
                        log.debug(f'{frame_no}, {c.getpeername()}')
                    ack = ACK

                ack_packet = packet(ACK_PACKET_FORMAT)
                ack_packet.set_args(ack, last_received_frame)
                sent = c.send(ack_packet.pack())
                if sent == 0:
                    log.warning(f'sent 0 bytes: {last_received_frame}')

            if frames_received == total_frames:
                break
        
        # if message != transfer_data:
        #     log.error(f'{len(message)}, {len(transfer_data)}')
        log.info(f'Recieved Client : {c.getpeername()} Frames: {frames_received} Msg len: {len(message)}')
        
        lock.acquire()
        global handled
        handled += 1
        lock.release()

    except struct.error as e:
        log.error('packing error', exc_info=True)
    except ConnectionResetError:
        log.warning('Client connection lost, gracefully ignoring client')
    except socket.error as e:
        log.error(f'socket error', exc_info=True)
    finally:
        log.info(f'Packets Rec: {frames_received} Total: {total_frames}')
        c.close()

def serve_traffic(sock):
    while True:
        try:
            global received
            received += 1

            client, address = sock.accept() # connection socket and its address
            sock.settimeout(TIME_OUT) #timeout on blocking sockets
            log.info(f'Connected from {str(address)}')
        
            thread = threading.Thread(target=handle_client, args=(client, ))
            thread.start()

        except Exception as e:
            raise e

def main():
    try:
        server = get_socket()
        serve_traffic(server)

    except KeyboardInterrupt:
        log.warning('---- Graceful shutdown ----')
        global received 
        global handled
        log.critical(f'Requests: Rec: {received}, Handle: {handled}')
    except TimeoutError:
        log.warning('---- Graceful Timeout ----')
    finally:
        log.info(f'Closing the server socket')
        server.close()

if __name__ == "__main__":
    main()