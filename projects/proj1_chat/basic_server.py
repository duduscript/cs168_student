import socket
import sys

class BasicServer(object):

    def __init__(self, port):
        self.address = '127.0.0.1'
        self.socket = socket.socket()
        self.socket.bind((self.address, int(port)))
        self.socket.listen(5)

    def handle(self, message, socket, address):
        print(message, socket, address)

    def run(self):
        while True:
            (new_socket, address) = self.socket.accept()
            message = new_socket.recv(1024)
            self.handle(message, new_socket, address)

if __name__ == '__main__':
    args = sys.argv
    if len(args) != 2:
        print("Please supply a port")
        sys.exit()
    server = BasicServer(args[1])
    server.run()
