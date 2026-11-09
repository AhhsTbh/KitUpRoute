import pytest
from dnslib import DNSRecord, RCODE
from app.ps5_dns import DNSProxy, is_allowed, parse_allowed_networks


def test_allowlist():
    networks = parse_allowed_networks("192.168.1.50/32,127.0.0.1/32")
    assert is_allowed("192.168.1.50", networks)
    assert not is_allowed("192.168.1.51", networks)


def test_open_resolver_forbidden():
    with pytest.raises(ValueError):
        parse_allowed_networks("0.0.0.0/0")
    with pytest.raises(ValueError):
        parse_allowed_networks("")


def test_unauthorized_request_refused_without_upstream():
    proxy = DNSProxy(allowed_cidrs="192.168.1.50/32")
    query = DNSRecord.question("example.org").pack()
    response = DNSRecord.parse(proxy.query(query, "192.168.1.51"))
    assert response.header.rcode == RCODE.REFUSED


def test_upstream_failure_is_servfail():
    proxy = DNSProxy(upstream="127.0.0.1", upstream_port=1, allowed_cidrs="127.0.0.1/32", timeout=0.1)
    query = DNSRecord.question("example.org").pack()
    response = DNSRecord.parse(proxy.query(query, "127.0.0.1"))
    assert response.header.rcode == RCODE.SERVFAIL
