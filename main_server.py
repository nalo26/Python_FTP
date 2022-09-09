from server_ftp import ServerFTP, User

if __name__ == "__main__":
    server = ServerFTP("127.0.0.1", 4001, "server_root")
    server.add_user(User("toto", "password"))

    server.listen_for_new_connections()
