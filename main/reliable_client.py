import socket
import struct
from packet import *
from constants import *
import sys
import time

data = "foo_bar" if len(sys.argv) == 1 else sys.argv[1]
data = data * 1024 * 1024 #70MB

def split_data(data=data):
    data_frames = {}
    data_cp = data
    while len(data_cp):
        # print(len(data_cp))
        data_frames[len(data_frames) + 1] = data_cp[:FRAME_DATA_SIZE]
        data_cp = data_cp[FRAME_DATA_SIZE:]
    
    return data_frames

def handle_data(server: socket):
    data_frames = split_data(data)
    total_length = len(data)
    current_frame = 1
    last_transmitted_frame = 0
    frames_transmitted = 0

    try:
        while frames_transmitted != len(data_frames):
            current_frame = last_transmitted_frame + 1

            data_packet = packet(DATA_PACKET_FORMAT)
            packet_args = (current_frame, data_packet.size(), len(data_frames), data_frames[current_frame].encode('ascii'), 0)
            data_packet.set_args(*packet_args)
            packet_bytes = data_packet.pack()

            server.send(packet_bytes)

            ack_packet = server.recv(BUFFER_SIZE)
            ack, last_transmitted_frame = packet(ACK_PACKET_FORMAT).unpack(ack_packet)

            if ack == ACK:
                frames_transmitted += 1

            if ack == NACK:
                # do nothing coz the loop retries based on the last transmitted frame
                pass
        
        print(f'Server: {server.getpeername()} Frames: {frames_transmitted} Msg len: {total_length}')
    except struct.error as e:
        print(f'ERROR: packing error {e}')
    except Exception as e:
        raise e
    finally:
        server.close()


def client():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        sock.settimeout(TIME_OUT)
        print(f'Server: {(host, port)}, Data/Frame: {FRAME_DATA_SIZE}')

        start = time.time()
        handle_data(sock)
        end = time.time()
        print(end - start)

    except Exception as e:
        raise e
    finally:
        sock.close()

if __name__ == "__main__":
    client()



