"""
Program Description: Distributed password manager server that stores and manages various usernames,
websites, and 

TODO:
	1. Make a better scheme for replicating (cluster-based) --> store first version on local cluster, replicas anywhere
	2. Add username security (don't allow user to access someone else's data)
	3. Remove all constants so serverCount is the only thing that knows how many servers we have
	4. Make number of chunks customizable easily with global variable
	5. Handle failures and joining
"""

import os
import traceback
import sys
import xmlrpc.client
import xmlrpc.server
from xmlrpc.server import SimpleXMLRPCRequestHandler
from xmlrpc.server import SimpleXMLRPCServer
from constants import hosts, portno, americasHosts, worldHosts, hostClusterMap, hostCountryMap
import sys
import math
import random
import time
import threading

print(hosts)

ids = {}

for i, host in enumerate(hosts):
	ids[host] = i

americasHosts = ['35.172.235.46', '44.199.229.51', '3.22.185.101', '18.191.134.62', '13.57.194.105',
'54.177.19.64', '34.222.143.244', '54.202.50.11', '3.99.158.136', '3.98.96.39', '15.228.252.96',
'15.229.0.10']

worldHosts = ['13.245.182.179', '13.246.6.180','18.166.176.112', '16.162.137.92', '108.136.118.131',
'108.136.41.214', '13.233.255.217', '15.206.211.195','15.152.35.76', '13.208.42.124', '13.125.213.112',
'52.79.85.82', '18.136.203.66', '54.251.84.92','3.104.66.60', '3.26.227.87', '18.183.60.155',
'54.95.115.193', '3.122.191.72', '3.73.75.196','34.244.200.204', '3.250.224.218', '18.130.129.70',
'13.40.95.197', '15.160.192.179', '15.160.153.56','35.180.109.137', '35.180.39.12', '13.48.137.111',
'13.48.3.201', '15.185.175.128', '157.175.185.52']

hostClusterMap = {
	'americas': americasHosts,
	'rest-of-world': worldHosts
}

hostCountryMap = {'35.172.235.46': 'Virginia', '44.199.229.51': 'Virginia',
'3.22.185.101': 'Ohio','18.191.134.62': 'Ohio','13.57.194.105': 'California',
'54.177.19.64': 'California','34.222.143.244': 'Oregon','54.202.50.11': 'Oregon',
'13.245.182.179': 'Cape Town','13.246.6.180': 'Cape Town','18.166.176.112': 'Hong Kong',
'16.162.137.92': 'Hong Kong','108.136.118.131': 'Jakarta','108.136.41.214': 'Jakarta',
'13.233.255.217': 'Mumbai','15.206.211.195': 'Mumbai','15.152.35.76': 'Osaka',
'13.208.42.124': 'Osaka','13.125.213.112': 'Seoul','52.79.85.82': 'Seoul',
'18.136.203.66': 'Singapore','54.251.84.92': 'Singapore','3.104.66.60': 'Sydney',
'3.26.227.87': 'Sydney','18.183.60.155': 'Tokyo','54.95.115.193': 'Tokyo',
'3.99.158.136': 'Canada','3.98.96.39': 'Canada','3.122.191.72': 'Frankfurt',
'3.73.75.196': 'Frankfurt','34.244.200.204': 'Ireland','3.250.224.218': 'Ireland',
'18.130.129.70': 'London','13.40.95.197': 'London','15.160.192.179': 'Milan',
'15.160.153.56': 'Milan','35.180.109.137': 'Paris','35.180.39.12': 'Paris',
'13.48.137.111': 'Stockholm','13.48.3.201': 'Stockholm','15.185.175.128': 'Bahrain',
'157.175.185.52': 'Bahrain','15.228.252.96': 'Sao Paulo','15.229.0.10': 'Sao Paulo'}

otherHosts = hosts.copy()

localPasswordData = {}
userPasswordMap = {}
otherServers = {}

myPrivateIP = myPublicIP = myCluster = ""

def getCluster(ip):
	for key, clusterList in hostClusterMap.items():
		if ip in clusterList:
			return key

def register(username, key, val, numChunks=4):
	"""
	registers a username, key, value across this and other
	machines. Only called via RPC from client program.
	@params:
		username: e.g. zbookbin
		key: combination of username and url, e.g. 'zbookbin amazon.com
		value: password to store
	"""
	print('in server register function')
	print("Current username:", username)
	print("Current key:", key)

	if numChunks > len(val):
		print("Too few chunks for this length password!")
		return "Not enough chunks for this length password"

	user = key.split(' ')[0]
	if username != user:
		return 'no permissions to register password for this user'

	# if new user tries to register but it already exists in our map, they must use the update command 
	if search(username, key) != 'No record of key':
		return "You already have a password for this site! Use the update command to override it."

	chunks = split_evenly(val, numChunks)
	chunkStorageList = []
	
	# list of servers that chunks can be stored on
	shuffledServerAddrs = list(otherServers.keys())

	print("trying to split up password amongst other hosts")
	# shuffling through the other server connections and splitting up the current password 
	# amongst those servers, and propagating the update to each server as well
	storedLocations, newShuffledServerAddrs = storeChunks(shuffledServerAddrs, key, chunkStorageList, chunks)
	# newShuffledServerAddrs stores the list of hosts that don't already have a piece of the passsword

	print("redistributing password for replication")
	replicationStoredLocations, newShuffledServerAddrs = storeChunks(newShuffledServerAddrs, key, chunkStorageList, chunks)
	storedLocations.extend(replicationStoredLocations) # stored locations contains the places the password is stored

	# propagate message out to nodes in my cluster
	print(f"Propagating to other nodes in my cluster: {myCluster}")
	otherHostsInCluster = hostClusterMap[myCluster].copy()
	otherHostsInCluster.remove(myPublicIP)


	threads = []
	# threads.append(threading.Thread(target = propagate, args = (key, chunkStorageList, otherHostsInCluster,)))
	threads.append([propagate, key, chunkStorageList, otherHostsInCluster])

	propagate(key, chunkStorageList, otherHostsInCluster)
	
	# tell nodes in other clusters to propagate the message to their respective neighbor nodes
	print("Local propagation complete. Now, telling one node in all other cluster to propagate to their cluster")
	otherClusters = hostClusterMap.copy()
	otherClusters.pop(myCluster)
	for ipList in list(otherClusters.values()):
		# pick one node randomly in each other cluster
		randNodeIP = random.choice(ipList)
		randNodeCluster = getCluster(randNodeIP)
		randNodeOtherHosts = hostClusterMap[randNodeCluster].copy()
		randNodeOtherHosts.remove(randNodeIP)
		
		# tell that random other node to propagate update to its own cluster
		threads.append([otherServers[randNodeIP].propagate, key, chunkStorageList, randNodeOtherHosts])
		print(f"Telling node: {ids[randNodeIP]} at cluster {randNodeCluster} to update their cluster")

	runThreads(threads)
	
	print("password has been distributed twice. register job complete!")
	return storedLocations

def storeChunks(shuffledServerAddrs, key, chunkStorageList, chunks):
	"""
	store 
	"""
	numChunks = len(chunks)
	newShuffledServerAddrs = shuffledServerAddrs
	storedLocations = []
	randomHosts = random.sample(shuffledServerAddrs, numChunks)

	chunkCount = 1
	for randomHost in randomHosts:
		connection = otherServers[randomHost]
		print("current connection: id=", ids[randomHost])
		connection.put(key+str(chunkCount), chunks[chunkCount-1])
		chunkStorageList.append([randomHost, chunkCount])
		storedLocations.append(hostCountryMap[randomHost])
		newShuffledServerAddrs.remove(randomHost)
		chunkCount+=1

	return storedLocations, newShuffledServerAddrs


# LOCAL helper method 
def split_evenly(a, n):
	"""
	Splits a list or string evenly into n chunks. 
	Returns a list of those chunks.
	"""
	n = min(n, len(a))
	q, r = divmod(len(a), n)

	chunks = []
	for i in range(n):
		start = i*q + min(i, r)
		end = (i+1)*q + min(i+1, r)
		chunks.append(a[start:end])
	return chunks


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

	# finalPassword = ''
	# for i in range(1,3):
	# 	if i not in results:
	# 		return -1
	# 	finalPassword += results[i]

	# return finalPassword

def getUserPasswordMap():
	return str(userPasswordMap)

def getLocalPasswordData():
	return str(localPasswordData)

# LOCAL method, no outgoing RPCs to other servers
def addHosts(userSite, chunkStorageList):
	"""
	Update this node's userPasswordMap to include the new piece/server mappings.
	@params:
		userSite (str): combination of a username and website
		chunkStorageList: updated mapping of which servers the chunks of this password are stored on.
	"""
	# NOTE: potential update - change map structure so that sites are their own dictionary nested
	for hostToChunk in chunkStorageList:
		hostAddr = hostToChunk[0]
		pieceNum = hostToChunk[1]
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
# REMOTE method, makes outgoing RPC calls to other servers
def propagate(user, chunkStorageList, hosts=hosts):
	"""
	Informs other hosts of updated password chunk mapping to servers
	"""

	print("updating local user-password map")
	addHosts(user, chunkStorageList)

	print("sending update to other server nodes")
	num_threads = 4
	hosts_split = split_evenly(hosts, num_threads)
	print('hosts_split:', hosts_split)
	propagateOps = []
	for i in range(num_threads):
		propagateOps.append([propagateThread, user, hosts_split[i], chunkStorageList])

	runThreads(propagateOps)

def propagateThread(user, hostsList, chunkStorageList):
	print('propogating to new hostsList')
	for ip in hostsList:
		otherServers[ip].addHosts(user, chunkStorageList)

def getPrivateIP():
	global myPrivateIP
	myPrivateIP = '0.0.0.0'
	res = os.popen('/sbin/ifconfig | grep inet | head -n 1').readline()
	splitIP = res.split(' ')

	count = 0
	for s in splitIP:
		if s != '':
			count += 1

		if count == 2:
			myPrivateIP = s
			break

	return myPrivateIP

def removePiece(key):
	print("in remove piece with key: " + str(key))
	if key not in localPasswordData:
		print("returning -1")
		return -1

	del localPasswordData[key]
	print("returning 1")
	return 1


def delete(username, key):
	print("starting delete...")

	user = key.split(' ')[0]

	if username != user:
		return 'no permissions to delete this password'

	if key not in userPasswordMap:
		return 'No record of key'

	print("getting all of the password pieces for the account: " + str(key))
	pieceNumToHost = userPasswordMap[key] # {1: [35.4523.42, 12.45.66], 2: [456.5434, 45.682.3943], 3: [35.4523.42, 12.45.66], 4: [456.5434, 45.682.3943]}
	pieces = ['' for i in range(len(pieceNumToHost.keys()))]

	# iterating through every password piece number and server host that is in charge of that
	# password piece
	for pieceNum, hostAddrs in pieceNumToHost.items():
		for hostAddr in hostAddrs:
			print('deleting piece ' + str(pieceNum) + ' from host ' + str(hostAddr))

			if hostAddr == myPublicIP:
				print("password piece found locally")
				removePiece(key + str(pieceNum))
			# password exists on other server machines
			else:
				# find piece on other machine with RPC
				print("password piece found remotely")
				connection = otherServers[hostAddr]
				removeResult = connection.removePiece(key + str(pieceNum))

	deletePropogation(username, key)

	return "Successful deletion!"

def deletePasswordData(key):
	if key not in userPasswordMap:
		return -1

	del userPasswordMap[key]
	return 1

def deletePropogation(user, key):
	print("deleting " + str(key) + "from all user-password maps")
	deletePasswordData(key)

	print("sending deletion update to other server nodes")
	num_threads = 4
	hosts_split = split_evenly(hosts, num_threads)
	print('hosts_split:', hosts_split)
	deleteOps = []
	for i in range(num_threads):
		deleteOps.append([propagateDeletionThread, key, hosts_split[i]])

	runThreads(deleteOps)

def propagateDeletionThread(key, hostsList):
	print('propogating to new hostsList')
	for ip in hostsList:
		otherServers[ip].deletePasswordData(key)

def runThreads(routines):
	""" Takes in a list of 'routines', which should be structured as a list
	containing the thread entrypoint, followed by the arguments. E.g. [myFunc, 1, 2]
	The threads are then run concurrently, and the function returns when all finish.
	"""
	threads = []
	for routine in routines:
		entry, *arguments = routine
		threads.append(threading.Thread(target=entry,args=(arguments)))

	for t in threads:
		t.start()
    
	for t in threads:
		t.join()

### Client Connection Methods ###

def ping():
	""" Simple ping method to time RPCs in order to figure out which server would be 
		best suited to serve a client
	"""
	return

def updateMyCluster(myClusterName, message):
	""" Given a message such as a new client registration, this method will update all the 
	nodes in its cluster of that new registration.
	
	"""
	
	message()
	return 0


def main():
	global myPrivateIP
	global myPublicIP
	global myCluster

	try:
		sys.stdout = open('outputServer.log', 'w') # print statements go to this file
		sys.stdout.reconfigure(line_buffering=True)

		t = time.localtime()
		current_time = time.strftime("%H:%M:%S", t)
		print("Running at:", current_time)

		myPublicIP = os.popen('curl -s ifconfig.me').readline()
		myPrivateIP = getPrivateIP()
		myCluster = getCluster(myPublicIP)

		serverCount = len(hosts)
		
		print("my (public) IP addr: ", myPublicIP)
		print("my (private) IP addr: ", myPrivateIP)
		print("my port num: ", portno)

		otherHosts.remove(myPublicIP)

		time.sleep(3) # I think we should make this longer since it'll only happen on startup

		for IPaddr in hosts:
			if IPaddr != myPublicIP:
				fullHostname = f'http://{IPaddr}:{portno}/'
				otherServers[IPaddr] = xmlrpc.client.ServerProxy(fullHostname)

		print("Connected to other hosts")

		with SimpleXMLRPCServer((myPrivateIP, portno), allow_none=True) as server:
			server.register_introspection_functions()
			server.register_function(register)
			server.register_function(search)
			server.register_function(put)
			server.register_function(getUserPasswordMap)
			server.register_function(getLocalPasswordData)
			server.register_function(addHosts)
			server.register_function(propagate)
			server.register_function(lookup)
			server.register_function(split_evenly)
			server.register_function(removePiece)
			server.register_function(delete)
			server.register_function(deletePasswordData)
			server.register_function(ping)
			
			print('about to serve forever')
			server.serve_forever()

	except Exception:
		print(traceback.format_exc())

if __name__ == "__main__":
	main()