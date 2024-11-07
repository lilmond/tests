from urllib.parse import urlparse
import asyncio
import ssl

async def fetch_http(url: str, receive: bool = True):
    parsed_url = urlparse(url)
    host = parsed_url.hostname
    port = parsed_url.port or (443 if parsed_url.scheme == "https" else 80)
    path = parsed_url.path or "/"

    if parsed_url.scheme == "https":
        ssl_context = ssl._create_unverified_context()
    else:
        ssl_context = None

    try:
        reader, writer = await asyncio.open_connection(host, port, ssl=ssl_context)

        request = f"GET {path} HTTP/1.1\r\nHost: {parsed_url.hostname}\r\nConnection: close\r\n\r\n"
        writer.write(request.encode())
        await writer.drain()

        if receive:
            response = []
            while True:
                line = await reader.readline()
                if not line:
                    break
                response.append(line.decode())
            
            writer.close()
            await writer.wait_closed()

            return "".join(response)
        
        writer.close()
        await writer.wait_closed()

    except Exception as e:
        print(f"Error: {e}")


async def main():
    url = "https://www.roblox.com/"
    receive = True

    # Single request
    #response = await fetch_http(url)
    #print(response)
    
    # Concurrent requests
    tasks = [fetch_http(url=url, receive=receive) for _ in range(50)]
    responses = await asyncio.gather(*tasks)

    for i, response in enumerate(responses, 1):
        print(f"[{i}] {response}")


asyncio.run(main())
