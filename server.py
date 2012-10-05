#!/usr/bin/env python
#Cite: http://www.tutorialspoint.com/python/python_networking.htm

import socket
import random
"""
s = socket.socket()
host = socket.gethostname()
port = 7734
s.bind((host, port))

s.listen(5)

while True:
    c, addr = s.accept()
    #do things
    print 'Got connection from', addr
    c.send('Thanks for connecting!')
    c.close()
"""

class node:
    def __init__(self):
        self.next = None
        self.hostname = None #The hostname of the peer
        self.port = None #Port numer to which the upload server of this peer is listening

class linked_list:
    def __init__(self):
        self.cur_node = None

    def add(self, hostname, port):
        new_node = node()
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

ll = linked_list()
ll.add("host0", 12345)
ll.add("host1", 12346)
ll.add("host2", 12347)

ll.print_list()
