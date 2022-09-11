from typing import List, Tuple


def get_command_and_args(string: str) -> Tuple[str, List[str]]:
    data = list(filter(None, string.split(" ")))
    cmd = data[0]
    args = data[1:]
    return cmd, args
