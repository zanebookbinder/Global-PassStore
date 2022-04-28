import os
import traceback
import sys
import xmlrpc.client
import xmlrpc.server
from xmlrpc.server import SimpleXMLRPCRequestHandler
from xmlrpc.server import SimpleXMLRPCServer
import sys
import time


myPrivateIP = os.popen('ifconfig | grep inet | head -n 1').readline()

print(myPrivateIP.split(' '))

with SimpleXMLRPCServer(('172.31.70.66', 8013)) as server:
    server.register_introspection_functions()

    def add(x, y):
        return x + y

    server.register_function(add)

    server.serve_forever()