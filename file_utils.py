import os


def is_user_granted_permissions(path: list[str], username: str) -> bool:
    permissions_file = os.path.join(os.curdir, "/".join(path), "__permissions__")
    if os.path.exists(permissions_file):
        with open(permissions_file, "r") as file:
            lines = file.readlines()
            if username in lines:
                return True
    else:
        return False


def dir(path: list[str]) -> list[str]:
    return os.listdir(os.path.join(os.curdir, "/".join(path)))


def cwd(current_path: list[str], new_path: str) -> tuple[list[str], bool] or bool:
    updated_path = current_path.copy()
    updated_path.append(new_path)
    if os.path.exists(os.path.join(os.curdir, "/".join(updated_path))):
        return updated_path, True
    return current_path, False


def pwd(path: list[str]) -> str:
    return "/".join(path)


def retr(path: list[str], file_name: str) -> (bytes or None):
    file_path = os.path.join(os.curdir, "/".join(path), file_name)
    if os.path.exists(file_path):
        return open(file_path, "rb").read()
    return None
    