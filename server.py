#!/usr/bin/env python
#Cite: http://www.tutorialspoint.com/python/python_networking.htm
#Cite: http://stackoverflow.com/questions/280243/python-linked-list

import socket
import random

s = socket.socket()
host = socket.gethostname()
port = 7734
s.bind((host, port))
s.listen(5)#May need to change this param

while True:
    c, addr = s.accept()
    #Need to spawn a new process for each new peer
    print 'Got connection from', addr
    print c.recv(1024)
    c.close()

def peer():
    print "I'm a new peer"

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
