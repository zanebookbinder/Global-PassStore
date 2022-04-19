import xmlrpc.client

s1 = xmlrpc.client.ServerProxy('http://localhost:8000')
s2 = xmlrpc.client.ServerProxy('http://localhost:8001')

s1.register('zbookbin', 'zbookbin nike.com', 'hello1234')
s1.register('dlittle', 'dlittle amazon.com', 'uhoh789')

s2.register('sbarker', 'sbarker gymshark.com', 'compscifun')
s1.register('zbookbin', 'zbookbin google.com', 'secondpass5')
s2.register('ahameed', 'ahameed bowdoin.edu', 'oops5678')

print(s1.getStoreMap())
print(s2.getStoreMap())

print(s1.search('zbookbin google.com'))
print(s1.search('zbookbin amazon.com'))



# # Print list of available methods
# print(s1.system.listMethods())