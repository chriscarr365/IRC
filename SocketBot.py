import socket
import select
import errno
import time

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
                elif message.__contains__('ChatBot'):
                    sendMessage("Yo")


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

def sendTime():
    output = "The time is..."
    print(output)
    sendMessage(output)

def sendDate():
    output = "The date is..."
    print(output)
    sendMessage(output)

def reply(s):
    # Print message
    print(f'Command was !{s}')

    switcher = {
        'time': sendTime,
        'date': sendDate
    }

    # Get the function from switcher dictionary
    func = switcher.get(s)
    try:
        func()
    except Exception as e:
        sendMessage('Thats not a valid command')

def sendMessage(message):
    # Send message if not empty
    if message:
        time.sleep(.5)
        # Encode message to bytes, prepare header and convert to bytes, like for username above, then send
        message = message.encode('utf-8')
        message_header = f"{len(message):<{HEADER_LEN}}".encode('utf-8')
        client_socket.send(message_header + message)

main()
















