"""
Threat Intelligence Honeypot — Example Demo

Generates SIMULATED attack logs (not real traffic), runs threat analysis,
and displays results. No actual network listeners are started.

This demo creates synthetic connection data that mimics common attack
patterns: port scanning, SSH brute force, HTTP exploit attempts,
and telnet probing.

Usage:
    python example.py
"""

import os
import sys
import shutil
import random
import tempfile
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from session_logger import SessionLogger, SessionRecord
from threat_analyzer import (
    analyze_sessions,
    profile_attacker,
    format_summary,
)


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


# Simulated attacker data
ATTACKER_IPS = [
    "192.168.1.100",
    "10.0.0.50",
    "172.16.0.25",
    "10.0.0.51",
    "192.168.1.200",
    "10.0.0.52",
    "172.16.0.30",
    "192.168.1.150",
    "10.0.0.99",
    "172.16.0.10",
    "192.168.1.175",
    "10.0.0.75",
]

SERVICES = [
    {"service": "ssh", "port": 2222},
    {"service": "http", "port": 8080},
    {"service": "telnet", "port": 2323},
]

SSH_PAYLOADS = [
    "SSH-2.0-PuTTY_Release_0.78",
    "root\npassword123",
    "admin\nadmin",
    "user\n123456",
    "",
]

HTTP_PAYLOADS = [
    "GET / HTTP/1.1\r\nHost: target\r\n\r\n",
    "GET /admin HTTP/1.1\r\nHost: target\r\n\r\n",
    "GET /../../etc/passwd HTTP/1.1\r\nHost: target\r\n\r\n",
    "POST /login HTTP/1.1\r\nHost: target\r\ncmd=whoami\r\n\r\n",
    "GET /wp-admin/ HTTP/1.1\r\nHost: target\r\n\r\n",
    "",
]

TELNET_PAYLOADS = [
    "root",
    "admin",
    "enable",
    "",
]

CLASSIFICATIONS = {
    "ssh": ["scan", "brute_force", "brute_force", "brute_force", "scan"],
    "http": ["scan", "scan", "exploit", "exploit", "scan", "scan"],
    "telnet": ["scan", "brute_force", "brute_force", "scan"],
}


def generate_simulated_sessions(
    count: int = 200,
    hours_span: int = 24,
) -> list:
    """
    Generate synthetic honeypot sessions mimicking realistic attack patterns.

    Creates a mix of port scans, brute force attempts, and exploit probes
    distributed across the time window with realistic attacker behavior.
    """
    sessions = []
    now = datetime.now(timezone.utc)
    start = now - timedelta(hours=hours_span)

    # Some IPs are more aggressive than others
    aggressive_ips = random.sample(ATTACKER_IPS, 3)

    for i in range(count):
        # Select attacker — aggressive IPs get more sessions
        if random.random() < 0.4:
            ip = random.choice(aggressive_ips)
        else:
            ip = random.choice(ATTACKER_IPS)

        # Select target service
        svc = random.choice(SERVICES)
        service = svc["service"]
        port = svc["port"]

        # Generate timestamp with realistic patterns
        # More activity during nighttime hours (automated attacks)
        hour_offset = random.gauss(hours_span / 2, hours_span / 4)
        hour_offset = max(0, min(hours_span, hour_offset))
        timestamp = start + timedelta(hours=hour_offset)

        # Select payload based on service
        if service == "ssh":
            payload = random.choice(SSH_PAYLOADS)
        elif service == "http":
            payload = random.choice(HTTP_PAYLOADS)
        else:
            payload = random.choice(TELNET_PAYLOADS)

        classification = random.choice(CLASSIFICATIONS[service])

        session = SessionRecord(
            session_id=f"sim_{i:04d}",
            timestamp=timestamp.isoformat(),
            source_ip=ip,
            source_port=random.randint(40000, 65535),
            dest_port=port,
            protocol="tcp",
            service=service,
            payload_preview=payload,
            payload_bytes=len(payload.encode("utf-8")),
            duration_seconds=round(random.uniform(0.1, 5.0), 3),
            geo_country="",
            geo_city="",
            classification=classification,
        )
        sessions.append(session)

    # Sort by timestamp
    sessions.sort(key=lambda s: s.timestamp)
    return sessions


def main():
    print_header("Threat Intelligence Honeypot — Demo")
    print("  Using SIMULATED attack data (no real network traffic)\n")

    # Work in temp directory
    demo_dir = tempfile.mkdtemp(prefix="honeypot_demo_")
    log_dir = os.path.join(demo_dir, "honeypot_logs")

    try:
        # ── Step 1: Generate simulated attack logs ───────────
        print_step(1, "Generating simulated attack sessions")

        sessions = generate_simulated_sessions(count=200, hours_span=24)
        print(f"  Generated {len(sessions)} simulated sessions")
        print(f"  Time span: 24 hours")
        print(f"  Unique IPs: {len(set(s.source_ip for s in sessions))}")

        # Log sessions
        logger = SessionLogger(log_dir=log_dir)
        for session in sessions:
            logger.log_session(session)

        stats = logger.get_stats()
        print(f"  Log files: {stats['log_files']}")
        print(f"  Total size: {stats['total_size_bytes']} bytes")

        # ── Step 2: Threat Analysis ──────────────────────────
        print_step(2, "Running threat analysis")

        summary = analyze_sessions(
            sessions, top_n=10, min_connections_to_flag=5
        )
        print(format_summary(summary))

        # ── Step 3: Attacker Profiling ───────────────────────
        print_step(3, "Profiling top attackers")

        for attacker in summary.top_attackers[:5]:
            ip = attacker["ip"]
            profile = profile_attacker(ip, sessions)

            color = RED if profile.total_connections >= 10 else YELLOW
            print(f"\n  {color}{BOLD}{ip}{RESET}")
            print(f"    Connections: {profile.total_connections}")
            print(f"    First seen:  {profile.first_seen}")
            print(f"    Last seen:   {profile.last_seen}")
            print(f"    Services:    {', '.join(profile.targeted_services)}")
            print(f"    Ports:       {', '.join(map(str, profile.targeted_ports))}")
            print(
                f"    Types:       {', '.join(profile.classifications)}"
            )
            print(f"    Avg payload: {profile.avg_payload_size} bytes")

        # ── Step 4: Attack Pattern Analysis ──────────────────
        print_step(4, "Attack pattern analysis")

        print("\n  Hourly Distribution (UTC):")
        max_count = max(
            (int(v) for v in summary.hourly_distribution.values()),
            default=1,
        )
        for hour, count in sorted(
            summary.hourly_distribution.items(), key=lambda x: int(x[0])
        ):
            bar_len = int((int(count) / max_count) * 30) if max_count else 0
            bar = "#" * bar_len
            print(f"    {int(hour):02d}:00 |{bar} ({count})")

        print(f"\n  Classification Breakdown:")
        for cls, count in summary.classification_distribution.items():
            pct = count / summary.total_sessions * 100
            print(f"    {cls:<15} {count:>4} ({pct:.1f}%)")

        # ── Step 5: Dashboard hint ───────────────────────────
        print_step(5, "Dashboard")
        print(
            f"  To view the interactive Streamlit dashboard, run:"
        )
        print(f"  {CYAN}streamlit run dashboard.py{RESET}")
        print(
            f"\n  (Copy the log files from the demo directory first,"
        )
        print(f"   or run example.py with log_dir set to ./honeypot_logs)")

    finally:
        # Cleanup
        print_header("Cleanup")
        shutil.rmtree(demo_dir, ignore_errors=True)
        print(f"  {GREEN}Temporary demo files removed{RESET}")

    print(f"\n{BOLD}Demo complete.{RESET}\n")


if __name__ == "__main__":
    main()
