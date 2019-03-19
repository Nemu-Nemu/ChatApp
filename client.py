import socket
import select
import sys


def prompt():
    sys.stdout.write('<You> ')
    sys.stdout.flush()


class Client:

    MSG_BUFFER = 4096

    def __init__(self, host='localhost', port=12800):
        self.host = host
        self.port = port

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(2)
        try:
            self.socket.connect((self.host, self.port))
        except:
            print('Unable to connect')
            sys.exit()
        print('Connected to {}:{}'.format(self.host, self.port))
        prompt()

    def reading_from_server(self):
        while True:
            socket_list = [sys.stdin, self.socket]
            read_socket, wlist, xlist = select.select(socket_list, [], [])

            for sock in read_socket:
                if sock == self.socket:
                    data = sock.recv(self.MSG_BUFFER)
                    if not data:
                        print('\nDisconnected from server')
                        sys.exit()
                    else:
                        sys.stdout.write(data.decode())
                        prompt()

                else:
                    msg = sys.stdin.readline()
                    self.socket.send(msg.encode())
                    prompt()

    def disconnect(self):
        self.socket.close()
