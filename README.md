# AirBite Server

AirBite is a socket programming application written in Python, designed to facilitate food ordering in an airport scenario. This server application allows restaurants in the airport to accept food orders from passengers, make the food, and deliver it to the gate or allow the passenger to pick it up. 

This repository contains the server-side implementation of AirBite, which communicates with clients over TCP port 3721. The server is responsible for handling incoming requests from clients, processing those requests, and coordinating with the restaurants to fulfill the orders.

## Dependencies

This server application has been developed and tested on Python 3. It uses the following libraries:

- `socket`: for creating and managing sockets for network communication
- `pickle`: for serializing and deserializing Python objects

These libraries are included in the Python standard library and should not require any additional installation.

## Usage

To run the server, simply execute the `server.py` file:
```bash
python server.py
```

By default, the server will listen for incoming connections on port 3721. Once a client connects to the server, the server will begin processing requests and communicating with the appropriate restaurants to fulfill orders.

To expose port from NAT and Firewalls, use port forwarding tools such as [ngrok](https://ngrok.com/docs/getting-started):
```bash
ngrok tcp 3721
```

## Commands

Currently supported commands:
```
register username password
login username password
list restaurant
exit
```

## Contributing

Contributions to AirBite are welcome! If you find a bug or have a feature request, please open an issue in the issue tracker. If you'd like to contribute code, please fork the repository and submit a pull request.

## License

This software is released under the MIT License. See the `LICENSE` file for more information.