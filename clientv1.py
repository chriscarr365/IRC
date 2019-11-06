import socket

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = ('localhost', 10000)
print('connecting to {} port {}'.format(*server_address))
print('Type exit at any point ')
sock.connect(server_address)
message = ""
messagetooutput = ""
active = True

while active:
    try:
        # Send data
        message = input("Type Message... ")
        if message == 'exit':
            active = False
            break
        message = bytes(message, 'utf-8')
        print('sending {!r}'.format(message))
        sock.sendall(message)

        # Look for the response
        amount_received = 0
        amount_expected = len(message)

        while amount_received < amount_expected:
            data = sock.recv(16)
            amount_received += len(data)
            #format data 
            data = format(data).split("b'")
            data = data[1]
            data = data.replace("'", "")
            #print (data)
            messagetooutput += format(data)
        print (messagetooutput)

    finally:
        print ("done")
        
print('closing socket')
sock.close()