from enum import Enum
from socket import socket
from threading import Thread
from typing import List

from client_tcp import ClientTCP
from enums import CommandTCP, CodeFTP
import file_utils
from ip_utils import parse_ip
from parser_utils import get_command_and_args
from server_tcp import ServerTCP


class User:
    def __init__(self, username: str = None, password: str = None) -> None:
        self.username = username
        self.password = password
        self.is_authenticated = False

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, User)
            and other.username == self.username
            and other.password == self.password
        )

    def __str__(self) -> str:
        return f"User {self.username}"


class FileChannel:
    def __init__(
        self,
        client_ip: str,
        file_sender: (ClientTCP or ServerTCP),
        client_socket: socket = None,
    ):
        self.client_ip = client_ip
        self.sender = file_sender
        self.socket = client_socket

    def send(self, data):
        if isinstance(self.sender, ClientTCP):
            self.sender.send(data)
        else:  # ServerTCP
            self.socket.send(data)


class ServerFTP:
    class LoginState(Enum):
        ACCEPTED = 0
        WAITING_FOR_PWD = 1
        WRONG_CREDENTIAL = 2

    def __init__(self, address: str, port: int, root_dir: str) -> None:
        self.serverTCP = ServerTCP(address, port)
        self.address = address
        self.port = port
        self.current_dir = root_dir.split("/")
        self.users: List[User] = []
        self.clients: List[FileChannel] = []

    def add_user(self, user: User) -> None:
        self.users.append(user)

    def login(self, user: User) -> LoginState:
        if user in self.users:
            user.is_authenticated = True
            return self.LoginState.ACCEPTED

        if user.username == "anonymous":
            if user.password in (None, ""):
                return self.LoginState.WAITING_FOR_PWD
            return self.LoginState.ACCEPTED

        if user.username in [u.username for u in self.users]:
            if user.password in (None, ""):
                return self.LoginState.WAITING_FOR_PWD
            return self.LoginState.WRONG_CREDENTIAL

        return self.LoginState.WRONG_CREDENTIAL

    def listen_for_new_connections(self) -> None:
        while True:
            client_socket, client_address = self.serverTCP.accept()
            Thread(
                target=self.handle_client, args=(client_socket, client_address)
            ).start()

    def handle_client(self, client_socket: socket, client_address) -> None:
        user = User()

        while True:
            data = client_socket.recv(2048).decode()
            if data == "":
                continue
            cmd, args = get_command_and_args(data)
            response = self.handle_client_commands(cmd, args, user, client_address)
            client_socket.send(str(response).encode("utf-8"))

    def handle_client_commands(
        self, cmd: str, args: List[str], user: User, client_address
    ) -> CodeFTP:
        if cmd not in [tcp_c.cmd for tcp_c in CommandTCP]:
            return CodeFTP.COMMAND_NOT_IMPL

        if cmd == CommandTCP.HELP.cmd:
            return self.handle_help()

        if cmd == CommandTCP.USER.cmd or cmd == CommandTCP.PASS.cmd:
            return self.handle_user_and_password(cmd, args, user)

        if not user.is_authenticated:
            return CodeFTP.COMMAND_NOT_IMPL

        if cmd == CommandTCP.CWD.cmd:
            return self.handle_cwd(args, user)

        if cmd == CommandTCP.LIST.cmd:
            return self.handle_list()

        if cmd == CommandTCP.PASV.cmd:
            return self.handle_pasv()

        if cmd == CommandTCP.PORT.cmd:
            return self.handle_port(args)

        if cmd == CommandTCP.PWD.cmd:
            return self.handle_pwd()

        if cmd == CommandTCP.RETR.cmd:
            return self.handle_retr(args, user, client_address)

        return CodeFTP.COMMAND_NOT_IMPL

    def accept_client(self, file_sender: ServerTCP) -> None:
        client_socket, client_address = file_sender.accept()
        self.clients.append(FileChannel(client_address[0], file_sender, client_socket))

    def handle_help() -> CodeFTP:
        response = CodeFTP.OK
        response.message += "\n"
        response.message += "\n".join([tcp_c.help() for tcp_c in CommandTCP])
        return response

    def handle_user_and_password(
        self, cmd: str, args: List[str], user: User
    ) -> CodeFTP:
        if len(args) != 1:
            return CodeFTP.SYNTAX_ERROR

        if cmd == CommandTCP.USER.cmd:
            user.username = args[0]

        elif cmd.startswith(CommandTCP.PASS.cmd):
            user.password = args[0]

        login_state = self.login(user)

        if login_state == self.LoginState.ACCEPTED:
            return CodeFTP.LOGGED_IN

        if login_state == self.LoginState.WRONG_CREDENTIAL:
            return CodeFTP.WRONG_USERNAME_OR_PWD

        return CodeFTP.USERNAME_OK_NEED_PWD

    def handle_cwd(self, args: List[str], user: User) -> CodeFTP:
        if len(args) != 1:
            return CodeFTP.SYNTAX_ERROR

        path = args[0]
        if "/" in path:
            return CodeFTP.SYNTAX_ERROR

        is_valid_path = True
        if path == "..":
            self.current_dir.pop()
        else:
            pathToCheck, is_valid_path = file_utils.cwd(self.current_dir, path)
            if file_utils.is_user_granted_permissions(pathToCheck, user.username):
                self.current_dir = pathToCheck
            else:
                return CodeFTP.REQUEST_DENIED

        if is_valid_path:
            response = CodeFTP.OK
            response.message = file_utils.pwd(self.current_dir)
        else:
            response = CodeFTP.FILE_NOT_AVAILABLE

        return response

    def handle_list(self) -> CodeFTP:
        response = CodeFTP.OK
        response.message = " ".join(file_utils.dir(self.current_dir))
        return response

    def handle_pasv(self) -> CodeFTP:
        file_sender = ServerTCP(self.address, None)
        Thread(target=self.accept_client, args=(file_sender,)).start()

        port = file_sender.socket.getsockname()[1]

        e = port // 256
        f = port % 256

        response = CodeFTP.ENTERING_PSV_MODE
        response.message += f" ({self.address.replace('.', ',')},{e},{f})"
        return response

    def handle_port(self, args: List[str]) -> CodeFTP:
        args = args[0]

        try:
            ip, port = parse_ip(args)
        except ValueError as error:
            response = CodeFTP.SYNTAX_ERROR
            response.message = str(error)
            return response

        file_sender = ClientTCP()
        file_sender.connect(ip, port)

        self.clients.append(FileChannel(ip, file_sender))

        return CodeFTP.OK

    def handle_pwd(self) -> CodeFTP:
        response = CodeFTP.OK
        response.message = file_utils.pwd(self.current_dir)
        return response

    def handle_retr(self, args: List[str], user: User, client_address) -> CodeFTP:
        if len(args) != 1:
            return CodeFTP.SYNTAX_ERROR
        try:
            file_sender = [c for c in self.clients if c.client_ip == client_address[0]][
                0
            ]
        except IndexError:  # client not in list
            return CodeFTP.NO_DATA_CONNECTION

        file_name = args[0]
        if file_utils.is_user_granted_permissions(self.current_dir, user.username):
            file_content = file_utils.retr(self.current_dir, file_name)
        else:
            return CodeFTP.REQUEST_DENIED
        if file_content is None:
            return CodeFTP.FILE_NOT_AVAILABLE

        file_sender.send(file_name.encode("utf-8"))
        file_sender.send(file_content)

        response = CodeFTP.OK
        response.message = "Success"
        return response
