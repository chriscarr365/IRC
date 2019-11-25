import socket
import struct
import sys

message = 'Very important data'

multicast_group = ('244.3.29.71' 10000)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.settimeout(0.2)

ttl = struct.pack('b', 1)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

try:
    print ('sending "%s"' % message)
    sent = sock.sendto(message, multicast_group)

    while True:
        print('Waiting to receive...')

        try:
            data, server = sock.recvfrom(16)
        except:
            print('Timed out, no more responces')
            break
        else:
            print('Received "%s" from %s' % (data,server))

finally:
    print('Closing Socket')
    sock.close()