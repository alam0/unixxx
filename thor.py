#!/usr/bin/env python2.7
#thor.py, a basic HTTP client

import os
import socket
import sys
import getopt
import logging
import math
import time
import signal
import errno

#Constants
REQUESTS = 1
PROCESSES = 1
URL = 'example.com'
ADDRESS = '0.0.0.0'
PORT = 80
PROGRAM = os.path.basename(sys.argv[0])
LOGLEVEL = logging.INFO


#Utility Functions
def usage(exit_code=0):
	print >>sys.stderr, '''Usage: thor.py [-r REQUESTS -p PROCESSES -v] URL
	
Options:
	-h		Show this help message
	-v		Set logging to DEBUG level
	
	-r REQUESTS	Number of requests per process (default is 1)
	-p PROCESSES Number of processes (default is 1)
'''.format(url=URL)
	sys.exit(exit_code)

#TCPClient Class
class TCPClient(object):
	
	def __init__(self, address=ADDRESS, port=PORT):
		''' Construct TCPClient objct with the specified address and port '''
		self.logger = logging.getLogger() #Grab logging instance
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Allocate TCP socket
		self.address = address
		self.port = port
	
	def handle(self):
		'''Handle connection'''
		self.logger.debug('Handle')
		raise NotImplementedError
	
	def run(self):
		''' Run client by connecting to specified address and port and then executing the handle mehtod '''
		logging.debug(self.address)
		logging.debug(self.port)
		try:
			# Connect to server with specified address and port, create file object
			self.socket.connect((self.address, self.port))
			self.stream = self.socket.makefile('w+')
		except socket.error as e:
			self.logger.error('Could not connect to {}:{}: {}'.format(self.address, self.port, e))
			sys.exit(1)
		
		self.logger.debug('Connected to {}:{}...'.format(self.address, self.port))
		
		#Run handle method and then the finish method
		try:
			self.handle()
		except Exception as e:
			self.logger.exception(e)
		finally:
			self.finish()
			
	def finish(self):
		''' Finish connection '''
		self.logger.debug('Finish')
		try:
			self.socket.shutdown(socket.SHUT_RDWR)
		except socket.error:
			pass  #Ignore socket errors
		finally:
			self.socket.close()



#HTTPClient Class
class HTTPClient(TCPClient):
	def __init__(self, url):
		TCPClient.__init__(self, None, None) # Initialize base class
		
		#Parsing URL
		self.url = url.split('://')[-1]
		if ':' not in self.url:
			self.port = 80
			self.domain = self.url.split('/', 1)[0]
		else:
			self.domain = self.url.split(':', 1)[0]
			self.porto = self.url.split(':', 1)[1]
			self.port = self.porto.split('/', 1)[0]
			
		self.host = self.domain
		self.logger.debug('Host: {}'.format(self.host))
		self.address = socket.gethostbyname(self.domain)
		self.logger.debug('Address: {}'.format(self.address))
		
		if '/' not in self.url:
			self.path ='/'
		else:
			self.path = '/' + self.url.split('/', 1)[-1]
	
	def handle(self):
		'''Handle connection'''
		self.logger.debug('Handle')
		self.logger.debug('Sending Request')
		try:
			#Send request
			self.stream.write('GET {} HTTP/1.0\r\n'.format(self.path))
			self.stream.write('Host: {}\r\n'.format(self.host))
			self.stream.write('\r\n')
			self.stream.flush()
		
			#Receive response
			self.logger.debug('Receiving Response')
			data = self.stream.readline()
			while data:
				sys.stdout.write(data) #can comment out to hide junk from server
				data = self.stream.readline()
		except socket.error as e:
			logging.exception(e)
			sys.exit(1)
			
#Main Execution
if __name__ == '__main__':
	#Parse command-line arguments
	try:
		options, arguments = getopt.getopt(sys.argv[1:], "hvr:p:")
	except getopt.GetoptError as e:
		usage(1)
	
	for option, value in options:
		if option == '-v':
			LOGLEVEL = logging.DEBUG
		elif option == '-r':
			REQUESTS = value
		elif option == '-p':
			PROCESSES = value
		else:
			usage(1)
			
	URL = arguments[0]
	
	# Set logging level
	logging.basicConfig(
		level = LOGLEVEL,
		format = '[%(asctime)s] %(message)s',
		datefmt = '%Y-%m-%d %H:%M:%S',
	)
	
	# Core control flow
	for process in range(PROCESSES):
		pid = os.fork()
		if pid == 0: #Children to perform requests
			totaltime = 0
			for request in range(REQUESTS):
				starttime = time.time()
				# Run Client
				client = HTTPClient(URL)
				try:
					client.run()
				except KeyboardInterrupt:
					sys.exit(0)
				endtime = time.time()
				elapsedtime = endtime - starttime
				logging.debug('{} | Elasped time: {:.2f} seconds'.format(os.getpid() ,elapsedtime))
				totaltime += elapsedtime
			logging.debug('{} | Average elasped time: {:.2f} seconds'.format(os.getpid() ,totaltime/int(REQUESTS)))
			sys.exit(0)
			
	#Clean up children
	for process in range(PROCESSES): #Parent
		try:
			pid, status = os.wait()
			logging.debug('Process {} terminated with exit status {}'.format(pid, status))
		except OSError as e:
			if e.errno == errno.EINTR:
				pid, status = os.wait()
			else:
				error(e)
				
		logging.debug
