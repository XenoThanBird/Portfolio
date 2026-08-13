"""
Network Inventory & Audit — Device Fingerprinting

MAC vendor lookup (OUI database subset) and OS fingerprinting via
TTL/window size heuristics.
"""

from dataclasses import dataclass
from typing import Optional

from scanner import DeviceInfo


# Common OUI prefixes (first 3 bytes of MAC address)
# In production, use a full OUI database from IEEE
OUI_DATABASE = {
    "00:50:56": "VMware",
    "00:0C:29": "VMware",
    "00:1C:42": "Parallels",
    "08:00:27": "VirtualBox",
    "52:54:00": "QEMU/KVM",
    "00:15:5D": "Hyper-V",
    "00:16:3E": "Xen",
    "B8:27:EB": "Raspberry Pi",
    "DC:A6:32": "Raspberry Pi",
    "E4:5F:01": "Raspberry Pi",
    "AC:DE:48": "Amazon (Ring/Echo)",
    "F0:D2:F1": "Amazon",
    "44:65:0D": "Amazon",
    "18:B4:30": "Nest/Google",
    "64:16:66": "Nest/Google",
    "30:FD:38": "Google",
    "F4:F5:D8": "Google",
    "70:B3:D5": "IEEE Registered (IoT)",
    "00:17:88": "Philips Hue",
    "94:10:3E": "Belkin/WeMo",
    "B0:C5:54": "D-Link",
    "C0:56:27": "Belkin",
    "00:24:E4": "Cisco",
    "00:1A:A1": "Cisco",
    "00:0D:BC": "Cisco",
    "00:14:22": "Dell",
    "00:1E:C9": "Dell",
    "3C:D9:2B": "HP",
    "00:21:5A": "HP",
    "00:25:B5": "HP",
    "D8:9E:F3": "Apple",
    "A4:83:E7": "Apple",
    "F0:18:98": "Apple",
    "00:1B:63": "Apple",
    "48:60:BC": "Apple",
    "3C:22:FB": "Apple",
    "98:01:A7": "Apple",
    "DC:2B:2A": "Apple",
    "F8:FF:C2": "Apple",
}

# TTL-based OS fingerprinting heuristics
# Different OSes use different default TTL values
TTL_FINGERPRINTS = {
    (60, 65): "Linux/Android",
    (120, 130): "Windows",
    (250, 256): "Cisco/Network Device",
    (30, 35): "Older Linux",
}


def lookup_mac_vendor(mac: str) -> str:
    """
    Look up the vendor/manufacturer from a MAC address using OUI prefix.

    The first 3 bytes (6 hex chars) of a MAC address identify the
    manufacturer (Organizationally Unique Identifier).
    """
    if not mac:
        return ""

    # Normalize MAC format
    mac_clean = mac.upper().replace("-", ":").replace(".", ":")
    parts = mac_clean.split(":")

    if len(parts) < 3:
        return ""

    # Try 3-byte prefix
    prefix = ":".join(parts[:3])
    return OUI_DATABASE.get(prefix, "")


def fingerprint_os(ttl: int = 0, open_ports: list = None) -> str:
    """
    Guess the operating system based on TTL and open port heuristics.

    TTL fingerprinting: different OSes use different initial TTL values.
    Port heuristics: certain port combinations are characteristic of
    specific OS types.
    """
    guesses = []

    # TTL-based guess
    if ttl > 0:
        for (low, high), os_name in TTL_FINGERPRINTS.items():
            if low <= ttl <= high:
                guesses.append(os_name)
                break

    # Port-based heuristics
    if open_ports:
        port_nums = {p.port if hasattr(p, "port") else p for p in open_ports}

        if 3389 in port_nums:
            guesses.append("Windows (RDP)")
        elif 445 in port_nums and 135 in port_nums:
            guesses.append("Windows (SMB+RPC)")

        if 22 in port_nums and 3389 not in port_nums:
            if 80 in port_nums or 443 in port_nums:
                guesses.append("Linux Server")

        if 548 in port_nums:
            guesses.append("macOS (AFP)")
        if 5353 in port_nums:
            guesses.append("macOS/Linux (mDNS)")

        if 80 in port_nums and len(port_nums) == 1:
            guesses.append("IoT/Embedded Device")

    if guesses:
        return guesses[0]
    return "Unknown"


def classify_device_type(device: DeviceInfo) -> str:
    """
    Classify a device type based on vendor, ports, and OS fingerprint.

    Categories: gateway, server, workstation, iot, unknown
    """
    vendor_lower = (device.vendor or "").lower()
    os_lower = (device.os_guess or "").lower()
    port_nums = {p.port for p in device.open_ports}

    # Gateway/Router detection
    if any(
        keyword in vendor_lower
        for keyword in ["cisco", "netgear", "linksys", "ubiquiti", "tp-link"]
    ):
        return "gateway"
    if 53 in port_nums and (80 in port_nums or 443 in port_nums):
        return "gateway"

    # Server detection
    server_ports = {22, 25, 53, 80, 443, 3306, 5432, 8080, 8443}
    if len(port_nums & server_ports) >= 3:
        return "server"
    if "server" in os_lower or "linux" in os_lower:
        return "server"

    # IoT detection
    iot_vendors = [
        "raspberry pi", "nest", "ring", "echo", "hue",
        "belkin", "wemo", "iot",
    ]
    if any(v in vendor_lower for v in iot_vendors):
        return "iot"
    if len(port_nums) <= 1 and 80 in port_nums:
        return "iot"

    # Workstation detection
    if "windows" in os_lower or "macos" in os_lower or "apple" in vendor_lower:
        return "workstation"
    if 3389 in port_nums or 548 in port_nums:
        return "workstation"

    return "unknown"


def enrich_device(device: DeviceInfo) -> DeviceInfo:
    """
    Enrich a device with fingerprinting data: vendor lookup,
    OS fingerprint, and device type classification.
    """
    # MAC vendor lookup
    if device.mac and not device.vendor:
        device.vendor = lookup_mac_vendor(device.mac)

    # OS fingerprinting
    if not device.os_guess:
        device.os_guess = fingerprint_os(
            ttl=device.ttl,
            open_ports=device.open_ports,
        )

    # Device type classification
    device.device_type = classify_device_type(device)

    return device
