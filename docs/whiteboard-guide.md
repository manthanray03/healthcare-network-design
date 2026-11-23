# Drawing the design from memory

A guide for explaining this network on a whiteboard in an interview, in about five minutes. Draw from the top down and say why at each step.

## 1. The ask (30 seconds)

"A provincial health authority: one data centre, two hospitals, five rural clinics. Clinical systems must stay up, patient data must be protected, clinics have almost no IT staff, and voice has to work."

## 2. Draw the shape (1 minute)

1. A box at the top for the **provincial WAN** (AS 65000), and the **edge router + pfSense** under it (AS 65100, eBGP).
2. Two **core switches** under the edge, joined by an EtherChannel. Label the box **Area 0**.
3. Servers hanging off the core: **AD/DNS/DHCP**, the **clinical app (HTTPS)**, **monitoring/syslog**.
4. Bottom left: **Hospital A (Area 1)** and **Hospital B (Area 2)**, each a pair of distribution switches.
5. Bottom right: **five clinics (Area 3, totally stubby)**, one router each.
6. Solid lines for primary links. A **dashed line** from each clinic back to pfSense: the **broadband + IPsec backup**.

## 3. Explain the decisions (2 minutes)

| Point on the board | What to say |
|---|---|
| OSPF areas | "Each site is its own area so a flap at a clinic doesn't make the hospitals recalculate. The cores summarize each area: 10.20/16, 10.30/16, 10.100.0/21." |
| Totally stubby clinics | "Clinics only need a default route, so their routers stay small and simple." |
| Six VLANs | "Clinical 10, Admin 20, VoIP 30, Guest 40, Medical devices 50, Management 99. Each has its own ACL." |
| ACLs | "Clinical PCs reach the clinical app on 443 only. Guest reaches the internet only. Medical devices reach only their server. Everything else is denied and logged." |
| HSRP | "Hospitals have two gateways per VLAN; if one dies the other takes over in seconds." |
| Clinic backup | "If a clinic's line drops, OSPF loses the route, a floating static on the core and a floating default on the clinic send traffic over IPsec: IKEv2, AES-256, SHA-256, DH 14." |
| Voice | "Phones mark EF 46; every WAN link has a priority queue for EF." |
| Management | "SSH only, from the management range only, AAA, SNMPv3, central syslog, MD5 on OSPF." |

## 4. The trade-off (1 minute)

"I compared a private WAN at every site against broadband plus IPsec. Private scored 3.8, hybrid 3.7, so it was close. I chose a hybrid: private links where downtime hurts patients most (data centre, hospitals), cheaper links plus a VPN backup at clinics."

## 5. What I would add next (30 seconds)

"802.1X so only known devices get on the clinical and medical VLANs, and intrusion detection at the edge."

## Numbers to remember

- 1 data centre, 2 hospitals, 5 clinics; 6 VLANs
- 10.10/16 data centre, 10.20/16 and 10.30/16 hospitals, 10.100.N.0/24 clinics
- OSPF areas 0, 1, 2, 3 (stub); eBGP AS 65100 to AS 65000
- IPsec: IKEv2, AES-256, SHA-256, DH group 14
- Voice: DSCP EF (46), priority queue
