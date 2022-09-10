def get_command_and_args(string: str) -> (str, list[str]):
    data = list(filter(None, string.split(" ")))
    cmd = data[0]
    args = data[1:] if len(data) > 1 else []
    return cmd, args
