import os


def dir(path: list[str]) -> list[str]:
    return os.listdir(os.path.join(os.curdir, "/".join(path)))


def cwd(currentPath: list[str], newPath: str) -> tuple[list[str], bool]:
    updatedPath = currentPath.copy()
    updatedPath.append(newPath)
    if os.path.exists(os.path.join(os.curdir, "/".join(updatedPath))):
        return updatedPath, True
    return currentPath, False


def pwd(path: list[str]) -> str:
    return "/".join(path)


def retr(path: list[str], file_name: str) -> (str | None):
    file_path = os.path.join(os.curdir, "/".join(path), file_name)
    if os.path.exists(file_path):
        return open(file_path, "r").read()
    return None
    