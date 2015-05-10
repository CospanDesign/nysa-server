
import unittest
import json
import sys
import os
import time
import socket
import threading
import SocketServer
from array import array as Array

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir))

from NysaServer.server import control_server

from nysa.common import status
from nysa.host import platform_scanner



def command_client(ip, port, command, args = {}):
    request = {}
    request["command"] = command
    for d in args:
        request[d] = args[d]
    message = json.dumps(request)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    response = ""
    try:
        sock.sendall(message)
        response = sock.recv(1024)
    finally:
        sock.close()
    return response

class Test (unittest.TestCase):

    def setUp(self):
        pass

    '''
    def test_start_server(self):
        print "Test start server"
        server = control_server.start_control_server_async()
        ip, port = server.server_address
        command_client(ip, port, "ping")

        control_server.shutdown_control_server(server)
    '''

    def test_start_sub_server(self):
        s = status.Status()
        s.set_level("verbose")
    
        s.Info("Find Nysa Device")
        nysa = platform_scanner.get_platforms(s)[0]

        server = control_server.start_control_server_async(nysa = nysa)
        ip, port = server.server_address
        command_client(ip, port, "ping")


        server_command = {}
        server_command["type"] = "video"
        server_command["args"] = {}
        server_command["args"]["height"] = 272
        server_command["args"]["width"] = 480
        server_command["args"]["fourcc"] = "RGBA"
        response = command_client(ip, port, "start-server", server_command)
        print "Response: %s" % str(response)
        response = command_client(ip, port, "list-servers")
        print "Response: %s" % str(response)

        server_command = {}
        server_command["type"] = "gpio"

        response = command_client(ip, port, "start-server", server_command)
        print "Response: %s" % str(response)

        control_server.shutdown_control_server(server)
