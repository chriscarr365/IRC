import socket
import select
import errno

HEADER_LEN = 10

IP = "127.0.0.1"
PORT = 1234
uname = "ChatBot"

# Create socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to socket ip and port
client_socket.connect((IP, PORT))

# Ensure connection is non-blocking
client_socket.setblocking(False)

# Prepare username and header
username = uname.encode('utf-8')
username_header = f"{len(username):<{HEADER_LEN}}".encode('utf-8')
client_socket.send(username_header + username)

def main():
    while True:

        try:
            # Now we want to loop over received messages (there might be more than one) and print them
            while True:

                # Receive our "header" containing username length, it's size is defined and constant
                username_header = client_socket.recv(HEADER_LEN)

                # If we received no data, server gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
                if not len(username_header):
                    print('Connection closed by the server')
                    sys.exit()

                # Convert header to int value
                username_length = int(username_header.decode('utf-8').strip())

                # Receive and decode username
                username = client_socket.recv(username_length).decode('utf-8')

                # Now do the same for message (as we received username, we received whole message, there's no need to check if it has any length)
                message_header = client_socket.recv(HEADER_LEN)
                message_length = int(message_header.decode('utf-8').strip())
                message = client_socket.recv(message_length).decode('utf-8')

                if message.__contains__('!'):
                    reply(message[1:])


        except IOError as e:
            # This is normal on non blocking connections - when there are no incoming data error is going to be raised
            # Some operating systems will indicate that using AGAIN, and some using WOULDBLOCK error code
            # We are going to check for both - if one of them - that's expected, means no incoming data, continue as normal
            # If we got different error code - something happened
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print('Reading error: {}'.format(str(e)))
                sys.exit()

            # We just did not receive anything
            continue

        except Exception as e:
            # Any other exception - something happened, exit
            print('Reading error: '.format(str(e)))
            sys.exit()  

def one():
    print ('this is function 1')

def two():
    print ('this is function 2')

def reply(s):
    # Print message
    print(f'{s}')

    switcher = {
        '1': one,
        '2': two
    }

    # Get the function from switcher dictionary
    func = switcher.get(s)
    func()

main()