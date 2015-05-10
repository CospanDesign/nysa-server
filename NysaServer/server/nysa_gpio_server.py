import socket
import threading
import SocketServer
import json
import time

from nysa.host.driver.gpio import GPIO

from server_base import ServerBase

MAX_RECV_SIZE = 4096

class gpio_request_handler(SocketServer.BaseRequestHandler):
    commands = {}

    def setup(self):
        print "GPIO TCP Request setup!"
        self.commands = {}
        self.commands["set_direction"] = self.set_direction
        self.commands["set_value"] = self.set_value
        self.commands["get_value"] = self.get_value
        self.commands["setup_interrupt"] = self.setup_interrupt

    def handle(self):
        print "GPIO In listening thread handler..."
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

    def set_direction(self, d):
        rd = {}
        rd["response"] = "ok"
        print "setting direction"
        if "pin" not in d:
            rd["response"] = "error"
            rd["error"] = "pin entry not in request"
            return rd

        if "direction" not in d:
            rd["response"] = "error"
            rd["error"] = "direction entry not in request"
            return rd


        if isinstance(d["pin"], list):
            if not isinstance(rd["direction"], list):
                rd["response"] = "error"
                rd["error"] = "pin is a list and direction is not a list"
                return rd

            if len(d["direction"]) != len(d["pin"]):
                rd["response"] = "error"
                rd["error"] = "pin is a list and direction is not a list"
                return rd
               
            for i in range(len(d["pin"])):
                self.server.gpio.set_pin_direction(d["pin"][i], d["direction"][i])

        else:
            pin = d["pin"]
            direction = d["direction"]
            self.server.gpio.set_pin_direction(d["pin"], d["direction"])
        
        return d

    def set_value(self, d):
        rd = {}
        print "set value"
        rd["response"] = "ok"
        print "setting value"
        if "pin" not in d:
            rd["response"] = "error"
            rd["error"] = "pin entry not in request"
            return rd

        if "value" not in d:
            rd["response"] = "error"
            rd["error"] = "value entry not in request"
            return rd


        if isinstance(d["pin"], list):
            if not isinstance(d["value"], list):
                rd["response"] = "error"
                rd["error"] = "pin is a list and value is not a list"
                return rd

            if len(d["value"]) != len(d["pin"]):
                rd["response"] = "error"
                rd["error"] = "pin is a list and value is not a list"
                return rd
               
            for i in range(len(d["pin"])):
                self.server.gpio.set_bit_value(d["pin"][i], d["value"][i])

        else:
            pin = d["pin"]
            value = d["value"]
            self.server.gpio.set_bit_value(d["pin"], d["value"])
        
        return rd

    def get_value(self, d):
        rd = {}
        rd["response"] = "ok"
        print "get value"
        values = []
        if "pin" not in rd:
            d["pin"] = [2, 3]
            #XXX: Fix to simplify interface for hackathon
            #rd["response"] = "error"
            #rd["error"] = "pin entry not in request"
            #return rd

        if isinstance(d["pin"], list):
            for p in d["pin"]:
                values.append(self.server.gpio.get_bit_value(p))

        else:
            values = self.server.gpio.get_bit_value(p)

        rd["value"] = values
        return rd

    def setup_interrupt(self, d):
        print "setup interrupt"
        rd = {}
        rd["response"] = "ok"
        print "setting interrupt"
        if "pin" not in d:
            rd["response"] = "error"
            rd["error"] = "pin entry not in request"
            return rd

        if "interrupt" not in d:
            rd["response"] = "error"
            rd["error"] = "interrupt entry not in request"
            return rd


        if isinstance(d["pin"], list):
            if not isinstance(d["interrupt"], list):
                rd["response"] = "error"
                rd["error"] = "pin is a list and interrupt is not a list"
                return rd

            if len(d["interrupt"]) != len(d["pin"]):
                rd["response"] = "error"
                rd["error"] = "pin is a list and interrupt is not a list"
                return rd
               
            for i in range(len(d["pin"])):
                self.server.gpio.set_interrupt_both_edge(d["pin"][i], d["interrupt"][i])

        else:
            pin = d["pin"]
            interrupt = d["interrupt"]
            self.server.gpio.set_bit_interrupt_both_edge(d["pin"], d["interrupt"])
        
        return rd

    def interrupt_callback(self, callback):
        rd = {}
        rd["response"] = "ok"
        print "GPIO Interrupt callback!"
        return rd


class NysaGPIOServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer, ServerBase):

    @staticmethod
    def name():
        return "gpio"

    @staticmethod
    def get_request_handler():
        return gpio_request_handler

    def get_name(self):
        return "gpio"
    
    def setup(self, nysa):
        self.n = nysa
        self.n.read_sdb()
        self.urn = self.n.find_device(GPIO)[0]
        print "Found a GPIO device: %s" % self.urn
        self.gpio = GPIO(self.n, self.urn)
        self.gpio.set_port_direction(0x00000003)
        self.gpio.set_port_raw(0x00000003)
        time.sleep(0.100)
        self.gpio.set_port_raw(0x00000000)
        print "setup gpios"

