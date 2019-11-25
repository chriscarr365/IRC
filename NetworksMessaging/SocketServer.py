import socket
import struct
import sys

multicast_group = '244.10.10.10'
server_address = ('', 10000)


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


print('Starting up {} port {}'.format(*server_address))
sock.bind(server_address)


group = socket.inet_aton(multicast_group)
mreg = struct.pack('4sL', group, socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP,
                socket.IP_ADD_MEMBERSHIP,
                mreg)

while True:
    print('\nWaiting to receive message')
    data, address = sock.recvfrom(1024)

    print('Received {} bytes from {}'.format(len(data), address))
    print(data)

    print('Sending acknowledgement to', address)
    sock.sendto(b'ack', address)
