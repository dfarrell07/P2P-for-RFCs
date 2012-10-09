#!/usr/bin/env python

import socket
import random
import sys
import time
from multiprocessing import Process, Value
import datetime

VERSION = "P2P-CI/1.0"
sport = 7734#Server's well-known port
OS = sys.platform

#Spawn upload server process
uport = random.randint(45000, 60000)#Upload port

def ul_server(uport):
    """TODO"""
    #Listen on uport
    s = socket.socket()
    host = socket.gethostname()
    s.bind((host, uport))
    s.listen(1)#not sure if this param is right
    print "PEER: Upload server started, listening on port " + str(uport)
    while True:
        #Get message
        con, addr = s.accept()
        message = con.recv()
        marray = message.split()

        #Validate message
        if marray[0] != 'GET' or marray[4] != 'Host:' or marray[6] != 'OS:':
            con.send(VERSION + "400 Bad Request\r\nDate: " 
            + str(datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT"))
            + "\r\nOS: " + OS)
            continue
        if marray[3] != VERSION:
            con.send(VERSION + "505 P2P-CI Version Not Supported\r\nDate: " 
            + str(datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")) 
            + "\r\nOS: " + OS)
            continue


        #Lookup RFC TODO - how we we get the RFCs?

        
        if True: #TODO If RFC found
            con.send(VERSION + "200 OK \r\nDate: " 
                + str(datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")) 
                + "\r\nOS: " + OS + "\r\nLast-Modified: " 
                + TODO_lm + "\r\nContent-Length: " 
                + TODO_cl + "\r\nContent-Type: " + TODO_ct + "\r\n" + TODO_data)
            continue
        else: #TODO If RFC not found
            con.send(VERSION + "404 Not Found\r\nDate: " 
                + str(datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT"))
                + "\r\nOS: " + OS)
            continue
        print "PEER: Upload server on port " + uport + " is closing"
        con.close()
        print "PEER: Upload server on port " + uport + " is closed"

p = Process(target=ul_server, args=(uport,))
p.daemon = True
p.start()

#Open server connection
s = socket.socket()
me = socket.gethostname()
server = me #Assuming client and server are on the same machine
s.connect((server, sport))

#Define messages to server
def do_add(rfc_num, title, host = me, port = uport):
    """Add a locally available RFC to the server's index"""
    s.send("ADD RFC " + str(rfc_num) + " " + VERSION + "\r\n" + "Host: " 
    + str(host) + "\r\n" + "Port: " + str(port) + "\r\n" + "Title: " 
    + str(title) + "\r\n\r\n")

#    s.send('ADD {rfc_num!s} {version!s}\r\nHost: {host!s}\r\nPort: {port!s}\r\nTitle: '
#        + '{title!s}\r\n\r\n'.format(rfc_num=rfc_num, version=VERSION, \
#        host=host, port=port, title=title))

    response = str(s.recv(2048))
    print "PEER FROM SERVER: " + response,
    #validate response

def do_lookup(rfc_num, title, host = me, port = uport):
    """Find peers that have the specifed RFC"""
    s.send("LOOKUP RFC " + str(rfc_num) + " " + VERSION + "\r\n" + "Host: " 
    + str(host) + "\r\n" + "Port: " + str(port) + "\r\n" + "Title: " 
    + str(title) + "\r\n\r\n")

    response = str(s.recv(2048))
    print "PEER FROM SERVER: " + response,
    #validate response

def do_list(host = me, port = uport):
    """Request the whole index of RFCs from the server"""
    s.send("LIST ALL " + VERSION + "\r\n" + "Host: " + str(host) + "\r\n" 
    + "Port: " + str(port) + "\r\n\r\n")

    response = str(s.recv(2048))
    print "PEER FROM SERVER: " + response,
    #validate response

# Define messages to peers TODO Currently sends to server
def do_get(rfc_num, host = me, OS = OS):
    """Request an RFC from a peer"""
    s.send("GET " + str(rfc_num) + " " + VERSION + "\r\n" + "Host: " 
    + str(host) + "\r\n" + "OS: " + str(OS) + "\r\n\r\n")

    response = str(s.recv(2048))
    print "PEER FROM SERVER: " + response,
    #validate response


# TODO Send peer's information to server 

# TODO Take commands from user via CLI and send messages to server and peers
time.sleep(.3)#Might should use a lock here TODO
while True:
    #Take command from user
    command = raw_input("=> ")
    if command == "":
        continue
    command = command.lower().split()

    #Handle command
    if command[0] == "exit":
        s.close
        p.terminate()
        sys.exit(0)
    elif command[0] == "get":
        do_get(command[1])
    elif command[0] == "list":
        do_list()
    elif command[0] == "lookup":
        do_lookup(command[1], command[2])
    elif command[0] == "add":
        do_add(command[1], command[2])
    elif command[0] == "help":
        print "help\t:\tPrint this help message"
        print "exit\t:\tClose the peer's connections and process"
        print "get <rfc_num>\t:\tDownload the given RFC"
        print "add <rfc_num> <rfc_title>\t:\tRegester the given RFC with the server"
        print "lookup <rfc_num> <rfc_title>\t:\tGet info of peers with given RFC"
        print "list\t:\tGet info about all RFCs known to server"
    else:
        print "Invalid command, see 'help'"
        
s.close
p.terminate()
