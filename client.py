import xmlrpc.client

#client


s = xmlrpc.client.ServerProxy('http://localhost:8001')
print(s.register(1, 35))
print(s.register(2, 27))

print(s.search(2))
print(s.search(3))


# Print list of available methods
print(s.system.listMethods())