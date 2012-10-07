#!/usr/bin/env python

import socket
import random
import sys
import time
from multiprocessing import Process, Value

VERSION = "P2P-CI/1.0"
sport = 7734#Server's port
OS = sys.platform

#Need to spawn upload server process
uport = random.randint(45000, 60000)#Upload port

def ul_server(uport):
    print "I'm the upload sever on port " + str(uport)
    while True:
        #Listen on uport
        s = socket.socket()
        host = socket.gethostname()
        s.bind((host, uport))
        s.listen(1)#not sure if this param is right

        #Get message
        c, addr = s.accept()
        message = c.recv()
        marray = message.split()

        #Validate message TODO
        if marray[0] != 'GET' or marray[4] != 'Host:' or marray[6] != 'OS:':
            s.send(VERSION + "400 Bad Request\r\nDate: " + TODO_date 
            + "\r\nOS: " + OS)
            continue
        if marray[3] != VERSION:
            s.send(VERSION + "505 P2P-CI Version Not Supported\r\nDate: " 
            + TODO_date + "\r\nOS: " + OS)
            continue


        #Lookup RFC

        
        if True: #TODO If RFC found
            s.send(VERSION + "200 OK \r\nDate: " + TODO_date + "\r\nOS: " + OS
                + "\r\nLast-Modified: " + TODO_lm + "\r\nContent-Length: " 
                + TODO_cl + "\r\nContent-Type: " + TODO_ct + "\r\n" + TODO_data)
            continue
        else: #TODO If RFC not found
            s.send(VERSION + "404 Not Found\r\nDate: " + TODO_date 
                + "\r\nOS: " + OS)
            continue

p = Process(target=ul_server, args=(uport,))
p.daemon = True
p.start()

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


#do_add(123, "First title")
#do_get(123)
#do_list()
do_lookup(123, "First title")
s.close



