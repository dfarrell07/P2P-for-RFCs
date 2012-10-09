#!/usr/bin/env python
#Cite: http://www.tutorialspoint.com/python/python_networking.htm
#Cite: http://stackoverflow.com/questions/280243/python-linked-list

import socket
from multiprocessing import Process
import sys

VERSION = "P2P-CI/1.0"

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
        new_node.rfc_title = str(rfc_title)
        new_node.hostname = str(hostname)
        new_node.next = self.cur_node
        self.cur_node = new_node

    def print_list(self):
        node = self.cur_node 
        result = ""
        while node:
            result += str(node.rfc_num) + " " + node.rfc_title + " " + node.hostname + " " + str(pll.get_upload_port(node.hostname)) + "\r\n"
            node = node.next
        return result

    def lookup_rfc(self, rfc_num, rfc_title):
        node = self.cur_node
        result = ""
        while node:
            if node.rfc_num == rfc_num and node.rfc_title == rfc_title:
                result += str(node.rfc_num) + " " + node.rfc_title + " " + node.hostname + " " + str(pll.get_upload_port(node.hostname)) + "\r\n"
            node = node.next
        return result

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

    def get_upload_port(self, hostname):
        node = self.cur_node
        while node:
            if node.hostname == hostname:
                return node.port
        return ""

rll = rfc_linked_list()
pll = peer_linked_list()

"""
rll.add("abc", 123, "host0")
rll.add("abcd", 1234, "host1")
rll.add("abcde", 12345, "host2")
print rll.print_list(),
sys.exit(0)
"""

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
            rfc_list = rll.print_list()
            if rfc_list != "":
                con.send(VERSION + " 200 OK\r\n\r\n" + rfc_list + "\r\n")
            else:
                con.send(VERSION + " 404 Not Found\r\n\r\n")
        elif marray[0] == 'lookup' and marray[1] == 'rfc' and marray[4] == 'host:' and marray[6] == 'port:' and marray[8] == 'title:':
            print "SERVER: Recieved LOOKUP: \n" + message,
            lookup_result = rll.lookup_rfc(marray[2], marray[9])
            if lookup_result != "":
                con.send(VERSION + " 200 OK\r\n\r\n" + lookup_result + "\r\n")
            else:
                con.send(VERSION + " 404 Not Found\r\n\r\n")
        elif marray[0] == 'add' and marray[1] == 'rfc' and marray[4] == 'host:' and marray[6] == 'port:' and marray[8] == 'title:':
            print "SERVER: Recieved ADD: \n" + message,
            rll.add(marray[2], marray[9], marray[5])#rfc_num, rfc_title, hostname
            pll.add(marray[5], marray[7])#hostname, port
            con.send(VERSION + " 200 OK\r\nRFC " + marray[2] + " " + marray[9] + " " + marray[5] + " " + marray[7] + "\r\n\r\n")
        else:
            print "Invalid request from peer:\n" + message,
            con.send(VERSION + " 400 Bad Request\r\n\r\n")

#Accept new peers and spawn them each a process
while True:
    con, addr = s.accept()
    #Need to spawn a new process for each new peer
    p = Process(target=manage_peer, args=(con, addr))
    p.daemon = True
    p.start()
    #TODO Need to delete orphaned data when a peer leaves the swarm

