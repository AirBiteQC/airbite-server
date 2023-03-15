import socket
import threading

# Listen to TCP port 3721 and print the data received from the client
# We need to make the application externally visible (accept incoming connections from outside the container)
HOST = '0.0.0.0'
PORT = 3721

def handle_client(conn, addr):
    # keep listening to incoming data from the client
    while 1:
        data = conn.recv(4096)
        if not data:
            break
        # parse data as a string and print it with client address and port
        print("[client", addr, ":", data.decode("utf-8"))

        # if the client sends HTTP request header, respond with a 200 OK
        if data.decode("utf-8").startswith("GET") or data.decode("utf-8").startswith("POST") or data.decode("utf-8").startswith("PUT") or data.decode("utf-8").startswith("DELETE") or data.decode("utf-8").startswith("HEAD") or data.decode("utf-8").startswith("OPTIONS") or data.decode("utf-8").startswith("PATCH"):
            print("Sending HTTP 200 OK")
            conn.send(b'HTTP/1.0 200 OK\r\n')
            conn.send(b"Content-Type: text/html\r\n\r\n")
            conn.send(b'<html><body><h1>AirBite Server</h1><p>Use a client to access server: https://github.com/AirBiteQC/airbite-client</p></body></html>')
            return
        # display second and third tokens, if first token of message is "register"
        elif data.decode("utf-8").strip().split()[0] == "register":
            print("Registration attempt from", data.decode("utf-8").strip().split()
                  [1], "with password", data.decode("utf-8").strip().split()[2])
        # display second and third tokens, if first token of message is "login"
        elif data.decode("utf-8").strip().split()[0] == "login":
            print("Login attempt from", data.decode("utf-8").strip().split()[1], "with password", data.decode("utf-8").strip().split()[2])
        elif data.decode("utf-8").strip().split()[0] == "list" and data.decode("utf-8").strip().split()[1] == "restaurant":
            print("List restaurant placeholder here")
        # close connection, if first token of message is "exit"
        elif data.decode("utf-8").strip().split()[0] == "exit":
            print("Closing connection")
            conn.close()
            return
        else:
            # send data back to client
            print("Sending data back to client:", data.decode("utf-8"))
            conn.sendall(data)
    conn.close()


if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(1)

    while 1:
        # keep listening to incoming connections and create a new thread for each connection
        conn, addr = s.accept()
        print('Connected by', addr)
        # create a new thread for each connection
        t = threading.Thread(target=handle_client, args=(conn, addr))
        t.start()

    s.close()


