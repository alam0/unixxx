# README
# Aron Lam, Travis Gayle, Nick Palutsis

##Describe the implementation of hulk.py. How does it crack passwords?

	Hulk.py takes in command line arguments, parses them and set variables like LENGTH, HASHES, and PREFIX.  
Hulk.py uses 2 sets, called hashes and found to store hashes from the hashes.txt file and found solutions.  
Combinations of passwords are created through itertools.product(ALPHABET, repeat=LENGTH).  
A for loop is used to iterate through the combinations (with PREFIX varaible added) to hash the combination, check if it matches anything in the hashes set, and add it to the found set if a match is found.  
Hulk.py finally, goes through the found set and prints out solutions of the correct length.  

##Explain how you tested hulk.py and verified that it works properly.

We tested hulk.py by running the example commands given on the homework10/project02 website and checked to see if the results matched. 

##Describe the implementation of fury.py. How does it:

###Utilize hulk.py to crack passwords?

Fury.py first starts a Work_Queue and specfies a log to write to. Then it creates a command variable that consists of a variation of "./hulk.py -l {}".format(length). There is also more formatting with prefixes such as the for loops used for passwords of length 6, 7, and 8. For those lengths, the command was "./hulk.py -l 5 -p {}".format(prefix of length 1,2,or 3). 
The itertools product function is used to create combinations of the prefixes. Then we add source files and submit the task to the queue for workers.

###Divide up the work among the different workers?

We started with a single worker to make sure that our script was working, but overall Work_queue does all of that for us after a request through condor for 200-400 workers.

###Keep track of what has been attempted?

We keep track of what is being attempted by using journal.json and which seemed to be dictionary with the commands as keys and returned strings as values. Journal_dump_passwords is script that Dr. Bui created and we call the script and redirect the output to a file called MYPASSWORDS. We did this so that we could see the results we found and for simpler submission to Deadpool.

###Recover from failures?

The master reassigns a task to a new worker if a worker fails. If a master fails, the journal takes care of that. Basically, there is just a process of reassigning a role so that everything functions.


##Explain how you tested fury.py and verified that it works properly.

Fury wass tested by checking MYPASSWORDS which was where journal_dump_passwords was redirected. In our script, we did a few iterations for passwords of length 1 to 5, then doing a separate series of tests from length 6 to 8. We also used the Unix pipeline to submit our results to the Deadpool, another form of verification.


##From your experience in this project and recalling your Discrete Math knowledge, what would make a password more difficult to brute-force: more complex alphabet or longer password? Explain.

A longer password would be more difficult to brute force. We used math to arrive at our answer. If we take a 4 lowercase-letter password 26 x 26 x 26 x 26 which is increasing the length by one more letter leads to 456976 passwords whereas adding uppercase letters 52 x 52 x 52 results in 140608 passwords which is significantly less than the previous example.

