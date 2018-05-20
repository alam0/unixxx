#!/usr/bin/env python2.7 

import os 
import socket
import sys

# Constants

PORT    = 9755 #found using nc -z xavier.h4x0r.space 9700-9799

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Allocate TCP socket
ADDRESS = socket.gethostbyname('xavier.h4x0r.space')
client.connect((ADDRESS, PORT))                             # Connect to server with ADDRESS and PORT

stream = client.makefile('w+')                              # Create file object from socket
data   = sys.stdin.readline()                               # Read from STDIN

#function to open self and write to server
def openSend():
	infile = open('final.py','r')
	stuff = infile.read()
	stream.write(stuff)
	stream.flush()
	
while data:
	if str(data) == 'PUT alam3 1024\n':
		sys.stdout.write( 'hi')
		infile = open('final.py','r')
		stream.write(infile.read())
	# Send STDIN to Server
	stream.write(data)
	stream.flush()

	# Read from Server to STDOUT
	data = stream.readline()
	sys.stdout.write(data)

    # Read from STDIN
	data = sys.stdin.readline()
	openSend()
	

	
'''
infile = open('final.py','r')
stuff = infile.readline()

while stuff:
	stream.write(stuff)
	stream.flush()
	
	stuff = stream.readline()
	sys.stdout.write(stuff)
	
	stuff = infile.readline()
'''
    
    
#least favorite part: Oracle and Spidey/Thor, still don't understand them
    
