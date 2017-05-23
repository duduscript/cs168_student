class channal_server(basic_server):

    def __init__(self, address, port):
        basic_server.__init__(self, address, port)
        self.channels = []
        self.user = {}

    def add_channel(self, channel_name):
        self.channels.append(channel(channel_name))

    def find_channel(self, channel_name):
        for ch in self.channels:
            if ch.name == channel_name:
                return ch
        return None

    def join_channel(self, channel_name, usr):
        ch = self.find_channel(channel_name)
        if ch == None:
            return False
        ch.append(user(usr))
        return True

    def handle(self, message, socket):
        if socket.
        if message == '\\list':
            pass
        elif message == '\\join':
            pass
        elif message == '\\create':
            pass
