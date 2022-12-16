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

async def handle_conn(reader, writer):
    start = time.time()
    ll = 0
    msg = transfer_data

    try:
        while ll < total_length:
            writer.write(msg[:BUFFER_SIZE].encode())
            msg = msg[BUFFER_SIZE:]
            ll += BUFFER_SIZE
            # print(ll, BUFFER_SIZE, len(msg))
            # if (ll // BUFFER_SIZE) % 10 == 0:
            await writer.drain()
        
        end = time.time()
        times.append(end - start)

        log.info(f'Server: {writer.get_extra_info("peername")} Msg len: {ll}')

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