# CLAUDE.md — AI Assistant Guide for Portfolio Repository

## Project Overview

This is Matthan Bird's AI/ML Portfolio — a collection of 10 production-grade projects spanning conversational AI, computer vision, robotics, cybersecurity, agentic architectures, and more. Each numbered directory is a self-contained module with its own documentation, configuration, and example scripts.

**Language**: Python 3.9+
**License**: All Rights Reserved (portfolio/demo purposes only)
**Contact**: bird.matthan@gmail.com

## Repository Structure

```
Portfolio/
├── 01_conversational_ivr/    # IVR routing with NLU + LLM confidence scoring
├── 02_prompt_engineering/     # GPT-4o prompt sets, function calling schemas
├── 03_ai_governance/          # Responsible AI policies, NERC CIP/NIST compliance
├── 04_nlp_tools/              # Streamlit dashboards for similarity & analytics
├── 05_wealth_building/        # AI-driven financial tracking & automation
├── 06_computer_vision/        # YOLOv8 + BLIP-2 monitoring, anomaly detection
├── 07_robotics/               # Boston Dynamics Spot mission orchestration
├── 08_agentic_ai/             # RAG agent, MCP server, multi-agent orchestrator
│   ├── rag_agent/
│   ├── mcp_server/
│   └── multi_agent/
├── 09_digital_twin/           # Encrypted vector search, knowledge graphs, lineage
│   └── storage/
├── 10_ai_sentinel_cybersecurity/  # FIM, network mapper, honeypot, vault, TLS
│   ├── sentinel/
│   ├── network_mapper/
│   ├── honeypot/
│   ├── file_vault/
│   └── tls_analyzer/
├── requirements.txt           # Master dependency list for all modules
├── toolkit_starter_notebook.py # Starter notebook / onboarding script
├── LICENSE
└── README.md
```

## Technology Stack

| Category | Technologies |
|----------|-------------|
| **Core** | Python 3.9+, Pandas, NumPy, scikit-learn |
| **LLMs/Embeddings** | OpenAI GPT-4o, Anthropic Claude, Sentence Transformers (all-MiniLM-L6-v2) |
| **Vision** | YOLOv8 (ultralytics), BLIP-2 (transformers), OpenCV |
| **Agentic** | LangChain, LangGraph, MCP, FAISS, Pydantic v2 |
| **Databases** | SQLite, ChromaDB, NetworkX (graph), SQLAlchemy |
| **Visualization** | Streamlit, Plotly, Seaborn, Matplotlib |
| **Security** | cryptography (Fernet/AES-256-GCM), Watchdog, python-nmap, scapy |
| **Robotics** | Boston Dynamics Spot SDK (bosdyn-client, bosdyn-mission) |
| **Config** | YAML (pyyaml), python-dotenv, Pydantic BaseSettings |

## Development Setup

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate

# Install all dependencies
pip install -r requirements.txt

# Some modules have additional requirements or .env.template files
# Check individual module directories for specifics
```

### Environment Variables

Modules that need API keys or credentials use `.env` files (gitignored). Look for `.env.template` files in subdirectories for required variables:

- `OPENAI_API_KEY` — modules 02, 08
- `ANTHROPIC_API_KEY` — module 08
- `SPOT_HOSTNAME`, `SPOT_USERNAME`, `SPOT_PASSWORD` — module 07

## Code Conventions

### Configuration Pattern
- **YAML files** (`config.yaml`) for static configuration (thresholds, paths, feature toggles)
- **Pydantic BaseSettings** for typed, validated runtime config (modules 08, 09)
- **Environment variables** via `python-dotenv` for secrets — never hardcode credentials

### Data Structures
- **Dataclasses** for immutable records: `RobotStatus`, `ChangeEvent`, `FileRecord`
- **Pydantic models** for validated I/O: `RAGQuery`, `RAGResponse`, `RAGMetrics`
- **TypedDict** for LangGraph state management

### Logging & Observability
- Python `logging` module with structured formatters
- **JSONL** for audit trails and metrics (cybersecurity modules)
- **CSV** for time-series data and test results
- **Markdown + JSON** dual-format report generation

### Error Handling
- Try-except with graceful degradation and fallback paths
- Optional imports with fallback when dependencies are missing
- Confidence-based routing with agent-transfer fallback (IVR module)

### Async Patterns
- `asyncio` for concurrent I/O (honeypot server, MCP client)
- `httpx` for async HTTP with retry logic
- Non-blocking patterns where real-time responsiveness matters

## Module-by-Module Summary

### 01 — Conversational IVR
Confidence-based intent routing with LLM fallback. Key files: `router_logic.py` (routing engine), `batch_evaluator.py` (accuracy testing), `example_utterance_clustering_cosine_similarity.py` (NLP clustering). Config: `router_taskmap.json`. Test data: `router_test_set.csv`.

### 02 — Prompt Engineering
Enterprise GPT-4o prompts for billing and support bots. `function_calling_schema.json` defines 6 OpenAI function tools. `prompt_test_runner.ipynb` for validation. `prompt_test_set.csv` for test cases.

### 03 — AI Governance
Documentation-only module. Policy templates, deployment best practices, training plans, RACI matrix (`.xlsx`). No executable code.

### 04 — NLP Tools
Two Streamlit apps: `streamlit_cosine_tool.py` (similarity scoring) and `llm_analytics_dashboard.py` (LLM performance metrics). Plus `address_training_pipeline.py` using libpostal.

### 05 — Wealth Building
`passive_income_dashboard.py` — Streamlit income/expense tracker. Strategy documents and sample CSV data.

### 06 — Computer Vision
`vision_monitor.py` — Real-time YOLOv8 + BLIP-2 pipeline with CSV/JSON logging and Grafana export. `anomaly_detector.py` — Time-series anomaly detection (threshold, Z-score, Isolation Forest) with SQLite storage. `alert_pipeline.py` — Multi-level alerting with cooldowns. Configured via `config.yaml`.

### 07 — Robotics
`spot_client.py` — Spot SDK wrapper with connect/power/capture/status methods. `mission_orchestrator.py` — Checkpoint-based mission scheduling. `report_generator.py` — Post-mission Markdown/JSON reports. Configured via `inspection_config.yaml`.

### 08 — Agentic AI (3 submodules)
- **rag_agent/**: LangGraph StateGraph workflow (analyze → retrieve → augment_tools → synthesize). FAISS vector store with persistence. Wikipedia & ArXiv tool integrations.
- **mcp_server/**: MCP protocol server with tool registration + async HTTP client with retries.
- **multi_agent/**: Agent orchestrator/dispatcher with JSONL audit logging and API key rotation.

### 09 — Digital Twin
Multi-database architecture: `vector_db.py` (ChromaDB with Fernet encryption), `knowledge_graph.py` (NetworkX with centrality/community analysis), `metadata_db.py` (SQLAlchemy ORM for data lineage). `encryptor.py` classifies sensitivity (HIGH/MEDIUM/LOW/PUBLIC) and encrypts accordingly.

### 10 — Cybersecurity Suite (5 submodules)
- **sentinel/**: File integrity monitoring via SHA-256 + Watchdog filesystem events.
- **network_mapper/**: Nmap-based discovery, MAC/OS fingerprinting, topology visualization.
- **honeypot/**: Async TCP listener simulating SSH/HTTP/Telnet with attack analysis dashboard.
- **file_vault/**: AES-256-GCM envelope encryption with PBKDF2 master key derivation and HMAC integrity.
- **tls_analyzer/**: TLS handshake inspection, X.509 parsing, compliance checking against security baselines.

## Testing Approach

There is no formal test suite or test runner. Testing is done through:
- **Batch evaluation scripts** — `01_conversational_ivr/batch_evaluator.py` validates router accuracy against CSV test sets
- **Example scripts** — Most modules include `example.py` for self-contained demos
- **Jupyter notebooks** — `02_prompt_engineering/prompt_test_runner.ipynb` for interactive prompt validation
- **Synthetic data generators** — `06_computer_vision/data_generator.py` creates test sensor data

## Key Files to Know

| File | Why It Matters |
|------|---------------|
| `requirements.txt` | Master dependency list — grouped by module |
| `.gitignore` | Excludes .env, *.db, *.pt, *.bin, logs/, vault_data/, baselines/ |
| `toolkit_starter_notebook.py` | Onboarding entry point |
| `06_computer_vision/config.yaml` | Representative YAML config pattern used across modules |
| `08_agentic_ai/rag_agent/agent.py` | Most complex code — LangGraph workflow with 4 nodes |
| `10_ai_sentinel_cybersecurity/file_vault/vault.py` | Envelope encryption reference implementation |

## Guidelines for AI Assistants

1. **Read before editing** — Each module is self-contained; understand its specific patterns before making changes.
2. **Preserve config-driven design** — Changes to behavior should go through YAML configs or Pydantic settings, not hardcoded values.
3. **No secrets in code** — Use `.env` files and `python-dotenv`. Never commit API keys, passwords, or credentials.
4. **Match existing style** — Use dataclasses for data records, Pydantic for validated models, YAML for config. Follow the module's existing patterns.
5. **Keep modules independent** — Cross-module imports should not be introduced. Each numbered directory is standalone.
6. **Respect the license** — This is a proprietary portfolio. Do not redistribute code or create derivative works without permission.
7. **Documentation matters** — Each module has its own README/markdown docs. Update them when making structural changes.
8. **No unnecessary abstractions** — Code is intentionally straightforward and readable. Don't over-engineer.
9. **Security-first in modules 09–10** — These modules handle encryption, integrity, and network security. Be extra careful with changes that could weaken security guarantees.
10. **Sensitive data patterns** — The `.gitignore` is carefully configured. Never commit database files (*.db), model weights (*.pt, *.bin), encrypted data (*.encrypted), vault keys, or log directories.
