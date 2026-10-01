#!/usr/bin/env python3
"""
backup_configs.py - Back up running configs and check interface status.

Reads an inventory CSV (columns: hostname, ip, device_type), connects over SSH
with Netmiko, saves each running config to <output>/<YYYY-MM-DD>/<hostname>.cfg,
and writes a summary CSV with interface up/down counts per device.

Credentials come from environment variables (NET_USER, NET_PASS, optional
NET_ENABLE) or an interactive prompt. Nothing is hardcoded.

Exit code: 0 if every device succeeded, 1 otherwise.
"""
from __future__ import annotations

import argparse
import csv
import getpass
import logging
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoAuthenticationException, NetmikoTimeoutException

log = logging.getLogger("backup")

SUMMARY_FIELDS = ["hostname", "ip", "status", "interfaces_up", "interfaces_down", "error"]
_SECRET_WORDS = re.compile(
    r"\b(secret|password|pre-shared-key|community|key-string|md5|auth|priv)\b", re.I
)


def load_inventory(path: Path) -> list[dict]:
    """Read the device inventory CSV and validate required columns."""
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        missing = {"hostname", "ip"} - set(reader.fieldnames or [])
        if missing:
            raise SystemExit(f"Inventory is missing columns: {', '.join(sorted(missing))}")
        rows = [
            {k: (v or "").strip() for k, v in row.items()}
            for row in reader
            if (row.get("hostname") or "").strip()
        ]
    if not rows:
        raise SystemExit("Inventory has no devices.")
    return rows


def sanitize(config: str) -> str:
    """Best-effort secret redaction. Always review before publishing."""
    cleaned = []
    for line in config.splitlines():
        stripped = line.lstrip()
        skip = (
            stripped.startswith("!")
            or stripped.startswith("no ")
            or "password-encryption" in stripped
        )
        match = None if skip else _SECRET_WORDS.search(line)
        if match:
            line = line[: match.end()] + " <REDACTED>"
        cleaned.append(line)
    return "\n".join(cleaned) + "\n"


def count_interfaces(output: str) -> tuple[int, int]:
    """Count interfaces with protocol up/down from 'show ip interface brief'.

    Administratively-down interfaces are ignored on purpose: they are
    intentionally shut, so they are not faults.
    """
    up = down = 0
    for line in output.splitlines()[1:]:
        if not line.strip() or "administratively down" in line:
            continue
        tokens = line.split()
        if len(tokens) < 2:
            continue
        protocol = tokens[-1].lower()
        if protocol == "up":
            up += 1
        elif protocol == "down":
            down += 1
    return up, down


def backup_device(
    dev: dict, user: str, password: str, secret: str, out_dir: Path, do_sanitize: bool, timeout: int
) -> dict:
    """Connect to one device, save its config, and return a summary row."""
    result = {
        "hostname": dev["hostname"],
        "ip": dev["ip"],
        "status": "FAILED",
        "interfaces_up": "",
        "interfaces_down": "",
        "error": "",
    }
    params = {
        "device_type": dev.get("device_type") or "cisco_ios",
        "host": dev["ip"],
        "username": user,
        "password": password,
        "conn_timeout": timeout,
    }
    if secret:
        params["secret"] = secret
    try:
        with ConnectHandler(**params) as conn:
            if secret:
                conn.enable()
            config = conn.send_command("show running-config")
            brief = conn.send_command("show ip interface brief")
        if do_sanitize:
            config = sanitize(config)
        safe_name = re.sub(r"[^A-Za-z0-9_.-]", "_", dev["hostname"])
        (out_dir / f"{safe_name}.cfg").write_text(config, encoding="utf-8")
        up, down = count_interfaces(brief)
        result.update(status="OK", interfaces_up=up, interfaces_down=down)
    except NetmikoAuthenticationException:
        result["error"] = "authentication failed"
    except NetmikoTimeoutException:
        result["error"] = "connection timed out"
    except Exception as exc:  # keep one bad device from stopping the run
        result["error"] = f"{type(exc).__name__}: {exc}"
    return result


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Back up device configs and check interfaces.")
    parser.add_argument("--inventory", default="inventory.csv", help="CSV of devices")
    parser.add_argument("--output", default="backups", help="Base output directory")
    parser.add_argument("--workers", type=int, default=5, help="Parallel SSH sessions")
    parser.add_argument("--timeout", type=int, default=30, help="Connection timeout in seconds")
    parser.add_argument("--sanitize", action="store_true", help="Redact secrets in saved configs")
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    inventory = load_inventory(Path(args.inventory))
    user = os.environ.get("NET_USER") or input("Username: ")
    password = os.environ.get("NET_PASS") or getpass.getpass("Password: ")
    secret = os.environ.get("NET_ENABLE", "")

    out_dir = Path(args.output) / datetime.now().strftime("%Y-%m-%d")
    out_dir.mkdir(parents=True, exist_ok=True)

    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(
                backup_device, dev, user, password, secret, out_dir, args.sanitize, args.timeout
            ): dev
            for dev in inventory
        }
        for future in as_completed(futures):
            row = future.result()
            results.append(row)
            if row["status"] == "OK":
                log.info("%s OK (up=%s, down=%s)", row["hostname"], row["interfaces_up"], row["interfaces_down"])
            else:
                log.error("%s FAILED: %s", row["hostname"], row["error"])

    summary = out_dir / f"summary_{datetime.now():%H%M%S}.csv"
    with summary.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=SUMMARY_FIELDS)
        writer.writeheader()
        writer.writerows(sorted(results, key=lambda r: r["hostname"]))

    failed = sum(1 for r in results if r["status"] != "OK")
    log.info("Done: %d succeeded, %d failed. Summary: %s", len(results) - failed, failed, summary)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
