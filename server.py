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
	1. updating above functions to be distributed  # I THINK THIS MIGHT BE DONE??
	2. How do we replace data from failed nodes?
	3. test replication with failed server
	4. change split password to avoid adding spaces
	5. add lots of comments and update variable names?
	6. Add username security (don't allow user to access someone else's data)
	7. Remove all constants so serverCount is the only thing that knows how many servers we have
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

try:
	sys.stdout = open('outputServer.log', 'w') # print statements go to this file
	sys.stdout.reconfigure(line_buffering=True)

	t = time.localtime()
	current_time = time.strftime("%H:%M:%S", t)
	print("Running at:", current_time)
	
	localPasswordData = {}
	userPasswordMap = {}

	hosts = ['35.172.235.46', '44.199.229.51', '3.22.185.101', '18.191.134.62', '13.57.194.105', 
	'54.177.19.64', '34.222.143.244', '54.202.50.11', '13.245.182.179', '13.246.6.180', '18.166.176.112', 
	'16.162.137.92', '108.136.118.131', '108.136.41.214', '13.233.255.217', '15.206.211.195', '15.152.35.76',
	 '13.208.42.124', '13.125.213.112', '52.79.85.82', '18.136.203.66', '54.251.84.92', '3.104.66.60', 
	 '3.26.227.87', '18.183.60.155', '54.95.115.193', '3.99.158.136', '3.98.96.39', '3.122.191.72', 
	 '3.73.75.196', '34.244.200.204', '3.250.224.218', '18.130.129.70', '13.40.95.197', '15.160.192.179',
	  '15.160.153.56', '35.180.109.137', '35.180.39.12', '13.48.137.111', '13.48.3.201', '15.185.175.128', 
	  '157.175.185.52', '15.228.252.96', '15.229.0.10']

	# hostmap = {'52.90.4.149':'172.31.55.0', '54.236.244.145':'172.31.53.196', '54.211.164.149':'172.31.52.8', '54.205.63.8':'172.31.53.249'}
	# privateIPs = [ '172.31.55.0', '172.31.53.196', '172.31.52.8', '172.31.53.249']
	myPublicIP = os.popen('curl -s ifconfig.me').readline()
	mytestIP = '0.0.0.0'

	res = os.popen('/sbin/ifconfig | grep inet | head -n 1').readline()
	splitIP = res.split(' ')

	count = 0
	for s in splitIP:
		if s != '':
			count += 1

		if count == 2:
			myPrivateIP = s
			break

	print('myPrivateIP:', myPrivateIP)

	# myPrivateIP = hostmap[myPublicIP]
	myPort = int(sys.argv[1])
	serverCount = len(hosts)
	
	print("my (public) IP addr: ", myPublicIP)
	print("my port num: ", myPort)
	
	otherHosts = hosts.copy()
	otherHosts.remove(myPublicIP)

	myName = f'http://{myPublicIP}:{myPort}' # we don't use myName at all

	allServers = {} # we don't use this at all either
	otherServers = {}

	time.sleep(3) # I think we should make this longer since it'll only happen on startup

	for IPaddr in hosts:
		fullHostname = f'http://{IPaddr}:{myPort}/'
		allServers[IPaddr] = xmlrpc.client.ServerProxy(fullHostname)
		if IPaddr != myPublicIP:
			otherServers[IPaddr] = xmlrpc.client.ServerProxy(fullHostname)

	print("Connected to other hosts")

	with SimpleXMLRPCServer((myPrivateIP, myPort), allow_none=True) as server:
		server.register_introspection_functions()

		# registers a username (zbookbin), key (zbookbin amazon.com), value (password)
		# across this machine and the other machines
		def register(username, key, val):
			print('in server register function')
			print("Current username:", username)
			print("Current key:", key)

			user = key.split(' ')[0]

			if username != user:
				return 'no permissions to register password for this user'

			chunks = splitPassword(val, 4)

			# 'zbookbin amazon.com1', 'zbookbin amazon.com2', etc.
			put(key + '1', chunks[0]) # store chunk1 on this machine
			propagate(key, myPublicIP, 1) # tell other hosts about this
			
			# randomly shuffle which servers store which chunk numbers
			shuffledServerAddrs = list(otherServers.keys())
			random.shuffle(shuffledServerAddrs)

			print("trying to split up rest of password amongst other hosts")
			# shuffling through the other server connections and splitting up the current password 
			# amongst those servers, and propagating the update to each server as well
			storeChunksAndPropogate(shuffledServerAddrs, key, chunks, 2)

			# shift randomized list by 1 so no server stores the same chunk twice
			shuffledServerAddrs = shiftList(shuffledServerAddrs)

			print("redistributing password for replication")
			storeChunksAndPropogate(shuffledServerAddrs, key, chunks, 1)

			put(key + '4', chunks[3]) # store last chunk on this machine
			propagate(key, myPublicIP, 4) # tell other host that this machines stores a piece of the zbookin amazon.com entry

			print("password has been distributed twice. register job complete!")
			return 1

		def shiftList(shuffledServerAddrs):
			first = shuffledServerAddrs[0]
			shuffledServerAddrs = shuffledServerAddrs[1:] + [first]
			return shuffledServerAddrs

		def storeChunksAndPropogate(shuffledServerAddrs, key, chunks, count):
			for IPaddr in shuffledServerAddrs:
				# shuffling the IP addresses so that no machine stores the same order chunk
				connection = otherServers[IPaddr]
				print("current connection: ", IPaddr)
				connection.put(key+str(count), chunks[count-1])
				propagate(key, IPaddr, count)
				count+=1


		def splitPassword(password, n):
			output = []

			# could probably make this more efficient with if instead of while
			while (len(password) % n) != 0:
				password += ' '

			size = int(len(password)/n)

			start = 0
			end = size

			for start in range(0, len(password), size):
				output.append(password[start:start+size])

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
		def search(username, key):
			print("starting search...")

			user = key.split(' ')[0]

			if username != user:
				return 'no permissions to search for this password'

			if key not in userPasswordMap:
				return 'No record of key'

			print(f"getting all of the password pieces for the account: {key}")
			pieceNumToHost = userPasswordMap[key]
			pieces = ['' for i in range(len(pieceNumToHost.keys()))]

			# iterating through every password piece number and server host that is in charge of that
			# password piece
			print("collecting password pieces from all the relevant server hosts")
			for pieceNum, hostAddrs in pieceNumToHost.items():
				foundPiece = False
				hostAddr = 0
				
				while not foundPiece and hostAddr < len(hostAddrs):
				# password exists on local machine password map
				
					if hostAddrs[hostAddr] == myPublicIP:
						print("password piece found locally")
						pieces[pieceNum-1] = lookup(key + str(pieceNum))
						foundPiece = True
					# password exists on other server machines
					else:
						# find piece on other machine with RPC
						print("looking up password piece on other server host")
						connection = otherServers[hostAddrs[hostAddr]]
						lookupResult = connection.lookup(key + str(pieceNum))
						if lookupResult != -1:
							print("found password piece on other server host")
							pieces[pieceNum-1] = lookupResult
							foundPiece = True
						else:
							print(f'expected pieceNum {pieceNum} on {hostAddrs[hostAddr]} but no password piece was found!!!')

					hostAddr += 1

			return ''.join(pieces).strip()

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
					userPasswordMap[userSite][pieceNum] = [hostAddr] # machine that password chunk is stored on
				# otherwise, this password pairing exists in the map already, no updates needed
				else:
					userPasswordMap[userSite][pieceNum].append(hostAddr)
			
			# new user, create a new entry in the map
			else:
				# associate the password piece number with the server host node that it is sto
				userPasswordMap[userSite] = {pieceNum: [hostAddr]}


		# user = id + site, host = machine hostname, pieceNum = password piece number
		def propagate(user, host, pieceNum):
			"""
			
			"""
			print("updating local user-password map")
			addHost(user, host, pieceNum)

			print("sending update to other server nodes")
			for ip, connection in otherServers.items():
				print('current connnection CHECK THIS: ', ip, connection)
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
		
		print('about to serve forever')
		server.serve_forever()

		sys.stdout.close()


except Exception:
    print(traceback.format_exc())

