import xmlrpc.client

print("before client connection setup")

s1 = xmlrpc.client.ServerProxy('http://52.90.4.149:8012/')
s2 = xmlrpc.client.ServerProxy('http://54.236.244.145:8012/')
s3 = xmlrpc.client.ServerProxy('http://54.211.164.149:8012/')
s4 = xmlrpc.client.ServerProxy('http://54.205.63.8:8012/')

print("setting up client connection to rpc servers ")

# s1.register('zbookbin', 'zbookbin nike.com', 'hello1234')
# s1.register('dlittle', 'dlittle amazon.com', 'uhoh789')

# s2.register('sbarker', 'sbarker gymshark.com', 'compscifun')
# s1.register('zbookbin', 'zbookbin google.com', 'secondpass5')
# s2.register('ahameed', 'ahameed bowdoin.edu', 'oops5678')

print(s1.getStoreMap())
print(s2.getStoreMap())
print(s3.getStoreMap())
print(s4.getStoreMap())

print(s1.search('zbookbin google.com'))
print(s1.search('zbookbin amazon.com'))


# # Print list of available methods
# print(s1.system.listMethods())
# storemap of user + site keys and password fragments


# {'zbookbin nike.com': {1: 'http://localhost:8000', 2: 'http://localhost:8001'}, 
# 'dlittle amazon.com': {1: 'http://localhost:8000', 2: 'http://localhost:8001'}, 
# 'sbarker gymshark.com': {1: 'http://localhost:8001', 2: 'http://localhost:8000'}, 
# 'zbookbin google.com': {1: 'http://localhost:8000', 2: 'http://localhost:8001'}, 
# 'ahameed bowdoin.edu': {1: 'http://localhost:8001', 2: 'http://localhost:8000'}}