# Listen to TCP port 3721 and print the data received from the client

import socket

HOST = 'localhost'
PORT = 3721

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)
conn, addr = s.accept()
print('Connected by', addr)

while 1:
    data = conn.recv(1024)
    if not data: break
    # parse data as a string and print it
    print("Client request: ", data.decode("utf-8"))
    # send data back to client
    conn.sendall(data)
conn.close()

