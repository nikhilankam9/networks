import math
import asyncio
import argparse
import logging
import time
from constants import *
from packet import *

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


times = []
total_length = len(transfer_data)
total_frames = math.ceil(total_length / FRAME_DATA_SIZE) + 1

async def handle_conn(reader, writer):
    start = time.time()

    current_frame = 1
    last_transmitted_frame = 0
    frames_transmitted = 0

    try:
        while frames_transmitted != total_frames:
            current_frame = last_transmitted_frame + 1

            data_packet = packet(DATA_PACKET_FORMAT)
            last_trans_data_loc = last_transmitted_frame * FRAME_DATA_SIZE
            packet_args = (current_frame, data_packet.size(), total_frames, \
                transfer_data[last_trans_data_loc: last_trans_data_loc + FRAME_DATA_SIZE].encode('ascii'), 0)
            data_packet.set_args(*packet_args)

            try:
                packet_bytes = data_packet.pack()
            except struct.error as e:
                log.error(f'packing error {last_transmitted_frame}')

            sent = writer.write(packet_bytes)
            await writer.drain()

            if sent == 0:
                log.warning(f'sent 0 bytes: {last_transmitted_frame}')

            ack_packet = await reader.read(BUFFER_SIZE)

            try:
                ack, last_transmitted_frame = packet(ACK_PACKET_FORMAT).unpack(ack_packet)
            except struct.error as e:
                log.error(f'unpacking error {len(ack_packet)}, {ack_packet[:10]}, {last_transmitted_frame}')

            if ack == ACK:
                frames_transmitted += 1

            if ack == NACK:
                # do nothing coz the loop retries based on the last transmitted frame
                pass
        
        end = time.time()
        times.append(end - start)

        log.info(f'Server: {writer.get_extra_info("peername")} Frames: {frames_transmitted} Msg len: {total_length}')
    except ConnectionResetError:
        if last_transmitted_frame == total_frames - 1:
            log.warning('gracefully ignoring last packet')
        else:
            log.error(f'connection', exc_info=True)
    finally:
        writer.close()

async def main():
    async with asyncio.TaskGroup() as tg:
        tasks = []
        for _ in range(no_of_clients):
            reader, writer = await asyncio.open_connection(host, port)
            task = tg.create_task(handle_conn(reader, writer))
            tasks.append(task)
        
        asyncio.gather(*tasks)


if __name__ == "__main__":
    start = time.time()
    asyncio.run(main())
    end = time.time()

    log.critical(f'Avg = {round(sum(times)/len(times), 3)}, \
        Max:{round(max(times), 3)}, \
        Min:{round(min(times), 3)}, \
        Total: {round(end - start, 3)}')