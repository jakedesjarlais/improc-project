import sys, os
sys.path.append("../common");
import time
import pygame

from data_transfer import recv_data, init_server
from huffcode import Encoder, Decoder
from lz4.frame import compress, decompress

PORT = 55000

WINDOW = (1920,1080)
pygame.init();
screen = pygame.display.set_mode(WINDOW);

image = pygame.image.load('../images/loading-screen.jpg');

init_server(PORT)

done = False
while not done:
    screen.blit(image, (0,0));
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    compressed_data = recv_data(PORT);
    data = decompress(compressed_data);

    image = pygame.image.frombuffer(data, WINDOW, 'RGB');

jpygame.quit()
