import xmlrpc.client
import sys

# Should we have the user connect to one machine?
# Should we add something telling the user where their password is stored?
myServer = '35.172.235.46'
ipString = 'http://' + myServer + ':8061/'
connection = xmlrpc.client.ServerProxy(ipString)

def main():
	print("~ Welcome to the PassStore.com: The most secure and reliable password storage system! ~\n")
	user = input("Please enter your username to login: ")

	print("Thanks for logging in! Your username is " + user)
	print("Executable commands:\n ->register [url] [password]\n ->search [url]\n ->update [url] [password]\n")

	while(True):
		parse = input("Enter your command: ").split(' ')
		if len(parse) < 2:
			print("Must include correct arguments starting with 'register', 'search', or 'update\'")
			continue
		command = parse[0]
		url = parse[1]
		if command == 'search':
			print('Password for ' + url + ' is: ' + search(user, url) + '\n')
		elif command == 'register':
			if len(parse) < 3:
				print("Must include three arguments for a register operation")

			print("One second while we register your password around the globe...")
			password = parse[2]
			result = register(user, url, password)
			print(result)
		elif command == 'update':
			if len(parse) < 3:
				print("Must include three arguments for a register operation")
			print("One second while we update your password...")
			password = parse[2]
			result = update(user, url, password)
			print(result)


def register(user, url, password):
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


if __name__ == "__main__":
	main()