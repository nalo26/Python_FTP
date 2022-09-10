from enum import Enum


class CommandTCP(Enum):
    CWD = ("CWD", "Change working directory", "directory")
    HELP = (
        "HELP",
        "Returns usage documentation on a command if specified, else a general help document is returned",
        "command"
    )
    LIST = ("LIST", "Returns information of a file or directory if specified, "
                    "else information of the current working directory is returned", None)
    PASS = ("PASS", "Authentication password", "password")
    PASV = ("PASV", "Enter passive mode", None)
    PORT = ("PORT", "Specifies an address and port to which the server should connect", "a,b,c,d,e,f")
    PWD = ("PWD", "Print working directory. Returns the current directory of the host", None)
    RETR = ("RETR", "Retrieve a copy of the file", "file")
    USER = ("USER", "Authentication username", "username")

    def __init__(self, command_string: str, description: str, arg: str or None) -> None:
        self.cmd = command_string
        self.description = description
        self.arg = arg

    def help(self):
        return f"{self.cmd} <{self.arg}>\t## {self.description}"


# https://en.wikipedia.org/wiki/List_of_FTP_server_return_codes
class CodeFTP(Enum):
    OK = (200, "OK")
    ENTERING_PSV_MODE = (227, "Entering passive mode")
    LOGGED_IN = (230, "User logged in. Type HELP to get a list of available commands")
    USERNAME_OK_NEED_PWD = (331, "Username OK, need password")
    NO_DATA_CONNECTION = (425, "Cannot open data connection")
    WRONG_USERNAME_OR_PWD = (430, "Wrong username or password")
    SYNTAX_ERROR = (501, "Syntax error in parameters or arguments")
    COMMAND_NOT_IMPL = (502, "Command not implemented")
    REQUEST_DENIED = (534, "Request denied")
    FILE_NOT_AVAILABLE = (550, "File or directory not available")

    def __init__(self, code: int, message: str) -> None:
        self.code = code
        self.message = message

    def __str__(self) -> str:
        return f"{self.code} {self.message}"
