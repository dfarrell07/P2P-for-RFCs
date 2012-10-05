#!/usr/bin/env python

import socket
import random

s = socket.socket()
host = socket.gethostname()
port = 7734
s.bind((host, port))

s.listen(5)

