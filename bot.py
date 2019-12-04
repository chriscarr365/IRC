#!/usr/bin/python3
import socket
import string
import sys
import select
import errno
import time
from time import strftime, gmtime
import random
import datetime



client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server = input("Server IP to connect to: ") # Server
port = 6667
channel = "#test" # channel to join
uname = "ProBot" # the bot name
client_socket.connect((server, port)) # Here we connect to the server using the port 6667
client_socket.send(bytes("USER "+ uname +" "+ uname +" "+ uname + " " + uname + "\n", "UTF-8")) # user information
client_socket.send(bytes("NICK "+ uname +"\n", "UTF-8")) # assign the nick to the bot
def joinchan(chan): # join channel(s).
  client_socket.send(bytes("JOIN "+ chan +"\n", "UTF-8")) 
  ircmsg = "" #a variable to output the server's initial data spew
  while ircmsg.find("End of NAMES list") == -1: #loops until the data spew is finished
    ircmsg = client_socket.recv(1024).decode("UTF-8") #decodes and 
    ircmsg = ircmsg.strip('\n\r')                     #strips the data 
    print(ircmsg)                                     #then prints it

def ping(): # respond to server Pings.
  client_socket.send(bytes("PONG :pingis\n", "UTF-8"))
  print("replied PONG to server")

def sendMessage(msg, target=channel): # sends messages to the target.
  client_socket.send(bytes("PRIVMSG "+ target +" :"+ msg +"\n", "UTF-8"))

def main():
  joinchan(channel) #send request to join channel "#test" by default
  
  while 1:
    ircmsg = client_socket.recv(1024).decode("UTF-8") #when a message is received we store and decode it
    ircmsg = ircmsg.strip('\n\r') #strip message of end line chars
    if ("PRIVMSG" in ircmsg): #checks if the message recieved is a message that should be interpreted
      splitmsg = ircmsg.split(':') #splits message into parts that will be parsed to form a response
      message = splitmsg[2]
      if message.__contains__('!'): #checks if there is a command in a channel message
        command = message.split('!')
        command = command[1].split(' ')[0]
        print("Command word is " + command[1])
        reply(command[1]) #responds to the command if it is valid
      if (uname in splitmsg[1]): #when the bot recieves a direct message
        print("I've been messaged!")
        recipientName = str(splitmsg[1].split('!')[0])
        replyRandom(recipientName)
    else:
      if ircmsg.find("PING :") != -1: #if the message is a server ping request
        ping() #reply with pong
        
###### The functions below are for handing the !commands in channel chat ######            
def funcTime():
    output = "The time is " + strftime("%H:%M:%S", gmtime())
    print(output)
    sendMessage(output)

def funcDate():
    output = "The date is " + strftime("%d-%m-%Y", gmtime())
    print(output)
    sendMessage(output)

def funcIP():
    output = "The server IP is " + server
    print(output)
    sendMessage(output)

def funcPort():
    output = "The server port is " + str(port)
    print(output)
    sendMessage(output)

def funcDayOfWeek():
  weekDays = ("Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday")
  currentDate = datetime.datetime.today()
  currentDay = currentDate.weekday()
  output = "Today is "+weekDays[currentDay]
  print(output)
  sendMessage(output)


# ======================================================================================================

def reply(s): #replies to channel !commands by parsing the command and calling the correct
    # Print message
    print(f'Command was !{s}')
    
    # Dictionary of function names and commands used to call
    switcher = {
        'time': funcTime,
        'Time': funcTime,
        'date': funcDate,
        'Date': funcDate,
        'ip': funcIP,
        'IP': funcIP,
        'port': funcPort,
        'Port': funcPort,
        'day': funcDayOfWeek,
        'Day': funcDayOfWeek

    }

    # Get the function from switcher dictionary
    func = switcher.get(s)
    
    try:
        func()
    except Exception as e:
        print('Invalid command: {}'.format(e))
        sendMessage('Thats not a valid command')


# Add to this list of random replies
#when a user private messages the bot, picks a random reply from the list below and sends it along to the user that messaged
def replyRandom(recipient):
    reply_list = [
        'Alright there',
        'Who are you?',
        'Yo',
        'I cannot believe you just said that',
        'Did I say you could talk to me?',
        'That is enough of that',
        'oof',
        'uhh nah',
        'Hold up. Not had coffee yet and I am not ready for this'
    ]
    reply=random.choice(reply_list) #randomly selects a message from the list
    print("Sending message "+reply+" to " + recipient)
    sendMessage(reply,recipient)
main() #calls the main method
 
