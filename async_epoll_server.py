"""
References:
http://scotdoyle.com/python-epoll-howto.html
https://docs.python.org/3.0/library/socket.html?highlight=socket#module-socket
https://docs.python.org/3.4/library/select.html
"""

import socket, select
import os
import pickle

from model import MyObject
"""
socket eventmask
EPOLLIN  - Available for read
EPOLLOUT - Available for write
EPOLLHUB - Hang up happened on the assoc. fd
"""

EOL1 = b'\n\n'
EOL2 = b'\n\r\n'
response  = b'HTTP/1.0 200 OK\r\nDate: Mon, 1 Jan 1996 01:01:01 GMT\r\n'
response += b'Content-Type: text/plain\r\nContent-Length: 13\r\n\r\n'
response += b'Hello, world!'

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serversocket.bind(('0.0.0.0', int(os.getenv('SOCKET_PORT'))))
serversocket.listen(1)  # backlog = maximum number of queued connections 1~5
serversocket.setblocking(0)  # none-blocking mode

epoll = select.epoll()

# fileno() returns socket file descriptor
# which can be used when accessing opened file.
epoll.register(serversocket.fileno(), select.EPOLLIN)

try:
    connections = {}; requests = {}; responses = {}
    while True:
        print('Waits for event...')
        events = epoll.poll(timeout=1) # waits for events.

        def take_events(events, connections, requests, responses):
            for fileno, event in events:
                if fileno == serversocket.fileno():
                    connection, address = serversocket.accept()
                    connection.setblocking(0)
                    epoll.register(connection.fileno(), select.EPOLLIN)
                    connections[connection.fileno()] = connection
                    requests[connection.fileno()] = b''
                    responses[connection.fileno()] = response
                elif event & select.EPOLLIN:
                    requests[fileno] += connections[fileno].recv(1024)
                    print('[data received]')
                    print(requests[fileno])
                    if EOL1 in requests[fileno] or EOL2 in requests[fileno]:
                        # epoll.modify(fileno, select.EPOLLOUT)
                        # print('-' * 40 + '\n' + requests[fileno].decode()[:-2])
                        data = pickle.loads(requests[fileno])
                        print(data['object'])
                        print(data['object'].name)
                        return True

                elif event & select.EPOLLOUT:
                    byteswritten = connections[fileno].send(responses[fileno])  # Returns the number of bytes sent.
                    responses[fileno] = responses[fileno][byteswritten:]
                    if len(responses[fileno]) == 0:
                        epoll.modify(fileno, 0)
                        connections[fileno].shutdown(socket.SHUT_RDWR)
                elif event & select.EPOLLHUP:
                    epoll.unregister(fileno)
                    connections[fileno].close()
                    del connections[fileno]
            return

        if take_events(events, connections, requests, responses):
            break

finally:
    epoll.unregister(serversocket.fileno())
    epoll.close()
    serversocket.close()
