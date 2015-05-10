import socket
import threading
import SocketServer
import json

from server_base import ServerBase

MAX_RECV_SIZE = 4096

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):

    def setup(self):
        self.commands = {
            "shutdown":self.shutdown,
            "ping":self.ping,
            "start-server":self.server.start_sub_server
        }

    def handle(self):
        print "In listening thread handler..."
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
        if "command" in request_dict:
            #print "Processing command"
            if request_dict["command"] not in self.commands:
                rd["response"] = "error"
                rd["error"] = "%s not in commands" % request_dict["command"]
                self.request.sendall(json.dumps(rd))
                return



        #response = "{}: {}".format(cur_thread.name, data)
        rd = self.commands[request_dict["command"]](request_dict)
        #rd["port"] = request_dict["port"]
        self.request.sendall(json.dumps(rd))

    def shutdown(self, d):
        rd = {}
        rd["response"] = "ok"
        return "ok"

    def ping(self, d):
        rd = {}
        rd["response"] = "ok"
        rd["value"] = "pong"
        return rd

class NysaGPIOServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer, ServerBase):

    @staticmethod
    def name():
        return "gpio"
    
    def setup(self, nysa):
        super (NysaGPIOServer, nysa)

def start_gpio_server(host = "localhost", port = None, nysa = None):
    server = NysaGPIOServer((host, port), ThreadedTCPRequestHandler)
    ip, port = server.server_address

    #Put the server in the background
    server_thread = threading.Thread(target = server.serve_forever)

    #Change to a daemon so the thread exit when the main thread exits
    server_thread.daemon = True
    server_thread.start()

    print "Server thread branched off, running server in the background"
    return server

def shutdown_gpio_server(server):
    server.shutdown()
