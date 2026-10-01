# Addressing Plan

All ranges are private (RFC 1918) or documentation ranges (RFC 5737).

## Sites

| Site | Block | OSPF area |
|---|---|---|
| Data centre | 10.10.0.0/16 (servers 10.10.100.0/24, mgmt 10.10.99.0/24) | 0 |
| Hospital A | 10.20.0.0/16 | 1 |
| Hospital B | 10.30.0.0/16 | 2 |
| Clinics 1 to 5 | 10.100.N.0/24 (N = clinic number) | 3 (stub) |

## Hospital VLANs (Hospital A shown; Hospital B uses 10.30.x.x)

| VLAN | Name | Subnet | Gateway (HSRP) |
|---|---|---|---|
| 10 | CLINICAL | 10.20.10.0/24 | 10.20.10.1 |
| 20 | ADMIN | 10.20.20.0/24 | 10.20.20.1 |
| 30 | VOIP | 10.20.30.0/24 | 10.20.30.1 |
| 40 | GUEST | 10.20.40.0/24 | 10.20.40.1 |
| 50 | MEDDEV | 10.20.50.0/24 | 10.20.50.1 |
| 99 | MGMT | 10.20.99.0/24 | 10.20.99.1 |

## Clinic template (clinic N)

| VLAN | Name | Subnet |
|---|---|---|
| 10 | CLINICAL | 10.100.N.0/26 |
| 20 | ADMIN | 10.100.N.64/27 |
| 30 | VOIP | 10.100.N.96/27 |
| 40 | GUEST | 10.100.N.128/27 |
| 99 | MGMT | 10.100.N.224/28 |

## Transit links

| Link | Subnet |
|---|---|
| DC-CORE1 to Hospital A DIST1 | 172.16.1.0/30 |
| DC-CORE1 to Hospital B DIST1 | 172.16.2.0/30 |
| DC-CORE1 to Clinic N | 172.16.(100+N).0/30 |
| Clinic N IPsec tunnel | 172.31.N.0/30 |
| DC edge to provincial WAN | 198.51.100.0/30 |
| pfSense WAN (VPN peer) | 203.0.113.1 |
| Clinic 1 backup internet link | 192.0.2.0/30 |

## Key servers

| Host | Address | Role |
|---|---|---|
| DC-WIN1 | 10.10.100.10 | Active Directory, DNS, DHCP |
| DC-EHR1 | 10.10.100.20 | Simulated clinical application (HTTPS) |
| DC-MON1 | 10.10.100.30 | Ubuntu: Zabbix, rsyslog |

## Management addresses (match `scripts/inventory.example.csv`)

| Device | Address | Where it lives |
|---|---|---|
| DC-EDGE-RTR | 10.10.99.1 | Loopback0 |
| DC-CORE1 | 10.10.99.11 | Loopback0 |
| HOSP-A-DIST1 | 10.20.99.2 | Vlan99 |
| HOSP-A-DIST2 | 10.20.99.3 | Vlan99 (mirror of DIST1) |
| HOSP-B-DIST1 | 10.30.99.2 | Vlan99 (same pattern as Hospital A) |
| CLINIC1-RTR | 10.100.1.225 | GigabitEthernet0/1.99 |
