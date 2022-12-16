import asyncio
import struct
import logging
import argparse
from constants import *
from packet import *

parser = argparse.ArgumentParser()
parser.add_argument( '-log',
                     '--loglevel',
                     default='warning',
                     help='Provide logging level. Example --loglevel debug, default=warning' )

args = parser.parse_args()
logging.basicConfig( level=args.loglevel.upper() )
log = logging.getLogger('server')

async def handle_client(reader, writer):
    frames_received = 0
    last_received_frame = 0
    message = ""
    total_frames = 0

    try:
        while True:
            
            data_packet = await reader.read(BUFFER_SIZE)
            # log.debug(f'got {len(data_packet)} from {writer.get_extra_info("peername")}')
            
            if len(data_packet) > 0:
                frame_no, frame_size, total_frames, data_piece, checksum = \
                    packet(DATA_PACKET_FORMAT).unpack(data_packet)
                ack = None
                if not ack and frame_no <= last_received_frame:
                    ack = ACK 

                if not ack and frame_size == len(data_packet): 
                    ack = NACK
                
                if not ack and frame_no == last_received_frame + 1:
                    last_received_frame += 1
                    frames_received += 1
                    # message += data_piece.decode('ascii').rstrip('\x00')
                    if frame_no % 2000 == 0:
                        log.debug(f'{frame_no}, {writer.get_extra_info("peername")}')
                    ack = ACK

                ack_packet = packet(ACK_PACKET_FORMAT)
                ack_packet.set_args(ack, last_received_frame)

                writer.write(ack_packet.pack())
                await writer.drain()

            if frames_received == total_frames:
                break
        
        # if message != transfer_data:
        #     log.error(f'{len(message)}, {len(transfer_data)}')
        log.info(f'Recieved Client : {writer.get_extra_info("peername")} Frames: {frames_received} Msg len: {len(message)}')
    
    except struct.error as e:
        log.error('packing error', exc_info=True)
    except ConnectionResetError:
        log.warning('Client connection lost, gracefully ignoring client')
    finally:
        log.info(f'Packets Rec: {frames_received} Total: {total_frames}')
        writer.close()

async def main():
    server = await asyncio.start_server(handle_client, host, port)
    addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    print(f'Serving on {addrs}')

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    # execute the coroutine and return result
    # talk abouut what is a coroutine vs subroutine
    asyncio.run(main())

# what is await
# start server and serve forever
# what are streams, reader and wrtiter