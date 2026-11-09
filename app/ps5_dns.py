"""LAN-only DNS forwarder for a PS5 using manual DNS settings.

This is a conventional DNS proxy, NOT a VPN, matchmaking-region selector, or
game-packet relay. Do not expose UDP/TCP port 53 to the public internet.
"""
import argparse
import ipaddress
import logging
import os
import socket
import socketserver
from dnslib import DNSRecord, RCODE

LOG = logging.getLogger("kitup.ps5_dns")


def parse_allowed_networks(value):
    """Explicit CIDR allowlist. Never default to an unrestricted resolver."""
    networks = [ipaddress.ip_network(part.strip(), strict=False)
                for part in value.split(",") if part.strip()]
    if not networks:
        raise ValueError("KITUP_DNS_ALLOWED_CIDRS must contain at least one CIDR")
    if any(net.prefixlen == 0 for net in networks):
        raise ValueError("Unrestricted 0.0.0.0/0 or ::/0 is forbidden")
    return networks


def is_allowed(address, networks):
    ip = ipaddress.ip_address(address)
    return any(ip in net for net in networks)


def failure_reply(packet, code):
    try:
        request = DNSRecord.parse(packet)
        response = request.reply()
        response.header.rcode = code
        return response.pack()
    except Exception:
        return b""


class DNSProxy:
    def __init__(self, upstream="1.1.1.1", upstream_port=53, allowed_cidrs="127.0.0.1/32", timeout=3):
        self.upstream = upstream
        self.upstream_port = upstream_port
        self.allowed = parse_allowed_networks(allowed_cidrs)
        self.timeout = timeout

    def query(self, packet, client_ip):
        if not is_allowed(client_ip, self.allowed):
            LOG.warning("Denied DNS request from %s", client_ip)
            return failure_reply(packet, RCODE.REFUSED)
        try:
            request = DNSRecord.parse(packet)
            with socket.create_connection((self.upstream, self.upstream_port), timeout=self.timeout) as sock:
                sock.sendall(len(packet).to_bytes(2, "big") + packet)
                length_bytes = recv_exact(sock, 2)
                length = int.from_bytes(length_bytes, "big")
                answer = recv_exact(sock, length)
            reply = DNSRecord.parse(answer)
            reply.header.id = request.header.id
            return reply.pack()
        except (OSError, ValueError, EOFError, Exception) as exc:
            LOG.warning("Upstream DNS request failed: %s", exc)
            return failure_reply(packet, RCODE.SERVFAIL)


def recv_exact(sock, count):
    data = bytearray()
    while len(data) < count:
        chunk = sock.recv(count - len(data))
        if not chunk:
            raise EOFError("DNS upstream disconnected")
        data.extend(chunk)
    return bytes(data)


class UDPServer(socketserver.ThreadingUDPServer):
    allow_reuse_address = True
    daemon_threads = True


class TCPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


class UDPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        packet, transport = self.request
        answer = self.server.proxy.query(packet, self.client_address[0])
        if answer:
            transport.sendto(answer, self.client_address)


class TCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        while True:
            try:
                length = int.from_bytes(recv_exact(self.request, 2), "big")
                if length == 0:
                    return
                packet = recv_exact(self.request, length)
                answer = self.server.proxy.query(packet, self.client_address[0])
                if answer:
                    self.request.sendall(len(answer).to_bytes(2, "big") + answer)
            except (EOFError, OSError):
                return


def main():
    parser = argparse.ArgumentParser(description="KitUp PS5 LAN DNS proxy (not VPN)")
    parser.add_argument("--bind", default=os.getenv("KITUP_DNS_BIND", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.getenv("KITUP_DNS_PORT", "5353")))
    args = parser.parse_args()
    proxy = DNSProxy(
        upstream=os.getenv("KITUP_DNS_UPSTREAM", "1.1.1.1"),
        upstream_port=int(os.getenv("KITUP_DNS_UPSTREAM_PORT", "53")),
        allowed_cidrs=os.getenv("KITUP_DNS_ALLOWED_CIDRS", "127.0.0.1/32"),
    )
    import threading
    udp = UDPServer((args.bind, args.port), UDPHandler)
    tcp = TCPServer((args.bind, args.port), TCPHandler)
    udp.proxy = tcp.proxy = proxy
    logging.basicConfig(level=logging.INFO)
    LOG.info("KitUp LAN DNS listening on %s:%d UDP/TCP; NO game traffic routing", args.bind, args.port)
    thread = threading.Thread(target=tcp.serve_forever, daemon=True)
    thread.start()
    try:
        udp.serve_forever()
    finally:
        udp.server_close()
        tcp.shutdown()
        tcp.server_close()


if __name__ == "__main__":
    main()
