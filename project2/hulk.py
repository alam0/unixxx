#!/usr/bin/env python2.7

#Aron Lam, Travis Gayle, Nick Palutsis
#Hulk a script that uses brute-force to smash a set of MD5 hashes

import sys
import os
import getopt
import hashlib
import string
import random
import itertools

#Constants
ALPHABET = string.ascii_lowercase + string.digits
LENGTH = 8 
HASHES = 'hashes.txt'
PREFIX = ''

#Utiliity Functions
def usage(exit_code=0):
	print >>sys.stderr, '''Usage: hulk.py [-a ALPHABET -l LENGTH -s HASHES -p PREFIX]
	
Options:
	-a	ALPHABET	Alphabet used for passwords
	-l	LENGTH	Length for passwords
	
	-s HASHES	Path to file containing hashes
	-p PREFIX 	Prefix to use for each candidate password
'''
	sys.exit(exit_code)

def md5sum(s):
	return hashlib.md5(s).hexdigest()
	
#Main Execution
if __name__ == '__main__':
	#Parsing command line arguments
	try:
		options, arguments = getopt.getopt(sys.argv[1:], "a:l:s:p:")
	except getopt.GetoptError as e:
		usage(1)
	
	for option, value in options:
		if option == '-a':
			ALPHABET = value
		elif option == '-l':
			LENGTH = int(value)
		elif option == '-s':
			HASHES = str(value)
		elif option == '-p':
			PREFIX = str(value)
		else:
			usage(1)
			
	#Use set because we dont need to store a value with keys
	hashes = set([l.strip() for l in open(HASHES)])
	found = set()
	
	passwordList = itertools.product(ALPHABET , repeat=LENGTH)
	
	for password in passwordList:
		candidate = ''.join(password)
		candidate = PREFIX + candidate
		
		guess = md5sum(candidate)
		if guess in hashes:
			found.add(candidate)
	
	#Print out correct length, including prefix
	TOTALENGTH = LENGTH + len(PREFIX)
	for candidate in sorted(found):
		if len(candidate) == TOTALENGTH:
			print candidate
		
		
		
		
		
