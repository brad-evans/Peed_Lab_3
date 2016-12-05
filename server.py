import socket                       # Import socket module
import operator                     # For encypt.
import sys                         # Encryption pin
import smp

from smp import longToBytes
from smp import padBytes

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
smp = smp.SMP(secret)
buffer = c.recv(4096)[ 4:]

buffer = smp.step2(buffer)
tempBuffer = padBytes( longToBytes( len( buffer ) + 4 ), 4 ) + buffer
c.send( tempBuffer )

buffer = c.recv(4096)[ 4:]

buffer = smp.step4(buffer)
tempBuffer = padBytes( longToBytes( len( buffer ) + 4 ), 4 ) + buffer
c.send( tempBuffer )

if smp.match:
    print "match"
else:
    print "no match"

while True:
   msg = c.recv(1024)


   print 'C>> ', msg
   msg = raw_input('S>>: ')
   c.send(msg);
   #c.close()                       # Close the connection
