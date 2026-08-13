"""
Threat Intelligence Honeypot — Threat Analyzer

Analyzes logged sessions: top attacking IPs, attack frequency,
port preference, time-of-day patterns, basic payload classification.
"""

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from session_logger import SessionLogger, SessionRecord


@dataclass
class ThreatSummary:
    """Summary of threat intelligence from honeypot sessions."""
    total_sessions: int = 0
    unique_ips: int = 0
    time_range_start: str = ""
    time_range_end: str = ""
    top_attackers: list = field(default_factory=list)
    port_distribution: dict = field(default_factory=dict)
    service_distribution: dict = field(default_factory=dict)
    classification_distribution: dict = field(default_factory=dict)
    hourly_distribution: dict = field(default_factory=dict)
    high_frequency_ips: list = field(default_factory=list)
    avg_payload_size: float = 0.0
    sessions_with_payload: int = 0


@dataclass
class AttackerProfile:
    """Profile of a single attacking IP."""
    ip: str = ""
    total_connections: int = 0
    first_seen: str = ""
    last_seen: str = ""
    targeted_services: list = field(default_factory=list)
    targeted_ports: list = field(default_factory=list)
    classifications: list = field(default_factory=list)
    avg_payload_size: float = 0.0


def analyze_sessions(
    sessions: list,
    top_n: int = 10,
    min_connections_to_flag: int = 3,
) -> ThreatSummary:
    """
    Analyze a list of session records and produce a threat summary.

    Identifies top attackers, port preferences, attack timing patterns,
    and classifies connection types.
    """
    if not sessions:
        return ThreatSummary()

    summary = ThreatSummary(total_sessions=len(sessions))

    # Collect metrics
    ip_counter = Counter()
    port_counter = Counter()
    service_counter = Counter()
    class_counter = Counter()
    hour_counter = Counter()
    ip_sessions = defaultdict(list)
    total_payload = 0
    payload_count = 0
    timestamps = []

    for s in sessions:
        ip_counter[s.source_ip] += 1
        port_counter[s.dest_port] += 1
        service_counter[s.service] += 1
        class_counter[s.classification] += 1
        ip_sessions[s.source_ip].append(s)

        if s.payload_bytes > 0:
            total_payload += s.payload_bytes
            payload_count += 1

        # Parse hour from timestamp
        try:
            dt = datetime.fromisoformat(s.timestamp.replace("Z", "+00:00"))
            hour_counter[dt.hour] += 1
            timestamps.append(dt)
        except (ValueError, AttributeError):
            pass

    # Basic stats
    summary.unique_ips = len(ip_counter)
    summary.port_distribution = dict(port_counter.most_common())
    summary.service_distribution = dict(service_counter.most_common())
    summary.classification_distribution = dict(class_counter.most_common())
    summary.hourly_distribution = {
        str(h): c for h, c in sorted(hour_counter.items())
    }

    if payload_count > 0:
        summary.avg_payload_size = round(total_payload / payload_count, 1)
        summary.sessions_with_payload = payload_count

    if timestamps:
        timestamps.sort()
        summary.time_range_start = timestamps[0].isoformat()
        summary.time_range_end = timestamps[-1].isoformat()

    # Top attackers
    summary.top_attackers = [
        {"ip": ip, "connections": count}
        for ip, count in ip_counter.most_common(top_n)
    ]

    # High-frequency IPs (potential automated attacks)
    summary.high_frequency_ips = [
        ip for ip, count in ip_counter.items()
        if count >= min_connections_to_flag
    ]

    return summary


def profile_attacker(ip: str, sessions: list) -> AttackerProfile:
    """Build a detailed profile for a specific attacking IP."""
    ip_sessions = [s for s in sessions if s.source_ip == ip]

    if not ip_sessions:
        return AttackerProfile(ip=ip)

    profile = AttackerProfile(
        ip=ip,
        total_connections=len(ip_sessions),
    )

    services = set()
    ports = set()
    classifications = set()
    total_payload = 0
    timestamps = []

    for s in ip_sessions:
        services.add(s.service)
        ports.add(s.dest_port)
        classifications.add(s.classification)
        total_payload += s.payload_bytes

        try:
            dt = datetime.fromisoformat(s.timestamp.replace("Z", "+00:00"))
            timestamps.append(dt)
        except (ValueError, AttributeError):
            pass

    profile.targeted_services = sorted(services)
    profile.targeted_ports = sorted(ports)
    profile.classifications = sorted(classifications)

    if ip_sessions:
        profile.avg_payload_size = round(
            total_payload / len(ip_sessions), 1
        )

    if timestamps:
        timestamps.sort()
        profile.first_seen = timestamps[0].isoformat()
        profile.last_seen = timestamps[-1].isoformat()

    return profile


def format_summary(summary: ThreatSummary) -> str:
    """Format threat summary as a human-readable string."""
    lines = [
        "Threat Intelligence Summary",
        "=" * 50,
        f"  Total Sessions:     {summary.total_sessions}",
        f"  Unique IPs:         {summary.unique_ips}",
        f"  Sessions w/ Payload: {summary.sessions_with_payload}",
        f"  Avg Payload Size:   {summary.avg_payload_size} bytes",
    ]

    if summary.time_range_start:
        lines.append(f"  Time Range:         {summary.time_range_start}")
        lines.append(f"                   to {summary.time_range_end}")

    lines.append("")
    lines.append("  Top Attackers:")
    for a in summary.top_attackers[:10]:
        lines.append(f"    {a['ip']:<20} {a['connections']} connections")

    lines.append("")
    lines.append("  Port Distribution:")
    for port, count in summary.port_distribution.items():
        lines.append(f"    Port {port:<6} {count} connections")

    lines.append("")
    lines.append("  Attack Classifications:")
    for cls, count in summary.classification_distribution.items():
        lines.append(f"    {cls:<15} {count}")

    if summary.high_frequency_ips:
        lines.append("")
        lines.append(
            f"  High-Frequency IPs ({len(summary.high_frequency_ips)}):"
        )
        for ip in summary.high_frequency_ips[:10]:
            lines.append(f"    {ip}")

    return "\n".join(lines)
