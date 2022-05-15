"""
Program Description: Distributed password manager server that stores and manages various usernames,
websites, and 

TODO:
	1. Add username security (don't allow user to access someone else's data)
	2. Remove all constants so serverCount is the only thing that knows how many servers we have
	3. Make number of chunks customizable easily with global variable
	4. Handle failures and joining
	5. Make update/register synchronized on one key
"""

from ast import arguments
import os
import traceback
import sys
import xmlrpc.client
import xmlrpc.server
from xmlrpc.server import SimpleXMLRPCRequestHandler
from xmlrpc.server import SimpleXMLRPCServer
from socketserver import ThreadingMixIn
from constants import hosts, portno, hostClusterMap, hostCountryMap
import math
import random
import time
import threading
import string

class AsyncXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer): pass

localPasswordData = {}
userPasswordMap = {}
otherServers = {}

serverActive = True

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

	if numChunks > len(val):
		print("Too few chunks for this length password!")
		return "Not enough chunks for this length password"

	user = key.split(' ')[0]
	if username != user:
		return 'no permissions to register password for this user'

	# if new user tries to register but it already exists in our map, they must use the update command 
	# if search(username, key) != 'No record of key':
	# 	return "You already have a password for this site! Use the update command to override it."

	chunks = split_evenly(val, numChunks)
	chunkStorageList = []
	
	print('start of register')
	otherNodesInCluster = hostClusterMap[myCluster].copy()
	otherNodesInCluster.remove(myPublicIP)

	print(f'Attemtping to store password for key: {key} to local cluster')
	localChunkStorageList = storeChunks(otherNodesInCluster, key, chunks)

	otherClusters = hostClusterMap.copy()
	otherClusters.pop(myCluster)
	replicationCluster = random.choice(list(otherClusters))
	print(f'Attemtping to replicate password for key: {key} to other cluster: {replicationCluster}')
	replicationNodes = otherClusters[replicationCluster]
	replicationChunkStorageList = storeChunks(replicationNodes, key, chunks)

	print(f"Propagating key " + key + " to other nodes in my cluster: {myCluster}")
	chunkStorageList = localChunkStorageList + replicationChunkStorageList
	propagate(key, chunkStorageList, otherNodesInCluster)
	print("Local propagation complete. Now, telling one node in all other cluster to propagate key " + key + " to their cluster")
	print('end of register')

	globalPropagateThread = threading.Thread(target=propagateToOtherClusters, args=(chunkStorageList, key))
	globalPropagateThread.start()
	print(f'Replicate threads started, returning from register method to client. {username}, {key}')
	return [hostCountryMap[host] for host, _ in replicationChunkStorageList]

def propagateToOtherClusters(chunkStorageList, key):
	print(f'Running propagateToOtherClusters funciton, for key: {key}')
	threads = []
	
	otherClusters = hostClusterMap.copy()
	otherClusters.pop(myCluster)
	connections = []
	for i, ipList in enumerate(list(otherClusters.values())):
		# pick one node randomly in each other cluster
		randNodeIP = random.choice(ipList)
		randNodeCluster = getCluster(randNodeIP)
		randNodeOtherHosts = hostClusterMap[randNodeCluster].copy()
		randNodeOtherHosts.remove(randNodeIP)

		connections[i] = xmlrpc.client.ServerProxy(urlFromIp(randNodeIP))
		
		# tell that random other node to propagate update to its own cluster
		threads.append([connections[i].propagate, key, chunkStorageList, randNodeOtherHosts])
		print(f"Telling node: {randNodeIP} at cluster {randNodeCluster} to update their cluster about key " + key)

	runThreads(threads)
	del connections
	
	print("password for key " + key + " has been distributed twice. register job complete!")
	return

def storeChunks(storageServers, key, chunks):
	"""
	store 
	"""
	numChunks = len(chunks)
	chunkStorageList = []
	randomHosts = random.sample(storageServers, numChunks)

	chunkCount = 1
	for ip in randomHosts:
		# connection = xmlrpc.client.ServerProxy(urlFromIp(randomHost))
		# print("current connection for key " + key + " : ip=", randomHost)
		# connection.put(key+str(chunkCount), chunks[chunkCount-1])
		safe_rpc(ip, put, key+str(chunkCount), chunks[chunkCount-1])
		chunkStorageList.append([ip, chunkCount])
		chunkCount+=1

	return chunkStorageList


# user = id + site, host = machine hostname, pieceNum = password piece number
# REMOTE method, makes outgoing RPC calls to other servers
def propagate(user, chunkStorageList, hosts):
	"""
	Informs other hosts of updated password chunk mapping to servers.
	Runs in threads, where each thread will propagate the userPWmap
	by calling a remote server's addHosts() function. 
	"""

	addHosts(user, chunkStorageList)

	print(f'in propagate method, propagating to hosts {hosts}, chunkStorageList {chunkStorageList}')
	for ip in hosts:
		# connection = xmlrpc.client.ServerProxy(urlFromIp(ip))
		# connection.addHosts(user, chunkStorageList)
		safe_rpc(ip, addHosts, user, chunkStorageList)

	# num_threads = 4
	# hosts_split = split_evenly(hosts, num_threads)
	# propagateOps = []
	# for i in range(num_threads):
	# 	propagateOps.append([propagateHelper, user, hosts_split[i], chunkStorageList])

	# runThreads(propagateOps)

def propagateHelper(user, ipList, chunkStorageList):
	print(f'running addHosts on ip {ipList}')
	for ip in ipList:
		# connection = xmlrpc.client.ServerProxy(urlFromIp(ip))
		# connection.addHosts(user, chunkStorageList)
		# del connection
		safe_rpc(ip, addHosts, user, chunkStorageList)

# LOCAL helper method 
def split_evenly(a, n):
	"""
	Splits a list or string evenly (if possible) into n chunks. 
	Returns a list of those chunks. If given a list/string with length
	smaller than n, the returned list will be of length len(a).
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
	print("Now storing " + val + " at key " + key)
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
				try:
					# connection = xmlrpc.client.ServerProxy('http://' + hostAddrs[hostAddr] + ':' + str(portno) + '/')
					# lookupResult = connection.lookup(key + str(pieceNum))
					# del connection
					lookupResult = safe_rpc(hostAddr[hostAddr], lookup, key + str(pieceNum))
					if lookupResult != -1:
						print("found password piece on other server host")
						pieces[pieceNum-1] = lookupResult
						foundPiece = True
					else:
						print(f'expected pieceNum {pieceNum} on {hostAddrs[hostAddr]} but no password piece was found!!!')
				except:
					print('server' + hostAddrs[hostAddr] + ' unavailable')

			hostAddr += 1

	return ''.join(pieces).strip()

def getUserPasswordMap():
	return str(userPasswordMap)

def getUserPasswordMapLength():
	return str(len(list(userPasswordMap.keys())))

def getLocalPasswordData():
	return str(localPasswordData)

# LOCAL method, no outgoing RPCs to other servers
def addHosts(userSite, chunkStorageList):
	"""
	Update this node's userPasswordMap to include the new piece/server mappings.
	@params:
		userSite (str): username and website, separated with a space
		chunkStorageList: updated list of tuples: (serverIP, pieceNumber)
	"""
	print(f'running addHosts locally, with key {userSite} and chunk list {chunkStorageList}')
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
				# connection = xmlrpc.client.ServerProxy(urlFromIp(hostAddr))
				# removeResult = connection.removePiece(key + str(pieceNum))
				# del connection
				safe_rpc(hostAddr, removePiece, key + str(pieceNum))

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
	deleteOps = []
	for i in range(num_threads):
		deleteOps.append([propagateDeletionThread, key, hosts_split[i]])

	runThreads(deleteOps)

def propagateDeletionThread(key, hostsList):
	print('propogating to new hostsList')
	for ip in hostsList:
		# connection = xmlrpc.client.ServerProxy(urlFromIp(ip))
		# connection.deletePasswordData(key)
		safe_rpc(ip, deletePasswordData, key)

		# otherServers[ip].deletePasswordData(key)

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

def urlFromIp(ip):
	""" Makes a full URL out of an IP address.
	"""
	return f'http://{ip}:{portno}/'

def startup():
	global myPublicIP
	global hostClusterMap
	global hostCountryMap
	global hosts
	# 1. pick 10 nodes in each cluster, time connections to them
	print('startup: making RPCs to 10 nodes in each cluster')
	clusterTimeMap = dict.fromkeys(list(hostClusterMap.keys()), [])
	for cluster, clusterHosts in hostClusterMap.items():
		timingHosts = random.sample(clusterHosts, min(10, len(clusterHosts)))
		for ip in timingHosts:
			# connection = xmlrpc.client.ServerProxy(urlFromIp(ip))
			start = time.perf_counter()
			safe_rpc(ip, ping)
			# connection.ping()
			stop = time.perf_counter()
			# del connection
			clusterTimeMap[cluster].append(stop - start)
	
	# 2. Pick the cluster with the shortest average time
	print('startup: picking cluster with shortest rpc time')
	minTime = float('inf')
	bestCluster = 'americas'
	for cluster, times in clusterTimeMap.items():
		currTime = sum(times)/len(times)
		if currTime < minTime:
			minTime = currTime
			bestCluster = cluster
	
	# 3. tell all other servers about new server
	print(f'startup: picked cluster {bestCluster}, telling all servers to addNewHost')
	for ip in hosts:
		# connection = xmlrpc.client.ServerProxy(urlFromIp(ip))
		# connection.addNewHost(myPublicIP, bestCluster)
		# del connection
		safe_rpc(ip, addNewHost, myPublicIP, bestCluster)

	hosts.append(myPublicIP)
	hostClusterMap[bestCluster].append(myPublicIP)
	hostCountryMap[myPublicIP] = 'Unknown'

	print('my ip in hosts? ', myPublicIP in hosts)
	print('startup successful')

def removeHost(ip):
	try:
		hosts.remove(ip)
		for clusterHosts in hostClusterMap.values():
			if ip in clusterHosts:
				clusterHosts.remove(ip)
	except:
		print(f'trying to remove ip {ip}, but it was already not in list of hosts.')

def addNewHost(host, cluster):
	hosts.append(host)
	hostClusterMap[cluster].append(host)
	print(f'adding new host {host} to cluster {cluster}')

### Client Connection Methods ###

def ping(ret=None):
	""" Simple ping method to time RPCs in order to figure out which server would be 
		best suited to serve a client
	"""
	return

def testNPasswordsStored(n):
	letters = string.ascii_lowercase
	chunk1 = 'may1'
	chunk2 = '4th'
	if myPublicIP == '3.98.96.39':

		for i in range(n):
			url = 'url' + str(i)
			userUrl = 'zbookbin ' + url + '1'
			put(userUrl, chunk1)			
			userPasswordMap[userUrl] = {1:['3.98.96.39'], 2:['3.99.158.136']}

	if myPublicIP == '3.99.158.136':
		
		for i in range(n):
			url = 'url' + str(i)
			userUrl = 'zbookbin ' + url + '2'
			put(userUrl, chunk2)			
			userPasswordMap[userUrl] = {1:['3.98.96.39'], 2:['3.99.158.136']}

def safe_rpc(ip, fn, *args):
	try:
		connection = xmlrpc.client.ServerProxy(urlFromIp(ip))
		result = connection.fn(*args)
		del connection
		return result
	except ConnectionRefusedError:
		handle_dead_host(ip)

def handle_dead_host(ip):
	pass

def kill():
	global serverActive

	print('Killing server now. Goodbye!')
	serverActive = False
	# server.shutdown()
	# exit(0)
	return 1

def main():
	global myPrivateIP
	global myPublicIP
	global myCluster
	global serverActive

	try:
		sys.stdout = open('outputServer.log', 'w') # print statements go to this file
		sys.stdout.reconfigure(line_buffering=True)

		t = time.localtime()
		current_time = time.strftime("%H:%M:%S", t)
		print("Running at:", current_time)

		myPublicIP = os.popen('curl -s ifconfig.me').readline()
		myPrivateIP = getPrivateIP()
		myCluster = getCluster(myPublicIP)

		if len(sys.argv) > 1 and sys.argv[1] == 'startup':
			startup()

		print("my (public) IP addr: ", myPublicIP)
		print("my (private) IP addr: ", myPrivateIP)
		print("my port num: ", portno)

		with AsyncXMLRPCServer((myPrivateIP, portno), allow_none=True) as server:

			# def quit():
			# 	server._BaseServer__shutdown_request = True
			# 	server.shutdown()
			# 	exit(0)

			server.register_introspection_functions()
			server.register_function(register)
			server.register_function(search)
			server.register_function(put)
			server.register_function(getUserPasswordMap)
			server.register_function(getUserPasswordMapLength)
			server.register_function(getLocalPasswordData)
			server.register_function(addHosts)
			server.register_function(propagate)
			server.register_function(lookup)
			server.register_function(split_evenly)
			server.register_function(removePiece)
			server.register_function(delete)
			server.register_function(deletePasswordData)
			server.register_function(ping)
			server.register_function(kill)
			server.register_function(addNewHost)
			
			print('about to serve forever')
			while(serverActive):
				# server.serve_forever()
				server.handle_request()

			print("shutting down server")

			exit(0)

	except Exception:
		print(traceback.format_exc())

if __name__ == "__main__":
	main()