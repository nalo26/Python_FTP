from enum import Enum


# https://en.wikipedia.org/wiki/List_of_FTP_server_return_codes
class CodeFTP(Enum):
    OK = (200, "OK")
    LOGGED_IN = (230, "User logged in")
    USERNAME_OK_NEED_PWD = (331, "Username OK, need password")
    WRONG_USERNAME_OR_PWD = (430, "Wrong username or password")
    SYNTAX_ERROR = (501, "Syntax error in parameters or arguments")
    COMMAND_NOT_IMPL = (502, "Command not implemented")
    FILE_NOT_AVAILABLE = (550, "File or directory not available")

    def __init__(self, code: int, message: str) -> None:
        self.code = code
        self.message = message

    def __str__(self) -> str:
        return f"{self.code} {self.message}"


class CommandTCP(Enum):
    USER = "USER"
    PASS = "PASS"
    DIR = "DIR"
    CWD = "CWD"
    RETR = "RETR"
    PASV = "PASV"
    PORT = "PORT"
    PWD = "PWD"
