import xmlrpc.client

print("before client connection setup")

s1 = xmlrpc.client.ServerProxy('http://172.31.55.0:8012/')
s2 = xmlrpc.client.ServerProxy('http://172.31.53.196:8012/')
s3 = xmlrpc.client.ServerProxy('http://172.31.52.8:8012/')
s4 = xmlrpc.client.ServerProxy('http://172.31.53.249:8012/')

print("setting up client connection to rpc servers ")

s1.register('zbookbin', 'zbookbin nike.com', 'hello1234')
s1.register('dlittle', 'dlittle amazon.com', 'uhoh789')

s2.register('sbarker', 'sbarker gymshark.com', 'compscifun')
s1.register('zbookbin', 'zbookbin google.com', 'secondpass5')
s2.register('ahameed', 'ahameed bowdoin.edu', 'oops5678')

print(s1.getLocalPasswordData())
print(s2.getLocalPasswordData())
print(s3.getLocalPasswordData())
print(s4.getLocalPasswordData())
print("\n\nuserPW maps:")
print(s1.getUserPasswordMap())
print(s2.getUserPasswordMap())
print(s3.getUserPasswordMap())

print(s1.search('zbookbin', 'zbookbin google.com'))
print(s1.search('zbookbin', 'zbookbin amazon.com'))

print(s3.search('dlittle', 'dlittle amazon.com'))
print(s4.search('ahameed', 'ahameed bowdoin.edu'))

# # Print list of available methods
print(s1.system.listMethods())
# storemap of user + site keys and password fragments