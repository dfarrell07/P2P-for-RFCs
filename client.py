#!/usr/bin/env python
# File: client.py
# Run with: "python ./client.py" 
# Tested with: Python 2.7.3
# Cite: http://goo.gl/MuP4t
# Cite: http://goo.gl/Ql3f5
# Public Domain

import socket
import errno
import random
import sys
from multiprocessing import Process
import datetime
import signal
import os
import glob
from collections import namedtuple
from datetime import date

DEBUG = False
VERSION = "P2P-CI/1.0"
files = []
sport = 7734# Server's well-known port
OS = sys.platform
watch_dir = "./watch"
peer_rfc = namedtuple("peer_rfc", ["rfc_num", "rfc_title", "hostname", "port"])
rfc = namedtuple("rfc", ["num", "title", "mtime", "size", "data"])

# Find my IP
# Cite: http://is.gd/gLzpdS
stmp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
stmp.connect(("gmail.com",80))
me = stmp.getsockname()[0]
stmp.close()

if DEBUG:
    print "PEER: You are in debug mode"

# Setup signal SIGCHLD handler
signal.signal(signal.SIGINT, signal.SIG_IGN)

def SIGCHLD_handler(signal, frame):
    """Check exit status of children to avoid zombies"""
    try:
        tpid = os.waitpid(0, os.WNOHANG)
    except:
        if DEBUG:
            print "PEER: Caught an error in SIGCHLD handler"
        return
    if DEBUG:
        print "PEER: Child process with PID", tpid, "closed"
signal.signal(signal.SIGCHLD, SIGCHLD_handler)

# Discover RFCs
if not os.path.exists(watch_dir):
    print "No watch directory exists.",
    os.makedirs(watch_dir)
    print "A new watch directory has been created."

os.chdir(watch_dir)
# Note: The modified time seems to not be very precise
def update_files():
    """Collect info of files in watch_dir"""
    global files
    files = []
    for f in glob.glob("*"):
        statbuf = os.stat(f)
        fd = open(f, 'r')
        files.append(rfc(num = f.split()[0], title = f.split()[1], \
            mtime = statbuf.st_mtime, size = statbuf.st_size, data = fd.read()))
        fd.close()

update_files()

def get_rfc(rfc_num):
    """Get the details of the RFC with the given number"""
    global files
    for i in range(len(files)):
        if files[i].num == rfc_num:
            return files[i]
    return ""

# Spawn upload server process
uport = random.randint(45000, 60000)# Upload port

def ul_server(uport):
    """Manage all requests from peers"""
    # Listen on uport
    s = socket.socket()
    host = socket.gethostname()
    s.bind((me, uport))
    s.listen(5)
    print "Upload server started, listening on " + me + ":" + str(uport)
    while True:
        # Get message
        try:
            con, addr = s.accept()
        except socket.error:
            continue
        except KeyboardInterrupt:
            print "\nPEER: Shutting down"
            s.close
            sys.exit(0)
        message = con.recv(4096)
        marray = message.split()

        if DEBUG:
            print "PEER FROM PEER:\n" + message,

        # Validate message from peer
        if marray[0] != 'GET' or marray[1] != "RFC" or marray[4] != 'Host:' \
            or marray[6] != 'OS:':
            con.send(VERSION + "400 Bad Request\r\nDate: " 
            + str(datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT"))
            + "\r\nOS: " + OS)
            if DEBUG:
                print "PEER: Message was invalid"
            continue
        if marray[3] != VERSION:
            con.send(VERSION + "505 P2P-CI Version Not Supported\r\nDate: " 
            + str(datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")) 
            + "\r\nOS: " + OS)
            if DEBUG:
                print "PEER: Version is not supported"
            continue

        if DEBUG:
            print "PEER: Message is valid"

        # Respond to peer
        resp_rfc = get_rfc(rfc_num = marray[2])
        if resp_rfc != "":
            if DEBUG:
                print "PEER: Sending RFC"
            con.send(VERSION + " 200 OK\r\nDate: " 
                + str(datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")) 
                + "\r\nOS: " + OS + "\r\nLast-Modified: " 
                + str(date.fromtimestamp(float(resp_rfc.mtime)).strftime("%a, %d %b %Y %H:%M:%S GMT")) 
                + "\r\nContent-Length: " + str(resp_rfc.size) 
                + "\r\nContent-Type: text/plain\r\n\r\n" + str(resp_rfc.data))
            if DEBUG:
                print "PEER: Response sent\n=> ",
            continue
        else:
            if DEBUG:
                print "PEER: RFC not found, sending 404"
            con.send(VERSION + " 404 Not Found\r\nDate: " 
                + str(datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT"))
                + "\r\nOS: " + OS)
            continue

p = Process(target = ul_server, args = (uport,))
p.daemon = True
p.start()

# Open server connection
s = socket.socket()
server = "10.0.0.3"
try:
    s.connect((server, sport))
except socket.error, e:
    if e.errno == errno.ECONNREFUSED:
        print "PEER ERROR: There is no server on", str(server) + ":" \
            + str(sport)
        s.close()
        p.terminate()
        sys.exit(1)
    else:
        print "PEER ERROR: There was an IOError", e.errno

# Define messages to server
def do_add(rfc_num, title, host = me, port = uport):
    """Add a locally available RFC to the server's index"""
    try:
        s.send("ADD RFC " + str(rfc_num) + " " + VERSION + "\r\n" + "Host: " 
            + str(host) + "\r\n" + "Port: " + str(port) + "\r\n" + "Title: " 
            + str(title) + "\r\n\r\n")
    except IOError, e:
        if e.errno == errno.EPIPE:
            print "PEER ERROR: There is no server on", str(server) + ":" \
                + str(sport)
            s.close()
            p.terminate()
            sys.exit(1)
        else:
            print "PEER ERROR: There was an IOError", e.errno

    response = str(s.recv(4096))
    if DEBUG:
        print "PEER FROM SERVER:\n" + response,

    # Validate response
    rarray = response.split()
    if rarray[0] == VERSION and rarray[1] == "200" and rarray[2] == "OK":
        return
    elif rarray[0] == VERSION and rarray[1] == "400" and rarray[2] == "Bad" \
        and rarray[3] == "Request":
        print "Server responded with a '400 Bad Request'"
    elif rarray[0] != VERSION:
        print "Unsupported server version", rarray[0]
    else:
        print "Unknown response from server:\n" + response,

def do_lookup(rfc_num, title, host = me, port = uport):
    """Find peers that have the specified RFC"""
    try:
        s.send("LOOKUP RFC " + str(rfc_num) + " " + VERSION + "\r\n" + "Host: " 
            + str(host) + "\r\n" + "Port: " + str(port) + "\r\n" + "Title: " 
            + str(title) + "\r\n\r\n")
    except IOError, e:
        if e.errno == errno.EPIPE:
            print "PEER ERROR: There is no server on", str(server) + ":" \
                + str(sport)
            s.close()
            p.terminate()
            sys.exit(1)
        else:
            print "PEER ERROR: There was an IOError", e.errno

    response = str(s.recv(4096))
    if DEBUG:
        print "PEER FROM SERVER:\n" + response,

    # Validate response
    rarray = response.split()
    # If RFC found
    if rarray[0] == VERSION and rarray[1] == "200" and rarray[2] == "OK":
        # Display RFCs to user
        rfcs = response.split("200 OK\r\n\r\n")[1]
        return peer_rfc(rfc_num = rarray[3], rfc_title = rarray[4], \
            hostname = rarray[5], port = rarray[6])
    # If RFC not found
    elif rarray[0] == VERSION and rarray[1] == "404" and rarray[2] == "Not" \
        and rarray[3] == "Found":
        return ""
    elif rarray[0] == VERSION and rarray[1] == "400" and rarray[2] == "Bad" \
        and rarray[3] == "Request":
        print "Server responded with a '400 Bad Request'"
    elif rarray[0] != VERSION:
        print "Unsupported server version", rarray[0]
    else:
        print "Unknown response from server:\n" + response,
    return ""

def do_list(host = me, port = uport):
    """Request the whole index of RFCs from the server"""
    try:
        s.send("LIST ALL " + VERSION + "\r\n" + "Host: " + str(host) + "\r\n" \
            + "Port: " + str(port) + "\r\n\r\n")
    except IOError, e:
        if e.errno == errno.EPIPE:
            print "PEER ERROR: There is no server on", str(server) + ":" \
                + str(sport)
            s.close()
            p.terminate()
            sys.exit(1)
        else:
            print "PEER ERROR: There was an IOError", e.errno

    response = str(s.recv(4096))

    if DEBUG:
        print "PEER FROM SERVER:\n" + response,

    # Validate response
    rarray = response.split()
    # If there are RFCs
    if rarray[0] == VERSION and rarray[1] == "200" and rarray[2] == "OK":
        # Display RFCs to user
        rfcs = response.split("200 OK\r\n\r\n")[1]
        print rfcs[:len(rfcs)-1],
    # If there are no RFCs
    elif rarray[0] == VERSION and rarray[1] == "404" and rarray[2] == "Not" \
        and rarray[3] == "Found":
        print "Server knows of no RFCs"
    elif rarray[0] == VERSION and rarray[1] == "400" and rarray[2] == "Bad" \
        and rarray[3] == "Request":
        print "Server responded with a '400 Bad Request'"
    elif rarray[0] != VERSION:
        print "Unsupported server version", rarray[0]
    else:
        print "Unknown response from server:\n" + response,

def do_hello(host = me, OS = OS, uport = uport):
    """Send HELLO message to server, including hostname and upload port"""
    try:
        s.send("HELLO " + VERSION + "\r\n" + "Host: " \
            + str(host) + "\r\n" + "OS: " + str(OS) + "\r\n" + "Upload port: " \
            + str(uport) + "\r\n\r\n")
    except IOError, e:
        if e.errno == errno.EPIPE:
            print "PEER ERROR: There is no server on", str(server) + ":" \
                + str(sport)
            s.close()
            p.terminate()
            sys.exit(0)
        else:
            print "PEER ERROR: There was an IOError", e.errno

    response = str(s.recv(4096))
    if DEBUG:
        print "PEER FROM SERVER:\n" + response,

    # Validate response
    rarray = response.split()
    if rarray[0] == VERSION and rarray[1] == "200" and rarray[2] == "OK":
        return
    elif rarray[0] == VERSION and rarray[1] == "400" and rarray[2] == "Bad" \
        and rarray[3] == "Request":
        print "Server responded with a '400 Bad Request'"
    elif rarray[0] != VERSION:
        print "Unsupported server version", rarray[0]
    else:
        print "Unknown response from server:\n" + response,

def do_goodbye(host = me, OS = OS, uport = uport):
    """Send GOODBYE message to server, including hostname and upload port"""
    try:
        s.send("GOODBYE " + VERSION + "\r\n" + "Host: " \
            + str(host) + "\r\n" + "OS: " + str(OS) + "\r\n" + "Upload port: " \
            + str(uport) + "\r\n\r\n")
    except IOError, e:
        if e.errno == errno.EPIPE:
            print "PEER ERROR: There is no server on", str(server) + ":" \
                + str(sport)
            s.close()
            p.terminate()
            sys.exit(1)
        else:
            print "PEER ERROR: There was an IOError", e.errno

    response = str(s.recv(4096))
    if response == "":
        print "PEER: The server has already left"
    elif DEBUG:
        print "PEER FROM SERVER: \n" + response,

    # Validate response
    rarray = response.split()
    if rarray[0] == VERSION and rarray[1] == "200" and rarray[2] == "OK":
        return
    elif rarray[0] == VERSION and rarray[1] == "400" and rarray[2] == "Bad" \
        and rarray[3] == "Request":
        print "Server responded with a '400 Bad Request'"
    elif rarray[0] != VERSION:
        print "Unsupported server version", rarray[0]
    else:
        print "Unknown response from server:\n" + response,

# Define messages to peers 
def do_get(rfc_num, rfc_title, host = me, OS = OS):
    """Request an RFC from a peer"""
    # Check if peer already has this RFC
    my_rfc = get_rfc(rfc_num)
    if my_rfc != "":
        print "You already have RFC", rfc_num
        return

    # Get hostname and upload port of some peer with RFC
    prfc = do_lookup(rfc_num, rfc_title)

    if prfc == "":
        print "The server doesn't know where to find RFC", rfc_num
        return

    # Open connection to peer's upload port
    p = socket.socket()
    try:
        print "Connecting to " + prfc.hostname + ":" + str(prfc.port)
        p.connect((prfc.hostname, int(prfc.port)))
    except socket.error, v:
        print "PEER ERROR: There was a socket error"
        errorcode = v[0]
        if errorcode == errno.ECONNREFUSED:
            print "PEER ERROR: There is no peer on " + prfc.hostname + ":" \
                + str(prfc.port)
            return

    # Send GET to peer
    try:
        p.send("GET RFC " + str(prfc.rfc_num) + " " + VERSION + "\r\n" \
            + "Host: " + str(prfc.hostname) + "\r\n" + "OS: " + str(OS) \
            + "\r\n\r\n")
    except IOError, e:
        if e.errno == errno.EPIPE:
            print "PEER ERROR: There is no peer on", prfc.hostname + ":" \
                + str(prfc.port)
            p.close()
            return
        else:
            print "PEER ERROR: There was an IOError", e.errno

    # Receive response
    response = str(p.recv(4096))
    if DEBUG:
        print "PEER FROM PEER: \n" + response,

    p.close()

    # Validate response
    rarray = response.split()
    if rarray[0] == VERSION and rarray[1] == "200" and rarray[2] == "OK" \
        and rarray[3] == "Date:" and rarray[10] == "OS:" \
        and rarray[12] == "Last-Modified:" and rarray[19] == "Content-Length:" \
        and rarray[21] == "Content-Type:" and rarray[22] == "text/plain":
        pass
    elif rarray[0] == VERSION and rarray[1] == "400" and rarray[2] == "Bad" \
        and rarray[3] == "Request":
        print "Peer responded with a '400 Bad Request'"
        return
    elif rarray[0] != VERSION:
        print "Unsupported peer version", rarray[0]
        return
    else:
        print "Unknown response from peer:\n" + response,
        return

    # Generate RFC file from response
    new_rfc = response.split("Content-Type: text/plain\r\n\r\n")[1]
    with open(str(rfc_num) + " " + rfc_title, "w") as fd:
        fd.write(new_rfc)
    fd.close()

    # Update RFC collection and inform server of new RFC
    update_files()
    new_rfc = get_rfc(str(rfc_num))
    do_add(new_rfc.num, new_rfc.title)

    print "Added RFC", new_rfc.num, new_rfc.title

def SIGINT_handler(signal, frame):
    """Close down properly when SIGINT is thrown"""
    print "\nShutting down client"
    do_goodbye()
    s.close
    p.terminate()
    sys.exit(0)
signal.signal(signal.SIGINT, SIGINT_handler)

# Send peer's hostname and upload port to server
do_hello()

# Send peer's RFCs
for i in range(len(files)):
    do_add(files[i].num, files[i].title)

# Take commands from user via CLI and send messages to server and peers
while True:
    # Take command from user
    command = raw_input("=> ")
    if command == "":
        continue
    command = command.lower().split()

    # Handle command
    if command[0] == "exit":
        if len(command) != 1:
            print "Usage: exit"
            continue
        print "Shutting down client"
        do_goodbye()
        s.close
        p.terminate()
        sys.exit(0)
    elif command[0] == "get":
        if len(command) != 3:
            print "Usage: get <rfc_num> <rfc_title>"
            continue
        do_get(command[1], command[2])
    elif command[0] == "list":
        if len(command) != 1:
            print "Usage: list"
            continue
        do_list()
    elif command[0] == "lookup":
        if len(command) != 3:
            print "Usage: lookup <rfc_num> <rfc_title>"
            continue
        rrfc = do_lookup(command[1], command[2])
        if rrfc == "":
            print "The server doesn't know where to find RFC", command[1]
            continue
        print rrfc.rfc_num, rrfc.rfc_title, rrfc.hostname, rrfc.port
    elif command[0] == "help":
        if len(command) != 1:
            print "Usage: help"
            continue
        print "help\t\t\t\t: Print this help message"
        print "exit\t\t\t\t: Close the peer's connections and process"
        print "get <rfc_num> <rfc_title>\t: Download the given RFC"
        print "lookup <rfc_num> <rfc_title>\t: Get info of peers with given RFC"
        print "list\t\t\t\t: Get info about all RFCs known to server"
    else:
        print "Invalid command, see 'help'"
