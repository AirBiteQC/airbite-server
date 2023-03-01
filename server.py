# Listen to TCP port 3721 and print the data received from the client

import socket

# We need to make the application externally visible (accept incoming connections from outside the container)
HOST = '0.0.0.0'
PORT = 3721

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)

while 1:
    conn, addr = s.accept()
    print('Connected by', addr)

    data = conn.recv(4096)
    if not data: break
    # parse data as a string and print it
    print("Client request:", data.decode("utf-8"))
    # if the client sends HTTP request header, respond with a 200 OK
    if data.decode("utf-8").startswith("GET") or data.decode("utf-8").startswith("POST") or data.decode("utf-8").startswith("PUT") or data.decode("utf-8").startswith("DELETE") or data.decode("utf-8").startswith("HEAD") or data.decode("utf-8").startswith("OPTIONS") or data.decode("utf-8").startswith("PATCH"):
        print("Sending HTTP 200 OK")
        conn.send(b'HTTP/1.0 200 OK\r\n')
        conn.send(b"Content-Type: text/html\r\n\r\n")
        conn.send(b'<html><body><h1>AirBite Server</h1><p>Use a client to access server: https://github.com/AirBiteQC/airbite-client</p></body></html>')
        conn.close()
    else:
        # send data back to client
        print("Sending data back to client:", data.decode("utf-8"))
        conn.sendall(data)
        conn.close()
s.close()


# conn.close()

