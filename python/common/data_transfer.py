
import socket, time


# Time out time in seconds
TIMEOUT = 10



def send_data(data, recv_ip='127.0.0.1', port=55000):
    sock = socket.socket()

    timeout_start = time.time();
    time_waiting = 0;
    while time_waiting < TIMEOUT:
        try:
            sock.connect((recv_ip, port));
            break;
        except:
            time_waiting = time.time() - timeout_start;
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
    start_time = time.time()
    transfer_time = 0
    while transfer_time < TIMEOUT:
        chunk = conn.recv(65536) 
        if not chunk:
            break                
        data_chunks.append(chunk);
        transfer_time = time.time() - start_time

    if (transfer_time >= TIMEOUT):
        return 0

      
    conn.close()
    return b''.join(data_chunks)
