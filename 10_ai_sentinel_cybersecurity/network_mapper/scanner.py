"""
Network Inventory & Audit — Scanner

Network scanner using python-nmap for device discovery and port scanning.
Falls back to socket-based scanning when nmap is not available.

IMPORTANT: Only scan networks you own or have explicit authorization to scan.
Unauthorized network scanning may violate laws and regulations.
"""

import socket
import concurrent.futures
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

try:
    import nmap
    HAS_NMAP = True
except ImportError:
    HAS_NMAP = False


@dataclass
class PortResult:
    """Result of scanning a single port."""
    port: int = 0
    state: str = ""  # open, closed, filtered
    service: str = ""
    version: str = ""
    protocol: str = "tcp"


@dataclass
class DeviceInfo:
    """Information about a discovered network device."""
    ip: str = ""
    hostname: str = ""
    mac: str = ""
    vendor: str = ""
    os_guess: str = ""
    device_type: str = "unknown"
    open_ports: list = field(default_factory=list)
    scan_time: str = ""
    ttl: int = 0
    risk_level: str = "low"  # low, medium, high, critical


def scan_ports_nmap(
    target: str,
    ports: str = "22,80,443",
    timeout: int = 10,
) -> list:
    """
    Scan ports using python-nmap (requires nmap installed on system).

    Returns a list of DeviceInfo with open ports.
    """
    if not HAS_NMAP:
        raise RuntimeError(
            "python-nmap not available — install nmap on your system "
            "and pip install python-nmap"
        )

    nm = nmap.PortScanner()
    devices = []

    try:
        nm.scan(
            hosts=target,
            ports=ports,
            arguments=f"-sV --host-timeout {timeout}s",
        )
    except nmap.PortScannerError as e:
        print(f"  Nmap scan error: {e}")
        return devices

    for host in nm.all_hosts():
        device = DeviceInfo(
            ip=host,
            hostname=nm[host].hostname() or "",
            scan_time=datetime.now(timezone.utc).isoformat(),
        )

        # Extract MAC and vendor if available
        if "mac" in nm[host].get("addresses", {}):
            device.mac = nm[host]["addresses"]["mac"]
        if "vendor" in nm[host]:
            vendors = nm[host]["vendor"]
            if vendors:
                device.vendor = list(vendors.values())[0]

        # Extract OS guess
        if "osmatch" in nm[host]:
            matches = nm[host]["osmatch"]
            if matches:
                device.os_guess = matches[0].get("name", "")

        # Extract open ports
        for proto in nm[host].all_protocols():
            for port in nm[host][proto]:
                port_info = nm[host][proto][port]
                if port_info["state"] == "open":
                    device.open_ports.append(
                        PortResult(
                            port=port,
                            state="open",
                            service=port_info.get("name", ""),
                            version=port_info.get("version", ""),
                            protocol=proto,
                        )
                    )

        devices.append(device)

    return devices


def scan_ports_socket(
    target: str,
    ports: str = "22,80,443",
    timeout: int = 2,
    max_concurrent: int = 50,
) -> list:
    """
    Scan ports using stdlib socket (no nmap dependency).

    Slower and less detailed than nmap, but works everywhere.
    """
    port_list = _parse_ports(ports)
    device = DeviceInfo(
        ip=target,
        scan_time=datetime.now(timezone.utc).isoformat(),
    )

    # Resolve hostname
    try:
        device.hostname = socket.getfqdn(target)
    except socket.herror:
        pass

    # Scan ports concurrently
    open_ports = []
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=max_concurrent
    ) as executor:
        futures = {
            executor.submit(_check_port, target, port, timeout): port
            for port in port_list
        }

        for future in concurrent.futures.as_completed(futures):
            port = futures[future]
            try:
                is_open, service, ttl = future.result()
                if is_open:
                    open_ports.append(
                        PortResult(
                            port=port,
                            state="open",
                            service=service,
                        )
                    )
                    if ttl > 0:
                        device.ttl = ttl
            except Exception:
                pass

    device.open_ports = sorted(open_ports, key=lambda p: p.port)
    return [device] if device.open_ports or target == "127.0.0.1" else []


def _check_port(host: str, port: int, timeout: int) -> tuple:
    """Check if a single port is open. Returns (is_open, service, ttl)."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))

        if result == 0:
            service = _guess_service(port)
            ttl = 0
            try:
                ttl = sock.getsockopt(socket.IPPROTO_IP, socket.IP_TTL)
            except (OSError, AttributeError):
                pass
            sock.close()
            return True, service, ttl

        sock.close()
        return False, "", 0

    except (socket.timeout, OSError):
        return False, "", 0


def _guess_service(port: int) -> str:
    """Guess service name from well-known port numbers."""
    services = {
        21: "ftp", 22: "ssh", 23: "telnet", 25: "smtp",
        53: "dns", 80: "http", 110: "pop3", 143: "imap",
        443: "https", 445: "smb", 993: "imaps", 995: "pop3s",
        3306: "mysql", 3389: "rdp", 5432: "postgresql",
        8080: "http-proxy", 8443: "https-alt",
    }
    return services.get(port, f"unknown-{port}")


def _parse_ports(ports_str: str) -> list:
    """Parse port specification string into a list of port numbers."""
    ports = []
    for part in ports_str.split(","):
        part = part.strip()
        if "-" in part:
            start, end = part.split("-", 1)
            ports.extend(range(int(start), int(end) + 1))
        else:
            ports.append(int(part))
    return sorted(set(ports))


def scan_network(
    target: str = "127.0.0.1",
    ports: str = "22,80,443",
    timeout: int = 2,
    max_concurrent: int = 50,
    use_nmap: bool = None,
) -> list:
    """
    Scan a network target for devices and open ports.

    Auto-selects nmap if available, falls back to socket scanning.
    """
    if use_nmap is None:
        use_nmap = HAS_NMAP

    if use_nmap and HAS_NMAP:
        print(f"  Using nmap scanner...")
        return scan_ports_nmap(target, ports, timeout)
    else:
        if use_nmap and not HAS_NMAP:
            print(
                "  nmap not available, falling back to socket scanner..."
            )
        return scan_ports_socket(target, ports, timeout, max_concurrent)


if __name__ == "__main__":
    import json
    from dataclasses import asdict

    print("Scanning localhost...")
    devices = scan_network("127.0.0.1")
    for d in devices:
        print(json.dumps(asdict(d), indent=2, default=str))
