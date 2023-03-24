import socket
import threading
import json

# Listen to TCP port 3721 and print the data received from the client
# We need to make the application externally visible (accept incoming connections from outside the container)
HOST = '0.0.0.0'
PORT = 3721

# dict to store the active clients: username to corresponding (conn, addr) pair
clients = {}
# read json file
with open('mainlist.json') as f:
    mainlist = json.load(f)
filechanged = False

def handle_client(conn, addr):
    # keep listening to incoming data from the client
    while 1:
        data = conn.recv(4096)
        if not data:
            break
        # parse data as a string and print it with client address and port
        print("[ client", addr, "]:", data.decode("utf-8"))

        # if the client sends HTTP request header, respond with a 200 OK
        if data.decode("utf-8").startswith("GET") or data.decode("utf-8").startswith("POST") or data.decode("utf-8").startswith("PUT") or data.decode("utf-8").startswith("DELETE") or data.decode("utf-8").startswith("HEAD") or data.decode("utf-8").startswith("OPTIONS") or data.decode("utf-8").startswith("PATCH"):
            print("Sending HTTP 200 OK")
            conn.send(b'HTTP/1.0 200 OK\r\n')
            conn.send(b"Content-Type: text/html\r\n\r\n")
            conn.send(b'<html><body><h1>AirBite Server</h1><p>Use a client to access server: https://github.com/AirBiteQC/airbite-client</p></body></html>')
            return
        # display second and third tokens, if first token of message is "register"
        elif data.decode("utf-8").strip().split("|")[0] == "register":
            print("Registration attempt from", data.decode("utf-8").strip().split("|")
                  [1], "and email", data.decode("utf-8").strip().split("|")[2], "with password", data.decode("utf-8").strip().split("|")[3])
            # check if email exists
            if data.decode("utf-8").strip().split("|")[2] in (user["email"] for user in mainlist["users"]):
                print("Registration failed (email already exists)")
                conn.sendall(b"Registration failed (email already exists)\r\n")
            else:
                print("Registration successful")
                conn.sendall(b"Registration successful\r\n")
                # add to users list
                mainlist["users"].append(
                    {"name": data.decode("utf-8").strip().split("|")[1], "email": data.decode("utf-8").strip().split("|")[2], "password": data.decode("utf-8").strip().split("|")[3], "role": "passenger"})
                print("Users list:", mainlist["users"])
                global filechanged # https://stackoverflow.com/questions/423379/using-global-variables-in-a-function-other-than-the-one-that-created-them
                filechanged = True
        # display second and third tokens, if first token of message is "login"
        elif data.decode("utf-8").strip().split("|")[0] == "login":
            print("Login attempt from", data.decode("utf-8").strip().split("|")[1], "with password", data.decode("utf-8").strip().split("|")[2])
            # check if email exists
            if data.decode("utf-8").strip().split("|")[1] in (user["email"] for user in mainlist["users"]):
                # check if password is correct
                if data.decode("utf-8").strip().split("|")[2] == next(user["password"] for user in mainlist["users"] if user["email"] == data.decode("utf-8").strip().split("|")[1]):
                    print("Login successful")
                    conn.sendall(b"Login successful\r\n")
                    # send user name and role
                    conn.sendall((next(user["name"] for user in mainlist["users"] if user["email"] == data.decode("utf-8").strip().split("|")[1]) + "|" + next(user["role"] for user in mainlist["users"] if user["email"] == data.decode("utf-8").strip().split("|")[1]) + "\r\n").encode("utf-8"))
                    # add to clients dict
                    clients[data.decode("utf-8").strip().split("|")[1]] = (conn, addr)
                    print("Clients dict:", clients)
                else:
                    print("Login failed")
                    conn.sendall(b"Login failed\r\n")
            else:
                print("Login failed")
                conn.sendall(b"Login failed\r\n")
        elif data.decode("utf-8").strip().split("|")[0] == "list" and data.decode("utf-8").strip().split("|")[1] == "restaurant":
            print("List restaurant placeholder here")
            conn.sendall(b"List restaurant placeholder here\r\n")
        # close connection, if first token of message is "logout"
        elif data.decode("utf-8").strip().split("|")[0] == "logout":
            # find the one with same (conn, addr) and remove from clients dict
            for key, value in clients.items():
                if value == (conn, addr):
                    del clients[key]
                    break
            print("Clients dict:", clients)
            print("Closing connection")
            conn.close()
            return
        else:
            # send data back to client
            print("Sending data back to client:", data.decode("utf-8"))
            conn.sendall(data)
    conn.close()

# https://stackoverflow.com/questions/60656088/how-to-get-wireless-lan-adapter-wi-fi-ip-address-in-python
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(1)

    print("Server on", get_ip(),
          "started, listening on port", PORT, "...")
    print("Press Ctrl+C to close socket.")

    try:
        while 1:
            # keep listening to incoming connections and create a new thread for each connection
            conn, addr = s.accept()
            print('Connected by', addr)
            # create a new thread for each connection
            t = threading.Thread(target=handle_client, args=(conn, addr))
            t.start()
    # close socket when interrupted by Ctrl+C
    except KeyboardInterrupt:
        print("\r\nCtrl+C pressed; Closing socket")
        s.close()
        if filechanged:
            print("New registration occurred; Saving changes to mainlist.json")
            with open('mainlist.json', 'w') as f:
                json.dump(mainlist, f, indent=4)

    s.close()


