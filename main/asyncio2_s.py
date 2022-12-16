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
    c = 0
    try:
        while True:
            data_packet = await reader.read(BUFFER_SIZE)
            # print(len(data_packet), c)
            c += len(data_packet)
            if (c // BUFFER_SIZE) % 10 == 0:
                print(f'connection to {writer.get_extra_info("peername")}, {c}')
            
            if c >= len(transfer_data):
                break
        
        log.info(f'Recieved Client : {writer.get_extra_info("peername")} Msg len: {c}')

    except ConnectionResetError:
        log.warning('Client connection lost, gracefully ignoring client')
    finally:
        writer.close()

async def main():
    server = await asyncio.start_server(handle_client, host, port)
    addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    print(f'Serving on {addrs}')

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())