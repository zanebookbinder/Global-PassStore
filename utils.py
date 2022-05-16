import sys
import xmlrpc.client
from constants import portno

def main():
	ip = sys.argv[1]
	connection = xmlrpc.client.ServerProxy(urlFromIp(ip))
	print("Available commands:")
	while(True):
		print("- 'upm' -> view userPasswordMap")
		print("- 'len' -> view number of passwords stored in the system")
		print("- 'pws' -> view local password data for the connected server")
		parse = input("Enter a command. > ")
		print()
		if parse == 'upm':
			print(connection.getUserPasswordMap())
		elif parse == 'len':
			print(connection.getUserPasswordMapLength())
		elif parse == 'pws':
			print(connection.getLocalPasswordData())
		print()


def urlFromIp(ip):
	""" Makes a full URL out of an IP address.
	"""
	return f'http://{ip}:{portno}/'
if __name__ == '__main__':
	main()