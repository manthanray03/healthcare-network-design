# Topology

```mermaid
graph TD
  ISP["Provincial WAN (simulated ISP, AS 65000)"]
  EDGE["DC-EDGE-RTR + pfSense (AS 65100)"]
  CORE1["DC-CORE1 (ABR)"]
  CORE2["DC-CORE2 (ABR)"]
  SRV["Servers: Windows AD/DNS/DHCP, Ubuntu Zabbix/syslog"]
  HA["Hospital A: DIST1 + DIST2 (Area 1)"]
  HB["Hospital B: DIST1 + DIST2 (Area 2)"]
  C["Clinics 1 to 5: one router each (Area 3, stub)"]

  ISP --- EDGE
  EDGE --- CORE1
  EDGE --- CORE2
  CORE1 --- CORE2
  CORE1 --- SRV
  CORE2 --- SRV
  CORE1 --- HA
  CORE2 --- HA
  CORE1 --- HB
  CORE2 --- HB
  CORE1 --- C
  EDGE -. IPsec VPN backup .- C
```

## Reading the diagram
- Solid lines are primary links. The dashed line is the backup path from each clinic over broadband and IPsec.
- DC-CORE1/2 act as OSPF area border routers and summarize each area toward the backbone.
- Hospitals have a distribution pair running HSRP. Clinics have a single router plus switch and access point.
