import socket


class ClientTCP:
    def __init__(self) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.buffer_size = 2048

    def connect(self, address: str, port: int) -> None:
        self.socket.connect((address, port))

    def close(self) -> None:
        self.socket.close()

    def send(self, message: str) -> int:
        return self.socket.send(message.encode("utf-8"))

    def receive(self) -> bytes:
        data = bytes()
        while True:
            buf = self.socket.recv(self.buffer_size)
            data += buf
            if len(buf) < self.buffer_size:
                break
        return data
