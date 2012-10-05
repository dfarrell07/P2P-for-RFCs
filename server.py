#!/usr/bin/env python
#Cite: http://www.tutorialspoint.com/python/python_networking.htm

import socket
import random

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
