import socket                       # Import socket module
import operator                     # For encypt.
import sys                         # Encryption pin
import smp


from smp import longToBytes
from smp import padBytes




s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)           # Socket object
host = '127.0.0.1'        # Get host name
port = 8000                         # Reserve best port.

print 'Connect to ', host, port
s.connect((host, port))
secret = raw_input("Enter shared secret: ")
smp = smp.SMP(secret)

buffer = smp.step1()
#print "buffer = {}\n".format(  buffer )
tempBuffer = padBytes( longToBytes( len( buffer ) + 4 ), 4 ) + buffer

s.send( tempBuffer )

buffer = s.recv(4096)[4:]
buffer = smp.step3(buffer)
tempBuffer = padBytes( longToBytes( len( buffer ) + 4 ), 4 ) + buffer
s.send( tempBuffer )

buffer = s.recv(4096)[4:]
smp.step5(buffer)
if smp.match:
    print "match"
else:
    print "no match"

while True:
    msg = raw_input('C>> ')

    s.send(msg)

    msg = s.recv(1024)

    print 'S>> ', msg
#s.close                     # C
