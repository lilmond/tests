# I will continue this tomorrow after playing CS2

import threading
import socket
import json

class Client(object):
    hostname = None
    username = None
    platform = None

    def __init__(self, client_sock: socket.socket, client_address: tuple):
        self.client_sock = client_sock
        self.client_address = client_address
        self.recv_login()
    
    def recv_message(self):
        message = b""

        while True:
            chunk = self.client_sock.recv(1)
            if not chunk:
                raise Exception("Connection closed unexpectedly")
            
            message += chunk
            if message.endswith(b"\r\n\r\n"):
                break
        
        return json.loads(message)

    def send_message(self, message: dict):
        return self.client_sock.send(f"{json.dumps(message)}\r\n\r\n".encode())

    def recv_login(self):
        login_message = self.recv_message()

        try:
            if not login_message["op"] == "LOGIN":
                raise Exception

            login_data = login_message["data"]

            self.hostname = login_data["hostname"]
            self.username = login_data["username"]
            self.platform = login_data["platform"]
        except Exception:
            print(f"{self.client_address} sent an invalid log in data: {login_message}\n")
            return

        print(f"{self.client_address} logged In:\n{login_message}")

class BasicCNC(object):
    clients = []

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
    
    def start(self):
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((self.host, self.port))
        server_sock.listen()

        while True:
            client_sock, client_address = server_sock.accept()
            threading.Thread(target=self.on_client_connect, args=[client_sock, client_address], daemon=True).start()
    
    def on_client_connect(self, client_sock: socket.socket, client_address: tuple):
        client = Client(client_sock=client_sock, client_address=client_address)
        print(f"{client.username} has logged in!")

def main():
    c2 = BasicCNC(host="0.0.0.0", port=4444)
    threading.Thread(target=c2.start, daemon=True).start()

    while True:
        full_command = input(">")

        try:
            command, args = full_command.split(" ", 1)
            args = args.split(" ")
        except Exception:
            command = full_command
            args = []
        
        print(f"Command: {command}\nArgs: {args}")

if __name__ == "__main__":
    main()
