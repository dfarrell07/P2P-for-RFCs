#!/usr/bin/env python
#Cite: http://www.tutorialspoint.com/python/python_networking.htm
#Cite: http://stackoverflow.com/questions/280243/python-linked-list

import socket
from multiprocessing import Process
import sys, errno

VERSION = "P2P-CI/1.0"

#Build data structures
class rfc_node:
    def __init__(self, rfc_num, rfc_title, hostname):
        self.next = None
        self.rfc_num = rfc_num
        self.rfc_title = rfc_title
        self.hostname = hostname

class rfc_linked_list:
    def __init__(self):
        self.head = None
        self.tail = None

    def add(self, rfc_num, rfc_title, hostname):
        new_node = rfc_node(rfc_num=rfc_num, rfc_title=rfc_title, hostname=hostname)

        if self.head == None:
            self.head = new_node

        if self.tail != None:
            self.tail.next = new_node

        self.tail = new_node

    def delete(self, hostname):
        """Deletes all rfc_node objects with param hostname"""
        while True:
            prev = None
            node = self.head
            if node == None:
                return
            while (node != None) and (node.hostname != hostname):
                prev = node
                node = node.next

            if node == None:
                return
            if prev == None:
                self.head = node.next
            else:
                prev.next = node.next

    def print_list(self):
        node = self.head
        result = ""
        while node:
            result += str(node.rfc_num) + " " + node.rfc_title + " " + node.hostname + " " + str(pll.get_upload_port(node.hostname)) + "\r\n"
            node = node.next
        return result

    def lookup_rfc(self, rfc_num, rfc_title):
        node = self.head
        result = ""
        while node:
            if node.rfc_num == rfc_num and node.rfc_title == rfc_title:
                result += str(node.rfc_num) + " " + node.rfc_title + " " + node.hostname + " " + str(pll.get_upload_port(node.hostname)) + "\r\n"
            node = node.next
        return result

class peer_node:
    def __init__(self, hostname, port):
        self.hostname = hostname #The hostname of the peer
        self.port = port #Port numer to which the upload server of this peer is listening
        self.next = None

class peer_linked_list:
    def __init__(self):
        self.head = None
        self.tail = None

    def add(self, hostname, port):
        new_node = peer_node(hostname=hostname, port=port)

        if self.head == None:
            self.head = new_node

        if self.tail != None:
            self.tail.next = new_node

        self.tail = new_node

    def delete(self, hostname, port):
        """Deletes any peer_node object that has param hostname and port.
        Assume that caller uses calls to get_upload_port to check that host
        doesn't already exist before calling add, so that there can be no dupe.
        This will only delete one object, even if there are dupes."""
        prev = None
        node = self.head
        if node == None:
            return
        while (node != None) and (node.hostname != hostname and node.port != port):
            prev = node
            node = node.next

        if prev == None:
            self.head = node.next
        else:
            prev.next = node.next

    def print_list(self):
        node = self.head
        while node != None:
            print node.hostname
            print node.port
            node = node.next

    def get_upload_port(self, hostname):
        node = self.head
        while node:
            if node.hostname == hostname:
                return node.port
            node = node.next
        return ""

rll = rfc_linked_list()
pll = peer_linked_list()

"""
rll.add(1, "abc", "127.0.0.1")
rll.add(2, "abc", "127.0.0.1")
rll.add(3, "abc", "127.0.0.1")
rll.add(4, "abc", "127.0.0.1")
rll.add(2, "abc", "127.0.0.2")
print rll.print_list()
rll.delete("127.0.0.1")
print rll.print_list()
sys.exit(0)
"""

#Setup networking
s = socket.socket()
host = socket.gethostbyname(socket.gethostname())
port = 7734#Well-known server port
s.bind((host, port))
s.listen(5)#May need to change this param

#Function to handle interactions with a peer
def manage_peer(con, addr):
    print 'SERVER: Managing new peer', socket.gethostbyname(addr[0]), addr[1]
    while True:
        #Get message from peer
        message = con.recv(4096)
        if message == "":
            print "Message from peer was null\n" + message, #TODO maybe remove
            try:
                con.send("Your message was null:\n" + message)
            except IOError, e:
                if e.errno == errno.EPIPE:
                    print "SERVER: Peer " + str(addr) + " left without saying GOODBYE."
                    pll.delete(hostname=socket.gethostbyname(addr[0]), port=addr[1])
                    rll.delete(hostname=socket.gethostbyname(addr[0]))
                    con.close()
                    sys.exit(0)
            continue
        marray = message.lower().split()

        #Handle message
        if marray[0] == 'hello' and marray[1] == str(VERSION).lower() and marray[2] == 'host:' and marray[4] == 'os:' and marray[6] == 'upload' and marray[7] == 'port:':
            print "SERVER: Recieved HELLO: \n" + message,
            if pll.get_upload_port(marray[8]) == "":
                pll.add(hostname=marray[3], port=marray[8])
                con.send(VERSION + " 200 OK\r\nYour host: " + marray[3] + "\r\nYour upload port: " + marray[8] + "\r\n\r\n") 
            else:
                con.send(VERSION + " 400 Bad Request\r\n\r\n")
        elif marray[0] == 'list' and marray[1] == 'all' and marray[2] == str(VERSION).lower() and marray[3] == 'host:' and marray[5] == 'port:': 
            print "SERVER: Recieved LIST: \n" + message,
            rfc_list = rll.print_list()
            if rfc_list != "":
                con.send(VERSION + " 200 OK\r\n\r\n" + rfc_list + "\r\n")
            else:
                con.send(VERSION + " 404 Not Found\r\n\r\n")
        elif marray[0] == 'lookup' and marray[1] == 'rfc' and marray[3] == str(VERSION).lower() and marray[4] == 'host:' and marray[6] == 'port:' and marray[8] == 'title:':
            print "SERVER: Recieved LOOKUP: \n" + message,
            lookup_result = rll.lookup_rfc(rfc_num=marray[2], rfc_title=marray[9])
            if lookup_result != "":
                con.send(VERSION + " 200 OK\r\n\r\n" + lookup_result + "\r\n")
            else:
                con.send(VERSION + " 404 Not Found\r\n\r\n")
        elif marray[0] == 'add' and marray[1] == 'rfc' and marray[3] == str(VERSION).lower() and marray[4] == 'host:' and marray[6] == 'port:' and marray[8] == 'title:':
            print "SERVER: Recieved ADD: \n" + message,
            rll.add(rfc_num=marray[2], rfc_title=marray[9], hostname=marray[5])
            con.send(VERSION + " 200 OK\r\nRFC " + marray[2] + " " + marray[9] + " " + marray[5] + " " + marray[7] + "\r\n\r\n")
        elif marray[0] == 'goodbye' and marray[1] == str(VERSION).lower() and marray[2] == 'host:' and marray[4] == 'os:' and marray[6] == 'upload' and marray[7] == 'port:':
            print "SERVER: Recieved GOODBYE: \n" + message,
            if pll.get_upload_port(marray[3]) != "":
                pll.delete(hostname=marray[3], port=marray[8])
                rll.delete(hostname=marray[3])
                con.send(VERSION + " 200 OK\r\nYour host: " + marray[3] + "\r\nYour upload port: " + marray[8] + "\r\n\r\n")
            else:
                con.send(VERSION + " 400 Bad Request\r\n\r\n")
            con.close()
            sys.exit(0)
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

