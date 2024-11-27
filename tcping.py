import argparse
import socket
import time

def main():
    parser = argparse.ArgumentParser(description="A simple TCP pinger written in Python.")
    parser.add_argument("hostname", type=str, help="Target hostname.")
    parser.add_argument("-p", "--port", type=int, default=80, help="Target port.")
    parser.add_argument("-t", "--timeout", type=int, default=10, help="Connection timeout value.")
    
    args = parser.parse_args()

    try:
        hostname = socket.gethostbyname(args.hostname)
    except Exception:
        print("Error: Invalid hostname.")
        return
    
    port = args.port

    if any([port < 1, port > 65535]):
        print("Error: Invalid port value.")
        return
    
    socket.setdefaulttimeout(args.timeout)

    while True:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            connect_time = time.time()
            sock.connect((hostname, port))
            connected_time = time.time()
            timestamp = connected_time - connect_time
        except Exception as e:
            print(f"Error: {e}")
            continue

        print(f"Ping: {(timestamp * 1000):.2f} ms")
        time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        exit()
