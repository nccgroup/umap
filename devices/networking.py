from threading import Thread
from socket import *
import sys

class netserver(Thread):
    def __init__( self, maxusb_app, port):
        Thread.__init__( self )

        self.maxusb_app = maxusb_app
    
        self.sock = socket( AF_INET, SOCK_STREAM )
        self.maxusb_app.netserver_to_endpoint_sd = self.sock

        self.maxusb_app.netserver_sd = self.sock
        try:
            self.sock.bind(( '', port ))
        except:
            print("Error: Could not bind to local port")
            return

        self.sock.listen(5)
   
    def run( self ):

        newsock = 0

        while (self.maxusb_app.server_running == True):
            try:
                if not newsock:
                    newsock, address = self.sock.accept()    

                self.maxusb_app.netserver_from_endpoint_sd = newsock

                reply = newsock.recv(16384)
                if len(reply) > 0:
                    print ("Socket reply: %s" % reply)
                    self.maxusb_app.reply_buffer = reply

            except:
                print ("Error: Socket Accept")
                sys.exit()

        self.maxusb_app.netserver_to_endpoint_sd.close()
        self.maxusb_app.netserver_from_endpoint_sd.close()


