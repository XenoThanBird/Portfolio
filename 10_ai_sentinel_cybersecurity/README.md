# 10 — The Sentinel Script: File Integrity Monitor

Automated file integrity monitoring for critical infrastructure defense. Detects unauthorized system changes in real-time through recursive hashing, baseline comparison, and multi-channel alerting.

## Overview

The Sentinel Script is a production-pattern File Integrity Monitor (FIM) that continuously watches directories for unauthorized changes — new files, modifications, deletions, and permission changes — and classifies each detection by severity based on configurable rules.

Designed for critical infrastructure environments where unauthorized file changes can indicate compromise, misconfiguration, or insider threats.

## Files

| File | Description |
| ---- | ----------- |
| `sentinel.py` | Core FIM engine — recursive SHA-256 hashing, baseline comparison, watch modes |
| `alert_handler.py` | Multi-channel alert routing with severity, cooldown, and dedup logic |
| `baseline_manager.py` | Baseline snapshot management — versioning, comparison, reporting |
| `config.yaml` | Full configuration — watch paths, severity rules, alert channels |
| `example.py` | Self-contained demo that simulates and detects file system changes |
| `.env.template` | Environment variable template |

## Features

- **SHA-256 recursive hashing** of monitored directories
- **Four change types detected**: added, modified, deleted, permission changed
- **Severity classification** (CRITICAL / HIGH / MEDIUM / LOW) based on file patterns
- **Two watch modes**: polling (stdlib-only) and watchdog (filesystem events)
- **Baseline versioning** with diff, comparison, and audit reporting
- **Multi-channel alerts**: color-coded console, JSONL log, optional webhook
- **Cooldown/dedup logic** to prevent alert storms
- **Graceful shutdown** with signal handling (SIGINT, SIGTERM)
- **Zero external services** — fully self-contained

## Quick Start

```bash
# Run the interactive demo (no setup required)
python example.py

# Or use the CLI directly:
python sentinel.py --mode baseline         # Create initial baseline
python sentinel.py --mode scan             # One-shot integrity check
python sentinel.py --mode watch            # Continuous monitoring
python sentinel.py --config custom.yaml    # Custom configuration
```

## Tech Stack

`Python` `SHA-256` `Watchdog` `YAML` `JSONL` `File Integrity Monitoring` `Cybersecurity`
