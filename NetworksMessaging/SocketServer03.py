import socket
import struct
import sys

multicast_group = '244.3.29.71'
server_address = ('', 10000)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.bind(server_address)

group = socket.inet_aton(multicast_group)
mreg = struct.pack('4sL', group, socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreg)

while True:
    print('\nWaiting to receive message')
    data, address = sock.recvfrom(1024)

    print('Received %s bytes from %s' % (len(data), address))
    print(data)

    print('Sending ack to', address)
    sock.sendto('ack', address)