import xmlrpc.client, sys


server

RPC methods:
1. Save password
	-update map
2. Retrieve password


hostname = sys.argv[1] # ip address of this server?
print(hostname)

server = xmlrpc.client.Server(hostname)

answer = server.FrontEndServer.search('romance')