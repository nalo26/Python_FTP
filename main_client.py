from client_ftp import ClientFTP


if __name__ == "__main__":
    client_ftp = ClientFTP(".")
    client_ftp.connect("127.0.0.1", 4021)
    client_ftp.handle_commands()
