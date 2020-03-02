import socketserver

from src.socketServer.mainServer.server.socket.connection import OnlineEducationServer


if __name__ == '__main__':
    server = socketserver.ThreadingTCPServer(('0.0.0.0', 5002), OnlineEducationServer)
    print("EDU SEVER is running.")
    server.serve_forever()
