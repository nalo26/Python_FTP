from ipaddress import ip_address
from typing import Tuple


def parse_ip(values: str) -> Tuple[str, int]:
    args = values.split(",")

    if len(args) != 6:
        raise ValueError()

    e, f = args[4:6]

    if not e.isdigit() or not f.isdigit():
        raise ValueError()

    port = 256 * int(e) + int(f)

    if not 1023 < port < 65536:
        raise ValueError("Port must be comprised between 1024 and 65535")

    a, b, c, d = args[0:4]

    try:
        ip = ".".join((a, b, c, d))
        ip_address(ip)  # checks validity of ip

    except ValueError:
        raise ValueError("Not a valid IP address")

    return ip, port
