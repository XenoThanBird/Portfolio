# Robotics & Autonomous Systems

AI/ML integration for autonomous inspection robots in industrial environments. This template demonstrates a generic mission orchestration framework built on the public Boston Dynamics Spot SDK.

No proprietary configurations, facility data, or employer-specific code is included.

---

## Template Files

| File | Description |
| ---- | ----------- |
| `mission_orchestrator.py` | Mission scheduling, execution loop, and status monitoring |
| `inspection_config.yaml` | Configurable inspection checkpoints and alert rules |
| `report_generator.py` | Post-mission report generation (Markdown + JSON) |
| `spot_client.py` | Lightweight Spot SDK wrapper for common operations |
| `.env.template` | Environment variable template for robot credentials |

---

## Features

- Mission scheduling with configurable checkpoint sequences
- Status monitoring and health checks during execution
- Configurable inspection points with pass/fail criteria
- Automatic report generation after each mission (Markdown + JSON)
- Alert pipeline integration for anomaly detection during patrols
- Built entirely on the [public Boston Dynamics Spot SDK](https://github.com/boston-dynamics/spot-sdk)

---

## Architecture

```text
┌─────────────────┐     ┌──────────────┐     ┌──────────────────┐
│ Mission Config   │────▶│ Orchestrator │────▶│ Spot SDK Client  │
│ (YAML)          │     │              │     │                  │
└─────────────────┘     │  schedule    │     │  authenticate    │
                        │  execute     │     │  navigate        │
┌─────────────────┐     │  monitor     │     │  capture_image   │
│ Alert Pipeline   │◀───│  alert       │     │  check_status    │
│                 │     │              │     └──────────────────┘
└─────────────────┘     └──────┬───────┘
                               │
                        ┌──────▼───────┐
                        │ Report Gen   │
                        │ (MD + JSON)  │
                        └──────────────┘
```

---

## Usage

```bash
# Install dependencies
pip install bosdyn-client bosdyn-mission pyyaml jinja2

# Configure robot connection (copy and edit .env.template)
cp .env.template .env

# Run a mission
python mission_orchestrator.py --config inspection_config.yaml

# Generate a report from the last mission
python report_generator.py --mission-dir logs/missions/latest
```

---

## Prerequisites

- Boston Dynamics Spot SDK (`bosdyn-client`, `bosdyn-mission`)
- Network access to a Spot robot (or use the SDK's mock client for testing)
- Python 3.9+

---

## Tech Stack

`Python` `Boston Dynamics Spot SDK` `YAML` `Jinja2` `asyncio`
