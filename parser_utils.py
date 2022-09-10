def get_command_and_args(string: str) -> tuple[str, list[str]]:
    data = list(filter(None, string.split(" ")))
    cmd = data[0]
    args = data[1:]
    return cmd, args
