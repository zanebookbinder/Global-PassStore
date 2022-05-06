import xmlrpc.client
import sys
import time
from constants import hosts, portno, americasHosts, worldHosts, hostClusterMap, hostCountryMap
import random

# ALLOW CLIENT TO INPUT A FILENAME TO STORE PASSKEYS

connection = None

def main():
	global connection

	print("~ Welcome to the PassStore.com: The most secure and reliable password storage system! ~\n")

	clusterHosts = []
	while(len(clusterHosts) == 0):
		region = input("\nPlease enter your region from the following choices:\n  Americas (A) \n  World (W) \n \nEnter here: ")
		clusterHosts = selectCluster(region, hostClusterMap)

	print("One moment while we connect you to the closest server...")
	myServer, pingTime = intelligently_pick_server(clusterHosts)
	print('You\'re connected to server ' + str(myServer) + ' located in ' + hostCountryMap[myServer] + ' with a ping of ' + str(round(pingTime, 3)) + ' seconds')

	serverUrl = urlFromIp(myServer)
	connection = xmlrpc.client.ServerProxy(serverUrl)

	while(True):
		user = input("\nPlease enter your username to login: ")

		print("Thanks for logging in! Your username is " + user)
		print("Executable commands:\n  ->register/r [url] [password]\n  ->search/s   [url]")
		print("  ->update/u   [url] [password]\n  ->delete/d   [url]\n  ->logout/l\n  ->quit/q\n")

		while(True):
			parse = input("Enter your command: ").split(' ')
			if len(parse) == 1 and parse[0] == '':
				continue
			if len(parse) == 1 and (parse[0] == 'logout' or parse[0] == 'l'):
				user = ""
				break
			if len(parse) == 1 and (parse[0] == 'quit' or parse[0] == 'q'):
				exit(0)
			if len(parse) < 2:
				print("Must include correct arguments starting with 'register', 'search', or 'update\'")
				continue
			command = parse[0]
			url = parse[1]
			if command == 'search' or command == 's':
				print('Password for ' + url + ' is: ' + search(user, url) + '\n')
			elif command == 'delete' or command == 'd':
				print("One second while we delete your password chunks stored around the globe...")
				print(delete(user, url) + '\n')
			elif command == 'register' or command == 'r':
				if len(parse) < 3:
					print("Must include three arguments for a register operation\n")
					continue

				print("One second while we register your password around the globe...")
				password = parse[2]
				result = register(user, url, password)
				print(result + '\n')
			elif command == 'update' or command == 'u':
				if len(parse) < 3:
					print("Must include three arguments for a register operation\n")
					continue
				print("One second while we update your password...")
				password = parse[2]
				result = update(user, url, password)
				print(result)

def register(user, url, password):
	start = time.perf_counter()

	if len(password) < 4:
		return "Sorry! Passwords must be at least 4 characters long"
	userUrl = user + ' ' + url
	storedLocations = connection.register(user, userUrl, password)
	if type(storedLocations) == list:
		storedLocations = list(set(storedLocations))
		stop = time.perf_counter()
		return "Success! Your password is stored in these places: " + str(storedLocations) + "\nThis operation took " + str(round(stop-start,2)) + " seconds"
	return "Failure! " + storedLocations

def search(user, url):
	userUrl = user + ' ' + url
	result = connection.search(user, userUrl)
	return result

def update(user, url, password):
	result = search(user, url)
	print("Old password was " + result)
	if result == 'No permissions to search for this password' or result == 'No record of key':
		return result

	return register(user, url, password)

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