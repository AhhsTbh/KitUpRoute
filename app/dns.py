"""Conventional forwarding DNS server; DOES NOT proxy or reroute games.
For local/authorized networks only. Avoid exposing an open recursive resolver.
"""
import os
import socket
import logging
from dnslib import DNSRecord, RCODE
from dnslib.server import BaseResolver, DNSServer, DNSLogger

logging.basicConfig(level=logging.INFO)
class Forwarder(BaseResolver):
 def __init__(self, upstream, port=53): self.upstream,self.port=upstream,port
 def resolve(self, request, handler):
  try:
   with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as s:
    s.settimeout(3)
    s.sendto(request.pack(),(self.upstream,self.port))
    data,_=s.recvfrom(65535)
   response=DNSRecord.parse(data)
   response.header.id=request.header.id
   return response
  except Exception:
   reply=request.reply();reply.header.rcode=RCODE.SERVFAIL;return reply

if __name__=='__main__':
 bind=os.getenv('DNS_BIND','127.0.0.1')
 port=int(os.getenv('DNS_PORT','5353'))
 upstream=os.getenv('DNS_UPSTREAM','1.1.1.1')
 print(f'KitUp DNS forwarding {bind}:{port} to {upstream}:53; no game traffic routing')
 server=DNSServer(Forwarder(upstream),port=port,address=bind,logger=DNSLogger('-request,-reply,-truncated,-error'))
 server.start()
