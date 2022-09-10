from client_ftp import ClientFTP


if __name__ == "__main__":
    client_ftp = ClientFTP()
    client = client_ftp.clientTCP
    client.connect("127.0.0.1", 4021)

    while True:
        cmd = input(">>> ")
        if cmd.upper() == "QUIT":
            break
        client.send(cmd)
        data = client.receive()
        print(data.decode())
        print()

    client.close()
