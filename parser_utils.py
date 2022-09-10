def get_command_and_args(string: str) -> tuple[str, list[str]]:
    data = string.split(" ")
    cmd = data[0]
    args = data[1:]
    return cmd, args
