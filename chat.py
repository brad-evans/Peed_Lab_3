#!usr/bin/env python

import socket
import threading
import select
import time
import operator
import sys
import smp
import hashlib
import os
import stem.process
from binascii import a2b_base64 as a2b
from binascii import b2a_base64 as b2a
from getpass import getpass
from smp import SMP
from stem.control import Controller
from stem.util import term
from curses.textpad import Textbox
from contextlib import contextmanager
from pyaxo import Axolotl
from time import sleep


from smp import longToBytes
from smp import padBytes

def main():

    class Chat_Server(threading.Thread):
            def __init__(self):
                #print "Chat_Server init"
                threading.Thread.__init__(self)
                self.running = 1
                self.conn = None
                self.addr = None
                self.host = '127.0.0.1'
                self.port = None
                self.a = None
            def run(self):
                #print "running chat server"
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.bind((self.host,self.port))
                s.listen(1)
                print "waiting for connection from client..."
                self.conn, addr = s.accept()
                print "\033[1;36mBegin Chat Conversation\033[0m"
                print "______________________________________________________"
                while self.running == True:
                    data = self.conn.recv(1024)


                    if data:
                        data = self.a.decrypt(data)
                        if data == 'exit':
                            self.running = 0
                        else:
                            print "\033[1;31mFriend:>>>> " + data + "\033[0m"
                    else:
                        break
                time.sleep(0)
            def kill(self):
                self.running = 0

    class Chat_Client(threading.Thread):
            def __init__(self):
                #print "Chat Client init"
                threading.Thread.__init__(self)
                self.host = None
                self.sock = None
                self.running = 1
                self.port = None
                self.a = None
            def run(self):
                #print "Chat Client Run"
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect((self.host, self.port))
                print "\033[1;36mBegin Chat Conversation\033[0m"
                print "______________________________________________________"
                while self.running == True:

                    rcv = self.sock.recv(1024)

                    data = ''+rcv
                    if data:
                        data = self.a.decrypt(data)
                        if data == 'exit':
                            self.running = 0
                        else:
                            print "\033[1;31mFriend:>>>> " + data + "\033[0m"
                    else:
                        break
                time.sleep(0)
            def kill(self):
                self.running = 0

    class Text_Input(threading.Thread):
            def __init__(self):
                #print "text input init"
                threading.Thread.__init__(self)
                self.running = 1
            def run(self):
                #print "text input run "
                while self.running == True:
                  text = raw_input('')
                  try:
                      text = text.replace('\n', '')

                      text = chat_client.a.encrypt(text)
                      chat_client.sock.sendall(text)
                  except:
                      Exception
                  try:
                      text = text.replace('\n', '')
                      text = chat_server.a.encrypt(text)
                      chat_server.conn.sendall(text)
                  except:
                      Exception
                  time.sleep(0.1)
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
        port = 8000


        s.bind((host, port))           # Bind to the port
        s.listen(3)
        print "waiting for connection..."                  # Now wait for client connection.
        c, addr = s.accept()           # Establish connection with client.
        print 'Got connection from', addr
        secret = raw_input("\033[1mEnter shared secret for SMP: \033[0m")
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
            print "\033[1;32mSMP Matched!!\033[0m"
            print "______________________________________________________"
            print "\033[1mSecure Chat Setup\033[0m"
            myName = raw_input("\033[1mEnter your name: \033[0m")
            otherName = raw_input("\033[1mEnter your friend's name: \033[0m")
            masterkey = raw_input("\033[1mEnter the master key: \033[0m")
            chat_server = Chat_Server()                       # Reserve best port.
            chat_server.a = Axolotl(myName, dbname = otherName + '.db', dbpassphrase = None, nonthreaded_sql = False)
            chat_server.a.createState(other_name = otherName, mkey = hashlib.sha256(masterkey).digest(), mode=False)
            rkey = b2a(chat_server.a.state['DHRs']).strip()
            print "\033[35mSend this ratchet key to your client: \033[0m", rkey
            #print 'Server started'
            #print 'Waiting for cients to connect...'
        else:
            print "\033[1;31mSMP did not Match \033[0m"
            s.close()
            sys.exit()

        chat_server.port = 8080
        chat_server.start()
        text_input = Text_Input()
        text_input.start()

    elif mode == '-c':
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)           # Socket object
        host = '127.0.0.1'        # Get host name
        port = 8000
                              # Reserve best port.

        print 'Connect to ', host, port
        s.connect((host, port))
        secret = raw_input("\033[1mEnter shared secret for SMP: \033[0m")
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
            print "\033[1;32mSMP Matched \033[0m"
            print "______________________________________________________"
            print "\033[1mSecure Chat Setup \033[0m"
            myName = raw_input("\033[1mEnter your name: \033[0m")
            otherName = raw_input("\033[1mEnter your friend's name: \033[0m")
            masterkey = raw_input("\033[1mEnter the master key: \033[0m")                         # Reserve best port.
            rkey = raw_input("\033[1mEnter the ratchet key (received from your partner): \033[0m")
        else:
            print "\033[1;31mSMP did not Match \033[0m"
            s.close()
            sys.exit()
        chat_client = Chat_Client()
        chat_client.a = Axolotl(myName, dbname=otherName + '.db', dbpassphrase=None,nonthreaded_sql=False)
        chat_client.a.createState(other_name=otherName,mkey=hashlib.sha256(masterkey).digest(),mode=True,other_ratchetKey=a2b(rkey))

        chat_client.host = '127.0.0.1'
        chat_client.port = 8080

        chat_client.start()
        text_input = Text_Input()
        text_input.start()

if __name__ == "__main__":
    main()
