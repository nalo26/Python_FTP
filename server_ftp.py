import threading
from socket import socket
from enum import Enum

from server_tcp import ServerTCP
from enums import CommandTCP as CMD
from enums import CodeFTP
import file_utils


class User:
    def __init__(self, username: str = None, password: str = None) -> None:
        self.username = username
        self.password = password
        self.isAuthenticated = False

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, User)
            and other.username == self.username
            and other.password == self.password
        )

    def __str__(self) -> str:
        return f"User {self.username}"


class ServerFTP:
    class LoginState(Enum):
        ACCEPTED = 0
        WAITING_FOR_PWD = 1
        WRONG_CREDENTIAL = 2

    def __init__(self, address: str, port: int, rootDir: str) -> None:
        self.serverTCP = ServerTCP(address, port)
        self.address = address
        self.port = port
        self.currentDir = rootDir.split("/")
        self.users = []

    def add_user(self, user: User) -> None:
        self.users.append(user)

    def login(self, user: User) -> LoginState:
        if user in self.users:
            user.isAuthenticated = True
            return self.LoginState.ACCEPTED

        if user.username in [u.username for u in self.users]:
            return self.LoginState.WAITING_FOR_PWD

        if user.username == "anonymous":
            if user.password in (None, ""):
                return self.LoginState.WAITING_FOR_PWD
            return self.LoginState.ACCEPTED

        return self.LoginState.WRONG_CREDENTIAL

    def listen_for_new_connections(self) -> None:
        while True:
            socket, address = self.serverTCP.accept()
            thread = threading.Thread(
                target=self.handle_client, args=(socket, address)
            )
            thread.start()

    def handle_client(self, client: socket, address: str) -> None:
        user = User()

        while True:
            data = client.recv(2048).decode()
            response = CodeFTP.OK

            if not user.isAuthenticated:
                response = self.handle_unauthenticated_client(data, user)

            else:
                response = self.handle_authenticated_client(data, user)

            client.send(str(response).encode("utf-8"))

    def handle_unauthenticated_client(
        self, raw_data: str, user: User
    ) -> CodeFTP:
        cmd, data = raw_data.split(" ")

        if cmd.startswith(CMD.USER.value) or cmd.startswith(CMD.PASS.value):
            if len(data) < 2:
                return CodeFTP.SYNTAX_ERROR

            if cmd.startswith(CMD.USER.value):
                user.username = data

            elif cmd.startswith(CMD.PASS.value):
                user.password = data

            login_state = self.login(user)

            if login_state == self.LoginState.ACCEPTED:
                return CodeFTP.LOGGED_IN

            if login_state == self.LoginState.WRONG_CREDENTIAL:
                return CodeFTP.WRONG_USERNAME_OR_PWD

            return CodeFTP.USERNAME_OK_NEED_PWD

        return CodeFTP.COMMAND_NOT_IMPL

    def handle_authenticated_client(self, data: str, user: User):
        response = CodeFTP.COMMAND_NOT_IMPL

        if data.startswith(CMD.CWD.value):
            if len(data.split(" ")) < 2:
                return CodeFTP.SYNTAX_ERROR

            path = data.split(" ")[1]
            if "/" in path:
                return CodeFTP.SYNTAX_ERROR

            is_valid_path = True
            if path == "..":
                self.currentDir.pop()
            else:
                self.currentDir, is_valid_path = file_utils.cwd(self.currentDir, path)

            if is_valid_path:
                response = CodeFTP.OK
                response.message = file_utils.pwd(self.currentDir)
            else:
                response = CodeFTP.FILE_NOT_AVAILABLE

        elif data.startswith(CMD.DIR.value):
            response = CodeFTP.OK
            response.message = " ".join(file_utils.dir(self.currentDir))

        elif data.startswith(CMD.PASV.value):
            pass

        elif data.startswith(CMD.PORT.value):
            pass

        elif data.startswith(CMD.PWD.value):
            response = CodeFTP.OK
            response.message = file_utils.pwd(self.currentDir)

        elif data.startswith(CMD.RETR.value):
            if len(data.split(" ")) < 2:
                return CodeFTP.SYNTAX_ERROR
            file_name = data.split(" ")[1]
            file_content = file_utils.retr(self.currentDir, file_name)
            if file_content is None:
                response = CodeFTP.FILE_NOT_AVAILABLE
            else:
                response = CodeFTP.OK
                response.message = file_content

        return response
