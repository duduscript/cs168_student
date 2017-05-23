import socket
import select


class channal_server(basic_server):

    def __init__(self, address, port):
        self.channels = {}
        self.sockets = []
        self.socket = socket.socket()
        self.socket.bind((address, port))
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
            if sock in ch:
                return ch
        return None

    def join_channel(self, channel_name, sock):
        ch = self.find_channel_by_name(channel_name)
        if ch == None:
            # show the error
            return False
        self.channels[channel_name].add(sock)
        return True

    def disconnect(self, sock):
        self.sockets.remove(sock)
        channel = self.find_channel_by_sock(sock)
        if channel != None:
            for ch_sock in self.channels[channel]:
                ch_sock.send(SERVER_CLIENT_LEFT_CHANNEL,self.names[sock])
        self.names.remove(sock)

    def connect(self, sock):
        sockfd, address = sock.accept()
        name = sockfd.recv()
        self.names[name] = sockfd
        self.sockets.append(sockfd)

    def run(self):
        ready_to_read,_,_ = select.select(self.sockets,[],[],0)
        for sock in ready_to_read:
            if sock == self.socket:
                self.connect(sock)
            else:
                data = sock.recv(1024)
                if data:
                    self.handle(data, sock)
                else:
                    self.disconnect(sock)

    def join(self, messages, socket):
        if len(messages) != 2:
            socket.send(SERVER_JOIN_REQUIRES_ARGUMENT)
        elif self.find_channel_by_name(messages[1]) != None:
            socket.send(SERVER_NO_CHANNEL_EXISTS,messages[1])
        else:
            channel = self.find_channel_by_sock(socket)
            if channel != None:
                self.channels[channel].remove(socket)
            self.channels[messages[1]].add(socket)
            for sock in self.channels[messages[1]]:
                if sock != socket:
                    sock.send(SERVER_CLIENT_JOINED_CHANNEL,self.names[socket])

    def create(self, messages, socket):
        if len(messages) != 2:
            sock.send(SERVER_CREATE_REQUIRES_ARGUMENT)
        elif self.find_channel_by_name(messages[1]) == None:
            socket.send(SERVER_CHANNEL_EXISTS,messages[1])
        else:
            self.create_channel(messages[1])

    def talk(self, message, socket):
        channel = self.find_channel_by_sock(socket)
        if channel == None:
            socket.send(SERVER_CLIENT_NOT_IN_CHANNEL)
        else:
            self.broadcast(channel,message,socket)



    def handle(self, message, socket):
        messages = message.split()
        if messages[0] == '/list':
            result = '\n'.join(self.channels.keys())
            socket.send(result)
        elif messages[0] == '/join':
            self.join(messages, socket)
        elif messages[0] == '/create':
            self.create(messages, socket)
        elif message[0].startswith('/'):
            socket.send(SERVER_INVALID_CONTROL_MESSAGE,messages[0])
        else:
            self.talk(message, socket)

    def broadcast(self, channel, message, socket):
        for sock in self.channels[channel]:
            if sock == socket:
                continue
            sock.send(message)
