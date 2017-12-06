import socket
 
HOST = '0.0.0.0'
PORT = 42050


s = socket.socket()
s.bind((HOST, PORT))

print "Server running", HOST, PORT
s.listen(5)
conn, addr = s.accept()
print'Connected by', addr

chunks = []
while True:
    chunk = conn.recv(65536) 
    if not chunk:
        break                
    chunks.append(chunk);
      
print "Done Receiving"
conn.close()

data = b''.join(chunks)

output_file = open('network.jpg', 'wb')
output_file.write(data);
output_file.close();
