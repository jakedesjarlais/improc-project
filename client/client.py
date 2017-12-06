
import socket
#import huffcode
 
SERVER_IP = '127.0.0.1'
PORT = 42050


s = socket.socket()
s.connect((SERVER_IP, PORT))

f = open('input.jpg', 'rb')

print "Sending Data ...."  
while True:      
    data_chunk = f.read(65536);
    if not data_chunk:
        break;
    s.sendall(data_chunk);

f.close()
print "Sending Complete"

s.close()
