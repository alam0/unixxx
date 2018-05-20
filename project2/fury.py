#!/usr/bin/env python2.7

#Aron Lam, Travis Gayle, Nick Palutsis
#fury.py, commander of multiple HULKS

import sys
import work_queue
import os
import hashlib
import itertools
import string
import json

#Constants
ALPHABET = string.ascii_lowercase + string.digits
HASHES = "hashes.txt"
SOURCES = ('hulk.py', HASHES)
PORT = 9284
JOURNAL = {}

#Main Execution

if __name__ == '__main__':
	#Start work queue
	queue = work_queue.WorkQueue(PORT, name='hulk-alam3', catalog=True)
	queue.specify_log('fury.log')
	
	#Combinations of length 1-5
	for length in range(1,6):
		command = './hulk.py -l {}'.format(length)
		#Need to make sure machines being used have hulk.py in them
		if command not in JOURNAL:
			task = work_queue.Task(command)
			#Add source files
			for source in SOURCES:
				task.specify_file(source, source, work_queue.WORK_QUEUE_INPUT)
			queue.submit(task)
		else:
			print >> sys.stderr, 'Already did', command
	
	# Guess of length 5 + a length 1 prefix
	for prefix1 in itertools.product(ALPHABET, repeat = 1):
		command = './hulk.py -l 5 -p {}'.format(''.join(prefix1))
		if command not in JOURNAL:
			task = work_queue.Task(command)
			for source in SOURCES:
				task.specify_file(source, source, work_queue.WORK_QUEUE_INPUT)
			queue.submit(task)
			
		else:
			print >> sys.stderr, 'Already did', command
	
	# Guess of length 5 + a length 2 prefix
	for prefix2 in itertools.product(ALPHABET, repeat = 2):
		command = './hulk.py -l 5 -p {}'.format(''.join(prefix2))
		if command not in JOURNAL:
			task = work_queue.Task(command)
			for source in SOURCES:
				task.specify_file(source, source, work_queue.WORK_QUEUE_INPUT)
			queue.submit(task)
			
		else:
			print >> sys.stderr, 'Already did', command
	
	# Guess of length 5 + a length 3 prefix
	for prefix3 in itertools.product(ALPHABET, repeat = 3):
		command = './hulk.py -l 5 -p {}'.format(''.join(prefix3))
		if command not in JOURNAL:
			task = work_queue.Task(command)
			for source in SOURCES:
				task.specify_file(source, source, work_queue.WORK_QUEUE_INPUT)
		
			queue.submit(task)
			
		else:
			print >> sys.stderr, 'Already did', command
	
	
	while not queue.empty():
		#Wait for a task to complete
		task = queue.wait()
		
		#Check if task is valid and if task returned successfully
		if task and task.return_status == 0:
			# Example recording
			JOURNAL[task.command] = task.output.split()
			with open('journal.json.new', 'w') as stream:
				json.dump(JOURNAL, stream)
			os.rename('journal.json.new', 'journal.json')
			
			
