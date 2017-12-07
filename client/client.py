import sys, os
sys.path.append("../common");
import time
import pygame

from data_transfer import send_data
from huffcode import Encoder, Decoder
from lz4.frame import compress, decompress

PORT = 55000

WINDOW = (1920,1080)
pygame.init();
screen = pygame.display.set_mode(WINDOW);


done = False
while not done:
    compressed_data = recv_data(port);
    data = decompress(compressed_data);

    image = pygame.image.frombuffer(data, WINDOW, 'RGB');

    screen.blit(image, (0,0));
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

jpygame.quit()
