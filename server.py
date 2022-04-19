import xmlrpc.client
import xmlrpc.server
from xmlrpc.server import SimpleXMLRPCRequestHandler
from xmlrpc.server import SimpleXMLRPCServer
import sys

passmap = {}
storemap = {}

if sys.argv[1] == '8000':
	otherHost = 'http://localhost:8001'
else:
	otherHost = 'http://localhost:8000'

s = xmlrpc.client.ServerProxy(otherHost)
myname = 'http://localhost:' + str(sys.argv[1])

# class RequestHandler(SimpleXMLRPCRequestHandler):
#     rpc_paths = ('/RPC2',)

#in with line: requestHandler=RequestHandler

with SimpleXMLRPCServer(('localhost', int(sys.argv[1])), allow_none=True) as server:
	
	server.register_introspection_functions()

	# registers a username (zbookbin), key (zbookbin amazon.com), value (password)
	# across this machine and the other machine
	def register(username, key, val):
		user = key.split(' ')[0]

		if username != user:
			return 'no permissions'

		site = key.split(' ')[1]

		chunk1 = val[0:len(val)//2] # password pieces
		chunk2 = val[len(val)//2:]

		put(key + '1', chunk1) # store chunk1 on this machine
		s.put(key + '2', chunk2) # store chunk2 on the other machine

		propogate(key, myname, 1) # tell other host that this machines stores a piece of the zbookin amazon.com entry
		propogate(key, otherHost, 2)  # tell other host that it stores a piece of the zbookin amazon.com entry

		return 1

	# put a (user + site), (password) pair into memory
	def put(key, val):
		passmap[key] = val
		return 1

	# return a password if stored (given a user + site)
	def lookup(key):
		if key in passmap:
			return passmap[key]

		return -1

	# collect the pieces of a password given user + site
	def search(key):

		if key not in storemap:
			return 'No record of key'

		machines = storemap[key]
		pieces = ['' for i in range(2)]

		for piece_num in machines:
			if machines[piece_num] == myname:
				pieces[piece_num-1] = lookup(key + str(piece_num))
			else:
				pieces[piece_num-1] = s.lookup(key + str(piece_num))

		return ''.join(pieces)

		
		
		# results = {}
		# for i in range(1,3): # how many pieces the password is in
		# 	newKey = key + str(i)
			
		# 	res = lookup(newKey) # check for this piece on this machine

		# 	if res != -1:
		# 		results[i] = res

		# 	res2 = s.lookup(newKey)

		# 	if res2 != -1:
		# 		results[i] = res2

		finalPassword = ''
		for i in range(1,3):
			if i not in results:
				return -1
			finalPassword += results[i]

		return finalPassword

	def getStoreMap():
		return str(storemap)

	def getPassMap():
		return str(passmap)

	def addHost(user, host, piece_num):
		if user in storemap:
			if piece_num not in storemap[user]:
				storemap[user][piece_num] = host # machine that password chunk is stored on
		else:
			storemap[user] = {piece_num: host}

	def propogate(user, host, piece_num):
		addHost(user, host, piece_num)
		s.addHost(user, host, piece_num)
			


	server.register_function(register)
	server.register_function(search)
	server.register_function(put)
	server.register_function(getStoreMap)
	server.register_function(getPassMap)
	server.register_function(addHost)
	server.register_function(propogate)
	server.register_function(lookup)
	server.serve_forever()