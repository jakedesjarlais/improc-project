import sys, os
sys.path.append("../common");

import time, pygame, pywt, numpy, StringIO, image_slicer, scipy, cPickle

from data_transfer import recv_data, init_server
from huffcode import Encoder, Decoder
from lz4.frame import compress, decompress
from mss import mss
from numpy import array
from numpy import reshape
from PIL import Image
from scipy import fftpack



BLOCK_SIZE = 40
THRESHOLD = .0019


def split_to_blocks(color_plane, size, block_size):
   return numpy.array([color_plane[i:i+block_size, j:j+block_size]
                       for j in reversed(range(0,size[0],block_size))
                       for i in range(0,size[1],block_size)])

def join(split_color_plane, size, block_size):
    joined = list();

    count = 0
    for i in range(0,size[1]/block_size):
        for j in range(0,block_size):
            arr = numpy.array([]);
            for k in range(0,size[0]/block_size):
                tmp_arr = reversed(split_color_plane[i*(size[1]/block_size) + k, 0:block_size, j])
                arr = numpy.append(arr, tmp_arr);
            joined.append(arr);

    return joined

def dct2(sub_image):
    dct_1d = scipy.fftpack.dct(sub_image, axis=0,norm='ortho')
    return scipy.fftpack.dct(dct_1d, axis=1, norm='ortho')

def idct2(sub_image):
    idct_1d = scipy.fftpack.idct(sub_image, axis=0 , norm='ortho')
    return scipy.fftpack.idct(idct_1d, axis=1 , norm='ortho')

def threshold(block):
    return block * (abs(block) > (THRESHOLD * numpy.max(block)))

def dct_compress_plane(image, size, block_size):
    dct = numpy.zeros((size[0],size[1]), dtype='complex');

    for i in range(0,size[0],block_size):
        for j in range(0,size[1],block_size):
            tmp = dct2(image[i:i+block_size, j:j+block_size]);

            # Threshold here
            dct[i:i+block_size, j:j+block_size] = tmp * (abs(tmp) > (THRESHOLD * numpy.max(tmp)))

    return dct;

def idct_decompress_plane(image, size, block_size):
    idct = numpy.zeros((size[0],size[1]));

    for i in range(0,size[0],block_size):
        for j in range(0,size[1],block_size):
            idct[i:i+block_size, j:j+block_size] = idct2( image[i:i+block_size,j:j+block_size] )

    return idct;



def dct_compress(image_str, size=(1920,1080, 3)):
    image_data = numpy.frombuffer(image_str, dtype='uint8');
    image_data = numpy.reshape(image_data, size)

    r = image_data[..., 0]
    g = image_data[..., 1]
    b = image_data[..., 2]

    r_compressed = dct_compress_plane(r, size, BLOCK_SIZE)
    g_compressed = dct_compress_plane(g, size, BLOCK_SIZE)
    b_compressed = dct_compress_plane(b, size, BLOCK_SIZE)

    data = (r_compressed, g_compressed, b_compressed)

    return cPickle.dumps(data);


def dct_decompress(image_data, size=(1920,1080,3)):
    image_data = cPickle.loads(image_data)

    image = numpy.zeros(size, 'uint8');
    image[..., 0] = numpy.clip(idct_decompress_plane(image_data[0], size, BLOCK_SIZE), 0, 255)
    image[..., 1] = numpy.clip(idct_decompress_plane(image_data[1], size, BLOCK_SIZE), 0, 255)
    image[..., 2] = numpy.clip(idct_decompress_plane(image_data[2], size, BLOCK_SIZE), 0, 255)

    return image;

