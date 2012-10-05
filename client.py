#!/usr/bin/env python

import socket
import random

VERSION = "P2P-CI/1.0"

s = socket.socket()
host = socket.gethostname()
port = 7734

def send_add(s, rfc_num, host, port, title):
    s.send("ADD " + str(rfc_num) + " " + VERSION + "\r\n" + "Host: " + str(host) 
        + "\r\n" + "Port: " + str(port) + "\r\n" + "Title: " + str(title) + "\r\n\r\n")

s.connect((host, port))
send_add(s, 123, host, port, "First title")
s.close



