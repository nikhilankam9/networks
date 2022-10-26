import socket
import struct
from packet import *
from constants import *

def get_socket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # socket family(ipv4 address family) and socket type(tcp)

    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # level(current socket itself), reuse = True(1)

    sock.bind((host, port))
    sock.listen(1) # backlog(# of unaccepted conn before refusing)
    print(f'TCP socket serving: {(host, port)}')

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
                frame_no, frame_size, total_frames, data, checksum = packet(DATA_PACKET_FORMAT).unpack(data_packet)
                
                ack = None
                if not ack and frame_no <= last_received_frame:
                    ack = ACK #gracefully ignoring if a duplicate packet is sent

                if not ack and frame_size == len(data_packet): # validating if the whole packet is received
                    ack = NACK
                
                #TODO: Add checksum validation
                if not ack and frame_no == last_received_frame + 1:
                    last_received_frame += 1
                    frames_received += 1
                    message += data.decode('ascii')
                    ack = ACK
                
                ack_packet = packet(ACK_PACKET_FORMAT)
                ack_packet.set_args(ack, last_received_frame)
                c.send(ack_packet.pack())

            if frames_received == total_frames:
                break


        print(f'Client: {c.getpeername()} Frames: {frames_received} Msg len: {len(message)}')

    except struct.error as e:
        print(f'ERROR: packing error {e}')
    except ConnectionResetError:
        print('Client connection lost, gracefully ignoring client')
    except Exception as e:
        raise e
    finally:
        c.close()

def serve_traffic(sock):
    while True:
        try:
            client, address = sock.accept() # connection socket and its address
            sock.settimeout(TIME_OUT) #timeout on blocking sockets
            print(f"Connected from {str(address)}")

            handle_client(client)

        except Exception as e:
            raise e

def main():
    try:
        server = get_socket()
        serve_traffic(server)

    except KeyboardInterrupt:
        print('---- Graceful shutdown ----')
    finally:
        server.close()

if __name__ == "__main__":
    main()