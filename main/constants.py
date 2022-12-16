# host = '172.31.14.136'
# host = 'ec2-18-237-37-212.us-west-2.compute.amazonaws.com'
host = 'localhost'
port = 8989
transfer_data = "foo_bar"

# transfer_data = transfer_data * 1024 #7KB
# transfer_data = transfer_data * 10 * 1024 #70KB
# transfer_data = transfer_data * 100 * 1024 #700KB
# transfer_data = transfer_data * 1024 * 1024 #7MB
transfer_data = transfer_data * 100 * 1024 * 1024 #70MB

# maximum data to be received at once is set by BUFFER_SIZE
BUFFER_SIZE = 8 * 1024 #8KB
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
1) ACK(1) or NAK(0)
2) Last received frame sequence number
'''