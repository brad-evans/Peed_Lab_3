#!usr/bin/env python

import socket
import threading
import select
import time
import operator
import sys
import smp


from smp import longToBytes
from smp import padBytes

def main():

    class Chat_Server(threading.Thread):
            def __init__(self):
                threading.Thread.__init__(self)
                self.running = 1
                self.conn = None
                self.addr = None
                self.host = '127.0.0.1'
                self.port = None
            def run(self):
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.bind((self.host,self.port))
                s.listen(1)
                print("waiting for connection from client")
                self.conn, addr = s.accept()     
                while self.running == True:
                    data = self.conn.recv(1024)
                    if data == 'exit':
                        self.running = 0
                    if data:
                        print "Client Says >> " + data
                    else:
                        break
                time.sleep(0)
            def kill(self):
                self.running = 0

    class Chat_Client(threading.Thread):
            def __init__(self):
                threading.Thread.__init__(self)
                self.host = None
                self.sock = None
                self.running = 1
                self.port = None
            def run(self):
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect((self.host, self.port))
                while self.running == True:
                    data = self.sock.recv(1024)
                    if data == 'exit':
                        self.running = 0
                    if data:
                        print "Server Says >> " + data
                    else:
                        break
                time.sleep(0)
            def kill(self):
                self.running = 0

    class Text_Input(threading.Thread):
            def __init__(self):
                threading.Thread.__init__(self)
                self.running = 1
            def run(self):
                while self.running == True:
                  text = raw_input('')
                  try:
                      chat_client.sock.sendall(text)
                  except:
                      Exception
                  try:
                      chat_server.conn.sendall(text)
                  except:
                      Exception
                  time.sleep(0)
            def kill(self):
                self.running = 0

    try:
        mode = sys.argv[1]
    except:
        exit(1)

    if mode == '-s':
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)           # Socket object
        host = '127.0.0.1'         # Get host name
        port = 8000                         # Reserve best port.


        print 'Server started'
        print 'Waiting for cients to connect...'

        s.bind((host, port))           # Bind to the port
        s.listen(3)                    # Now wait for client connection.
        c, addr = s.accept()           # Establish connection with client.
        print 'Got connection from', addr
        secret = raw_input("Enter shared secret: ")
        smpr = smp.SMP(secret)
        buffer = c.recv(4096)[ 4:]

        buffer = smpr.step2(buffer)
        tempBuffer = padBytes( longToBytes( len( buffer ) + 4 ), 4 ) + buffer
        c.send( tempBuffer )

        buffer = c.recv(4096)[ 4:]

        buffer = smpr.step4(buffer)
        tempBuffer = padBytes( longToBytes( len( buffer ) + 4 ), 4 ) + buffer
        c.send( tempBuffer )

        if smpr.match:
            print "match"
        else:
            print "no match"
            s.close()
            sys.exit()
        chat_server = Chat_Server()
        chat_server.port = int(raw_input("Enter port to listen on: "))
        chat_server.start()
        text_input = Text_Input()
        text_input.start()

    elif mode == '-c':
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)           # Socket object
        host = '127.0.0.1'        # Get host name
        port = 8000                         # Reserve best port.

        print 'Connect to ', host, port
        s.connect((host, port))
        secret = raw_input("Enter shared secret: ")
        smpr = smp.SMP(secret)

        buffer = smpr.step1()
        #print "buffer = {}\n".format(  buffer )
        tempBuffer = padBytes( longToBytes( len( buffer ) + 4 ), 4 ) + buffer

        s.send( tempBuffer )

        buffer = s.recv(4096)[4:]
        buffer = smpr.step3(buffer)
        tempBuffer = padBytes( longToBytes( len( buffer ) + 4 ), 4 ) + buffer
        s.send( tempBuffer )

        buffer = s.recv(4096)[4:]
        smpr.step5(buffer)
        if smpr.match:
            print "match"
        else:
            print "no match"
            s.close()
            sys.exit()
        chat_client = Chat_Client()
        chat_client.host = raw_input("Enter host to connect to: ")
        chat_client.port = int(raw_input("Enter port to connect to: "))
        chat_client.start()
        text_input = Text_Input()
        text_input.start()

if __name__ == "__main__":
    main()
