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

print(s1.getPasswordData())
print(s2.getPasswordData())
print(s3.getPasswordData())
print(s4.getPasswordData())

print(s1.search('zbookbin google.com'))
print(s1.search('zbookbin amazon.com'))


# # Print list of available methods
print(s1.system.listMethods())
# storemap of user + site keys and password fragments


# {'zbookbin nike.com': {1: 'http://localhost:8000', 2: 'http://localhost:8001'}, 
# 'dlittle amazon.com': {1: 'http://localhost:8000', 2: 'http://localhost:8001'}, 
# 'sbarker gymshark.com': {1: 'http://localhost:8001', 2: 'http://localhost:8000'}, 
# 'zbookbin google.com': {1: 'http://localhost:8000', 2: 'http://localhost:8001'}, 
# 'ahameed bowdoin.edu': {1: 'http://localhost:8001', 2: 'http://localhost:8000'}}