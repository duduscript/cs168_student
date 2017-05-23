import socket
import sys

class BasicClient(object):

    def __init__(self, address, port):
        self.address = address
        self.port = int(port)

    def send(self, message):
        self.socket = socket.socket()
        self.socket.connect((self.address, self.port))
        self.socket.send(message)

if __name__ == '__main__':
    args = sys.argv
    if len(args) != 3:
        print "Please supply a server address and port."
        sys.exit()
    client = BasicClient(args[1], args[2])
    while True:
        msg = raw_input()
        client.send(msg)
