import xmlrpc.client

s = xmlrpc.client.ServerProxy('http://172.31.70.66:8013')
print(s.add(2,3))

print(s.system.listMethods())