# Evidence

Save lab output here as you run the tests in `docs/test-plan.md`, one file per test:

- `TC-01-dhcp-relay.txt` (command output) or `TC-01-dhcp-relay.png` (screenshot)
- `TC-04-failover-ping.txt`, `TC-06-ikev2-sa.txt`, and so on

Before you commit anything:

- Remove passwords, pre-shared keys, SNMP credentials and certificates.
- Keep only private (RFC 1918) and documentation (RFC 5737) addresses.
- Then update the test's **Actual result** and **Status** in `docs/test-plan.md`.
