#!/usr/bin/env python
#File: client.py
#Run with: "python ./client.py" 
#Tested with: Python 2.7.3
#Cite: http://stackoverflow.com/questions/5161166/python-handling-specific-error-codes

import socket
import errno
import random
import sys
import time
from multiprocessing import Process, Value
import datetime
import signal
import os
import glob
from collections import namedtuple

VERSION = "P2P-CI/1.0"
sport = 7734#Server's well-known port
OS = sys.platform
watch_dir = "./watch"

#Discover RFCs
rfc = namedtuple("rfc", ["num", "title", "mtime", "size", "data"])

if not os.path.exists(watch_dir):
    os.makedirs(watch_dir)

os.chdir(watch_dir)
files = []
def update_files(files=files):
    for f in glob.glob("*"):
        statbuf = os.stat(f)
        fd = open(f, 'r')
        files.append(rfc(num=f.split()[0], title=f.split()[1], mtime=statbuf.st_mtime, size=statbuf.st_size, data=fd.read()))
        fd.close()

update_files()

def get_rfc(rfc_num):
    for i in range(len(files)):
        if files[i].num == rfc_num:
            return files[i]
    return ""

#Spawn upload server process
uport = random.randint(45000, 60000)#Upload port

def ul_server(uport):
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
        if marray[0] != 'GET' or marray[1] != "RFC" or marray[4] != 'Host:' or marray[6] != 'OS:':
            con.send(VERSION + "400 Bad Request\r\nDate: " 
            + str(datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT"))
            + "\r\nOS: " + OS)
            continue
        if marray[3] != VERSION:
            con.send(VERSION + "505 P2P-CI Version Not Supported\r\nDate: " 
            + str(datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")) 
            + "\r\nOS: " + OS)
            continue

        #Respond
        resp_rfc = get_rfc(rfc_num=marray[2])
        if resp_rfc != "":
            con.send(VERSION + "200 OK \r\nDate: " 
                + str(datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")) 
                + "\r\nOS: " + OS + "\r\nLast-Modified: " 
                + resp_rfc.mtime + "\r\nContent-Length: "#TODO convert to proper time format 
                + resp_rfc.size + "\r\nContent-Type: text/plain\r\n" + resp_rfc.data)
            continue
        else:
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

#Get peer's IP address
#s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#s.connect(('google.com', 0))
#me = s.getsockname()[0]
me = socket.gethostbyname(socket.gethostname())

#Open server connection
s = socket.socket()
server = me #Assuming client and server are on the same machine
try:
    s.connect((server, sport))
except socket.error, v:
    errorcode=v[0]
    if errorcode==errno.ECONNREFUSED:
        print "PEER: There is no server on " + server

#Define messages to server
def do_add(rfc_num, title, host = me, port = uport):
    """Add a locally available RFC to the server's index"""
    s.send("ADD RFC " + str(rfc_num) + " " + VERSION + "\r\n" + "Host: " 
    + str(host) + "\r\n" + "Port: " + str(port) + "\r\n" + "Title: " 
    + str(title) + "\r\n\r\n")

    response = str(s.recv(2048))
    print "PEER FROM SERVER: \n" + response,
    #validate response

def do_lookup(rfc_num, title, host = me, port = uport):
    """Find peers that have the specifed RFC"""
    s.send("LOOKUP RFC " + str(rfc_num) + " " + VERSION + "\r\n" + "Host: " 
    + str(host) + "\r\n" + "Port: " + str(port) + "\r\n" + "Title: " 
    + str(title) + "\r\n\r\n")

    response = str(s.recv(2048))
    print "PEER FROM SERVER: \n" + response,
    #validate response

def do_list(host = me, port = uport):
    """Request the whole index of RFCs from the server"""
    s.send("LIST ALL " + VERSION + "\r\n" + "Host: " + str(host) + "\r\n" 
    + "Port: " + str(port) + "\r\n\r\n")

    response = str(s.recv(2048))
    print "PEER FROM SERVER: \n" + response,
    #validate response

def do_hello(host = me, OS = OS, uport = uport):
    """Send HELLO message to server, including hostname and upload port"""
    s.send("HELLO " + VERSION + "\r\n" + "Host: "
    + str(host) + "\r\n" + "OS: " + str(OS) + "\r\n" + "Upload port: "
    + str(uport) + "\r\n\r\n")

    response = str(s.recv(2048))
    print "PEER FROM SERVER: \n" + response,
    #validate response

def do_goodbye(host = me, OS = OS, uport = uport):
    """Send GOODBYE message to server, including hostname and upload port"""
    s.send("GOODBYE " + VERSION + "\r\n" + "Host: "
    + str(host) + "\r\n" + "OS: " + str(OS) + "\r\n" + "Upload port: "
    + str(uport) + "\r\n\r\n")

    response = str(s.recv(2048))
    print "PEER FROM SERVER: \n" + response,
    #validate response

# Define messages to peers TODO Currently sends to server. Need to lookup peer host and upload port, then send connect and message them.
def do_get(rfc_num, host = me, OS = OS):
    """Request an RFC from a peer"""
    s.send("GET " + str(rfc_num) + " " + VERSION + "\r\n" + "Host: " 
    + str(host) + "\r\n" + "OS: " + str(OS) + "\r\n\r\n")

    response = str(s.recv(2048))
    print "PEER FROM SERVER: \n" + response,
    #validate response
    #TODO need to generate file from response
    update_files()
    new_rfc = get_rfc(str(rfc_num))
    do_add(new_rfc.num, new_rfc.title)


#Cite: http://stackoverflow.com/questions/1112343/how-do-i-capture-sigint-in-python
def signal_handler(signal, frame):
    print 'Shutting down client'
    do_goodbye()
    s.close
    p.terminate()
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

time.sleep(.5)#Might should use a lock here TODO stretch requirement

# Send peer's hostname and upload port to server
do_hello()

# Send peer's RFCs
for i in range(len(files)):
    do_add(files[i].num, files[i].title)

# Take commands from user via CLI and send messages to server and peers
while True:
    #Take command from user
    command = raw_input("=> ")
    if command == "":
        continue
    command = command.lower().split()

    #Handle command
    if command[0] == "exit":
        if len(command) != 1:
            print "Usage: exit"
            continue
        print 'Shutting down client'
        do_goodbye()
        s.close
        p.terminate()
        sys.exit(0)
    elif command[0] == "get":
        if len(command) != 2:
            print "Usage: get <rfc_num>"
            continue
        do_get(command[1])
    elif command[0] == "list":
        if len(command) != 1:
            print "Usage: list"
            continue
        do_list()
    elif command[0] == "lookup":
        if len(command) != 3:
            print "Usage: lookup <rfc_num> <rfc_title>"
            continue
        do_lookup(command[1], command[2])
    elif command[0] == "add":
        if len(command) != 3:
            print "Usage: add <rfc_num> <rfc_title>"
            continue
        do_add(command[1], command[2])
    elif command[0] == "help":
        if len(command) != 1:
            print "Usage: help"
            continue
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
