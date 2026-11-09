# KitUp Route cloud DNS deployment — first infrastructure milestone

**Status:** Deployment files prepared; no VPS provisioned, public DNS IP assigned, or PS5 connectivity verified.

## Purpose and limitations

The DNS gateway forwards ordinary DNS queries from an explicitly allowlisted public IP. It does not proxy game traffic, select matchmaking regions, change public IP addresses, or provide a VPN. Do not advertise those capabilities until real relays and console testing exist.

## Why a separate host

Render's current web service is HTTP-only for this use case; a PS5 needs a public IPv4 address with DNS available on UDP/TCP port 53. Deploy this gateway on a VPS with a public IPv4 address and inbound UDP/TCP 53 support. The service must be operated and secured by an authorized administrator.

## Deployment prerequisites

- A VPS with Docker Compose and a stable public IPv4 address.
- Firewall allowing inbound UDP/TCP 53 **only from authorized public IPs**. Also restrict outbound traffic to the DNS upstream as appropriate.
- The PS5 household's *public* IPv4 address (not the PS5's private 192.168.x.x address). If it changes, update the allowlist and firewall.
- Never set `KITUP_DNS_ALLOWED_CIDRS=0.0.0.0/0`. An open resolver can be abused for DNS amplification.

## Start

From the repository root on the VPS:

```bash
export KITUP_DNS_ALLOWED_CIDRS="YOUR_AUTHORIZED_PUBLIC_IPV4/32"
docker compose -f deploy/dns-compose.yml up -d --build
```

Configure the VPS firewall to allow only the same authorized public IP to reach UDP/TCP 53. Set the PS5's Primary DNS to the VPS public IPv4 address, test its Internet Connection, and confirm DNS queries appear in server logs. If the console fails, restore DNS to Automatic.

**Do not enter the Render dashboard URL as a DNS server.** It is not a DNS endpoint.

## Next milestone

Build authenticated device enrollment and a controlled IP allowlist sync to replace manual server edits. Add rate limiting, metrics, uptime monitoring, and a second independent resolver for redundancy before any public rollout. Only after verified DNS connectivity should we research game-specific selective routing with explicit endpoint validation and measurement.
