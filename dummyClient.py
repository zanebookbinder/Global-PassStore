import xmlrpc.client

s = xmlrpc.client.ServerProxy('http://35.172.235.46:8013')
print(s.add(2,3))

print(s.system.listMethods())