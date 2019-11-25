import socket
import time

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = ('localhost', 10000)
print('Connecting to {} port {}'.format(*server_address))
sock.connect(server_address)

try:
    message  = b'This is our message. It is very long but will only be transmitted in chunks of 16 at a time'
    print('Sending {!r}'.format(message))
    sock.sendall(message)

    amount_received = 0;
    amount_expected = len(message)

    while amount_received < amount_expected:
        data = sock.recv(16)
        amount_received += len(data)
        print('Received {!r}'.format(data))

finally:
    print('Closing socket')
    sock.close()

