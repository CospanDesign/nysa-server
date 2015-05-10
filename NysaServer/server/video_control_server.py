import os
import sys

import socket
import threading
import SocketServer
import json
import time
import Queue
from array import array as Array

from nysa.host.driver.lcd_SSD1963 import LCDSSD1963
import numpy as np
import cv2
WIDTH = 480
HEIGHT = 272




from server_base import ServerBase

MAX_RECV_SIZE = 4096

class video_control_request_handler(SocketServer.BaseRequestHandler):
    commands = {}

    def setup(self):
        print "VideoControl TCP Request setup!"
        self.commands = {}
        self.commands["play"] = self.server.play
        self.commands["stop"] = self.server.stop
        self.commands["picture"] = self.display_picture
        self.commands["status"] = self.server.status

    def handle(self):
        print "VideoControl In listening thread handler..."
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

    def display_picture(self, d):
        rd = d
        rd["response"] = "ok"
        size = d["size"]

        data = self.request.recv(MAX_RECV_SIZE)
        return rd

class NysaVideoControlServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer, ServerBase):

    started = False

    @staticmethod
    def name():
        return "video_control"

    @staticmethod
    def get_request_handler():
        return video_control_request_handler

    def get_name(self):
        return "video_control"
 
    def play(self, d):
        if self.video_worker is None:
            self.video_worker = VideoWorkerThread(self.lcd,
                                                  self.hwq,
                                                  self.hrq)
            self.video_worker.setDaemon(True)
            self.video_worker.start()

        self.hwq.put(d)
        rd = self.hrq.get()
        return rd

    def stop(self, d):
        rd = d
        if self.video_worker is not None:
            self.hwq.put(d)
            rd = self.hrq.get()
            self.video_worker = None
        else:
            rd["response"] = "error"
            rd["error"] = "Video is not playing"
        return rd

    def status(self, d):
        rd = d
        rd["response"] = "ok"
        value = None
        while (1):
            try:
                value = self.hrq.get(block = False)

            except Queue.Empty:
                if value == None:
                    rd["response"] = "ok"
                    rd["status"] = "nothing going on"
                else:
                    rd["response"] = "ok"
                    rd["status"] = value
        return rd
   
    def setup(self, nysa):
        if NysaVideoControlServer.started:
            self.stop({})

        NysaVideoControlServer.started = True
        self.n = nysa
        self.n.read_sdb()
        self.hwq = Queue.Queue(10)
        self.hrq = Queue.Queue(10)
        self.urn = self.n.find_device(LCDSSD1963)[0]
        self.video_worker = None
        print "Found a VideoControl device: %s" % self.urn
        self.lcd = LCDSSD1963(self.n, self.urn)
        print "setup video_controls"
        self.lcd.setup()

class VideoWorkerThread(threading.Thread):
    def __init__(self,
                 driver,
                 host_write_queue,
                 host_read_queue):
        super(VideoWorkerThread, self).__init__()
        self.lcd = driver
        self.host_write_queue = host_write_queue
        self.host_read_queue = host_read_queue
        self.state = "waiting"

    def run(self):
        video_capture = None
        while (1):
            if self.state == "waiting":
                rd = {}
                video_capture = None
                try:
                    command = self.host_write_queue.get(block = True)
                except Queue.Empty:
                    print "Queue is empty exiting"
                    return

                print "command: %s" % str(command)

                #d = json.loads(command)
                d = command
                if d["command"] == "play":
                    self.state = d["command"]
                    if "file" not in d:
                        print "No File specified running big buck bunny"
                        d["file"] = "/home/edison/bbb.avi"
                    filename = d["file"]
                    if not os.path.exists(filename):
                        rd["response"] = "error"
                        rd["error"] = "File: %s does not exists" % d["file"]

                try:
                    video_capture = cv2.VideoCapture()
                    video_capture.open(d["file"])
                except:
                    print "Error while openening: %s" % d["file"]
                    rd["response"] = "error"
                    rd["error"] = "Open CV Failed to open file: %s does not exists" % d["file"]
                   
                rd = d
                rd["response"] = "ok"
                print "Play the video"
                self.host_read_queue.put(rd)
            else:
                try:
                    command = self.host_write_queue.get(block = False)
                    print "Video Worker Thread User Requested something..."
                    #d = json.loads(command)
                    d = command
                    rd = d
                    rd["response"] = "ok"
                    if (d["command"] == "stop") or (d["command"] == "close"):
                        print "\tstopping"
                        self.state == "waiting"
                        self.host_read_queue.put(rd)
                        return

                except Queue.Empty:
                    pass

                ret, frame = video_capture.read()
                if ret == False:
                    print "Video Worker Thread... Go back to waiting"
                    self.state = "waiting"
                    rd["response"] = "ok"
                    rd["value"] = "finished"
                    continue
                
                frame = cv2.resize(frame, dsize = (WIDTH, HEIGHT))
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGRA)
                data = Array('B', frame.tostring())
                self.lcd.dma_writer.write(data)


                

