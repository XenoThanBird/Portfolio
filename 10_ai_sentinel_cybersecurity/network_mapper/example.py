"""
Network Inventory & Audit — Example Demo

Scans localhost/loopback to discover open ports, performs device
fingerprinting, generates a network topology visualization and
inventory report.

Only scans 127.0.0.1 (localhost) — safe for demonstration.
For real network scans, modify config.yaml with your authorized subnet.

IMPORTANT: Only scan networks you own or have explicit authorization
to scan. Unauthorized scanning may violate laws and regulations.

Usage:
    python example.py
"""

import os
import sys
import shutil
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scanner import scan_network, DeviceInfo, PortResult
from device_fingerprint import (
    enrich_device,
    lookup_mac_vendor,
    fingerprint_os,
)
from report_generator import (
    generate_markdown_report,
    assess_risk,
    save_reports,
)

try:
    from network_visualizer import visualize_topology, HAS_VISUALIZATION
except ImportError:
    HAS_VISUALIZATION = False


# ANSI colors
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


def print_header(text: str) -> None:
    print(f"\n{BOLD}{CYAN}{'=' * 60}{RESET}")
    print(f"{BOLD}{CYAN}  {text}{RESET}")
    print(f"{BOLD}{CYAN}{'=' * 60}{RESET}\n")


def print_step(num: int, text: str) -> None:
    print(f"\n{BOLD}Step {num}: {text}{RESET}")
    print("-" * 40)


def create_simulated_devices() -> list:
    """
    Create simulated network devices for demo purposes.

    These represent what a real network scan might discover
    on a home or small office network.
    """
    devices = [
        DeviceInfo(
            ip="192.168.1.1",
            hostname="gateway.local",
            mac="00:24:E4:AA:BB:CC",
            vendor="",
            os_guess="",
            open_ports=[
                PortResult(port=53, state="open", service="dns"),
                PortResult(port=80, state="open", service="http"),
                PortResult(port=443, state="open", service="https"),
            ],
            ttl=255,
        ),
        DeviceInfo(
            ip="192.168.1.10",
            hostname="web-server.local",
            mac="00:14:22:DD:EE:FF",
            vendor="",
            os_guess="",
            open_ports=[
                PortResult(port=22, state="open", service="ssh"),
                PortResult(port=80, state="open", service="http"),
                PortResult(port=443, state="open", service="https"),
                PortResult(port=3306, state="open", service="mysql"),
            ],
            ttl=64,
        ),
        DeviceInfo(
            ip="192.168.1.20",
            hostname="workstation-01.local",
            mac="D8:9E:F3:11:22:33",
            vendor="",
            os_guess="",
            open_ports=[
                PortResult(port=445, state="open", service="smb"),
                PortResult(port=3389, state="open", service="rdp"),
            ],
            ttl=128,
        ),
        DeviceInfo(
            ip="192.168.1.50",
            hostname="smart-hub.local",
            mac="B8:27:EB:44:55:66",
            vendor="",
            os_guess="",
            open_ports=[
                PortResult(port=80, state="open", service="http"),
            ],
            ttl=64,
        ),
        DeviceInfo(
            ip="192.168.1.100",
            hostname="old-server.local",
            mac="3C:D9:2B:77:88:99",
            vendor="",
            os_guess="",
            open_ports=[
                PortResult(port=21, state="open", service="ftp"),
                PortResult(port=23, state="open", service="telnet"),
                PortResult(port=80, state="open", service="http"),
                PortResult(port=445, state="open", service="smb"),
            ],
            ttl=128,
        ),
    ]
    return devices


def main():
    print_header("Network Inventory & Audit — Demo")
    print("  Scanning localhost + simulated network devices\n")

    demo_dir = tempfile.mkdtemp(prefix="netmap_demo_")

    try:
        # ── Step 1: Scan localhost ───────────────────────────
        print_step(1, "Scanning localhost (127.0.0.1)")

        common_ports = "22,23,25,53,80,110,143,443,445,3306,3389,5432,8080,8443"
        real_devices = scan_network(
            target="127.0.0.1",
            ports=common_ports,
            timeout=1,
        )

        if real_devices:
            print(f"  {GREEN}Localhost scan complete{RESET}")
            for d in real_devices:
                port_count = len(d.open_ports)
                print(f"    {d.ip}: {port_count} open port(s)")
                for p in d.open_ports:
                    print(f"      - {p.port}/{p.service} ({p.state})")
        else:
            print(f"  {YELLOW}No open ports found on localhost{RESET}")

        # ── Step 2: Load simulated devices ───────────────────
        print_step(2, "Loading simulated network inventory")
        print("  (In production, these would come from a real network scan)")

        sim_devices = create_simulated_devices()
        all_devices = real_devices + sim_devices

        print(f"  Total devices: {len(all_devices)}")

        # ── Step 3: Device fingerprinting ────────────────────
        print_step(3, "Fingerprinting devices")

        for device in all_devices:
            device = enrich_device(device)
            risk_level, risk_flags = assess_risk(device)
            device.risk_level = risk_level

            color = GREEN
            if risk_level == "critical":
                color = RED
            elif risk_level == "warning":
                color = YELLOW

            print(
                f"  {color}[{risk_level.upper():>8}]{RESET} "
                f"{device.ip:<16} "
                f"{device.device_type:<12} "
                f"{device.os_guess:<20} "
                f"{device.vendor}"
            )

            for flag in risk_flags:
                print(
                    f"             ! Port {flag['port']} "
                    f"({flag['service']}): {flag['reason']}"
                )

        # ── Step 4: Network visualization ────────────────────
        print_step(4, "Generating network topology visualization")

        if HAS_VISUALIZATION:
            viz_path = os.path.join(demo_dir, "network_topology.png")
            output = visualize_topology(
                all_devices,
                output_file=viz_path,
                figsize=(14, 10),
            )
            print(f"  {GREEN}Topology saved:{RESET} {output}")
        else:
            print(
                f"  {YELLOW}Skipping visualization "
                f"(install networkx + matplotlib){RESET}"
            )

        # ── Step 5: Generate reports ─────────────────────────
        print_step(5, "Generating inventory reports")

        report_dir = os.path.join(demo_dir, "reports")
        saved = save_reports(
            all_devices,
            output_dir=report_dir,
            formats="both",
        )

        print(f"  {GREEN}Reports saved:{RESET}")
        for path in saved:
            print(f"    -> {path}")

        # Show report preview
        md_report = generate_markdown_report(all_devices)
        preview = md_report.split("\n")[:25]
        print(f"\n  Report Preview:")
        for line in preview:
            print(f"    {line}")
        print(f"    ... ({len(md_report.split(chr(10)))} total lines)")

        # ── Step 6: Risk summary ─────────────────────────────
        print_step(6, "Risk summary")

        critical = sum(1 for d in all_devices if d.risk_level == "critical")
        warning = sum(1 for d in all_devices if d.risk_level == "warning")
        low = sum(1 for d in all_devices if d.risk_level == "low")

        total_ports = sum(len(d.open_ports) for d in all_devices)

        print(f"  Devices scanned: {len(all_devices)}")
        print(f"  Total open ports: {total_ports}")
        print(f"  {RED}Critical risk:  {critical}{RESET}")
        print(f"  {YELLOW}Warning risk:   {warning}{RESET}")
        print(f"  {GREEN}Low risk:       {low}{RESET}")

    finally:
        print_header("Cleanup")
        shutil.rmtree(demo_dir, ignore_errors=True)
        print(f"  {GREEN}Temporary demo files removed{RESET}")

    print(f"\n{BOLD}Demo complete.{RESET}\n")


if __name__ == "__main__":
    main()
