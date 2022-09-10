from client_tcp import ClientTCP
from server_tcp import ServerTCP
from parser_utils import get_command_and_args
from enums import CommandTCP, CodeFTP
from ip_utils import parse_ip
from threading import Thread
from socket import socket
import re


class ClientFTP:
    def __init__(self, root: str) -> None:
        self.client_tcp_control = ClientTCP()
        self.client_tcp_data: ClientTCP or None = None
        self.serverTCP: ServerTCP or None = None
        self.root_dir = root
        self.file_name = None
        self.buffer_size = 2048
        
    def connect(self, remote_address: str, remote_port: int) -> None:
        self.client_tcp_control.connect(remote_address, remote_port)
        
    def handle_commands(self) -> None:
        print("Type QUIT to exit this FTP client\n")
        print("Type HELP for a complete list of commands accepted by an FTP Server")

        while True:
            user_input = input(">>> ")

            if user_input.upper() == "QUIT":
                break

            cmd, args = get_command_and_args(user_input)

            if cmd == CommandTCP.PORT.cmd:
                try:
                    ip, port = parse_ip(user_input.split(" ")[1])
                    Thread(target=self.create_active_channel, args=(ip, port)).start()
                except ValueError as error:
                    print(str(error))
                
            self.client_tcp_control.send(user_input.encode("utf-8"))
            data = self.client_tcp_control.receive().decode()
            
            if cmd == CommandTCP.PASV.cmd and data.startswith(str(CodeFTP.ENTERING_PSV_MODE.code)):
                match = re.search(r"\((\d+,\d+,\d+,\d+,\d+,\d+)\)", data)
                if match is not None:
                    ip, port = parse_ip(match.group(1))
                    Thread(target=self.create_passive_channel, args=(ip, port)).start()

            print(data)
            print()
            
        self.close()

    def create_passive_channel(self, ip: str, port: int) -> None:
        self.client_tcp_data = ClientTCP()
        self.client_tcp_data.connect(ip, port)
        while True:
            self.receive_file(self.client_tcp_data.socket)

    def create_active_channel(self, ip: str, port: int) -> None:
        self.serverTCP = ServerTCP(ip, port)
        own_ftp_server_socket, ftp_server_address = self.serverTCP.accept()
        while True:
            self.receive_file(own_ftp_server_socket)

    def receive_file(self, ftp_socket: socket) -> None:
        if self.file_name is None:
            filename = ftp_socket.recv(2048)
            self.file_name = filename.decode("utf-8")
        
        with open(f"{self.root_dir}/{self.file_name}", "wb") as f:
            while True:
                buf = ftp_socket.recv(self.buffer_size)
                f.write(buf)
                if len(buf) < self.buffer_size:
                    break
        self.file_name = None

    def close(self) -> None:
        if self.serverTCP is not None:
            self.serverTCP.close()
        if self.client_tcp_data is not None:
            self.client_tcp_data.close()
        self.client_tcp_control.close()
