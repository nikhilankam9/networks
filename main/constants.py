host = '127.0.0.1'
port = 8989

# maximum data to be received at once is set by BUFFER_SIZE
BUFFER_SIZE = 10240
FRAME_DATA_SIZE = BUFFER_SIZE - 4 * 4 # considering the 4 int in the packet

TIME_OUT = 300
ACK = 1
NACK = 0

DATA_PACKET_FORMAT = '3I '+ str(FRAME_DATA_SIZE) +'s I'
''' A data packet consists 
1) Current frame sequence number
2) Size of the frame
3) Total number of frames
4) Encoded part of the message
5) Checksum
'''

ACK_PACKET_FORMAT = '2I'
''' An acknowledgement packet consists
1) __ACK(1) or __NAK(0)
2) Last received frame sequence number
'''