import struct
import socket

def build_dns_query(domain):
    transaction_id = 0x1234
    flags = 0x0100
    qdcount = 1
    ancount = 0
    nscount = 0
    arcount = 0

    header = struct.pack(">HHHHHH", transaction_id, flags, qdcount, ancount, nscount, arcount)

    qname = b"".join(struct.pack("B", len(part)) + part.encode() for part in domain.split(".")) + b"\x00"

    qtype = 1
    qclass = 1

    question = struct.pack(">HH", qtype, qclass)

    dns_query = header + qname + question
    return dns_query

def parse_dns_response(response):
    transaction_id, flags, qdcount, ancount, nscount, arcount = struct.unpack(">HHHHHH", response[:12])
    print(f"Transaction ID: {transaction_id}\nFlags: {flags}\nQuestions: {qdcount}\nAnswers RRs: {ancount}\nAuthority RRs: {nscount}\nAdditional RRs: {arcount}\n")

    offset = 12
    while response[offset] != 0:
        offset += 1
    offset += 5

    answers = []
    for _ in range(ancount):
        name = struct.unpack("H", response[offset:offset+2])[0]
        offset += 2

        type_, class_, ttl, rdlength = struct.unpack(">HHIH", response[offset:offset+10])
        offset += 10

        if type_ == 1:
            ip = struct.unpack(">BBBB", response[offset:offset+4])
            ip_address = ".".join(map(str, ip))
            answers.append(ip_address)
        offset += rdlength
    
    return answers


def send_dns_request(domain, server="8.8.8.8"):
    dns_query = build_dns_query(domain=domain)

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.settimeout(2)
        s.sendto(dns_query, (server, 53))
    
        try:
            response, _ = s.recvfrom(512)
            return response
        except soket.timeout:
            print("Request timed out")
            return None

domain = "www.roblox.com"
response = send_dns_request(domain=domain)

if response:
    ip_addresses = parse_dns_response(response)
    if ip_addresses:
        print(f"Resolved IP Addresses: {ip_addresses}")
    else:
        print(f"No A records found")
else:
    print(f"No response received")
