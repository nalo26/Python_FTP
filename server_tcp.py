import socket


class ServerTCP:
    def __init__(self, address: str, port: int = None) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if port is None:  # bind port on a random available one
            self.socket.bind((address, 0))
        else:
            self.socket.bind((address, port))
        self.socket.listen(2)
        print(f"[Starting TCP Server on port {self.socket.getsockname()[1]}]")

    def accept(self) -> tuple:
        return self.socket.accept()

    def close(self) -> None:
        self.socket.close()
