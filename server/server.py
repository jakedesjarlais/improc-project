import socket
import pygame
import time

from mss import mss
 
DEST_IP = '192.168.0.3'
PORT = 55000

MONITOR = {'top': 0, 'left': 0, 'width': 1920, 'height': 1080}



fb_grabber = mss();

while True:
    pixels = fb_grabber.grab(monitor);
    send_data(pixel.rgb);
