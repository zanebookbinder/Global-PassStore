import os
import traceback
import sys
import xmlrpc.client
import xmlrpc.server
from xmlrpc.server import SimpleXMLRPCRequestHandler
from xmlrpc.server import SimpleXMLRPCServer
import sys
import time


res = os.popen('ifconfig | grep inet | head -n 1').readline()
splitIP = res.split(' ')

count = 0
for s in splitIP:
    if s != '':
        count += 1

    if count == 2:
        myPrivateIP = s
        break

print(myPrivateIP)

with SimpleXMLRPCServer(('35.172.235.46', 8013)) as server:
    server.register_introspection_functions()

    def add(x, y):
        return x + y

    server.register_function(add)

    server.serve_forever()