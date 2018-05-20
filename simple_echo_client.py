#!/usr/bin/env python2.7

import os
import socket
import sys

# Constants

ADDRESS = '127.0.0.1'
PORT    = 9234
PROGRAM = os.path.basename(sys.argv[0])

# Echo Client

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Allocate TCP socket
client.connect((ADDRESS, PORT))                             # Connect to server with ADDRESS and PORT

stream = client.makefile('w+')                              # Create file object from socket
data   = sys.stdin.readline()                               # Read from STDIN

while data:
    # Send STDIN to Server
    stream.write(data)
    stream.flush()

    # Read from Server to STDOUT
    data = stream.readline()
    sys.stdout.write(data)

    # Read from STDIN
    data = sys.stdin.readline()
