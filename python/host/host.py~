import sys, os
sys.path.append("../common");
import socket
import pygame
import time

from data_transfer import send_data
from mss import mss
from lz4.frame import compress, decompress
 
DEST_IP = '192.168.0.3'
PORT = 55000

MONITOR = {'top': 0, 'left': 0, 'width': 1600, 'height': 1200}



fb_grabber = mss();

while True:
    pixels = fb_grabber.grab(MONITOR);
    compressed_data = compress(pixels.rgb);
    send_data(compressed_data, DEST_IP, PORT);
