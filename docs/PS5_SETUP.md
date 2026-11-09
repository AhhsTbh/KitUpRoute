# KitUp Route — PS5 LAN DNS setup (experimental)

## What this does
The new `app/ps5_dns.py` is an allowlisted DNS forwarding service. It does **not** operate as a VPN, change your public IP, select Warzone matchmaking servers, or route game UDP traffic. Region selection in the web dashboard remains a saved preference only.

## What hardware is required
PS5's manual DNS fields require an IP address reachable by the console on port **53**. A cloud-hosted Render web service cannot supply that LAN DNS endpoint. You need an always-on device on the same home network (e.g. a Raspberry Pi, mini PC, or router that can run Python) or another securely designed DNS gateway. An iPhone alone is not a reliable always-on LAN DNS server.

## Local testing (before configuring PS5)
On the LAN device:
1. Install Python 3.12+ and `pip install dnslib`.
2. Find the device's LAN IPv4 address and the PS5's LAN IPv4 address. Assign stable DHCP leases if possible.
3. Set `KITUP_DNS_ALLOWED_CIDRS` to the **PS5's /32 address** and the device's loopback address, e.g. `192.168.1.50/32,127.0.0.1/32` (replace with your actual addresses).
4. Run as a user with permission to bind port 53:
   ```bash
   KITUP_DNS_ALLOWED_CIDRS="192.168.1.50/32,127.0.0.1/32" python -m app.ps5_dns --bind 192.168.1.10 --port 53
   ```
   Replace `192.168.1.10` with the LAN device IP. For local non-privileged testing, use `--bind 127.0.0.1 --port 5353`.
5. Permit **only LAN/PS5** traffic to UDP/TCP 53 in the host firewall. **Do not port-forward DNS port 53 from your router to the internet.**

## PS5 configuration
PS5: Settings → Network → Settings → Set Up Internet Connection → select your connection → Advanced Settings → DNS Settings → Manual. Set Primary DNS to the LAN device IP. Use a secondary resolver only if you understand that the console may bypass your local DNS proxy. Leave IP addressing and MTU automatic unless you have a specific need. Test Internet Connection, then test game connectivity. Restore DNS to Automatic if anything fails.

## Limits and verification
- DNS resolution is not packet routing and does not guarantee a change in game matchmaking region.
- If your router isolates clients or a firewall blocks DNS, the console cannot reach the service.
- Public IP, ping, and actual matchmaking location must be independently measured; don't infer them from the dashboard's selected region.
- The Render service hosts only the web dashboard/API; this LAN process must be deployed separately.
- The resolver intentionally denies clients outside `KITUP_DNS_ALLOWED_CIDRS`; unrestricted CIDRs are rejected.
