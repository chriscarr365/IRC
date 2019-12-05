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
clients = {
}
channels = {"#test"}

servername = "127.0.0.1/1234"

#def send_to_client(self, buffer, key):



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

    def getNickname(self):
        return self.nickname

    def setNickname(self, nickname):
        self.nickname = nickname

    def getRealname(self):
        return self.realname

    def setRealname(realname):
        self.realname = realname

    def getUser(self):
        return self.user

    def setUser(user):
        self.user = user
    
    def getSocket(self):
        return self.socket

    def getIdentity(self):
        return '%s!%s@%s' % (self.nickname, self.user, servername)

    def joinChannel(self, channelname):
        # add user to the channel(create new channel if doesnt exist)
        chnl = channels.setdefault(channelname, channel(channelname))
        chnl.clients.add(self)
        # add channel to user's channel list
        self.channels[chnl.name] = channel

        # send the topic over to HexChat
        response_join_channel = ':%s TOPIC %s :%s\r\n' % (chnl.topic_by, chnl.name, chnl.topic)
        self.writebuffer += response_join_channel

        # send the join channel message to all in channel, including self
        response_join_channel = ':%s JOIN :%s\r\n' % (self.getIdentity(), channelname)
        for client in chnl.clients:
            client.writebuffer += response_join_channel

        nicks = [client.nickname for client in chnl.clients]

        response_join_channel = ':%s 353 %s = %s :%s\r\n' % (servername, self.nickname, chnl.name, ' '.join(nicks))
        self.writebuffer += response_join_channel

        response_join_channel = ':%s 366 %s %s: End of /NAMES list\r\n' % (servername, self.nickname, chnl.name)
        self.writebuffer += response_join_channel

        self.socket.send(self.writebuffer.encode())

        #send_to_client(self.writebuffer, key=self.server.get_key())
        #stringToSend()
        #key.fileobj.send(":test!tester@127.0.0.1 JOIN #test\n".encode())
        self.socket.send(self.writebuffer)

        #self.socket.send(":self.nickname!self.user@IP JOIN #channelname".encode())

        self.writebuffer = ""



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

clients[listeningSocket] = []

def handling(command, arguments, key, mask):
    currSock = key.fileobj
    print("~~~~~~~~~~~~~~~~~~~~~~")
    print("Arguments is " + arguments)
    print("Commands is " + command)
    print("~~~~~~~~~~~~~~~~~~~~~~")

    # recieve nickname from HexChat Client and set in Client class instance in server client list
    if command.upper() == "NICK":
        print("NICKNAME COMMAND")
        count = 0
        for target in clients:
            for key, value in clients.items():
                print(key, value)   #DICTIONARY ITEMS(KEY AND ALL ITS VALUES
            print(target)           #server socket
            print(currSock)         #client socket
            temp = clients[listeningSocket] #list from key
            print(temp)             #prints client list
            temp2 = temp[count]
            print(temp2.socket)     #client socket in dictionary

            if currSock == temp2.socket:
                print("TESTER")
                clients[listeningSocket][count].setNickname(arguments)
                print("NICKNAME ASSIGNED IS: " + clients[listeningSocket][count].nickname)
                print("~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                break

    # recieve username from HexChat Client and set in Client class instance in server client list
    if command.upper() == "USER":
        print("USERNAME")
        temp = arguments.split()
        uname = temp[0]
        for client in clients:
            print(client)
            #if client.getSocket() == currSock:
                #client.setUser(uname)

    # receieve JOIN command from HexChat
    if command.upper() == "JOIN":
        # make sure channel argument starts with #
        key.fileobj.send(":test!tester@127.0.0.1 JOIN #test\n".encode())
        if arguments.startswith("#"):
            #loop through servers clients list
            for client in clients:
                #if clientslist.socket is equal to currentSocket then you have found correct Client instance for currSocket
                print(client)
                #if client.getSocket() == currSock:
                    #key.fileobj.send(":test!tester@127.0.0.1 JOIN #test\n".encode())
                    # uses correct client instance to join channel
                    #client.joinchannel(arguments)
        else:
            print("invalid channel format")
    else:
        print("random")

def parse(input):
    temp = input.split()
    arguments = temp[1:]
    command = temp[0]
    return command, arguments


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
    clients[listeningSocket].append(newclient)



# Main part of the multi-client server
# key is the namedtuple returned from select() that contains the socket object(fileobj) and data object.
# mask contains the events that are ready.
def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    #for client in clients:
        #if client.socket == sock:


    # if socket is ready for reading then this is true
    if mask & selectors.EVENT_READ:
        #since True, sock.recv() is called
        recv_data = sock.recv(1024)

        # if data is received
        if recv_data:
            # append any data that is read into recv_data to data.outb so it can be sent later
            data.outb += recv_data

            #take recieved data and isolate into command and arguments
            command, arguments = parse(recv_data.decode("utf-8"))

            #run handler on command and arguments
            handling(command, arguments[0], key, mask)

            message = data.outb.decode("utf-8")
            print(message)


        # if no data is received, the client has closed their socket
        else:
            # output that server is closing connection to disconnecting socket
            print("Closing connection to", data.addr)

            # unregister from sel so socket is no longer monitored by select()
            sel.unregister(sock)

            # close the socket
            sock.close()

    # if socket is ready for writing then this is true
    if mask & selectors.EVENT_WRITE:
        # if has received data from socket
        if data.outb:
            # send data out to clients
            print("echoing", repr(data.outb), "to", data.addr)

            # if read startswith @:
                # isolate nickname message is targetting
                # for target in clients:
                    # user = clients[target]
                    # set msgTarget to target[nickname]
                    # if isolated nickname is in MsgTarget:
                        # send message only to targettedUser

            # loop through sockets and send
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
