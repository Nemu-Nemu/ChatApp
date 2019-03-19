from server import Server


server = Server()
server.start()
server.await_clients()
server.close()
