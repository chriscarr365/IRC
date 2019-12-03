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
server = "127.0.0.1" # Server
port = 6667
channel = "#test" # channel to join
uname = "ProBot" # the bot name
adminname = "chris" #Your IRC nickname. 
exitcode = "bye " + uname #exit code for admins to close the bot remotely
client_socket.connect((server, port)) # Here we connect to the server using the port 6667
client_socket.send(bytes("USER "+ uname +" "+ uname +" "+ uname + " " + uname + "\n", "UTF-8")) # user information
client_socket.send(bytes("NICK "+ uname +"\n", "UTF-8")) # assign the nick to the bot
def joinchan(chan): # join channel(s).
  client_socket.send(bytes("JOIN "+ chan +"\n", "UTF-8")) 
  ircmsg = ""
  while ircmsg.find("End of NAMES list") == -1: 
    ircmsg = client_socket.recv(1024).decode("UTF-8")
    ircmsg = ircmsg.strip('\n\r')
    print(ircmsg)

def ping(): # respond to server Pings.
  client_socket.send(bytes("PONG :pingis\n", "UTF-8"))
  print("replied PONG to server")

def sendMessage(msg, target=channel): # sends messages to the target.
  client_socket.send(bytes("PRIVMSG "+ target +" :"+ msg +"\n", "UTF-8"))

def main():
  joinchan(channel)
  
  while 1:
    ircmsg = client_socket.recv(1024).decode("UTF-8")
    ircmsg = ircmsg.strip('\n\r')
    print(ircmsg)
    if ("PRIVMSG" in ircmsg): 
      splitmsg = ircmsg.split(':')
      print("message split 1: "+splitmsg[1])
      print("message split 2: "+splitmsg[2])
      message = splitmsg[2]
      if message.__contains__('!'):
        command = message.split('!')
        print("Command word is " + command[1])
        reply(command[1])
      if (uname in splitmsg[]):
        if (uname in message):
          print("I heard my name")
          replyRandom()
    else:
      if ircmsg.find("PING :") != -1:
        ping()
        
            
def funcTime():
    output = "The time is... " + strftime("%H:%M:%S", gmtime())
    print(output)
    sendMessage(output)

def funcDate():
    output = "The date is... " + strftime("%d-%m-%Y", gmtime())
    print(output)
    sendMessage(output)

def funcIP():
    output = "The IP is... " + server
    print(output)
    sendMessage(output)

def funcPort():
    output = "The date is... " + str(port)
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

def reply(s):
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


# Add to this list of random replys
def replyRandom():
    reply_list = [
        'Whats up',
        'Who are you?',
        'Yo'
    ]
    sendMessage(random.choice(reply_list))
main()
 
