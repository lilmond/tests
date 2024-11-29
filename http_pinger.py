from urllib.parse import urlparse
import argparse
import logging
import socket
import socks
import time
import ssl
import sys
import os

class Colors:
    RED = "\u001b[31;1m"
    GREEN = "\u001b[32;1m"
    YELLOW = "\u001b[33;1m"
    BLUE = "\u001b[34;1m"
    RESET = "\u001b[0;0m"

def clear_console():
    if sys.platform == "win32":
        os.system("cls")
    elif sys.platform in ["linux", "linux2"]:
        os.system("clear")

def main():
    parser = argparse.ArgumentParser(description="A simple HTTP server pinger.")
    parser.add_argument("url", metavar="URL", type=str, help="Target's full URL.")
    parser.add_argument("-d", "--delay", type=float, default=1.0, help="Sleep time between requests.")
    parser.add_argument("-t", "--timeout", metavar="TIMEOUT", type=int, default=5, help="Socket connection timeout value.")
    parser.add_argument("-p", "--proxy", type=str, help="Use proxy to ping? Type the address if so, example: socks5://127.0.0.1:9050")
    parser.add_argument("-gr", "--get-response", action="store_true", default=False, help="Whether to receive response header and body from the server and print it in the terminal.")
    parser.add_argument("--header", dest="headers", action="append", help="Add a custom header. Example: \"--header Authorization: token123\"")
    parser.add_argument("--tor", action="store_true", help="Use Tor proxies, basically connect to socks5://127.0.0.1:9050 by default")

    args = parser.parse_args()

    parsed_url = urlparse(args.url)

    if not parsed_url.port:
        if parsed_url.scheme == "https":
            port = 443
        else:
            port = 80
    else:
        port = int(parsed_url.port)

    hostname = parsed_url.hostname

    socket.setdefaulttimeout(args.timeout)
    
    logging.basicConfig(
        format="[%(asctime)s] %(message)s",
        datefmt="%H:%M:%S",
        level=logging.INFO,
    )

    clear_console()

    logging.info(f"Initializing HTTP Pinger on {Colors.GREEN}{hostname}:{port}{Colors.RESET}...")

    sequence = 1

    while True:
        try:
            if args.tor:
                sock = socks.socksocket(socket.AF_INET, socket.SOCK_STREAM)
                sock.set_proxy(proxy_type=socks.SOCKS5, addr="127.0.0.1", port=9050)
            elif args.proxy:
                proxy_url = urlparse(args.proxy)
                proxy_type = getattr(socks, f"PROXY_TYPE_{proxy_url.scheme.upper()}")

                sock = socks.socksocket(socket.AF_INET, socket.SOCK_STREAM)
                sock.set_proxy(proxy_type=proxy_type, addr=proxy_url.hostname, port=proxy_url.port)
            else:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            try:
                connect_time = time.time()
                sock.connect((hostname, port))
                connected_time = time.time()
            except Exception:
                time.sleep(1)
                logging.info(f"{Colors.RED}Connection failed.{Colors.RESET}")
                continue

            connection_timestamp_ms = f"{((connected_time - connect_time) * 1000):.2f}"

            if parsed_url.scheme == "https":
                ctx = ssl._create_unverified_context()
                sock = ctx.wrap_socket(sock=sock, server_hostname=hostname)


            http_headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                #"accept-encoding": "gzip, deflate, br, zstd",
                "Accept-Language": "en-US,en;q=0.9",
                "Connection": "keep-alive",
                "Dnt": "1",
                "Host": f"{hostname}" + (f":{port}" if not port in [80, 443] else ""),
                "Sec-Ch-Ua": "\"Microsoft Edge\";v=\"129\", \"Not=A?Brand\";v=\"8\", \"Chromium\";v=\"129\"",
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": "\"Windows\"",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0"
            }

            if args.headers:
                for header in args.headers:
                    header_name, header_value = header.split(":", 1)
                    header_name = header_name.strip().lower()
                    header_value = header_value.strip()

                    http_headers[header_name] = header_value

            http_header = f"GET {parsed_url.path if parsed_url.path else '/'} HTTP/1.1\r\n"

            for header in http_headers:
                http_header += f"{header}: {http_headers[header]}\r\n"
            
            http_header += "\r\n"

            sock.send(http_header.encode())

            first_line = b""

            while True:
                chunk = sock.recv(1)

                if not chunk:
                    raise Exception("Connection closed unexpectedly.")
                
                first_line += chunk

                if first_line.endswith(b"\r\n"):
                    break
            
            http_code = first_line.decode().split(" ", 1)[1].strip()

            if http_code.startswith("2"):
                color = Colors.GREEN
            else:
                color = Colors.RED

            logging.info(f"{color}({sequence}) Ping: {connection_timestamp_ms} ms | {http_code}{Colors.RESET}")

            if args.get_response:
                # Get response headers
                headers_data = b""

                while True:
                    chunk = sock.recv(1)
                    
                    if not chunk:
                        raise Exception("Connection closed unexpectedly.")

                    headers_data += chunk

                    if headers_data.endswith(b"\r\n\r\n"):
                        break
                
                # Response headers dictionary
                headers_dict = {}

                for line in headers_data.decode().strip().splitlines():
                    header_name, header_value = line.split(":", 1)
                    header_name = header_name.strip().lower()
                    header_value = header_value.strip()

                    headers_dict[header_name] = header_value
                                
                logging.info(f"{Colors.BLUE}({sequence}) Response Headers:{Colors.RESET}\n{headers_data.decode(errors='replace')}")

                # Get response body
                body_data = b""

                while True:
                    try:
                        if headers_dict.get("content-length"):
                            if int(headers_dict["content-length"]) <= 0:
                                break

                        chunk = sock.recv(1)
                        
                        if not chunk:
                            raise Exception("Connection closed unexpectedly.")
                        
                        body_data += chunk

                        if body_data.endswith(b"\r\n\r\n"):
                            break

                        if headers_dict.get("content-length"):
                            if len(body_data) >= int(headers_dict["content-length"]):
                                break

                    except socket.timeout:
                        print("Timed out while receiving body response...")
                        break

                if body_data:
                    logging.info(f"{Colors.BLUE}({sequence}) Response Body:{Colors.RESET}\n{body_data.decode(errors='replace')}")
                else:
                    logging.info(f"{Colors.BLUE}({sequence}) No Response Body.{Colors.RESET}")

            sequence += 1

            time.sleep(args.delay)
        except Exception as e:
            logging.info(f"{Colors.RED}ERROR: {e}{Colors.RESET}")
            time.sleep(args.delay)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        exit()
