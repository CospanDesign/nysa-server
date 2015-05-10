import socket
import threading
import SocketServer
import json
from server_base import ServerBase

MAX_RECV_SIZE = 4096
DEFAULT_CONTROL_PORT = 12591

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):

    commands = {}

    def setup(self):
        self.commands = {
            "shutdown":self.shutdown,
            "ping":self.ping,
            "start-server":self.server.start_sub_server,
            "list-servers":self.server.list_servers
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

    def list_servers(self, d):
        #XXX: Need a way to read the servers in the directory dynamically without requireing me to include them here... something with metaclass or with init should do this
        return server.list_servers(d)

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):

    def setup(self, nysa):
        self.n
        self.sub_servers = []

        from nysa_gpio_server import NysaGPIOServer
        script_list = ServerBase.plugins

        self.server_types = {}
        for s in script_list:
            self.server_types[s.name()] = s

    def start_sub_server(self, d):
        print "d: %s" % str(d)
        rd = {}
        rd["response"] = "ok"
        if d["type"] not in self.server_types:
            rd["response"] = "error"
            rd["error"] = "Server: %s does not exist" % d["type"]
            return rd

        if self.nysa is None:
            rd["response"] = "error"
            rd["error"] = "Nysa is None!"
            return rd

        port = 0
        if "port" in d:
            port = d["port"]

        server_type = self.server_types[d["type"]
        s = server_type(host = "localhost", port = port, nysa = self.n)
        ip, port = server.server_address

        #Put the server in the background
        server_thread = threading.Thread(target = server.serve_forever)

        server_thread.setDeamon()

        return rd

    def list_servers(self, d):
        server_list = self.server_types.keys()
        rd = {}
        rd["response"] = "ok"
        rd["value"] = server_list
        return rd


def start_control_server(host = "localhost", port = DEFAULT_CONTROL_PORT, nysa = None):
    server = ThreadedTCPServer((host, port), ThreadedTCPRequestHandler)
    server.setup(nysa)
    ip, port = server.server_address

    #Put the server in the background
    server_thread = threading.Thread(target = server.serve_forever)

    #Change to a daemon so the thread exit when the main thread exits
    server_thread.setDaemon()
    server_thread.start()

    print "Server thread branched off, running server in the background"
    return server

def shutdown_control_server(server):
    server.shutdown()
