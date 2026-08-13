# AI Sentinel — Infrastructure Defense Suite

Defensive tooling for critical-infrastructure environments: integrity
monitoring for the systems that must not drift, network visibility for
the segments that must not surprise you, deception-based early warning,
encryption for data at rest, and TLS compliance verification for
everything in transit.

## Why infrastructure defense is different

Critical-infrastructure environments — energy, water, industrial
control, and the enterprise networks that support them — invert the
usual security priorities. Availability and integrity outrank
confidentiality; an undetected configuration change can matter more
than a stolen document. Monitoring must be passive-first and
non-disruptive, tooling must run without cloud dependencies inside
segmented networks, and every action needs an audit trail because
regulated operators must be able to show *what* changed, *when*, and
*what was done about it*.

The five tools in this suite are built around those constraints. Each
addresses one layer of a defense-in-depth posture, runs entirely
locally, and produces structured, auditable output (JSONL, Markdown,
JSON).

| Defense layer | Tool | Question it answers |
| ---- | ---- | ---- |
| Integrity | Sentinel FIM | Has anything changed on systems that should be static? |
| Visibility | Network Inventory & Audit | What is on this network segment, and what is it exposing? |
| Early warning | Threat Intelligence Honeypot | Who is probing us, and how? |
| Data protection | Envelope Encryption Vault | Is sensitive data unreadable and tamper-evident at rest? |
| Transport compliance | TLS Analyzer | Do our endpoints meet the security baseline we claim? |

## Tools

### 1. Sentinel — File Integrity Monitor

Automated file integrity monitoring with real-time detection of
unauthorized changes. In infrastructure environments, FIM is a
front-line control: HMIs, jump hosts, and configuration stores should
not change outside maintenance windows, and when they do, someone
should know within seconds.

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

Network discovery and exposure auditing for authorized segments. You
cannot defend assets you have not enumerated; in segmented industrial
networks, the inventory *is* the security boundary, and an unexpected
device or open service is a finding by definition.

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

Deception-based early warning: simulated SSH/HTTP/Telnet listeners that
log and profile connection attempts. On a properly segmented network,
*any* connection to a honeypot is signal — a tripwire that fires before
an intruder reaches real assets.

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
streamlit run dashboard.py                  # Interactive threat dashboard
```

### 4. Envelope Encryption File Vault

AES-256-GCM envelope encryption with per-file data keys, master key
rotation, and HMAC integrity verification — the data-at-rest pattern
for configuration archives, incident evidence, and operational records
that must be both confidential and provably untampered.

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

TLS/SSL inspection and baseline compliance checking. Regulated
operators do not just need secure transport — they need to *demonstrate*
it. The inspector deliberately observes whatever a server negotiates
(including legacy protocols and invalid certificates, read-only) so the
compliance checker can flag exactly the misconfigurations that matter.

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

## Design principles

- **Passive-first, non-disruptive** — observation over interaction;
  nothing in this suite modifies a monitored system
- **No cloud dependencies** — every tool runs locally, suitable for
  air-gapped and segmented environments
- **Auditable by default** — structured JSONL/Markdown/JSON output so
  findings can be reconstructed and attributed
- **Config-driven** — YAML configuration throughout; behavior changes
  without code changes

## Tech Stack

`Python` `SHA-256` `AES-256-GCM` `HMAC-SHA256` `PBKDF2` `asyncio` `ssl/socket` `Watchdog` `NetworkX` `matplotlib` `Streamlit` `python-nmap` `YAML` `JSONL`

## Responsible Use

These tools are built for **defense of systems you own or are
authorized to protect**. Always:

- Only scan networks you own or have explicit written permission to scan
- Deploy honeypots on your own infrastructure, never to deceive real users
- Encrypt only data you are authorized to handle
- Follow your organization's security policies and applicable
  regulations, including sector-specific requirements for critical
  infrastructure
