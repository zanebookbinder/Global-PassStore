import xmlrpc.client
import sys
import time
from constants import hosts, portno, hostClusterMap
import random
import string
import threading
from multiprocessing import Process
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures.process import ProcessPoolExecutor

connection = None
letters = string.ascii_lowercase
serverUrl = ''

def main():
	global connection, serverUrl
	serverUrl = urlFromIp('3.98.96.39')

	connection = xmlrpc.client.ServerProxy(serverUrl)

	# test1()
	# test2()
	# test3()
	# test4()

def test1():
	global registerCounter
	print("Test 1: num clients vs. register time")

	threadCounts = [1, 5, 10, 20, 50]
	repititions = 2

	for t in threadCounts:
		print("Testing with " + str(t) + " clients")

		threads = []
		for i in range(t):
			threads.append([testRegisterTime, 'zbookbin', repititions, 4])

		start = time.perf_counter()
		runThreads(threads)
		stop = time.perf_counter()
		print("TIME FOR " + str(t) + " CLIENT IS: " + str(round((stop-start) / repititions, 3)))
	
	time.sleep(10)
	totalPW = sum(threadCounts) * repititions
	print(f'We should now have {totalPW} passwords registered. how many do we have?')
	newConn = xmlrpc.client.ServerProxy(urlFromIp('18.130.129.70'))
	print(newConn.getUserPasswordMapLength())


def test2():
	print("Test 2: Node failures vs percentage of successful searches")

	with open('websites.txt') as file:
		lines = file.readlines()
		lines = [line.rstrip() for line in lines]
		lines = [line for line in lines if not line == '']
	
	for i, url in enumerate(lines):
		threadConnection = xmlrpc.client.ServerProxy(serverUrl)
		register('zbookbin', url, 'mypassword5', 2)

	killedServers = 0

	allHosts = hosts.copy()
	allHosts.remove('3.98.96.39')

	while killedServers < 28:
		failed = 0
		for url in lines:
			result = []
			try:
				result.append(search('zbookbin', url))
				result.append(search('zbookbin', url))
				if type(result[1]) != str:
					failed+=1
				elif result[1] != 'mypassword5':
					failed+=1
			except:
				failed+=1

		print('with ' + str(killedServers) + ' servers killed, failed searches (of 100): ' + str(failed))
		killedServers+=2
	
		s1 = random.choice(allHosts)
		allHosts.remove(s1)
		url1 = urlFromIp(s1)

		s2 = random.choice(allHosts)
		allHosts.remove(s2)
		url2 = urlFromIp(s2)

		print('shutting down', s1, s2)
		killConnection = xmlrpc.client.ServerProxy(url1)
		killConnection.kill()

		killConnection = xmlrpc.client.ServerProxy(url2)
		killConnection.kill()

def test3():
	print("Test 3: Number of passwords stored in GPS vs. search time")

	urls = []
	for i in range(1000000):
		urls.append('url' + str(i))

	for _ in range(3):
		print(testSearchTime('zbookbin', 50, urls))

def test4():
	print("Test 4: Password chunk count vs. registration time")

	chunkCounts = [2, 3, 4, 5, 6, 7, 8, 9, 10]
	for c in chunkCounts:
		threadConnection = xmlrpc.client.ServerProxy(serverUrl)
		print("testing average registration time with " + str(c) + " chunks")
		print(testRegisterTime('zbookbin', 2, c))

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

	for t in threads:
		t.join()

def testRegisterTime(user, repetitions, numChunks):
	password = "hello12345"

	start = time.perf_counter()
	for q in range(repetitions):
		url = ''.join(random.choice(letters) for i in range(5)) + f'-t{threading.get_ident()}'
		register(user, url, password, numChunks)
	stop = time.perf_counter()

	return round((stop - start) / repetitions, 3)

def testSearchTime(user, repetitions, urls):

	start = time.perf_counter()
	for _ in range(repetitions):
		url = random.choice(urls)
		search(user, url)
	stop = time.perf_counter()

	print("TOTAL: ", str(round(stop-start,3)))
	return (stop - start) / repetitions

def register(user, url, password, numChunks):
	start = time.perf_counter()

	if len(password) < numChunks:
		return "Sorry! Passwords must be at least as long as numChunks"
	userUrl = user + ' ' + url
	threadConnection = xmlrpc.client.ServerProxy(serverUrl)

	storedLocations = threadConnection.register(user, userUrl, password, numChunks)
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