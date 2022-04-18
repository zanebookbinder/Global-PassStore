import xmlrpc.client
import xmlrpc.server
from xmlrpc.server import SimpleXMLRPCRequestHandler
from xmlrpc.server import SimpleXMLRPCServer
import sys

# server

# RPC methods:
# 1. Save password
# 	-update map
# 2. Retrieve password

m = {}

class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

with SimpleXMLRPCServer(('localhost', 8001), requestHandler=RequestHandler, allow_none=True) as server:
	
	server.register_introspection_functions()

	def register(key, val):
		m[key] = val
		return 1

	def search(key):
		if key in m:
			return m[key]
		return -1

	server.register_function(register)
	server.register_function(search)
	server.serve_forever()