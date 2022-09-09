import socket


class ClientTCP:
    def __init__(self) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, address: str, port: int) -> None:
        self.socket.connect((address, port))

    def close(self) -> None:
        self.socket.close()

    def send(self, message: str) -> int:
        return self.socket.send(message.encode("utf-8"))

    def receive(self) -> bytes:
        # TODO: dynamic buffer size
        return self.socket.recv(2048)
