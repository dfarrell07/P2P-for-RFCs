#!/usr/bin/env python

import socket
import random

s = socket.socket()
host = socket.gethostname()
port = 7734

s.connect((host, port))
print s.recv(1024)
s.close
