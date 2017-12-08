

def parse_args(argv):
    raw = False
    lz4 = False
    huffman = False
    wavelet = False
    dct = False
    ip = None
    wavetype = None
    help_message = False

    for arg in argv:
        if (arg == '--raw'):
            if (lz4 or huffman or wavelet or dct):
                print '--raw cannot be delcared with other compression flags'
                quit()
            raw = True
        elif (arg == '--lz4'):
            if (huffman):
                print '--huffman cannot be declared with --lz4 compression flag'
                quit()
            lz4 = True
        elif (arg == '--huffman'):
            if (lz4):
                print '--lz4 cannot be declared with --huffman compression flag'
                quit()
            huffman = True
        elif (arg == '--wavelet'):
            if (dct):
                print '--wavelet cannot be declared with the --dct compression flag'
                quit()
            wavelet = True
        elif (arg.split('=')[0] == '--wavetype'):
            wavetype = arg.split('=')[1]
        elif (arg == '--dct'):
            if (wavelet):
                print '--dct cannot be declared with the --wavelet compression flag'
                quit()
            dct = True
        elif (arg == '--help'):
            help_message = True;
            break;
        elif (arg.split('=')[0] == '--ip'):
            ip = arg.split('=')[1]

    return ({ 'RAW' : raw,
             'LZ4' : lz4,
             'HUFFMAN' : huffman,
             'WAVELET' : wavelet,
             'WAVETYPE' : wavetype,
             'DCT' : dct,
             'IP' : ip,
             'HELP' : help_message })
 
