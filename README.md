# KitUp Route — PS5-first prototype

An independent, free-to-use gaming routing project. **This repository is a functional control-plane/DNS prototype, not a complete NoLagVPN replacement or functioning game VPN.** No regional relay is deployed, and changing a DNS resolver alone cannot select a game server or proxy arbitrary game traffic.

## Included
- Mobile-first purple/gold dashboard and regional clocks (8 proposed choices)
- FastAPI API with admin-token-protected region preference and SQLite persistence
- DNS forwarding server (UDP) with configurable upstream
- Dockerfile, example environment, and API tests
- Explicit routing status flags; no fake latency readings

## Local setup

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
export KITUP_ADMIN_TOKEN="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
uvicorn app.main:app --host 127.0.0.1 --port 8080
```
Open http://127.0.0.1:8080. Paste the configured token into the dashboard to save a region preference. Do not expose the token in client source code.

To test the DNS prototype in a separate terminal:

```sh
python -m app.dns
```

It defaults to UDP 127.0.0.1:5353, forwarding to 1.1.1.1:53. This is **not accessible from PS5** and deliberately does not create an open public DNS resolver.

## Docker

```sh
docker build -t kitup-route .
docker run --rm -p 127.0.0.1:8080:8080 -e KITUP_ADMIN_TOKEN='replace-with-long-secret' kitup-route
```

For production: use HTTPS, persistent database volume, proper authentication and rate limiting, DNS access controls, logging/privacy controls, monitoring, and safe firewall rules. Do not expose an unrestricted recursive DNS server to the public internet.

## PS5 compatibility roadmap
1. Deploy secure DNS endpoints and test basic DNS reachability on PS5.
2. Research and validate game-specific DNS behavior using authorized traffic observations and game/network terms.
3. Implement optional regional relay infrastructure, where technically feasible, with proper TLS, authentication and security controls.
4. Measure real latency/jitter/packet loss and compare against direct Xfinity routing.
5. Test PS5 gameplay and matchmaking behavior before describing any region as operational.
6. Add fail-open/recovery instructions and optional Xbox/PC support.

## Reality checks
- PS5 has custom DNS settings but does not natively run a generic VPN client.
- DNS alone cannot intercept all game packets, route UDP gameplay, or guarantee matchmaking regions.
- The region selector currently stores preferences only; regional relays are **not** implemented.
- Running infrastructure costs money even when users are not charged.
- Do not use this prototype as your PS5 DNS until a secured public resolver has been deployed and tested.

## Tests

```sh
pytest -q
```
