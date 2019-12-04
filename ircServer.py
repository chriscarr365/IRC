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
import traceback
#import libserver

sel = selectors.DefaultSelector()
IP = "127.0.0.1"
PORT = 1234

daemon_threads = True
allow_reuse_address = True
clients = {}
channels = {}

servername = "127.0.0.1/1234"

#nickname,name,socket
class client(object):
    def __init__(self, socket): #client_address
        self.user = None
        #self.host = client_address
        #self.server = server
        self.nickname = None
        self.realname = None
        self.socket = socket
        self.channels = {}
        self.writebuffer = ""
        self.readbuffer = ""
        self.sent_ping = False

    def getIdentity(self):
        return '%s!%s@%s' % (self.nickname, self.user, servername)

    def joinChannel(self, channelname):
        # add user to the channel(create new channel if doesnt exist)
        chnl = channels.setdefault(channelname, channel(channelname))
        chnl.clients.add(self)
        # add channel to user's channel list
        self.channels[chnl.name] = channel

        # send the topic over to HexChat
        response_join_channel = ':%s TOPIC %s :%s\r\n' % (channel.topic_by, channel.name, channel.topic)
        self.writebuffer += response_join_channel

        # send the join channel message to all in channel, including self
        #response_join_channel = ':%s JOIN :%s\r\n' % (self.server.get_prefix() % (self.nickname, self.username, self.server.HOST), channelname)
        response_format = ':%s JOIN :%s\r\n' % (self.getIdentity(), channelname)
        for client in chnl.clients:
            client.writebuffer += response_join_channel

        nicks = [client.nickname for client in channel.clients]

        response_join_channel = ':%s 353 %s = %s :%s\r\n' % (servername, self.nickname, chnl.name, ' '.join(nicks))
        self.writebuffer += response_join_channel

        response_join_channel = ':%s 366 %s %s: End of /NAMES list\r\n' % (servername, self.nickname, chnl.name)
        self.writebuffer += response_join_channel

class channel(object):
    def __init__(self, name, topic="No topic"):
        self.name = name
        self.topic_by = "Unknown"
        self.topic = topic
        self.clients = set()
        


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

    newclient = client(conn)
    clients[conn] = newclient


# Main part of the multi-client server
# key is the namedtuple returned from select() that contains the socket object(fileobj) and data object.
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
            message = data.outb.decode("utf-8")

            #isolate #channelname from message
            channelname = message.split(" ")[1]


            #tester prints
            print(channelname)
            print(message.strip("\r"))

            #makesure only works with #<channel>
            #if channelname.startswith("#"):
                #currClient.joinChannel(channelname)


            # if read startswith @:
                # isolate nickname message is targetting
                # for target in clients:
                    # user = clients[target]
                    # set msgTarget to target[nickname]
                    # if isolated nickname is in MsgTarget:
                        # send message only to targettedUser

            #loop through sockets and send
            #sent = sock.send(data.outb)     # should be ready to write
            #data.outb = data.outb[sent:]


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
