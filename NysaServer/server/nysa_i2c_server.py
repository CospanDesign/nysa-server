import os
import sys

import socket
import threading
import SocketServer
import json
import time
import Queue
from array import array as Array

from nysa.host.driver.i2c import I2C
import numpy as np
import cv2

DRIVER = I2C
NAME = "i2c"

from server_base import ServerBase

MAX_RECV_SIZE = 4096


class i2c_request_handler(SocketServer.BaseRequestHandler):
    commands = {}

    def setup(self):
        print "I2C TCP Request setup!"
        self.commands = {}
        self.commands["write"] = self.i2c_write
        self.commands["read"] = self.i2c_read

    def handle(self):
        print "I2C In listening thread handler..."
        data = self.request.recv(MAX_RECV_SIZE)
        cur_thread = threading.current_thread()
        request_dict = {}
        rd = {}
        response = ""
        try:
            request_dict = json.loads(data)
        except ValueError as e:
            rd["response"] = "error"
            rd["error"] = "{}: Error while parsing JSON String: %s".format(str(e))
            self.request.sendall(json.dumps(rd))
            return

        #Process request....
        print "request dict: %s" % str(request_dict)

        if "command" not in request_dict:
            rd["response"] = "error"
            rd["error"] = "%s not in commands" % request_dict["command"]
            self.request.sendall(json.dumps(rd))
            return

        rd = self.commands[request_dict["command"]](request_dict)
        for key in request_dict:
            if key not in rd:
                rd[key] = request_dict[key]
        print "Sending: %s" % json.dumps(rd)
        self.request.sendall(json.dumps(rd))

    def i2c_write(self, d):
        rd = d
        rd["response"] = "ok"
        return rd

    def i2c_read(self, d):
        rd = d
        rd["response"] = "ok"
        return rd

class NysaI2CServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer, ServerBase):

    @staticmethod
    def name():
        return NAME

    @staticmethod
    def get_request_handler():
        return i2c_request_handler

    def get_name(self):
        return NAME
 
    def setup(self, nysa):
        self.n = nysa
        self.n.read_sdb()
        self.urn = self.n.find_device(DRIVER)[0]
        self.i2c = I2C(self.n, self.urn)
        self.i2c.reset()


