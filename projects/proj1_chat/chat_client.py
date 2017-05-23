import socket
import select
import utils
import sys

class chat_client(object):

    def __init__(self, name, address, port):
        self.name = name
        self.address = address
        self.port = int(port)
        self.sockets = [sys.stdin]

    def prompt(self):
        sys.stdout.write(utils.CLIENT_MESSAGE_PREFIX)
        sys.stdout.flush()

    def run(self):
        sock = socket.socket()
        #sock.settimeout(2)
        try:
            sock.connect((self.address,self.port))
            sock.send(self.name)
        except:
            print(utils.CLIENT_CANNOT_CONNECT,
                    self.address,
                    self.port)
            sys.exit()
        self.sockets.append(sock)
        self.prompt()

        while True:
            ready_to_read,_,_ = select.select(self.sockets,[],[])
            for s in ready_to_read:
                if s == sock:
                    data = s.recv(1024)
                    if not len(data):
                        print(utils.CLIENT_SERVER_DISCONNECTED,
                                self.address,
                                self.port)
                        sys.exit()
                    datas = data.split(':::')
                    if len(datas) == 1:
                        sys.stdout.write('\n'+datas[0]+'\n')
                    else:
                        sys.stdout.write('\n['+datas[0]+'] '+datas[1]+'\n')
                    sys.stdout.flush()
                else:
                    data = sys.stdin.readline()
                    sock.send(data[:-1])
                self.prompt()


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage:python chat_client.py username address port")
    client = chat_client(sys.argv[1],sys.argv[2],sys.argv[3])
    client.run()

