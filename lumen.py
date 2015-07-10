#!/usr/bin/python

import sys
import socket
import os
import json
import signal
import select
import time
from time import sleep
from btle import Peripheral, BTLEException

SERVER_SOCKET = "/tmp/lumen_socket"
BULB = "7C:66:9D:7D:38:16"

#def connect():
  #from gattlib import GATTRequester
  
  #class Requester(GATTRequester):
    #def on_notification(self, handle, data):
        #print("- notification on handle: {}\n".format(handle))
        
  #global req;
  #if req == None:
    #bulb = "7C:66:9D:7D:38:16"
    #req = Requester(bulb)
    #req.write_by_handle(0x25, str(bytearray( [0x08, 0x61, 0x07, 0x66, 0xa7, 0x68, 0x0f, 0x5a, 0x18, 0x3e, 0x5e, 0x7a, 0x3e, 0x3c, 0xbe, 0xaa, 0x8a, 0x21, 0x4b, 0x6b] )))
    #connect.data1 = req.read_by_handle(0x28)
    #req.write_by_handle(0x25, str(bytearray( [0x07, 0xdf, 0xd9, 0x9b, 0xfd, 0xdd, 0x54, 0x5a, 0x18, 0x3e, 0x5e, 0x7a, 0x3e, 0x3c, 0xbe, 0xaa, 0x8a, 0x21, 0x4b, 0x6b] )))
    #connect.data2 = req.read_by_handle(0x28)
  #return req

def is_server_running():
  return os.path.exists(SERVER_SOCKET)

class Server:
  req = None
  class BTconnect:
    chars = {}
    def __init__(self):
      try:
        self.p = Peripheral(BULB)
        characteristics = self.p.getCharacteristics()
        for c in characteristics:
          self.chars[c.getHandle()] = c
      except BTLEException as e:
        print str(e)
      
    def read_by_handle(self, handle):
      return self.chars[handle].read()
    
    def write_by_handle(self, handle, data):
      self.chars[handle].write(data, True)

  def connect(self):
    if self.req == None:
      self.req = self.BTconnect()
      self.req.write_by_handle(0x25, str(bytearray( [0x08, 0x61, 0x07, 0x66, 0xa7, 0x68, 0x0f, 0x5a, 0x18, 0x3e, 0x5e, 0x7a, 0x3e, 0x3c, 0xbe, 0xaa, 0x8a, 0x21, 0x4b, 0x6b] )))
      self.data1 = bytearray(self.req.read_by_handle(0x28))
      self.req.write_by_handle(0x25, str(bytearray( [0x07, 0xdf, 0xd9, 0x9b, 0xfd, 0xdd, 0x54, 0x5a, 0x18, 0x3e, 0x5e, 0x7a, 0x3e, 0x3c, 0xbe, 0xaa, 0x8a, 0x21, 0x4b, 0x6b] )))
      self.data2 = bytearray(self.req.read_by_handle(0x28))
    return self.req
    
  def battery(self):
    #from gattlib import GATTResponse
    
    #class notify(GATTResponse):
    #  def on_response(self, data):
    #      print("notify: {}".format(data))
    #battery.notify = notify()
    #connect().read_by_handle_async(0x36, battery.notify)
    batt = self.connect().read_by_handle(0x36)
    return batt

  def devicename(self):
    name = self.connect().read_by_handle(0x03)
    print(name)

  def status(self):
    status = self.connect().read_by_handle(0x25)
    print(status)

  def off(self):
    self.data1[0] = 0x00
    self.connect().write_by_handle(0x25, str(self.data1))

  def on(self):
    self.data1[0] = 0x01
    self.data1[4] = 0xb5
    self.connect().write_by_handle(0x25, str(self.data1))

  def cool(self):
    self.data1[0] = 0x01
    self.data1[6] = 0x50
    self.connect().write_by_handle(0x25, str(self.data1))

  def warm(self):
    self.data1[0] = 0x01
    self.data1[6] = 0x51
    self.connect().write_by_handle(0x25, str(self.data1))

  def disco1(self):
    self.data1[0] = 0x01
    self.data1[6] = 0x52
    self.connect().write_by_handle(0x25, str(self.data1))

  def disco2(self):
    self.data1[0] = 0x01
    self.data1[6] = 0x53
    self.connect().write_by_handle(0x25, str(self.data1))

  def normal(self):
    self.data1[0] = 0x01
    self.data1[6] = 0x54
    self.connect().write_by_handle(0x25, str(self.data1))

  def warm_white(self, n):
    self.data1[0] = 0x01
    self.data1[1] = 0xdf
    self.data1[6] = 0x54
    n = float(n)
    if n >= 100:
      self.data1[2] = 0xd9
      self.data1[3] = 0x9a
      self.data1[4] = 0x58
    elif n >= 90:
      self.data1[2] = 0xd9
      self.data1[3] = 0x9b
      self.data1[4] = 0xa3
    elif n >= 70:
      self.data1[2] = 0xd9
      self.data1[3] = 0x9b
      self.data1[4] = 0xb5
    elif n >= 50:
      self.data1[2] = 0xd9
      self.data1[3] = 0x9b
      self.data1[4] = 0x87
    elif n >= 30:
      self.data1[2] = 0xd9
      self.data1[3] = 0x9b
      self.data1[4] = 0x99
    else:
      self.data1[2] = 0xd9
      self.data1[3] = 0x9b
      self.data1[4] = 0xf2
    self.connect().write_by_handle(0x25, str(self.data1))
      
  def white(self):
    self.warm_white(100)
    
  def color(self, r, g, b):
    self.data1[0] = 0x01
    self.data1[6] = 0x54
    _r = float(r) / 255;
    _g = float(g) / 255;
    _b = float(b) / 255;
    k = 1 - max(_r, _g, _b)
    c = (1 - _r - k) / (1 - k)
    m = (1 - _g - k) / (1 - k)
    y = (1 - _b - k) / (1 - k)
    self.data1[1] = int(round(c * 105) + 120)
    self.data1[2] = int(round(m * 105) + 120)
    self.data1[3] = int(round(y * 105) + 120)
    self.data1[4] = int(round((1 - k) * 15) + 240)
    self.connect().write_by_handle(0x25, str(self.data1))

  def restart(self):
    print("restart")
    #print(sys.argv[0], sys.argv)
    self.restart = True
    
  def ping(self):
    self.battery()
      
  def server(self):
    
    self.alive = True
    def handler(sig, frame):
      if sig == signal.SIGTERM:
        alive = False
        print("Kill server")
        os.remove(SERVER_SOCKET)
        sys.exit(0)
    
    signal.signal(signal.SIGTERM, handler)

    print("Start server")
    self.battery()
    
    lastping = time.time()
    
    sock = socket.socket( socket.AF_UNIX, socket.SOCK_DGRAM )
    sock.setblocking(0)
    try:
      umask_ = os.umask(0000); 
      sock.bind(SERVER_SOCKET)
      os.umask(umask_);
      while self.alive and not self.restart:
        
        #ping
        if time.time() - lastping >= 5:
          lastping = time.time()
          self.ping()
          
        #get commands
        r, w, e = select.select([sock], [], [sock], 0.5)
        for s in r:
          try:
            datagram = s.recv(1024)
            args = json.loads(datagram)
            if self.commands[args[1]] != None:
              try:
                #print args[1] + "(" + str(args[2:]) + ")"
                self.commands[args[1]](*args[2:])
              except TypeError as e:
                print(e.args)
                pass
              except RuntimeError as e:
                print(e.errno, e.strerror)
                pass
              except:
                print("Exception: ", sys.exc_info()[0])
                pass
          except KeyError:
            # unknown command
            pass
          except:
            pass
    except:
      # die. we will be back
      pass
    sock.close()

    print("End server")
    os.remove(SERVER_SOCKET)
    
    if self.restart:
      os.execvp(sys.argv[0], sys.argv)

  def __init__(self):
    self.restart = None
    self.alive = None
    self.commands = {}
    def register(command, fn):
      self.commands[command] = fn
      
    register("restart", self.restart)
    register("on", self.on)
    register("off", self.off)
    register("cool", self.cool)
    register("warm", self.warm)
    register("disco1", self.disco1)
    register("disco2", self.disco2)
    register("normal", self.normal)
    register("white", self.white)
    register("warm_white", self.warm_white)
    register("color", self.color)
    register("status", self.status)
    register("devicename", self.devicename)
    register("battery", self.battery)

    self.server()

def should_launch_server():
  if not is_server_running():
    if (os.fork() == 0):
      Server()
      sys.exit(0)

should_launch_server()

if os.path.exists(SERVER_SOCKET):
  client = socket.socket( socket.AF_UNIX, socket.SOCK_DGRAM )
  try:
    client.connect(SERVER_SOCKET)
    client.send(json.dumps(sys.argv))
    client.close()
  except socket.error as e:
    os.remove(SERVER_SOCKET)
    should_launch_server()

    

