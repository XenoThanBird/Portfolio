# 10 — AI Sentinel: Cybersecurity Suite

Defensive cybersecurity tools for critical infrastructure — file integrity monitoring, network auditing, threat intelligence, encryption, and TLS compliance analysis.

## Overview

The AI Sentinel Cybersecurity Suite is a collection of five production-pattern security tools demonstrating defensive cybersecurity capabilities. Each tool addresses a different domain of the security lifecycle: detection, discovery, deception, protection, and compliance.

Designed for critical infrastructure environments where security monitoring, encryption, and compliance are mission-critical requirements.

## Tools

### 1. The Sentinel Script — File Integrity Monitor

Automated file integrity monitoring with real-time detection of unauthorized system changes.

| File | Description |
| ---- | ----------- |
| `sentinel.py` | Core FIM engine — recursive SHA-256 hashing, baseline comparison, watch modes |
| `alert_handler.py` | Multi-channel alert routing with severity, cooldown, and dedup logic |
| `baseline_manager.py` | Baseline snapshot management — versioning, comparison, reporting |
| `config.yaml` | Full configuration — watch paths, severity rules, alert channels |
| `example.py` | Self-contained demo that simulates and detects file system changes |

```bash
python example.py                           # Interactive demo
python sentinel.py --mode baseline          # Create baseline
python sentinel.py --mode scan              # One-shot integrity check
python sentinel.py --mode watch             # Continuous monitoring
```

### 2. Network Inventory & Audit

Network discovery and port scanning tool — identify devices and exposed services on authorized networks.

| File | Description |
| ---- | ----------- |
| `network_mapper/scanner.py` | Network scanner with nmap and socket fallback — device discovery, port scanning |
| `network_mapper/device_fingerprint.py` | MAC vendor lookup (OUI database), OS fingerprinting via TTL/port heuristics |
| `network_mapper/network_visualizer.py` | NetworkX + matplotlib topology visualization — nodes colored by device type |
| `network_mapper/report_generator.py` | Markdown/JSON inventory report with risk flags for exposed services |
| `network_mapper/config.yaml` | Target subnet, port ranges, scan timeout, visualization settings |
| `network_mapper/example.py` | Demo scanning localhost + simulated network with visualization and report |

```bash
cd network_mapper
python example.py                           # Scan localhost + simulated devices
```

### 3. Threat Intelligence Honeypot

Simulated service listeners that log and analyze connection attempts for threat intelligence.

| File | Description |
| ---- | ----------- |
| `honeypot/honeypot_server.py` | Async TCP listener (asyncio) simulating SSH, HTTP, and Telnet services |
| `honeypot/session_logger.py` | JSONL session logging — source IP, port, timestamp, payload, classification |
| `honeypot/threat_analyzer.py` | Attack analysis — top IPs, frequency, port preference, time patterns |
| `honeypot/dashboard.py` | Streamlit dashboard — connection timeline, top IPs, port heatmap, patterns |
| `honeypot/config.yaml` | Listener ports, log directory, analysis window, dashboard settings |
| `honeypot/example.py` | Demo with SIMULATED attack logs — generates synthetic data, runs analysis |

```bash
cd honeypot
python example.py                           # Generate and analyze simulated attacks
streamlit run dashboard.py                   # Interactive threat dashboard
```

### 4. Envelope Encryption File Vault

AES-256 envelope encryption with per-file data keys, master key rotation, and HMAC integrity verification.

| File | Description |
| ---- | ----------- |
| `file_vault/vault.py` | Envelope encryption engine — per-file data keys wrapped by master key |
| `file_vault/key_manager.py` | Master key generation (PBKDF2), storage, rotation, versioning |
| `file_vault/integrity_verifier.py` | HMAC-SHA256 verification — detect tampering without decryption |
| `file_vault/vault_cli.py` | CLI interface — encrypt, decrypt, rotate-keys, verify, list commands |
| `file_vault/config.yaml` | Vault directory, key storage, encryption algorithm, HMAC settings |
| `file_vault/example.py` | Demo: encrypt, verify, rotate keys, decrypt, tamper detection |

```bash
cd file_vault
python example.py                           # Full envelope encryption demo
python vault_cli.py encrypt secret.txt      # Encrypt a file
python vault_cli.py verify                  # Verify all vault files
python vault_cli.py rotate-keys             # Rotate master key
```

### 5. TLS Handshake Analyzer

TLS/SSL certificate and compliance analyzer — inspect certificate chains, cipher suites, and protocol versions.

| File | Description |
| ---- | ----------- |
| `tls_analyzer/tls_inspector.py` | TLS handshake capture — certificate chain, cipher suite, protocol version |
| `tls_analyzer/cert_analyzer.py` | X.509 certificate parsing — issuer, subject, SANs, key size, expiry |
| `tls_analyzer/compliance_checker.py` | Security baseline checks — deprecated protocols, weak ciphers, short keys |
| `tls_analyzer/report_generator.py` | Markdown/JSON compliance report with pass/fail/warning status |
| `tls_analyzer/config.yaml` | Target hosts, compliance rules, warning thresholds |
| `tls_analyzer/example.py` | Demo: analyze google.com and github.com TLS configurations |

```bash
cd tls_analyzer
python example.py                           # Analyze public host TLS configs
python tls_inspector.py github.com          # Quick single-host inspection
```

## Features

- **File Integrity Monitoring** — SHA-256 hashing, baseline comparison, four change types, severity classification
- **Network Discovery** — Device fingerprinting, port scanning, risk assessment, topology visualization
- **Threat Intelligence** — Honeypot logging, attacker profiling, time-pattern analysis, Streamlit dashboard
- **Envelope Encryption** — Per-file data keys, master key rotation, HMAC integrity, CLI tooling
- **TLS Compliance** — Certificate inspection, cipher validation, protocol checking, compliance reports
- **Zero External Services** — All tools run locally with no cloud dependencies

## Tech Stack

`Python` `SHA-256` `AES-256-GCM` `HMAC-SHA256` `PBKDF2` `asyncio` `ssl/socket` `Watchdog` `NetworkX` `matplotlib` `Streamlit` `python-nmap` `YAML` `JSONL`

## Responsible Use

These tools are designed for **defensive security** — protecting systems you own and have authorization to monitor. Always:

- Only scan networks you own or have explicit written permission to scan
- Use honeypots on your own infrastructure, not to deceive real users
- Encrypt data you are authorized to handle
- Follow your organization's security policies and applicable regulations
