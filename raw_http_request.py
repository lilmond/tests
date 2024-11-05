# I haven't tested this code, just wrote it on GitHub using my browser for my 10 years daily contribution streak.

from urllib.parse import urlparse
import threading
import argparse
import socket
import ssl

def main():
  parser = argparse.ArgumentParser("URL", type=str, help="Target full URL")
  args = parser.parse_args()
  
  parsed_url = urlparse(args.URL)

  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.connect((parsed_url.hostname, parsed_url.port or (443 if parsed_url.scheme == "https" else 80)))

  if parsed_url.scheme == "https":
    ctx = ssl._create_unverified_context()
    sock = ctx.wrap_socket(sock=sock, server_hostname=parsed_url.hostname)

  headers = {
    "Host": parsed_url.hostname,
    "User-Agent": "Python Raw HTTP Request"
  }

  http_data = f"GET {parsed_url.path or '/'} HTTP/1.1\r\n"

  for header in headers:
    http_data += f"{header}: {headers[header]}\r\n"

  http_data += "\r\n"
  
  sock.send(http_data.encode())

  while True:
    sock.recv(1024)

if __name__ == "__main__":
    main()
