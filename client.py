import xmlrpc.client
import sys
import time
from constants import portno
import random

# Should we have the user connect to one machine?
# Should we add something telling the user where their password is stored?
# eventually move towards a smart client that knows which server is the best one to connect to

connection = None

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
	# myServer = '35.172.235.46'
	serverUrl = url_from_ip(myServer)
	connection = xmlrpc.client.ServerProxy(serverUrl)

	while(True):
		user = input("\nPlease enter your username to login: ")

		print("Thanks for logging in! Your username is " + user)
		print("Executable commands:\n  ->register/r [url] [password]\n  ->search/s   [url]\n  ->update/u   [url] [password]\n  ->delete/d   [url]\n  ->logout/l\n")

		while(True):
			parse = input("Enter your command: ").split(' ')
			if len(parse) == 1 and parse[0] == '':
				continue
			if len(parse) == 1 and (parse[0] == 'logout' or parse[0] == 'l'):
				user = ""
				break
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
	if len(password) < 4:
		return "Sorry! Passwords must be at least 4 characters long"
	userUrl = user + ' ' + url
	storedLocations = connection.register(user, userUrl, password)
	if type(storedLocations) == list:
		storedLocations = list(set(storedLocations))
		return "Success! Your password is stored in these places: " + str(storedLocations)
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

def url_from_ip(ip):
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
		url = url_from_ip(ip)
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