import xmlrpc.client

print("before client connection setup")

hosts = ['35.172.235.46', '44.199.229.51', '3.22.185.101', '18.191.134.62', '13.57.194.105', 
	'54.177.19.64', '34.222.143.244', '54.202.50.11', '13.245.182.179', '13.246.6.180', '18.166.176.112', 
	'16.162.137.92', '108.136.118.131', '108.136.41.214', '13.233.255.217', '15.206.211.195', '15.152.35.76',
	 '13.208.42.124', '13.125.213.112', '52.79.85.82', '18.136.203.66', '54.251.84.92', '3.104.66.60', 
	 '3.26.227.87', '18.183.60.155', '54.95.115.193', '3.99.158.136', '3.98.96.39', '3.122.191.72', 
	 '3.73.75.196', '34.244.200.204', '3.250.224.218', '18.130.129.70', '13.40.95.197', '15.160.192.179',
	  '15.160.153.56', '35.180.109.137', '35.180.39.12', '13.48.137.111', '13.48.3.201', '15.185.175.128', 
	  '157.175.185.52', '15.228.252.96', '15.229.0.10']

connectionMap = {}

for ip in hosts:
	ipString = 'http://' + ip + ':8012/'
	connectionMap[ip] = xmlrpc.client.ServerProxy(ipString)

print("setting up client connection to rpc servers ")

connectionMap['35.172.235.46'].register('zbookbin', 'zbookbin nike.com', 'hello1234')
print("password 1 registered")
connectionMap['15.229.0.10'].register('dlittle', 'dlittle amazon.com', 'uhoh789')
print("password 2 registered")

print("some local password data:")
print(connectionMap['35.172.235.46'].getLocalPasswordData())
print(connectionMap['15.229.0.10'].getLocalPasswordData())
print(connectionMap['18.183.60.155'].getLocalPasswordData())
print(connectionMap['15.160.192.179'].getLocalPasswordData())
print("\n\nsome userPasswordMaps:")
print('\n' + connectionMap['18.183.60.155'].getUserPasswordMap())
print('\n' + connectionMap['15.160.153.56'].getUserPasswordMap())
print('\n' + connectionMap['54.95.115.193'].getUserPasswordMap())

print("searching for first password (hello1234)")
print(connectionMap['54.95.115.193'].search('zbookbin', 'zbookbin nike.com'))
print("searching for nonexistant password")
print(connectionMap['13.246.6.180'].search('zbookbin', 'zbookbin amazon.com'))

# # Print list of available methods
print(connectionMap['16.162.137.92'].system.listMethods())
# storemap of user + site keys and password fragments