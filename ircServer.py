# code used from https://realpython.com/python-sockets/#multi-connection-client-and-server
import select
import socket
import sys
import time
from datetime import datetime
import os
import re
import selectors
import types

sel = selectors.DefaultSelector()
IP = "127.0.0.1"
PORT = 1234

# Create a socket
# socket.AF_INET - address family, IPv4, some otehr possible are AF_INET6, AF_BLUETOOTH, AF_UNIX
# socket.SOCK_STREAM - TCP, conection-based, socket.SOCK_DGRAM - UDP, connectionless, datagrams, socket.SOCK_RAW - raw IP packets
listeningSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind, so server informs operating system that it's going to use given IP and port
# For a server using 0.0.0.0 means to listen on all available interfaces, useful to connect locally to 127.0.0.1 and remotely to LAN interface IP
listeningSocket.bind((IP, PORT))

# This makes server listen to new connections
listeningSocket.listen()
print("listening on", (IP, PORT))

# Ensure connection is non-blocking
listeningSocket.setblocking(False)

# Listening Socket so we want to read
sel.register(listeningSocket, selectors.EVENT_READ, data=None)


# Accepting Connection from Client
def accept_wrapper(sock):  # Should be ready to read since listeningsocket was registered for the Read Event
    conn, addr = sock.accept()
    print("Accepted Connection from", addr)  # Server shows connected client
    conn.setblocking(False)  # Ensure connection is in non-blocking mode

    # create object to hold data wanted to be included alongside the socket
    data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')

    # Want to check when Client is ready for Both Read and Write so set the events
    events = selectors.EVENT_READ | selectors.EVENT_WRITE

    # Pass events mask, socket and data objects to the selector for register
    sel.register(conn, events, data=data)

# Main part of the multi-client server
# key od the namedtuple returned from select() that contains the socket object(fileobj) and data object.
# mask contains the events that are ready.
def service_connection(key, mask):
    sock = key.fileobj
    data = key.data

    # if socket is ready for reading then this is true
    if mask & selectors.EVENT_READ:
        #since True, sock.recv() is called
        recv_data = sock.recv(1024)

        # if data is received
        if recv_data:
            # append any data that is read into recv_data to data.outb so it can be sent later
            data.outb += recv_data

        # if no data is received, the client has closed their socket
        else:
            # output that server is closing connection to disconnecting socket
            print("Closing connection to", data.addr)

            # unregister from sel so socket is no longer monitored by select()
            sel.unregister(sock)

            # close the socket
            sock.close()

    # if socket is ready for reading then this is true
    if mask & selectors.EVENT_WRITE:
        # if has received data from socket
        if data.outb:
            # send data out to clients
            print("echoing", repr(data.outb), "to", data.addr)
            sent = sock.send(data.outb)     # should be ready to write
            data.outb = data.outb[sent:]


while True:
    # block until there are sockets ready for I/O, returns list of (key, events) tuple, a tuple for each socket
    # key is a SelectorKey namedtuple that contains a file obj attribute
    # key.fileobj is the socket object, mask is an even mask of the operations which are ready
    events = sel.select(timeout=None)
    for key, mask in events:
        # if key.data is none, has to be a listening socket so accept connection and register
        if key.data is None:
            accept_wrapper(key.fileobj)

        # client socket so run services required
        else:
            service_connection(key, mask)