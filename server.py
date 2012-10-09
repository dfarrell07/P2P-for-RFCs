#!/usr/bin/env python
#Cite: http://www.tutorialspoint.com/python/python_networking.htm
#Cite: http://stackoverflow.com/questions/280243/python-linked-list

import socket
import random
from multiprocessing import Process

#Build data structures

class rfc_node:
    def __init__(self):
        self.next = None
        self.rfc_num = None
        self.rfc_title = None
        self.hostname = None

class rfc_linked_list:
    def __init__(self):
        self.cur_node = None

    def add(self, rfc_num, rfc_title, hostname):
        new_node = rfc_node()
        new_node.rfc_num = rfc_num
        new_node.rfc_title = rfc_title
        new_node.hostname = hostname
        new_node.next = self.cur_node
        self.cur_node = new_node

    def print_list(self):#Likely need to return as string, not print
        node = self.cur_node 
        while node:
            print node.rfc_num
            print node.rfc_title
            print node.hostname
            node = node.next

class peer_node:
    def __init__(self):
        self.next = None
        self.hostname = None #The hostname of the peer
        self.port = None #Port numer to which the upload server of this peer is listening

class peer_linked_list:
    def __init__(self):
        self.cur_node = None

    def add(self, hostname, port):
        new_node = peer_node()
        new_node.hostname = hostname
        new_node.port = port
        new_node.next = self.cur_node
        self.cur_node = new_node

    def print_list(self):
        node = self.cur_node
        while node:
            print node.hostname
            print node.port
            node = node.next

rll = rfc_linked_list()
pll = peer_linked_list()

#Setup networking
s = socket.socket()
host = socket.gethostname()
port = 7734#Well-known server port
s.bind((host, port))
s.listen(5)#May need to change this param

#Function to handle interactions with a peer
def manage_peer(con, addr):
    print 'SERVER: Managing new peer', addr
    while True:
        #Get message from peer
        message = con.recv(4096)
        if message == "":
            print "Message from peer was null\n" + message,
            con.send("Your message was null:\n" + message)
            continue
        marray = message.lower().split()

        #Handle message
        if marray[0] == 'list' and marray[1] == 'all' and marray[3] == 'host:' and marray[5] == 'port:': 
            print "SERVER: Recieved LIST: \n" + message,
            con.send("I got your LIST request")
        elif marray[0] == 'lookup' and marray[3] == 'host:' and marray[5] == 'port:' and marray[7] == 'title:':
            print "SERVER: Recieved LOOKUP: \n" + message,
            con.send("I got your LOOKUP request")
        elif marray[0] == 'add' and marray[3] == 'host:' and marray[5] == 'port:' and marray[7] == 'title:':
            print "SERVER: Recieved ADD: \n" + message,
            con.send("I got your ADD request")
        else:
            print "Invalid request from peer:\n" + message,
            con.send("Your request was invalid:\n" + message)

#Accept new peers and spawn them each a process
while True:
    con, addr = s.accept()#XXX Here we bind, listen and then accept a connection
    #Need to spawn a new process for each new peer
    p = Process(target=manage_peer, args=(con, addr))
    p.daemon = True
    p.start()

