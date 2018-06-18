import socket
import pickle
import sys, os

from model import MyObject

# Create a TCP/IP socket.
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect.
server_address = ('localhost', int(os.getenv('SOCKET_PORT')))
sock.connect(server_address)

try:
    ob = MyObject()
    ob.name = 'apple'
    bytes_data = pickle.dumps({'object': ob})
    bytes_data += b'\n\r\n'
    sock.sendall(bytes_data)

finally:
    sock.close()