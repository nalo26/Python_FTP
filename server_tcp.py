import socket


class ServerTCP:
    def __init__(self, address: str, port: int) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((address, port))
        self.socket.listen(2)
        print(f"[Starting TCP Server on port {port}]")

    def accept(self) -> tuple:
        return self.socket.accept()
