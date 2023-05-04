import random
import socket
import threading
import json
import time
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import smtplib
from email.mime.text import MIMEText

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

private_key = open("private_key.txt", "r").read()
# function to Decrypt string using private key
def decrypt(encrypted_message: str, private_key: str):
    '''
    Decrypt string using private key.

    Parameters:
    encrypted_message (str): Encrypted message in hexadecimal encoded string format.

    Returns:
    str: Decrypted message in string format.
    '''

    cipher = PKCS1_OAEP.new(RSA.import_key(private_key))
    decrypted_message = cipher.decrypt(bytes.fromhex(encrypted_message))
    return decrypted_message.decode()


def send_email(email: str, subject: str, message: str):
    '''
    Send email to the specified email address.
    
    Parameters:
    email (str): Email address of the recipient.
    subject (str): Subject of the email.
    message (str): Message of the email.
    
    Returns:
    None
    '''
    smtp_server = 'smtp.gmail.com'
    port_number = 587
    sender = 'airbite368@gmail.com'
    password = 'wozholuuovycqhvp'
    recipient = email

    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient

    try:
        smtpObj = smtplib.SMTP(smtp_server, port_number)
        smtpObj.starttls()  # establish a secure connection
        smtpObj.login(sender, password)
        smtpObj.sendmail(sender, recipient, msg.as_string())
        print('Email content:', msg.as_string(), sep='\n')
        print('Email sent successfully')
    except smtplib.SMTPException as e:
        print('Failed to send email. Error message: ', e)


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
            print("Login attempt from", data.decode("utf-8").strip().split("|")
                  [1], "with password", data.decode("utf-8").strip().split("|")[2])
            # check if email exists
            if data.decode("utf-8").strip().split("|")[1] in (user["email"] for user in mainlist["users"]):
                # check if password is correct
                if data.decode("utf-8").strip().split("|")[2] == next(user["password"] for user in mainlist["users"] if user["email"] == data.decode("utf-8").strip().split("|")[1]):
                    print("Login successful for", next(user["role"] for user in mainlist["users"] if user["email"] == data.decode("utf-8").strip().split("|")[1]), "with name", next(user["name"] for user in mainlist["users"] if user["email"] == data.decode("utf-8").strip().split("|")[1]))
                    # send user name and role
                    conn.sendall(b"Login successful|" + (next(user["name"] for user in mainlist["users"] if user["email"] == data.decode("utf-8").strip().split("|")[1]) + "|" + next(user["role"] for user in mainlist["users"] if user["email"] == data.decode("utf-8").strip().split("|")[1]) + "\r\n").encode("utf-8"))
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
            # construct a string with restaurant names (user whose role is "restaurant") separated by "|"
            restaurantlist = ""
            for user in mainlist["users"]:
                if user["role"] == "restaurant":
                    restaurantlist += user["name"] + "|"
            restaurantlist = restaurantlist[:-1]
            print("Sending restaurant list to client:", restaurantlist)
            conn.sendall(json.dumps(restaurantlist).encode("utf-8") + b"\r\n")
        elif data.decode("utf-8").strip().split("|")[0] == "select":
            restaurant = data.decode("utf-8").strip().split("|")[1]
            # replace spaces with underscores
            restaurant = restaurant.replace(" ", "_")
            menu = ""
            # Get the restaurant's menu from corresponding file
            with open(restaurant + "_Menu.txt", "r") as f:
                menu = f.read()
            # print the first 100 characters of the menu
            print("Sending menu to client:", menu[:100] + "...(truncated)")
            conn.sendall(menu.encode("utf-8") + b"\r\n")
        elif data.decode("utf-8").strip().split("|")[0] == "order":
            print("Order received from client:", data.decode("utf-8").strip())
            # get the restaurant email
            restaurantemail = next(user["email"] for user in mainlist["users"] if user["name"] == data.decode("utf-8").strip().split("|")[3])
            # sleep for random time between 5 and 10 seconds
            time.sleep(random.randint(5, 10))
            # send email to passenger
            send_email(data.decode("utf-8").strip().split("|")[2], "AirBite: Your order has been received", "Dear " + data.decode("utf-8").strip().split("|")[1] + ",\n\nYour order for restaurant " + data.decode("utf-8").strip().split("|")[3] + " has been received and will be delivered to you shortly.\n\nRegards,\nAirBite")
            # # get the restaurant's socket from clients dict
            # restaurantsocket = next(value[0] for key, value in clients.items() if key == restaurantemail)
            # # send order to restaurant
            # restaurantsocket.sendall(data)
            print("Order sent to restaurant")
            
        # remove user from client dict, if first token of message is "logout"
        elif data.decode("utf-8").strip().split("|")[0] == "logout":
            # find the one with same (conn, addr) and remove from clients dict
            for key, value in clients.items():
                if value == (conn, addr):
                    del clients[key]
                    break
            print("Clients dict:", clients)
        # close connection, if first token of message is "exit"
        elif data.decode("utf-8").strip().split("|")[0] == "exit":
            print("Closing connection")
            conn.close()
            return
        elif data.decode("utf-8").strip() == "Hello Server":
            print("Sending hello to client")
            conn.sendall(b"Hello Client\r\n")

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

    # send_email("deuki1209@gmail.com", "test", "test message")

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
        exit()



