import signal
import sys
from SimpleWebSocketServer import *



clients = []
class McastWebService(WebSocket):


   def handleMessage(self):
      for client in list(clients):
         if client != self:
            client.sendMessage(self.address[0] + ' - ' + self.data)

   def handleConnected(self):
      print self.address, 'connected'
      for client in list(clients):
         client.sendMessage(self.address[0] + u' - connected')
      clients.append(self)

   def handleClose(self):
      clients.remove(self)
      print self.address, 'closed'
      for client in list(clients):
         client.sendMessage(self.address[0] + u' - disconnected')

server = SimpleWebSocketServer('',54662, McastWebService)
server.serveforever()
