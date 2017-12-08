import sys, os
sys.path.append("../common");

import time, pygame

from data_transfer import send_data
from huffcode import huffman_compress
from wavelet_compress import wavelet_compress
from dct_compress import dct_compress
from lz4.frame import compress
from parse_args import parse_args
from mss import mss


# Project settings
DEFAULT_IP = '127.0.0.1' # Set appropriate IP
PORT = 5000
MONITOR = {'top': 0, 'left': 0, 'width': 1920, 'height': 1080}
WINDOW = (1920, 1080)

HELP_MESSAGE = ('USAGE: The host script streams its framebuffer to the client script.\n'
                'Note that the client script MUST be started before the host script\n'
                'and the compression types of both must match.\n'
                '\n'
                '       python host.py [OPTIONS] [LOSSY] [LOSSLESS]\n'
                '\n'
                '       OPTIONS\n'
                '           --help to display this message\n'
                '           --ip to set the destination IP Address\n'
                '           --raw to indicate no compression. Note that this cannot be\n'
                '                 included with any compression flags\n'
                '\n'
                '       LOSSY COMPRESSION TYPES\n'
                '           --wavelet for Wavelet based compression\n'
                '           --wavetype to indicate the wavelet type. See PyWave for list\n'
                '                      of wavetype options. Note this will only\n'
                '                      take effect when the dct option is selected\n'
                '           --dct for block based DCT compression. Block size of 20\n'
                '\n'
                '       LOSSLESS COMPRESSION TYPES\n'
                '           --huffman for huffman encoding\n'
                '           --lz4 for fast LZ4 encoding\n')
               



# Parse user arguements
args = parse_args(sys.argv)
if (args['HELP']):
    print HELP_MESSAGE
    quit()

if (args['IP'] is not None):
    destination_ip = args['IP']
else:
    destination_ip = DEFAULT_IP

    
# Object for grabbing frame buffer
fb_grabber = mss();
frame_count = 0
cum_time_compression = 0
cum_time_data_transfer = 0

while True:
    frame_buffer = fb_grabber.grab(MONITOR);
    data = frame_buffer.rgb

    # Compress frame based on user input
    start_time_compression = time.time();
    if (not args['RAW']):
        if (args['WAVELET']):
            if (args['WAVETYPE'] is not None):
                data = wavelet_compress(data, WINDOW, args['WAVETYPE']);
            else:
                data = wavelet_compress(data, WINDOW);
        elif (args['DCT']):
            data = dct_compress(data);

        if (args['LZ4']):
            data = compress(data);
        elif (args['HUFFMAN']):
            data = huffman_compress(data); 
            
    # Cumulative time for decompression
    end_time_compression = time.time()
    compression_time = end_time_compression - start_time_compression

    cum_time_compression = cum_time_compression + compression_time

    print 'Current Compression Latency:', compression_time 

    # Send data to client
    start_time_data_transfer = time.time()
    try:
        send_data(data, destination_ip, PORT);
    except:
        break;
    cum_time_data_transfer = cum_time_data_transfer + (time.time() - start_time_data_transfer)

    frame_count = frame_count + 1

if (frame_count > 0):
    print 'Average Compression Latency:', cum_time_compression/frame_count,
    print 'Average Data Transfer Time:', cum_time_data_transfer/frame_count,

