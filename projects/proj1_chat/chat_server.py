import socket
import select
import utils
import sys

class chat_server(object):

    def __init__(self, address, port):
        self.channels = {}
        self.sockets = []
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
        self.socket.bind((address, int(port)))
        self.socket.listen(10)
        self.sockets.append(self.socket)
        self.names = {}

    def create_channel(self, channel_name):
        self.channels[channel_name] = set()

    def find_channel_by_name(self, channel_name):
        if channel_name in self.channels:
            return self.channels[channel_name]
        else:
            return None

    def find_channel_by_sock(self, sock):
        for ch in self.channels:
            if sock in self.channels[ch]:
                return ch
        return None

    def disconnect(self, sock):
        print('[LOG] disconnect function')
        self.sockets.remove(sock)
        channel = self.find_channel_by_sock(sock)
        if channel != None:
            self.channels[channel].pop()
            for ch_sock in self.channels[channel]:
                ch_sock.send(utils.SERVER_CLIENT_LEFT_CHANNEL.format(self.names[sock]))
        self.names.pop(sock)

    def connect(self, sock):
        print('[LOG] connect function')
        sockfd, address = sock.accept()
        name = sockfd.recv(1024)
        self.names[sockfd] = name
        self.sockets.append(sockfd)

    def run(self):
        while True:
            print('[LOG] in run loop')
            ready_to_read,_,_ = select.select(self.sockets,[],[])
            for sock in ready_to_read:
                if sock == self.socket:
                    self.connect(sock)
                else:
                    data = sock.recv(1024)
                    if data:
                        self.handle(data, sock)
                    else:
                        self.disconnect(sock)
        self.socket.close()

    def join(self, messages, socket):
        print('[LOG] join function')
        if len(messages) != 2:
            socket.send(utils.SERVER_JOIN_REQUIRES_ARGUMENT)
        elif self.find_channel_by_name(messages[1]) == None:
            socket.send(utils.SERVER_NO_CHANNEL_EXISTS.format(messages[1]))
        else:
            channel = self.find_channel_by_sock(socket)
            if channel != None:
                self.channels[channel].remove(socket)
                for ch_sock in self.channels[channel]:
                    ch_sock.send(utils.SERVER_CLIENT_LEFT_CHANNEL.format(self.names[socket]))
            self.channels[messages[1]].add(socket)
            for sock in self.channels[messages[1]]:
                if sock != socket:
                    sock.send(utils.SERVER_CLIENT_JOINED_CHANNEL.format(self.names[socket]))

    def create(self, messages, socket):
        print('[LOG] create function')
        if len(messages) != 2:
            socket.send(utils.SERVER_CREATE_REQUIRES_ARGUMENT)
        elif self.find_channel_by_name(messages[1]) != None:
            socket.send(utils.SERVER_CHANNEL_EXISTS.format(messages[1]))
        else:
            self.create_channel(messages[1])
            socket.send('')

    def talk(self, message, socket):
        print('[LOG] talk function')
        channel = self.find_channel_by_sock(socket)
        if channel == None:
            socket.send(utils.SERVER_CLIENT_NOT_IN_CHANNEL)
        else:
            self.broadcast(channel,message,socket)
            socket.send('')

    def handle(self, message, socket):
        print('[LOG] handle %s',message)
        messages = message.split()
        if messages[0] == '/list':
            result = '\n'.join(self.channels.keys())
            socket.send(result)
        elif messages[0] == '/join':
            self.join(messages, socket)
        elif messages[0] == '/create':
            self.create(messages, socket)
        elif message[0].startswith('/'):
            socket.send(utils.SERVER_INVALID_CONTROL_MESSAGE.format(messages[0]))
        else:
            self.talk(message, socket)

    def broadcast(self, channel, message, socket):
        print('[LOG] broadcast function')
        for sock in self.channels[channel]:
            if sock == socket or sock == self.socket:
                continue
            sock.send(':::'.join([self.names[sock], message]))


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: python chat_server.py address port')
        sys.exit()
    server = chat_server(sys.argv[1],sys.argv[2])
    server.run()
