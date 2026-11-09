# KitUp Route deployment and PS5 testing

## 1. Deploy the control dashboard

The repository contains `render.yaml` and a Dockerfile. In Render, create a new Blueprint service from this repository and review the plan and environment before deploying. Hosting plan availability and charges depend on your provider. Keep `KITUP_ADMIN_TOKEN` secret; never commit it or share screenshots of it. The prototype uses `/tmp/kitup.db` on Render and selections may be lost when the instance restarts.

Visit `/healthz` and `/api/status` on the deployed HTTPS URL. `relay_connected` and `game_routing_verified` should remain false until verified infrastructure is running.

## 2. DNS service safety

The existing `app.dns` forwarder binds only to `127.0.0.1:5353` by default. It is not a public resolver and cannot be used directly from PS5. Do not expose UDP 53 to the internet without network-level allowlists, anti-abuse rate limits, logging/privacy policy, firewalling, and a documented fallback. Public recursive resolvers are commonly abused for DNS amplification attacks.

## 3. PS5 tests (only after a secured DNS endpoint exists)

Record your current DNS settings. On PS5 navigate to Settings > Network > Settings > Set Up Internet Connection, choose your connection, Advanced Settings, DNS Settings > Manual. Enter only a tested endpoint. Run Test Internet Connection. If sign-in, store, or gameplay breaks, immediately restore DNS Settings > Automatic.

## 4. Game routing research

A DNS response changes hostname resolution, not arbitrary UDP/TCP gameplay traffic. To claim region switching, demonstrate that supported matchmaking endpoints can legally and reliably use an authorized relay, that authentication and TLS are handled safely, and that the actual matchmaking region changes in controlled tests. Many modern game services use certificate validation, hardcoded addresses, encrypted DNS, or independently assigned data centers. Do not intercept third-party TLS or claim easier lobbies.

## 5. Verification checklist

- API health and authentication tests pass
- Web UI works on iPhone Safari
- Resolver answers permitted DNS requests and rejects unauthorized clients
- Fail-safe restoration instructions are tested
- Real latency, jitter and loss are measured against the direct Xfinity route
- Console tests verify gameplay stability and actual routing effects

**Current status:** The first two items are partly implemented; all console routing claims remain unverified.
