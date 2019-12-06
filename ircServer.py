# code used from https://realpython.com/python-sockets/#multi-connection-client-and-server
#some code from https://github.com/fboender/hircd
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

sel = selectors.DefaultSelector()
IP = "10.0.42.17"
PORT = 6667
ServerName = "AfzalChrisCammy Server"

daemon_threads = True
allow_reuse_address = True
clients = {
}
channels = {}

servername = "10.0.42.17/6667"



#represents each client 
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
    #getters and setters for each client variable
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

    def setUser(self, user):
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
        response_join_channel = ':%s JOIN :%s\r\n' % (self.getIdentity(), channelname)

        for client in chnl.clients:
            client.writebuffer += response_join_channel

        nicks = [client.nickname for client in chnl.clients]
        #sends response to client when join channel is successful
        response_join_channel = ':%s 353 %s = %s :%s\r\n' % (servername, self.nickname, chnl.name, ' '.join(nicks))
        updateList = response_join_channel

        self.writebuffer += response_join_channel
        #when name list has been send
        response_join_channel = ':%s 366 %s %s: End of /NAMES list\r\n' % (servername, self.nickname, chnl.name)
        self.writebuffer += response_join_channel
        print(self.writebuffer)
        self.socket.send(self.writebuffer.encode())

        currSock = self.getSocket()

        count = 0 #iterator for sending client list to all in channel
        for target in clients[listeningSocket]:#sends list of clients to all in channel
            temp = clients[listeningSocket]  # list from key
            clientToCheck = temp[count]

            for key in clientToCheck.channels.keys():
                if key.find(channelname):
                    print("Updating Channel Clients List on all Clients")
                    clientToCheck.socket.send(updateList.encode(("utf-8")))     #only updates list for those who join channel manually, but not those who join on loadup through window

            count += 1

        self.writebuffer = ""



class channel(object): #stores channel information
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

def handling(command, arguments, key, mask): #method to handle any client messages
    currSock = key.fileobj #socket that data was recieved from
    # recieve nickname from HexChat Client and set in Client class instance in server client list
    if command.upper() == "NICK":
        print("NICKNAME COMMAND")
        count = 0
        for target in clients[listeningSocket]:
            for key, value in clients.items():
                print(key, value)   #DICTIONARY ITEMS(KEY AND ALL ITS VALUES
            temp = clients[listeningSocket] #set variable to list the key is pointing to, can then use temp to access Client Fields/methods

            temp2 = temp[count]

            if currSock == temp2.socket:        #only works for first connection
                clients[listeningSocket][count].setNickname(arguments)
                assignedNick = clients[listeningSocket][count].nickname
                break
            
            else:
                count += 1
    # recieve username from HexChat Client and set in Client class instance in server client list
    if command.upper() == "USER":
        print("USERNAME COMMAND")
        count = 0
        for target in clients[listeningSocket]:
            for key, value in clients.items():
                print(key, value)   #DICTIONARY ITEMS(KEY AND ALL ITS VALUES
            print(target)           #server socket
            print(currSock)         #client socket
            temp = clients[listeningSocket] #list from key
            print(temp)             #prints client list
            temp2 = temp[count]

            if currSock == temp2.socket:    # if found client socket in dictionary
                print("~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                clients[listeningSocket][count].setUser(arguments)
                assignedNick = clients[listeningSocket][count].nickname
                print("USERNAME ASSIGNED IS: " + clients[listeningSocket][count].user)
                numberOfClients = len(clients[listeningSocket])
                temp2.socket.send(bytes(":127.0.0.1 001 "+ assignedNick + " :Hi, welcome to IRC \n", "UTF-8")) #send info to client about the server
                temp2.socket.send(bytes(":127.0.0.1 002 "+ assignedNick + " :Your host is " +servername+", running version 4 \n", "UTF-8"))
                temp2.socket.send(bytes(":127.0.0.1 251 "+ assignedNick + " :There are "+str(numberOfClients)+ " users and 0 services on 1 server \n", "UTF-8"))
                temp2.socket.send(bytes(":127.0.0.1 422 "+ assignedNick + " :MOTD File is missing \n", "UTF-8"))
                print("~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                break
            else:
                count += 1

    # receieve JOIN command from HexChat
    if command.upper() == "JOIN": #TODO when to join a server, send client info of everyone already in that server
        if arguments.startswith("#"):
            #loop through servers clients list
            count = 0   #iterator to loop through Clients list stored in dictionary
            for target in clients[listeningSocket]:
                for key, value in clients.items():
                    temp = clients[listeningSocket]  # list from key
                    temp2 = temp[count]

                    if currSock == temp2.socket:
                        temp2.joinChannel(arguments)
                        print("JOINED SUCCESS")
                    else:
                        count += 1
        else:
            print("invalid channel format")
    if command.upper() == "MODE": #handled in join channel so this is redundant
        print("received mode but doing nothing with it")
    if command.upper() == "WHO": #handled in join channel so this is redundant
        print("received who but doing nothing with it")
    if command.upper() == "QUIT":
        print("f")
    if command.upper() == "PING": #handle ping with pong
        count = 0
        for target in clients[listeningSocket]:
            temp = clients[listeningSocket] #list from key
            temp2 = temp[count]

            if currSock == temp2.socket: 
                temp2.socket.send(bytes(":"+ servername +" PONG "+ servername + " :" +arguments+ "\n", "UTF-8"))
                break
            else:
                count += 1
    if command.upper() == "PRIVMSG": #handle private message command
        messageContent= arguments.split(":")
        senderName = "" #the sender
        count = 0
        for target in clients[listeningSocket]:
            temp = clients[listeningSocket] #list from key
            temp2 = temp[count]
            if currSock == temp2.socket:    #finding out who the sender is based on their socket
                senderName = temp2.nickname
                break
            else:
                count += 1
            
        destination = messageContent[0]
        messageText = messageContent[1]
        if destination.startswith("#"): #checks if this to be sent a channel
            #send to channel
            dataToSend = (bytes(":"+senderName+"!"+ senderName + "@"+ IP +" PRIVMSG "+ destination +":"+ messageText +"\n", "UTF-8"))
            #targetUser = destination
            count = 0
            for target in clients[listeningSocket]:
                temp = clients[listeningSocket] #list from key
                clientToCheck = temp[count]
                for key in clientToCheck.channels.keys(): #checks client channels to see if they're in the one we want
                    if key.find(destination):
                        if clientToCheck.nickname == senderName:
                            break
                        clientToCheck.socket.send(dataToSend) #client is in channel, so send message
                        break #prevents message being sent several times if client is in more than one channel
                        
                count += 1
        else:
            #send as personal message
            
            targetUser = destination
            count = 0
            for target in clients[listeningSocket]: #checks for every client if it's the one we want
                temp = clients[listeningSocket] #list from key
                socketTosend = temp[count]
                targetUser = targetUser.strip()
                if targetUser == socketTosend.nickname: #found the user we need
                    socketTosend.socket.send(bytes(":"+senderName+"!"+ senderName + "@"+ IP +" PRIVMSG "+ targetUser +" :"+ messageText +"\n", "UTF-8"))
                    break
                else:
                    count += 1
    
    else:
        print("command not captured. Command is : " + command.upper())

def parse(input): #gets the info we need from a message
    temp = input.split()
    arguments = temp[1:]
    command = temp[0]
    if (command == "PRIVMSG"): #if privmsg we need the full parameters of message content
        temp = input
        arguments = temp.split(" ", 1)#slightly different split method
        temp = arguments[1]
        arguments = temp
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
            #print(data.outb.decode("utf-8"))
            #take recieved data and isolate into command and arguments
            line=(recv_data.decode("utf-8")).split("\n") #splits input into lines
            for x in line: #for each line of input
                if x:
                    print("the line to be processed is: "+ x)
                    command, arguments = parse(x)
                #run handler on command and arguments
                    if command == "PRIVMSG":
                        handling(command, arguments, key, mask)#call handling for privmsg with full arguments
                    else:
                        handling(command, arguments[0], key, mask)#calls handling with the params from the next line
                else:
                    break

            #message = data.outb.decode("utf-8")
            #print(message)


        # if no data is received, the client has closed their socket
        else:
            # output that server is closing connection to disconnecting socket
            print("Closing connection to", data.addr)

            # unregister from sel so socket is no longer monitored by select()
            sel.unregister(sock)

            # close the socket
            sock.close()





while True:
    # block until there are sockets ready for I/O, returns list of (key, events) tuple, a tuple for each socket
    # key is a SelectorKey namedtuple that contains a file obj attribute
    # key.fileobj is the socket object, mask is an even mask of the operations which are ready
    events = sel.select(timeout=None)
    for key, mask in events:
        # if key.data is none, has to be a listening socket so accept connection and register
        if key.data is None:
            accept_wrapper(key.fileobj)

        # client socket so run services required to start handling client commands
        else:
            service_connection(key, mask)
