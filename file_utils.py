import os
from typing import List, Tuple


def is_user_granted_permissions(path: List[str], username: str) -> bool:
    permissions_file = os.path.join(os.curdir, "/".join(path), "__permissions__")
    if os.path.exists(permissions_file):
        with open(permissions_file, "r", encoding="utf-8") as file:
            lines = file.readlines()
            return username in lines
    else:
        return False


def dir(path: List[str]) -> List[str]:
    return os.listdir(os.path.join(os.curdir, "/".join(path)))


def cwd(current_path: List[str], new_path: str) -> Tuple[List[str], bool]:
    updated_path = current_path.copy()
    updated_path.append(new_path)
    if os.path.exists(os.path.join(os.curdir, "/".join(updated_path))):
        return updated_path, True
    return current_path, False


def pwd(path: List[str]) -> str:
    return "/".join(path)


def retr(path: List[str], file_name: str) -> (bytes or None):
    file_path = os.path.join(os.curdir, "/".join(path), file_name)
    if os.path.exists(file_path):
        return open(file_path, "rb").read()
    return None
