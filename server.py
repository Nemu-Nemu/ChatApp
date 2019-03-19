import socket
import select

import logging
import logger_config

logger = logging.getLogger('application')


class Server:

    MSG_BUFFER = 4096

    def __init__(self, host='localhost', port=12800):
        self.host = host
        self.port = port
        self.readable_connections = []

    def broadcast_data(self, sock, msg):
        for socket in self.readable_connections:
            # do not send this to the main socket or the client who
            # generated this message
            if socket != self.socket and socket != sock:
                try:
                    socket.send(msg.encode())
                except:
                    # connection is lost
                    logger.exception(
                        'Client disconnected when trying to receive a message')
                    socket.close()
                    self.readable_connections.remove(socket)

    def start(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # socket itself is reusable and searchable
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except socket.error as e:
            logger.error('Could not create a socket for the server')
            logger.debug(e)
        self.socket.bind((self.host, self.port))

    def await_clients(self):
        self.socket.listen(10)
        self.readable_connections.append(self.socket)
        logger.info('Server started on port {}'.format(self.port))
        logger.info('Awainting clients...')

        while True:
            read_sockets, write_sockets, error_sockets = select.select(
                self.readable_connections,
                [],
                [])

            for sock in read_sockets:
                if sock == self.socket:
                    self._accept_new(sock)
                else:
                    data = self._read_client(sock)
                    peer_name = ':'.join(list(map(str, sock.getpeername())))
                    if data:
                        self.broadcast_data(sock, "\r<" + peer_name + '> ' +
                                            data.decode())
                    else:
                        self.broadcast_data(
                            sock,
                            "\nClient {} is offline\n".format(sock.getpeername()))
                        logger.info("Client {} is offline".format(
                            sock.getpeername()))
                        sock.close()
                        self.readable_connections.remove(sock)

    def _accept_new(self, sock):
        if sock == self.socket:
            conn, info = self.socket.accept()
            self.readable_connections.append(conn)
            logger.info('Client {} is connected'.format(info))
            self.broadcast_data(
                conn, "\n{} entered room\n".format(info))

    def _read_client(self, sock):
        try:
            data = sock.recv(self.MSG_BUFFER)
            return data
        except:
            print('Got an exception while receiving client data')
            self.broadcast_data(
                sock,
                "\nClient {} is offline\n".format(sock.getpeername()))
            print("Client {} is offline".format(sock.getpeername()))
            sock.close()
            self.readable_connections.remove(sock)

    def close(self):
        self.socket.close()

    def stop(self):
        self.send_to_all('STOP')
        for connection in self.readable_connections:
            connection.close()
        self.socket.close()
