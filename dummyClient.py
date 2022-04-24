import xmlrpc.client

s = xmlrpc.client.ServerProxy('http://52.90.4.149:8000')
print(s.add(2,3))

print(s.system.listMethods())