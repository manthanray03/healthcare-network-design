# pfSense: edge firewall and clinic VPN hub

pfSense terminates the backup IPsec tunnels from the five clinics and filters what comes in over broadband. Values below are lab settings; secrets are kept out of the repository.

## Interfaces

| Interface | Address | Purpose |
|---|---|---|
| WAN | 203.0.113.1/29, gateway 203.0.113.6 | Broadband internet; VPN peer address for the clinics |
| LAN | 172.16.0.6/30, gateway 172.16.0.5 (DC-CORE1) | Toward the data centre core |
| ipsec1 to ipsec5 (VTI) | 172.31.N.1/30 | One route-based tunnel per clinic |

## IPsec (route-based, one tunnel per clinic)

| Setting | Phase 1 (IKE) | Phase 2 (ESP) |
|---|---|---|
| Version / mode | IKEv2 | Routed (VTI), local 172.31.N.1, remote 172.31.N.2 |
| Encryption | AES-256-CBC | AES-256 |
| Integrity | SHA-256 | SHA-256 |
| Key exchange | DH group 14 | PFS group 14 |
| Lifetime | 28,800 s | 3,600 s |
| Authentication | Pre-shared key, one per clinic, stored in the password vault | |
| Remote peer | Clinic 1: 192.0.2.2 (others: that clinic's backup address) | |
| Dead peer detection | On, 10 s delay, 5 retries | |

These match `clinic1-router.cfg` (IKEv2 proposal AES-256 / SHA-256 / group 14, transform set `esp-aes 256 esp-sha256-hmac`, PFS group 14).

## Static routes

| Destination | Gateway | Why |
|---|---|---|
| 10.10.0.0/16, 10.20.0.0/16, 10.30.0.0/16 | 172.16.0.5 (LAN) | Reach the data centre and hospitals |
| 10.100.N.0/24 | 172.31.N.2 (ipsecN) | Reach clinic N over its tunnel |

DC-CORE1 has floating static routes for each clinic /24 pointing at 172.16.0.6 (AD 250), so the tunnel is used only when a clinic's primary link is down.

## Firewall rules

**WAN** (default deny; blocks private and bogon sources)

| # | Action | Protocol | Source | Destination | Port | Note |
|---|---|---|---|---|---|---|
| 1 | Pass | UDP | Clinic backup addresses (alias) | 203.0.113.1 | 500, 4500 | IKE and NAT-T |
| 2 | Pass | ESP | Clinic backup addresses (alias) | 203.0.113.1 | | IPsec |
| 3 | Block, log | Any | Any | Any | | Default deny (implicit, logging on) |

**IPsec / VTI** (traffic from clinics over the backup path)

| # | Action | Protocol | Source | Destination | Port | Note |
|---|---|---|---|---|---|---|
| 1 | Pass | UDP | Clinic subnets | 10.10.100.10 | 53, 67 | DNS and DHCP relay |
| 2 | Pass | TCP | Clinic clinical VLANs | 10.10.100.20 | 443 | Clinical application |
| 3 | Pass | UDP | Clinic subnets | 10.10.100.30 | 514 | Syslog |
| 4 | Pass | UDP/TCP | Clinic VoIP VLANs | Voice servers (alias) | SIP, RTP range | Voice |
| 5 | Block, log | Any | Any | Any | | Everything else |

**LAN**

| # | Action | Protocol | Source | Destination | Port | Note |
|---|---|---|---|---|---|---|
| 1 | Pass | TCP | 10.10.99.128/25 | 172.16.0.6 | 443, 22 | Admin from the management VLAN only |
| 2 | Pass | UDP | 10.10.100.30 | 172.16.0.6 | 161 | SNMPv3 polling |
| 3 | Pass | Any | 10.0.0.0/8 | Clinic subnets | | Return path and DC-initiated management |
| 4 | Block, log | Any | Any | 172.16.0.6 | | Nothing else may reach the firewall itself |

## Hardening and logging

- Web GUI on HTTPS only, reachable from the management VLAN only; SSH with keys, password login off.
- Remote syslog to 10.10.100.30 (firewall events, VPN, gateway status).
- Gateway monitoring on each VTI so tunnel loss shows up in the logs.
- Configuration backed up after every change (Diagnostics > Backup), stored encrypted outside the firewall.
