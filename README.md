# Healthcare Network Design Lab

Design of a network for a **fictional provincial health authority**, with partial lab simulation in Packet Tracer/GNS3: 1 data centre, 2 hospitals, and 5 rural clinics. The project covers requirements, architecture, security, a WAN options analysis, a test plan, a rollout plan, and a small Python tool for config backups.

> **Scope note:** This is a learning/lab project. Sites are fictional and all addresses come from private or documentation ranges (RFC 1918 and RFC 5737). The repository contains no real credentials, keys, or production data. Configs are templates: validate them in your own lab and record results in `docs/test-plan.md`.

## Design at a glance

| Area | Approach |
|---|---|
| Layout | Hierarchical: data centre core, hospital distribution pairs, standard clinic template |
| Segmentation | VLANs 10 Clinical, 20 Admin, 30 VoIP, 40 Guest, 50 Medical devices, 99 Management |
| Routing | OSPF (Area 0 data centre, Areas 1 and 2 hospitals, Area 3 clinics as stub), eBGP to simulated provincial WAN |
| Resilience | Dual cores, EtherChannel, HSRP at hospitals, IPsec VPN backup path for clinics |
| Security | Least-privilege ACLs, pfSense edge firewall, IPsec (AES-256/SHA-256), SSH-only management, SNMPv3, central syslog |
| Services | Windows Server (AD, DNS, DHCP), Ubuntu (Zabbix, rsyslog) |
| Voice/QoS | VoIP VLAN, DSCP EF (46) priority queuing |

## Repository layout

```
docs/
  design-summary.pdf   Two-page design summary
  topology.md          Mermaid topology diagram (renders on GitHub)
  ip-plan.md           VLAN and addressing plan
  test-plan.md         Test cases and result log
  whiteboard-guide.md  How to draw and explain the design from memory
configs/
  dc-core1-abr.cfg         OSPF ABR and summarization
  dc-edge-router.cfg       eBGP to provincial WAN
  hospital-a-dist1.cfg     VLANs, HSRP, ACLs, OSPF, hardening
  clinic1-router.cfg       Clinic template: subinterfaces, QoS, OSPF stub, VPN backup
  pfsense-notes.md         Firewall rules and IPsec parameters
evidence/                Lab screenshots and command output (add your own)
scripts/
  backup_configs.py        Nightly config backup and interface check (Netmiko)
  inventory.example.csv    Example device inventory
  requirements.txt
LICENSE                    MIT
```

## Config backup tool

```bash
cd scripts
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp inventory.example.csv inventory.csv     # edit with your lab devices
export NET_USER=admin NET_PASS='your-lab-password'
python backup_configs.py --inventory inventory.csv --output ../backups --sanitize
```

It connects over SSH, saves each running config to `backups/<date>/<hostname>.cfg`, counts interfaces up/down, and writes a summary CSV. Credentials come from environment variables or a prompt, never from the file. `--sanitize` redacts secrets on a best-effort basis; always review configs before publishing.

## Publishing your own lab configs

Export your real lab configs, then remove passwords, keys, SNMP communities, and any real addresses before pushing. Keep `.gitignore` as provided.

## Author

Manthan Ray, Regina, SK. [LinkedIn](https://linkedin.com/in/manthanray)
