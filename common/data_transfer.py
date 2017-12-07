
import socket
 
def send_data(data, recv_ip='127.0.0.1', port=55000):
    sock = socket.socket()

    while True:
        try:
            sock.connect((recv_ip, port))
            break
        except:
            pass;

    idx1 = 0
    idx2 = 65536
    while True:      
        data_chunk = data[idx1:idx2];
        if not data_chunk:
            break;
        sock.sendall(data_chunk);
        idx1 = idx2 
        idx2 = idx2 + 65536

    sock.close()

sock = 0

def init_server(port='55000'):
    global sock
    sock = socket.socket()
    sock.bind(('0.0.0.0', port))
    sock.listen(5)

# Recieves data from any incoming connection on specified port 
def recv_data(port='55000'):
    global sock

    conn, addr = sock.accept()

    data_chunks = []
    while True:
        chunk = conn.recv(65536) 
        if not chunk:
            break                
        data_chunks.append(chunk);
      
    conn.close()
    return b''.join(data_chunks)
