#!/usr/bin/env python

import socket
import random
import sys
import time

VERSION = "P2P-CI/1.0"
sport = 7734
OS = sys.platform
uport = random.randint(45000, 60000)

#Open server connection
s = socket.socket()
me = socket.gethostname()
server = me #Assuming client and server are on the same machine
s.connect((server, sport))

def do_lookup(rfc_num, title, host = me, port = uport):
    s.send("LOOKUP " + str(rfc_num) + " " + VERSION + "\r\n" + "Host: " 
    + str(host) + "\r\n" + "Port: " + str(port) + "\r\n" + "Title: " 
    + str(title) + "\r\n\r\n")

    response = s.recv(2048)
    #validate response

def do_list(host = me, port = uport):
    s.send("LOOKUP ALL " + VERSION + "\r\n" + "Host: " + str(host) + "\r\n" 
    + "Port: " + str(port) + "\r\n\r\n")

    response = s.recv(2048)
    #validate response

def do_add(rfc_num, title, host = me, port = uport):
    s.send("ADD " + str(rfc_num) + " " + VERSION + "\r\n" + "Host: " 
    + str(host) + "\r\n" + "Port: " + str(port) + "\r\n" + "Title: " 
    + str(title) + "\r\n\r\n")

    response = s.recv(2048)
    #validate response

def do_get(rfc_num, host = me, OS = OS):
    s.send("GET " + str(rfc_num) + " " + VERSION + "\r\n" + "Host: " 
    + str(host) + "\r\n" + "OS: " + str(OS) + "\r\n\r\n")

    response = s.recv(2048)
    #validate response


do_add(123, "First title")
#do_list()
#do_lookup(123, "First title")
s.close



