import xmlrpc.client
import sys
import time
from constants import hosts, portno, americasHosts, worldHosts, hostClusterMap, hostCountryMap
import random
import string
import threading
from multiprocessing import Process
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures.process import ProcessPoolExecutor

connection = None
letters = string.ascii_lowercase
serverUrl = 'http://3.98.96.39:8062/'

def main():
	global connection, serverUrl

	connection = xmlrpc.client.ServerProxy(serverUrl)

	test1(connection)

def test1(connection):
	print("Test 1: num clients vs. register time") # should we do this on random servers or the same server?

	# threadCounts = [1, 5, 10, 20, 50]
	# threadCounts = [2]

	# for t in threadCounts:
		# print("Testing with " + str(t) + " clients")
	testRegisterTime('zbookbin', 3, 4, connection, 0)
	# threads = []
	# for i in range(3):
	# 	thisConnection = xmlrpc.client.ServerProxy(serverUrl)
		# threads.append([testRegisterTime, 'zbookbin', 2, 4, serverUrl, i])

	# runThreads(threads)


def test2():
	print("Test 2: Node failures vs percentage of successful searches")
	# idk how we do this one

def test3():
	print("Test 3: Number of passwords stored in GPS vs. search time")

	passwordCounts = [1, 9, 90, 900] # 1, 10, 100, 1000 total passwords
	urls = []

	for p in passwordCounts:
		print("Testing search time with " + str(p) + ' passwords stored')
		for _ in range(p):
			url = ''.join(random.choice(letters) for i in range(15))
			urls.append(url)
			password = "hello12345"
			register('zbookbin', url, password, 4, connection)

		print(testSearchTime('zbookbin', 5, urls))


def test4():
	print("Test 4: Password chunk count vs. registration time")

	chunkCounts = [2, 3, 4, 5, 6, 7, 8, 9, 10]

	for c in chunkCounts:
		print("testing average registration time with " + str(c) + " chunks")
		print(testRegisterTime('zbookbin', 5, c, connection))


# register 5 passwords with either of these chunk Counts and find the average time
# need to make split a parameter for server.register

	
# threads = []
# for _ in range(50):
# 	threads.append([testRegisterTime, 'zbookbin', ])

# runThreads(threads)

#register(user, url, password)
#search (user, url)
#update (user, url, password)
#delete(ursr, url)

def runThreads(routines):
	""" Takes in a list of 'routines', which should be structured as a list
	containing the thread entrypoint, followed by the arguments. E.g. [myFunc, 1, 2]
	The threads are then run concurrently, and the function returns when all finish.
	"""
	threads = []
	for routine in routines:
		entry, *arguments = routine
		threads.append(threading.Thread(target=entry, args=(arguments)))
	
	for t in threads:
		t.start()

def testRegisterTime(user, repetitions, numChunks, connection, i):
	password = "hello12345"

	# ran = random.choice(hosts)
	# thisUrl = "http://" + ran + ":8062/"

	start = time.perf_counter()
	for q in range(repetitions):
		print(q)
		url = ''.join(random.choice(letters) for i in range(15))
		register(user, url, password, numChunks, connection, i)
	stop = time.perf_counter()

	return round((stop - start) / repetitions, 3)

def testSearchTime(user, repetitions, urls):

	start = time.perf_counter()
	for _ in range(repetitions):
		url = random.choice(urls)
		search(user, url)
	stop = time.perf_counter()

	return (stop - start) / repetitions


def register(user, url, password, numChunks, thisConnection, i):
	start = time.perf_counter()

	if len(password) < numChunks:
		return "Sorry! Passwords must be at least as long as numChunks"
	userUrl = user + ' ' + url
	
	print("Register:", user, url, password, numChunks, thisConnection)


	myConnection = xmlrpc.client.ServerProxy(serverUrl)

	storedLocations = myConnection.register(user, userUrl, password, numChunks)
	print("Done with register:", user, url, password, numChunks, myConnection)
	if type(storedLocations) == list:
		storedLocations = list(set(storedLocations))
		stop = time.perf_counter()
		return "Success! Your password is stored in these places: " + str(storedLocations) + "\nThis operation took " + str(round(stop-start,2)) + " seconds"
	return "Failure! " + str(storedLocations)

def search(user, url):
	userUrl = user + ' ' + url
	result = connection.search(user, userUrl)
	return result

def update(user, url, password):
	result = search(user, url)
	print("Old password was " + result)
	if result == 'No permissions to search for this password' or result == 'No record of key':
		return result

	return register(user, url, password, 4, connection)

def delete(user, url):
	userUrl = user + ' ' + url
	return connection.delete(user, userUrl)

def urlFromIp(ip):
	""" Makes a full URL out of an IP address.
	"""
	return f'http://{ip}:{portno}/'

def time_server(ip):
	connection = xmlrpc.client.ServerProxy(ip)
	start = time.perf_counter()
	connection.ping()
	stop = time.perf_counter()

	return stop - start

def intelligently_pick_server(myCluster):
	curBestTime = 100
	curBestServer = myCluster[0]

	for ip in random.sample(myCluster[1:], 10):
		url = urlFromIp(ip)
		time = time_server(url)
		if time < curBestTime:
			curBestTime = time
			curBestServer = ip

	return curBestServer, curBestTime

def selectCluster(region, hostClusterMap):
	if region in ['Americas', 'A']:
		return hostClusterMap['americas']
	if region in ['World', 'W']:
		return hostClusterMap['rest-of-world']
	else:
		print("Invalid cluster!")
		return []

if __name__ == "__main__":
	main()