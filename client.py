import xmlrpc.client
import sys
import time
from constants import hosts, portno, americasHosts, worldHosts, hostClusterMap, hostCountryMap
import random

# ALLOW CLIENT TO INPUT A FILENAME TO STORE PASSKEYS

connection = None
chunkCount = 4

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
		enteredValid = False
		user = None

		while not enteredValid:
			option = input("\nEnter L if you want to login or C to create a new account: ")

			if option == 'L':
				loggedIn = False

				while not loggedIn:
					user = input("\nPlease enter your username: ")
					masterPassword = input("\nPlease enter your GPS account password: ")
					if search(user, '__GPSpassword__') == masterPassword:
						print("Success! You're logged in as " + user + '\n')
						loggedIn = True
						enteredValid = True
					else:
						print("Incorrect username password, please try again")
					del masterPassword
			elif option == 'C':
				user = input("\nPlease enter your username: ")
				if search(user, '__GPSpassword__') != 'No record of key':
					print('There is already an account with this password')
				else:
					masterPassword = input("\nPlease enter your new GPS account password: ")
					result = register(user, '__GPSpassword__', masterPassword)
					del masterPassword

					if 'Success!' in result:
						print('Your GPS password is saved and you can now use it to login!\n')
						enteredValid = True
					else:
						print('GPS password storage failed')
			else:
				print("Invalid command, please try again")

		print("Thanks for logging in! Your username is " + user)
		print("Executable commands:\n  ->register/r [url] [password]\n  ->search/s   [url]")
		print("  ->update/u   [url] [password]\n  ->delete/d   [url]\n  ->chunk count/c    [num]\n  ->logout/l\n  ->quit/q\n")

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
				if url == '__GPSpassword__':
					print("Sorry, deleting your GPS password will make you unable to login.")
				else:
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
			elif command == 'chunk count' or command == 'c':
				updateChunkCount(url)

def register(user, url, password):
	global chunkCount
	start = time.perf_counter()

	if len(password) < chunkCount:
		return "Sorry! Passwords must be at least as long as chunkCount"
	userUrl = user + ' ' + url
	storedLocations = connection.register(user, userUrl, password, chunkCount)
	if type(storedLocations) == list:
		storedLocations = list(set(storedLocations))
		stop = time.perf_counter()
		return "Success! Your password is saved, and is being replicated to: " + str(storedLocations) + "\nThis operation took " + str(round(stop-start,2)) + " seconds"
	return "Failure! " + storedLocations

def search(user, url):
	userUrl = user + ' ' + url
	result = connection.search(user, userUrl)
	return result

def update(user, url, password):
	result = search(user, url)
	if result == 'No record of key':
		return 'No record of key. Can\'t update this password'
	print("Old password was " + result)
	if result == 'No permissions to search for this password' or result == 'No record of key':
		return result

	delete(user, url)

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

def updateChunkCount(c):
	global chunkCount
	if c.isdigit():
		if int(c) < 11 and int(c) > 1: 
			chunkCount = int(c)
			print("Registration chunk count is updated to " + str(chunkCount) + '\n')
		else:
			print("Chunk count must be between 2 and 10 (inclusive)")
	else:
		print("Chunk count must be a number")

if __name__ == "__main__":
	main()