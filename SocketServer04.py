import socket
import select
import threading

HEADER_LENGTH = 10

IP = "127.0.0.1"
PORT = 1234

# Create a socket
# socket.AF_INET - address family, IPv4, some otehr possible are AF_INET6, AF_BLUETOOTH, AF_UNIX
# socket.SOCK_STREAM - TCP, conection-based, socket.SOCK_DGRAM - UDP, connectionless, datagrams, socket.SOCK_RAW - raw IP packets
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# SO_ - socket option
# SOL_ - socket option level
# Sets REUSEADDR (as a socket option) to 1 on socket
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind, so server informs operating system that it's going to use given IP and port
# For a server using 0.0.0.0 means to listen on all available interfaces, useful to connect locally to 127.0.0.1 and remotely to LAN interface IP
server_socket.bind((IP, PORT))

# This makes server listen to new connections
server_socket.listen()

# List of sockets for select.select()
sockets_list = [server_socket]

# List of connected clients - socket as a key, user header and name as data
clients = {}

# dictionary for channels
channels = {
    "#General": [clients],
    "#Memes": [clients],
    "#Sports": [clients]
}

print(f'Listening for connections on {IP}:{PORT}...')


# Handles message receiving
def receive_message(client_socket):
    try:

        # Receive our "header" containing message length, it's size is defined and constant
        message_header = client_socket.recv(HEADER_LENGTH)

        # If we received no data, client gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
        if not len(message_header):
            return False

        # Convert header to int value
        message_length = int(message_header.decode('utf-8').strip())

        # Return an object of message header and message data
        return {'header': message_header, 'data': client_socket.recv(message_length)}

    except:

        # If we are here, client closed connection violently, for example by pressing ctrl+c on his script
        # or just lost his connection
        # socket.close() also invokes socket.shutdown(socket.SHUT_RDWR) what sends information about closing the socket (shutdown read/write)
        # and that's also a cause when we receive an empty message
        return False


while True:

    # Calls Unix select() system call or Windows select() WinSock call with three parameters:
    #   - rlist - sockets to be monitored for incoming data
    #   - wlist - sockets for data to be send to (checks if for example buffers are not full and socket is ready to send some data)
    #   - xlist - sockets to be monitored for exceptions (we want to monitor all sockets for errors, so we can use rlist)
    # Returns lists:
    #   - reading - sockets we received some data on (that way we don't have to check sockets manually)
    #   - writing - sockets ready for data to be send thru them
    #   - errors  - sockets with some exceptions
    # This is a blocking call, code execution will "wait" here and "get" notified in case any action should be taken
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

    # Iterate over notified sockets
    for notified_socket in read_sockets:

        # If notified socket is a server socket - new connection, accept it
        if notified_socket == server_socket:

            # Accept new connection
            # That gives us new socket - client socket, connected to this given client only, it's unique for that client
            # The other returned object is ip/port set
            client_socket, client_address = server_socket.accept()

            # Client should send his name right away, receive it
            user = receive_message(client_socket)

            # If False - client disconnected before he sent his name
            if user is False:
                continue

            # Add accepted socket to select.select() list
            sockets_list.append(client_socket)

            # Also save username and username header
            clients[client_socket] = user

            print('Accepted new connection from {}:{}, username: {}'.format(*client_address,
                                                                            user['data'].decode('utf-8')))

        # Else existing socket is sending a message
        else:

            # Receive message
            message = receive_message(notified_socket)

            # If False, client disconnected, cleanup
            if message is False:
                print('Closed connection from: {}'.format(clients[notified_socket]['data'].decode('utf-8')))

                # Remove from list for socket.socket()
                sockets_list.remove(notified_socket)

                # Remove from our list of users
                del clients[notified_socket]

                continue

            # Get user by notified socket, so we will know who sent the message
            user = clients[notified_socket]

            print(f'Received message from {user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')

            # initialise and setup direct messaging assigning variable to only the message data of message
            directmessage = ""
            directmessage = message["data"].decode("utf-8")


            ##################################################################DIRECT MESSAGE###################################################################
            if directmessage.startswith("@"):
                msgTarget = ""
                msgData = ""

                # get target and msgdata
                msgTarget, msgData = directmessage.split(' ', 1)

                # remove @ from message target username
                msgTarget = msgTarget.strip('@')

                # clients["data"[1:"data".index(':')].lower()].send("data"["data".index(':') + 1:])
                print(f'recieved direct message[' + "'" + msgData + "'" + '] to user: ' + msgTarget)  # PRINT
                for target_socket in clients:
                    user = clients[target_socket]
                    sockUname = {user["data"].decode("utf-8")}

                    msgDataBytes = str.encode(msgData)

                    if msgTarget in sockUname:
                        # send to target
                        target_socket.send(user['header'] + user['data'] + message['header'] + msgDataBytes)
                        break
            ##################################################################DIRECT MESSAGE####################################################################

            # Iterate over connected clients and broadcast message
            for client_socket in clients:
##################################################################DIRECT MESSAGE###################################################################
                if directmessage.startswith("@"):
                    break
##################################################################DIRECT MESSAGE####################################################################
                # But don't sent it to sender
                if client_socket != notified_socket:
                    # Send user and message (both with their headers)
                    # We are reusing here message header sent by sender, and saved username header send by user when he connected
                    client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

    # It's not really necessary to have this, but will handle some socket exceptions just in case
    for notified_socket in exception_sockets:
        # Remove from list for socket.socket()
        sockets_list.remove(notified_socket)

        # Remove from our list of users
        del clients[notified_socket]


# Class for Channel Thread, connect to channel and interact with channel
class ChannelThread(threading.Thread):
    # Initialise fields
    def __init__(self):
        threading.Thread.__init__(self)
        self.clients = []  # clients connected to Channel
        # Create a socket

        # socket.AF_INET - address family, IPv4, some otehr possible are AF_INET6, AF_BLUETOOTH, AF_UNIX
        # socket.SOCK_STREAM - TCP, conection-based, socket.SOCK_DGRAM - UDP, connectionless, datagrams, socket.SOCK_RAW - raw IP packets
        self.channel_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind, so server informs operating system that it's going to use given IP and port
        # For a server using 0.0.0.0 means to listen on all available interfaces, useful to connect locally to 127.0.0.1 and remotely to LAN interface IP
        self.channel_socket.bind(('127.0.0.1', 1234))

        _, self.port = 1234

        # This makes server listen to new connections
        self.channel_socket.listen()  # for normal channels unlimited number of connections

        self.daemon = True
        self.start()

    # connect new client to channel
    def run(self):
        while True:
            client = self.channel_socket.accept()
            if not client:
                break
            # add client to list of clients who can use channel
            self.clients.append(client)

    def sendall(selfself, msg):
        for client in self.clients:
            client.send(user['header'] + user['data'] + message['header'] + message['data'])

    # def sendMsg(self):
    # for all clients in  the network, output message
    # Maybe use Recieve message from above as static and change socket details to channel sockets.


# Class for Channel, create channel and set up connection
class Channel(threading.Thread):
    # initialise fields
    def __init__(self):
        threading.Thread.__init__(self)

        self.daemon = True
        self.channel_thread = ChannelThread()

    # register and connect to channel socket
    # update_callback
    # return "tcp://%s:%d" % (socket.gethostname(), self.channel_thread.port)
    def getAddress(self):
        host = socket.gethostname()
        port = self.channel_thread.port
        return host, port

    def register(self, host, port):
        self.peer_chan_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.peer_chan_sock.connect((host, port))
        self.peer_chan_sock.setblocking(False)
        # self._callback = update_callback
        self.start()

    # def deal_with_message(self, msg):
    # self._callback(msg)

    def run(self):
        data = ""
        while True:
            new_data = self.peer_chan_sock.recv(1024)
            if not new_data:
                # connection reset by peer
                break
            data += new_data
            msgs = data.split("\n\n")
            if msgs[-1]:
                data = msgs.pop()
            for msg in msgs:
                self.deal_with_message(msg)

    def send_value(self, channel_value):
        self.channel_thread.sendall("%s\n\n" % channel_value)

#to run channel example code
#process A : Client A
#c = Channel()

#process B : Client B
#c = Channel()
#c.register(host, port)

#process A : CLient A
#c.send("whatever")

#process B : Client B(anyone on channel)
#recieves "whatever"

# IP "127.0.0.1"
# Port 1234

# todolist
# def connectChannel():
# def createChannel():
# def getChannel():
