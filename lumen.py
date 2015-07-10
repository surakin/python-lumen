#!/usr/bin/python

import sys
import socket
import os
import json
import signal

SERVER_SOCKET = "/tmp/lumen_socket"

from time import sleep

req = None

def connect():
  from gattlib import GATTRequester
  global req;
  if req == None:
    bulb = "7C:66:9D:7D:38:16"
  
    req = GATTRequester(bulb)
  req.write_by_handle(0x25, str(bytearray( [0x08, 0x61, 0x07, 0x66, 0xa7, 0x68, 0x0f, 0x5a, 0x18, 0x3e, 0x5e, 0x7a, 0x3e, 0x3c, 0xbe, 0xaa, 0x8a, 0x21, 0x4b, 0x6b] )))
  req.write_by_handle(0x25, str(bytearray( [0x07, 0xdf, 0xd9, 0x9b, 0xfd, 0xdd, 0x54, 0x5a, 0x18, 0x3e, 0x5e, 0x7a, 0x3e, 0x3c, 0xbe, 0xaa, 0x8a, 0x21, 0x4b, 0x6b] )))
  return req

def off():
  connect().write_by_handle(0x25, str(bytearray( [0x00])))

def on():
  connect().write_by_handle(0x25, str(bytearray( [0x01, 0, 0, 0, 0xb5])))

def cool():
  connect().write_by_handle(0x25, str(bytearray( [0x01, 0, 0, 0, 0, 0, 0x50])))

def warm():
  connect().write_by_handle(0x25, str(bytearray( [0x01, 0, 0, 0, 0, 0, 0x51])))

def disco1():
  connect().write_by_handle(0x25, str(bytearray( [0x01, 0, 0, 0, 0, 0, 0x52])))

def disco2():
  connect().write_by_handle(0x25, str(bytearray( [0x01, 0, 0, 0, 0, 0, 0x53])))

def normal():
  connect().write_by_handle(0x25, str(bytearray( [0x01, 0, 0, 0, 0, 0, 0x54])))

def warm_white(n):
  n = float(n)
  if n >= 100:
    connect().write_by_handle(0x25, str(bytearray( [0x01, 0xdf, 0xd9, 0x9a, 0x58, 0, 0x54])))
  elif n >= 90:
    connect().write_by_handle(0x25, str(bytearray( [0x01, 0xdf, 0xd9, 0x9b, 0xa3, 0, 0x54])))
  elif n >= 70:
    connect().write_by_handle(0x25, str(bytearray( [0x01, 0xdf, 0xd9, 0x9b, 0xb5, 0, 0x54])))
  elif n >= 50:
    connect().write_by_handle(0x25, str(bytearray( [0x01, 0xdf, 0xd9, 0x9b, 0x87, 0, 0x54])))
  elif n >= 30:
    connect().write_by_handle(0x25, str(bytearray( [0x01, 0xdf, 0xd9, 0x9b, 0x99, 0, 0x54])))
  else:
    connect().write_by_handle(0x25, str(bytearray( [0x01, 0xdf, 0xd9, 0x9b, 0xf2, 0, 0x54])))
    
def white():
  warm_white(100)
  
def color(r, g, b):
  _r = float(r) / 255;
  _g = float(g) / 255;
  _b = float(b) / 255;
  k = 1 - max(_r, _g, _b)
  c = (1 - _r - k) / (1 - k)
  m = (1 - _g - k) / (1 - k)
  y = (1 - _b - k) / (1 - k)
  connect().write_by_handle(0x25, str(bytearray( [0x01, int(round(c * 105) + 120), int(round(m * 105) + 120), int(round(y * 105) + 120), int(round((1-k) * 15) + 240), 0, 0x54])))

commands = {}
def register(command, fn):
  commands[command] = fn
  
register("on", on)
register("off", off)
register("cool", cool)
register("warm", warm)
register("disco1", disco1)
register("disco2", disco2)
register("normal", normal)
register("white", white)
register("warm_white", warm_white)
register("color", color)

def is_server_running():
  return os.path.exists(SERVER_SOCKET)

def server():
  alive = True
  def handler(sig):
    if sig == signal.SIGTERM:
      alive = False
      
  signal.signal(signal.SIGTERM, handler)
  
  print("Start server")
  sock = socket.socket( socket.AF_UNIX, socket.SOCK_DGRAM )
  try:
    umask_ = os.umask(0000); 
    sock.bind(SERVER_SOCKET)
    os.umask(umask_);
    while alive:
      datagram = sock.recv(1024)
      if not datagram:
        break;
      else:
        args = json.loads(datagram)
        try:
          if commands[args[1]] != None:
            try:
              print args[1] + "(" + str(args[2:]) + ")"
              commands[args[1]](*args[2:])
            except TypeError as e:
              print(e.args)
            except:
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
  os.remove(SERVER_SOCKET)
  print("End server")
 
if not is_server_running():
  if (os.fork() == 0):
    server()
  else:
    sleep(0.5)

if os.path.exists(SERVER_SOCKET):
  client = socket.socket( socket.AF_UNIX, socket.SOCK_DGRAM )
  client.connect(SERVER_SOCKET)
  client.send(json.dumps(sys.argv))
  client.close()

#connect().write_by_handle(0x25, str(bytearray( [0x01, 0x7e, 0xca, 0xbe, 255, 0, 0x54])))
#color(255, 255, 255)
#off()

#req.write_by_handle(0x25, str(bytearray( [0x01, 0x00, 0x00, 0x00, 0xb5])))
#char-write-req 0x0025 01610766b5680f5a183e5e7a3e3cbeaa8a214b6b
