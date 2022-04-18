import xmlrpc.client

s1 = xmlrpc.client.ServerProxy('http://localhost:8000')
s2 = xmlrpc.client.ServerProxy('http://localhost:8001')

print(s1.register('zbookbin', 'zbookbin nike.com', 'hello1234'))
print(s1.register('dlittle', 'dlittle amazon.com', 'uhoh789'))

print(s2.register('sbarker', 'sbarker gymshark.com', 'compscifun'))
print(s1.register('zbookbin', 'zbookbin google.com', 'secondpass5'))
print(s2.register('ahameed', 'ahameed bowdoin.edu', 'oops5678'))

print(s1.p())
print(s2.p())

# print(s1.search(2))
# print(s1.search(3))


# # Print list of available methods
# print(s1.system.listMethods())