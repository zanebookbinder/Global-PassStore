"""
Program Description: Distributed password manager server that stores and manages various usernames,
websites, and 

Functions to update:
	register(username, key, val):
		* needs to be updated so that it can split the value (password) along multiple machines
	
	search(key):
		* update for multiple machines

	propagate(user, host, piece_num):
		* update information for all machines in distributed system
		

TODO:
	1. updating above functions to be distributed 
	2. ssh script: copy server.py file to all machines, start program
				ex. copy server.py:
					scp server.py [local] [remote]
			Goal:
				- Single shell script [one-time use]: ssh into machines, git clone repo
				- Recurring shell script [repeated use]: ssh into machines, git pull, execute specific python file
	3. create a function to split a password string into multiple chunks
	4. adding replication of password



"""

import os
import traceback
import sys
import xmlrpc.client
import xmlrpc.server
from xmlrpc.server import SimpleXMLRPCRequestHandler
from xmlrpc.server import SimpleXMLRPCServer
import sys
import math
import random
import time


# put everything in a big try/except so we can print error messages
try:
	sys.stdout = open('serverOut.log', 'w')
	sys.stdout.reconfigure(line_buffering=True)

	t = time.localtime()
	current_time = time.strftime("%H:%M:%S", t)
	print("Running at:", current_time)
	
	localPasswordData = {}
	userPasswordMap = {}
	# NOTE: a potentially useful data structure will be mapping a hostAddr to all of the users/sites/pieceNums it stores. 
	# this may be useful when we start replicating data. 

	hostmap = {'52.90.4.149':'172.31.55.0', '54.236.244.145':'172.31.53.196', '54.211.164.149':'172.31.52.8', '54.205.63.8':'172.31.53.249'}
	privateIPs = [ '172.31.55.0', '172.31.53.196', '172.31.52.8', '172.31.53.249' ]
	# publicIPs = ['52.90.4.149', '54.236.244.145', '54.211.164.149', '54.205.63.8']
	myPublicIP = os.popen('curl -s ifconfig.me').readline()
	myPrivateIP = hostmap[myPublicIP]
	myPort = int(sys.argv[1])
	
	print("my (private) IP addr: ", myPrivateIP)
	print("my port num: ", myPort)
	
	otherHosts = privateIPs.copy()
	otherHosts.remove(myPrivateIP)
	myName = f'http://{myPrivateIP}:{myPort}'


	allServers = {} # map of all hostnames to server connections (including )
	otherServers = {}

	#issue: it won't be able to connect to the other processes until they've been started
	time.sleep(0.5)


	for IPaddr in otherHosts:
		fullHostname = f'http://{IPaddr}:{myPort}/'
		allServers[IPaddr] = xmlrpc.client.ServerProxy(fullHostname)
		if IPaddr != myPrivateIP:
			otherServers[IPaddr] = xmlrpc.client.ServerProxy(fullHostname)

	

	print("Connected to other hosts")

	with SimpleXMLRPCServer((myPrivateIP, myPort), allow_none=True) as server:
		
		server.register_introspection_functions()

		# registers a username (zbookbin), key (zbookbin amazon.com), value (password)
		# across this machine and the other machine
		def register(username, key, val):
			print('in server register function')
			print("Current username:", username)
			print("Current key:", key)

			user = key.split(' ')[0]

			if username != user:
				return 'no permissions'

			site = key.split(' ')[1]

			# turn this into its own method later
			chunks = splitPassword(val, 4)

			# 'zbookbin amazon.com1', 'zbookbin amazon.com2'
			put(key + '1', chunks[0]) # store chunk1 on this machine
			print("before propagate to other hosts")
			propagate(key, myName, 1) # tell other host that this machines stores a piece of the zbookin amazon.com entry
			print("after propagate to other hosts")
			
			count = 2
			# guess: splitting up the password and storing it on difference 
			print("trying to split up rest of password amongst other hosts")

			# shuffling through the other server connections and splitting up the current password 
			# amongst those servers, and propagating the update to each server as well
			for IPaddr in random.shuffle(otherServers.keys()):
				# shuffling the IP addresses so that no machine stores the same order chunk
				connection = otherServers[IPaddr]
				print("current connection: ", IPaddr)
				connection.put(key+str(count), chunks[count-1])
				propagate(key, IPaddr, count)
				count+=1

			print("password has been distributed. register job complete!")
			return 1


		def splitPassword(password, n):
			output = []

			size = math.floor(len(password)/n)

			start = 0
			end = size
			for i in range(n):
				output.append(password[start:end+1])
				start += size
				end += size
				if end > len(password) - 1:
					end = len(password) - 1

			return output

		# put a (user + site), (password) pair into memory
		def put(key, val):
			localPasswordData[key] = val
			return 1

		# return a password if stored (given a user + site)
		def lookup(key):
			if key in localPasswordData:
				return localPasswordData[key]

			return -1

		# collect the pieces of a password given user + site
		def search(key):

			if key not in userPasswordMap:
				return 'No record of key'

			machines = userPasswordMap[key]
			pieces = ['' for i in range(2)]

			for pieceNum in machines:
				if machines[pieceNum] == myName:
					pieces[pieceNum-1] = lookup(key + str(pieceNum))
				else:
					pieces[pieceNum-1] = s.lookup(key + str(pieceNum))

			return ''.join(pieces)

			finalPassword = ''
			for i in range(1,3):
				if i not in results:
					return -1
				finalPassword += results[i]

			return finalPassword


		def getUserPasswordMap():
			return str(userPasswordMap)


		def getLocalPasswordData():
			return str(localPasswordData)


		# zbookbin amazon: {1: '8000', 2: '8001'} if password abcdef
		# NOTE: potential update - change map structure so that sites are their own dictionary nested
		# under user keys 
		def addHost(userSite, hostAddr, pieceNum):
			"""
			Adds a new password piece number and the associated server node that is storing that
			password to the user password map.
			Example of new entry in the user map
			
			@params:
				userSite (str) - A combination of a username and website that identifies a user's account on that site
					ex. "zbookbin amazon"
				hostAddr (str) - An http url identifying the server machine that is storing the password piece 
					ex. "http://172.31.55.0:8012"
				pieceNum (int) - A number that identifies the order of the password piece
					ex. 3

			@return:
				None
			"""
			# if the user has passwords stored in the map already
			
			if userSite in userPasswordMap:
				# if this password chunk number doesn't exist in the map
				if pieceNum not in userPasswordMap[userSite]:
					# create a new site + password entry for the existing user
					userPasswordMap[userSite][pieceNum] = hostAddr # machine that password chunk is stored on
				# otherwise, this password pairing exists in the map already, no updates needed
			
			# new user, create a new entry in the map
			else:
				# associate the password piece number with the server host node that it is sto
				userPasswordMap[userSite] = {pieceNum: hostAddr}


		# user = id + site, host = machine hostname, pieceNum = password piece number
		def propagate(user, host, pieceNum):
			"""
			
			"""
			print("updating local user-password map")
			addHost(user, host, pieceNum)

			print("sending update to other server nodes")
			for connection in otherServers.values():
				connection.addHost(user, host, pieceNum)


		server.register_function(register)
		server.register_function(search)
		server.register_function(put)
		server.register_function(getUserPasswordMap)
		server.register_function(getLocalPasswordData)
		server.register_function(addHost)
		server.register_function(propagate)
		server.register_function(lookup)
		server.register_function(splitPassword)
		
		print('about to serve forever - help im trapped in a process')
		server.serve_forever()

		sys.stdout.close()


except Exception:
    print(traceback.format_exc())



# import xmlrpc.client
# import xmlrpc.server
# from xmlrpc.server import SimpleXMLRPCRequestHandler
# from xmlrpc.server import SimpleXMLRPCServer
# import sys

# localPasswordData = {}
# userPasswordMap = {}

# if sys.argv[1] == '8000':
# 	otherHost = 'http://localhost:8001'
# else:
# 	otherHost = 'http://localhost:8000'

# s = xmlrpc.client.ServerProxy(otherHost)
# myname = 'http://localhost:' + str(sys.argv[1])

# with SimpleXMLRPCServer(('localhost', int(sys.argv[1])), allow_none=True) as server:
	
# 	server.register_introspection_functions()

# 	# registers a username (zbookbin), key (zbookbin amazon.com), value (password)
# 	# across this machine and the other machine
# 	def register(username, key, val):
# 		user = key.split(' ')[0]

# 		if username != user:
# 			return 'no permissions'

# 		site = key.split(' ')[1]

# 		# turn this into its own method later
# 		chunk1 = val[0:len(val)//2] # password pieces
# 		chunk2 = val[len(val)//2:]

# 		# 'zbookbin amazon.com1', 'zbookbin amazon.com2'
# 		put(key + '1', chunk1) # store chunk1 on this machine
# 		s.put(key + '2', chunk2) # store chunk2 on the other machine

# 		propagate(key, myname, 1) # tell other host that this machines stores a piece of the zbookin amazon.com entry
# 		propagate(key, otherHost, 2)  # tell other host that it stores a piece of the zbookin amazon.com entry

# 		return 1

# 	# put a (user + site), (password) pair into memory
# 	def put(key, val):
# 		localPasswordData[key] = val
# 		return 1

# 	# return a password if stored (given a user + site)
# 	def lookup(key):
# 		if key in localPasswordData:
# 			return localPasswordData[key]

# 		return -1

# 	# collect the pieces of a password given user + site
# 	def search(key):

# 		if key not in userPasswordMap:
# 			return 'No record of key'

# 		machines = userPasswordMap[key]
# 		pieces = ['' for i in range(2)]

# 		for pieceNum in machines:
# 			if machines[pieceNum] == myname:
# 				pieces[pieceNum-1] = lookup(key + str(pieceNum))
# 			else:
# 				pieces[pieceNum-1] = s.lookup(key + str(pieceNum))

# 		return ''.join(pieces)

# 		finalPassword = ''
# 		for i in range(1,3):
# 			if i not in results:
# 				return -1
# 			finalPassword += results[i]

# 		return finalPassword


# 	def userPasswordMap():
# 		return str(userPasswordMap)


# 	def getlocalPasswordData():
# 		return str(localPasswordData)


# 	# zbookbin amazon: {1: '8000', 2: '8001'} if password abcdef
# 	def addHost(user, host, pieceNum):
# 		if user in userPasswordMap:
# 			if pieceNum not in userPasswordMap[user]:
# 				userPasswordMap[user][pieceNum] = host # machine that password chunk is stored on
# 		else:
# 			userPasswordMap[user] = {pieceNum: host}


# 	# user = id + site, host = machine hostname, pieceNum = password piece number
# 	def propagate(user, host, pieceNum):
# 		addHost(user, host, pieceNum)
# 		s.addHost(user, host, pieceNum)


# 	server.register_function(register)
# 	server.register_function(search)
# 	server.register_function(put)
# 	server.register_function(userPasswordMap)
# 	server.register_function(getlocalPasswordData)
# 	server.register_function(addHost)
# 	server.register_function(propagate)
# 	server.register_function(lookup)
# 	server.serve_forever()