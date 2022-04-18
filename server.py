import xmlrpc.client
import xmlrpc.server
from xmlrpc.server import SimpleXMLRPCRequestHandler
from xmlrpc.server import SimpleXMLRPCServer
import sys

passmap = {}
storemap = {}

if sys.argv[1] == '8000':
	host = 'http://localhost:8001'
else:
	host = 'http://localhost:8000'

s = xmlrpc.client.ServerProxy(host)
myname = 'http://localhost:' + str(sys.argv[1])

# class RequestHandler(SimpleXMLRPCRequestHandler):
#     rpc_paths = ('/RPC2',)

#in with line: requestHandler=RequestHandler

with SimpleXMLRPCServer(('localhost', int(sys.argv[1])), allow_none=True) as server:
	
	server.register_introspection_functions()

	def register(username, key, val):
		user = key.split(' ')[0]

		if username != user:
			return 'no permissions'

		site = key.split(' ')[1]

		chunk1 = val[0:len(val)//2]
		chunk2 = val[len(val)//2+1:]

		put(key + '1', chunk1)
		s.put(key + '2', chunk2)

		propogate(key, myname)
		propogate(key, host)

		return 1

	def put(key, val):
		passmap[key] = val
		return 1

	def search(key):
		if key in passmap:
			return passmap[key]
		return -1

	def p():
		#return str(passmap), str(storemap)
		return str(storemap)

	def addHost(user, host):
		if user in storemap:
			if host not in storemap[user]:
				storemap[user].append(host) # machine that password is stored on
		else:
			storemap[user] = [host]

	def propogate(user, host):
		addHost(user, host)
		s.addHost(user, host)
			


	server.register_function(register)
	server.register_function(search)
	server.register_function(put)
	server.register_function(p)
	server.register_function(addHost)
	server.register_function(propogate)
	server.serve_forever()