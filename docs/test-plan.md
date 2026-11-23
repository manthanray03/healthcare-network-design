# Test plan and result log

Ten tests check that the design does what the requirements ask. Run them in the Packet Tracer or GNS3 lab, record the actual result and save the output in `evidence/` as `TC-xx-short-name.txt` or `.png`.

**Status key:** Not run | Pass | Fail | Partial (explain in Notes)

| ID | Test | Requirement it proves | Status |
|---|---|---|---|
| TC-01 | DHCP relay | Clinical systems available | Not run |
| TC-02 | VLAN isolation (guest) | Patient data protected | Not run |
| TC-03 | ACL enforcement (clinical and medical devices) | Patient data protected | Not run |
| TC-04 | Clinic WAN failure and failover to IPsec | Clinical systems available 24/7 | Not run |
| TC-05 | HSRP failover at a hospital | Clinical systems available 24/7 | Not run |
| TC-06 | IPsec VPN operation | Patient data protected in transit | Not run |
| TC-07 | Voice and QoS marking | Reliable voice for care teams | Not run |
| TC-08 | Monitoring alerts | Manageable at scale | Not run |
| TC-09 | Configuration backup | Manageable at scale | Not run |
| TC-10 | Management access restrictions | Patient data protected | Not run |

## TC-01 DHCP relay

- **Steps:** Connect a PC to a clinical access port at Hospital A (VLAN 10). Run `ipconfig /renew` (Windows) or `dhclient` (Linux). On HOSP-A-DIST1 run `show ip dhcp relay` / `debug ip dhcp server packet` briefly.
- **Expected:** The PC gets an address in 10.20.10.0/24 with gateway 10.20.10.1 and DNS 10.10.100.10, served by DC-WIN1 through the helper address.
- **Actual result:**
- **Evidence:**

## TC-02 VLAN isolation (guest)

- **Steps:** From a guest PC (VLAN 40) ping 10.10.100.20 and 10.20.10.1, then browse to a public test site.
- **Expected:** Internal addresses fail; the internet works. `show ip access-lists GUEST-IN` shows hits on the deny lines.
- **Actual result:**
- **Evidence:**

## TC-03 ACL enforcement (clinical and medical devices)

- **Steps:** From a clinical PC, open https://10.10.100.20 and try SSH (TCP 22) to 10.10.100.20. From a medical device VLAN host, try to reach 10.10.100.10.
- **Expected:** HTTPS works; SSH is blocked and logged by `CLINICAL-IN`; the medical device can only reach 10.10.100.20 on 443.
- **Actual result:**
- **Evidence:**

## TC-04 Clinic WAN failure and failover to IPsec

- **Steps:** Start a continuous ping from a Clinic 1 PC to 10.10.100.20. Shut CLINIC1-RTR Gi0/0. Watch `show ip route 0.0.0.0` on the clinic and `show ip route 10.100.1.0` on DC-CORE1. Bring Gi0/0 back up.
- **Expected:** Traffic moves to Tunnel1 after the OSPF dead timer (about 40 seconds with default timers). DC-CORE1 installs the floating static via 172.16.0.6. Traffic returns to the primary path when the link recovers.
- **Actual result:** (record the number of lost pings)
- **Evidence:**

## TC-05 HSRP failover at a hospital

- **Steps:** Continuous ping from a Hospital A clinical PC to 10.10.100.20. Shut the uplink or reload HOSP-A-DIST1.
- **Expected:** DIST2 becomes active for every VLAN (`show standby brief`); a few pings are lost; DIST1 takes back over when it returns (preempt).
- **Actual result:**
- **Evidence:**

## TC-06 IPsec VPN operation

- **Steps:** With Clinic 1 on the backup path, run `show crypto ikev2 sa` and `show crypto ipsec sa` on CLINIC1-RTR and check Status > IPsec on pfSense.
- **Expected:** IKEv2 SA is READY with AES-CBC-256, SHA-256, DH group 14; encrypt and decrypt counters increase while traffic flows.
- **Actual result:**
- **Evidence:**

## TC-07 Voice and QoS marking

- **Steps:** Place a call between a Clinic 1 phone (VLAN 30) and a hospital phone while generating bulk traffic across the WAN. Run `show policy-map interface GigabitEthernet0/0`.
- **Expected:** Voice packets arrive marked DSCP EF (46) and are counted in the `VOICE` priority class; no drops in that class.
- **Actual result:**
- **Evidence:**

## TC-08 Monitoring alerts

- **Steps:** Shut a monitored interface (for example HOSP-A-DIST1 Gi1/0/24) and wait.
- **Expected:** DC-MON1 receives the syslog message and raises an interface-down problem within the polling interval; it clears when the link returns.
- **Actual result:**
- **Evidence:**

## TC-09 Configuration backup

- **Steps:** Copy `scripts/inventory.example.csv` to `inventory.csv` with your lab devices and run `python backup_configs.py --inventory inventory.csv --output ../backups --sanitize`.
- **Expected:** One `.cfg` file per device in `backups/<date>/`, a summary CSV with interface counts, and no passwords or keys left in the saved files.
- **Actual result:**
- **Evidence:**

## TC-10 Management access restrictions

- **Steps:** From a clinical PC, try SSH and Telnet to 10.20.99.2. Repeat SSH from a host in 10.10.99.128/25.
- **Expected:** Telnet is refused everywhere; SSH from the clinical VLAN is refused by `MGMT-ONLY`; SSH from the management VLAN works.
- **Actual result:**
- **Evidence:**
