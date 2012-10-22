#!/usr/bin/env python
#Cite: http://www.tutorialspoint.com/python/python_networking.htm

import socket
from multiprocessing import Process, Manager
import sys, errno
from collections import namedtuple

VERSION = "P2P-CI/1.0"

#Linked list that can be shared between processes
#Note: I bild a 'normal' ll, but then learned that it couldn't be shared
#Reason: http://stackoverflow.com/questions/1268252/python-possible-to-share-in-memory-data-between-2-separate-processes/1269055#1269055
#I can provide the ll if needed, it's in my git history
rfc_node = namedtuple("rfc_node", ["rfc_num", "rfc_title", "hostname"])
peer_node = namedtuple("peer_node", ["hostname", "port"])

manager = Manager()

rll = manager.list()
pll = manager.list()

#Functions for managing linked list
def remove_rfcs_by_host(hostname):
    removed = 0
    for i in range(len(rll)):
        i -= removed
        if rll[i].hostname == hostname:
            del rll[i]
            removed += 1

def get_ul_port(hostname):
    for i in range(len(pll)):
        if pll[i].hostname == hostname:
            return pll[i].port
    return ""

def get_hosts_by_rfc(rfc_num, rfc_title):
    result = ""
    for i in range(len(rll)):
        if rll[i].rfc_num == rfc_num and rll[i].rfc_title == rfc_title:
            result += str(rll[i].rfc_num) + " " + rll[i].rfc_title + " " + rll[i].hostname + " " + str(get_ul_port(rll[i].hostname)) + "\r\n"
    return result

def print_rll():
    result = ""
    for i in range(len(rll)):
        result += str(rll[i].rfc_num) + " " + rll[i].rfc_title + " " + rll[i].hostname + " " + str(get_ul_port(rll[i].hostname)) + "\r\n"
    return result 

def is_new_peer(hostname, port):
    for i in range(len(pll)):
        if pll[i].hostname == hostname and pll[i] == port:
            return False
    return True

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
            try:
                con.send("Your message was null:\n" + message)
            except IOError, e:
                if e.errno == errno.EPIPE:
                    print "SERVER: Peer " + str(addr) + " left without saying GOODBYE."
                    del pll[pll.index(peer_node(hostname=socket.gethostbyname(addr[0]), port=addr[1]))]
                    remove_rfcs_by_host(socket.gethostbyname(addr[0]))
                    con.close()
                    sys.exit(0)
            continue
        marray = message.lower().split()

        #Handle message
        if marray[0] == 'hello' and marray[1] == str(VERSION).lower() and marray[2] == 'host:' and marray[4] == 'os:' and marray[6] == 'upload' and marray[7] == 'port:':
            print "SERVER: Recieved HELLO: \n" + message,
            if is_new_peer(marray[3], marray[8]):
                pll.append(peer_node(hostname=marray[3], port=marray[8]))
                con.send(VERSION + " 200 OK\r\nYour host: " + marray[3] + "\r\nYour upload port: " + marray[8] + "\r\n\r\n") 
            else:
                con.send(VERSION + " 400 Bad Request\r\n\r\n")
        elif marray[0] == 'list' and marray[1] == 'all' and marray[2] == str(VERSION).lower() and marray[3] == 'host:' and marray[5] == 'port:': 
            print "SERVER: Recieved LIST: \n" + message,
            rfc_list = print_rll()
            if rfc_list != "":
                con.send(VERSION + " 200 OK\r\n\r\n" + rfc_list + "\r\n")
            else:
                con.send(VERSION + " 404 Not Found\r\n\r\n")
        elif marray[0] == 'lookup' and marray[1] == 'rfc' and marray[3] == str(VERSION).lower() and marray[4] == 'host:' and marray[6] == 'port:' and marray[8] == 'title:':
            print "SERVER: Recieved LOOKUP: \n" + message,
            lookup_result = get_hosts_by_rfc(rfc_num=marray[2], rfc_title=marray[9])
            if lookup_result != "":
                con.send(VERSION + " 200 OK\r\n\r\n" + lookup_result + "\r\n")
            else:
                con.send(VERSION + " 404 Not Found\r\n\r\n")
        elif marray[0] == 'add' and marray[1] == 'rfc' and marray[3] == str(VERSION).lower() and marray[4] == 'host:' and marray[6] == 'port:' and marray[8] == 'title:':
            print "SERVER: Recieved ADD: \n" + message,
            rll.append(rfc_node(rfc_num=marray[2], rfc_title=marray[9], hostname=marray[5]))
            con.send(VERSION + " 200 OK\r\nRFC " + marray[2] + " " + marray[9] + " " + marray[5] + " " + marray[7] + "\r\n\r\n")
        elif marray[0] == 'goodbye' and marray[1] == str(VERSION).lower() and marray[2] == 'host:' and marray[4] == 'os:' and marray[6] == 'upload' and marray[7] == 'port:':
            print "SERVER: Recieved GOODBYE: \n" + message,
            if get_ul_port(marray[3]) != "":
                del pll[pll.index(peer_node(hostname=marray[3], port=marray[8]))]
                remove_rfcs_by_host(marray[3])
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
    p = Process(target=manage_peer, args=(con, addr))
    p.daemon = True
    p.start()
