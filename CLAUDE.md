# CLAUDE.md — AI Assistant Guide for Portfolio Repository

## Project Overview

This is Matthan Bird's AI/ML Portfolio — production-grade projects spanning conversational AI, speech recognition, computer vision, robotics, infrastructure defense, agentic architectures, and full-stack AI lifecycle management, organized into eight capability sections. Each top-level directory is a self-contained section with its own documentation, configuration, and example scripts. (A former wealth-building module was extracted to its own repository.)

**Language**: Python 3.9+
**License**: Apache-2.0
**Contact**: bird.matthan@gmail.com

## Repository Structure

```
Portfolio/
├── conversational-ai/         # Conversational AI section (unified README)
│   ├── ivr-routing/           # IVR routing with NLU + LLM confidence scoring
│   ├── prompt-engineering/    # GPT-4o prompt sets, function calling schemas
│   ├── nlp-tools/             # Streamlit dashboards for similarity & analytics
│   └── asr-lab/               # ASR config testing & sensitivity optimization
│       └── configs/
├── ai-governance/             # Responsible AI policies, NERC CIP/NIST compliance
├── computer-vision/           # YOLOv8 + BLIP-2 monitoring, anomaly detection
├── robotics/                  # Boston Dynamics Spot mission orchestration
├── agentic-ai/                # RAG agent, MCP server, multi-agent orchestrator
│   ├── rag_agent/
│   ├── mcp_server/
│   └── multi_agent/
├── digital-twin/              # Encrypted vector search, knowledge graphs, lineage
│   └── storage/
├── infrastructure-defense/    # FIM (sentinel.py), network mapper, honeypot, vault, TLS
│   ├── network_mapper/
│   ├── honeypot/
│   ├── file_vault/
│   └── tls_analyzer/
├── ai-solution-lifecycle/     # Full-stack AI lifecycle platform (FastAPI + Vue 3)
│   ├── backend/
│   │   └── app/               # models/, routers/, schemas/, services/
│   └── frontend/
│       └── src/               # api/, components/, router/, stores/, views/
├── packages/
│   ├── agent-governance-kit/  # Installable package: audit chain, scrubber,
│   │   ├── src/agent_governance_kit/   # sentinel, failure state machine, HITL gate
│   │   ├── tests/             # pytest suite (own CI job, ≥80% coverage floor)
│   │   └── examples/          # end-to-end demo (make demo)
│   └── value-registry/        # Installable package: opportunity value model +
│       ├── src/value_registry/  # model registry, evidence-classed figures
│       ├── data/              # fixed-seed synthetic catalog (140 entries)
│       ├── examples/          # rubric + portfolio YAML (synthetic)
│       └── tests/             # pytest suite (own CI job, ≥80% coverage floor)
├── requirements.txt           # Master dependency list for all modules
├── toolkit_starter_notebook.py # Starter notebook / onboarding script
├── SECURITY.md
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
| **Speech/ASR** | Azure Speech, Deepgram, Speechmatics, Kore.ai integration (asr-lab) |
| **Web/API** | FastAPI, SQLAlchemy + Alembic, Vue 3, Pinia, Tailwind CSS, Vite (ai-solution-lifecycle) |
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

- `OPENAI_API_KEY` — prompt-engineering, agentic-ai, ai-solution-lifecycle
- `ANTHROPIC_API_KEY` — agentic-ai, ai-solution-lifecycle
- `SPOT_HOSTNAME`, `SPOT_USERNAME`, `SPOT_PASSWORD` — robotics
- `DATABASE_URL`, `SECRET_KEY`, `LLM_PROVIDER` — ai-solution-lifecycle

## Code Conventions

### Configuration Pattern
- **YAML files** (`config.yaml`) for static configuration (thresholds, paths, feature toggles)
- **Pydantic BaseSettings** for typed, validated runtime config (agentic-ai, digital-twin)
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

### conversational-ai/ (4 submodules, unified README)
- **ivr-routing/**: Confidence-based intent routing with LLM fallback. Key files: `router_logic.py` (routing engine), `batch_evaluator.py` (accuracy testing), `example_utterance_clustering_cosine_similarity.py` (NLP clustering). Config: `router_taskmap.json`. Test data: `router_test_set.csv`.
- **prompt-engineering/**: Enterprise GPT-4o prompts for billing and support bots. `function_calling_schema.json` defines 6 OpenAI function tools. `prompt_test_runner.ipynb` for validation. `prompt_test_set.csv` for test cases.
- **nlp-tools/**: Two Streamlit apps: `streamlit_cosine_tool.py` (similarity scoring) and `llm_analytics_dashboard.py` (LLM performance metrics). Plus `address_training_pipeline.py` using libpostal.
- **asr-lab/**: ASR configuration testing and optimization for IVR systems (Kore.ai, Azure Speech, Deepgram, Speechmatics). `batch_asr_tester.py` — batch-tests configs against background-noise scenarios. `sensitivity_optimizer.py` — RMS-based sensitivity threshold calculation. `asr_config_tester_app.py` — Streamlit testing dashboard. YAML/JSON config converters and sample engine configs in `configs/`. Has its own `requirements.txt` and `Dockerfile`.

### ai-governance/
Documentation-only module. Policy templates, deployment best practices, training plans, RACI matrix (`.xlsx`). No executable code.

### computer-vision/
`vision_monitor.py` — Real-time YOLOv8 + BLIP-2 pipeline with CSV/JSON logging and Grafana export. `anomaly_detector.py` — Time-series anomaly detection (threshold, Z-score, Isolation Forest) with SQLite storage. `alert_pipeline.py` — Multi-level alerting with cooldowns. Configured via `config.yaml`.

### robotics/
`spot_client.py` — Spot SDK wrapper with connect/power/capture/status methods. `mission_orchestrator.py` — Checkpoint-based mission scheduling. `report_generator.py` — Post-mission Markdown/JSON reports. Configured via `inspection_config.yaml`.

### agentic-ai/ (3 submodules)
- **rag_agent/**: LangGraph StateGraph workflow (analyze → retrieve → augment_tools → synthesize). FAISS vector store with persistence. Wikipedia & ArXiv tool integrations.
- **mcp_server/**: MCP protocol server with tool registration + async HTTP client with retries.
- **multi_agent/**: Agent orchestrator/dispatcher with JSONL audit logging and API key rotation.

### digital-twin/
Multi-database architecture: `vector_db.py` (ChromaDB with Fernet encryption), `knowledge_graph.py` (NetworkX with centrality/community analysis), `metadata_db.py` (SQLAlchemy ORM for data lineage). `encryptor.py` classifies sensitivity (HIGH/MEDIUM/LOW/PUBLIC) and encrypts accordingly.

### infrastructure-defense/ (5 components)
- **sentinel.py** (module root, with `baseline_manager.py` and `alert_handler.py`): File integrity monitoring via SHA-256 + Watchdog filesystem events.
- **network_mapper/**: Nmap-based discovery, MAC/OS fingerprinting, topology visualization.
- **honeypot/**: Async TCP listener simulating SSH/HTTP/Telnet with attack analysis dashboard.
- **file_vault/**: AES-256-GCM envelope encryption with PBKDF2 master key derivation and HMAC integrity.
- **tls_analyzer/**: TLS handshake inspection, X.509 parsing, compliance checking against security baselines.

### ai-solution-lifecycle/
Full-stack platform for evaluating and managing AI solution deployments. **Backend** (`backend/app/`): FastAPI + SQLAlchemy + Alembic — routers, models, schemas, and services for projects, milestones, RACI, SLAs, alerts, risks, change requests, prompt library, model catalog, value scoring (weighted 6-dimension engine with ROI/NPV), and LLM-backed document generation (OpenAI/Anthropic/mock providers). **Frontend** (`frontend/src/`): Vue 3 + Pinia + Tailwind SPA with views/components per domain. `seed_demo.py` seeds synthetic demo data. Dockerized (per-service Dockerfiles).

## Testing Approach

There is no formal test suite or test runner. Testing is done through:
- **Batch evaluation scripts** — `conversational-ai/ivr-routing/batch_evaluator.py` validates router accuracy against CSV test sets
- **Example scripts** — Most modules include `example.py` for self-contained demos
- **Jupyter notebooks** — `conversational-ai/prompt-engineering/prompt_test_runner.ipynb` for interactive prompt validation
- **Synthetic data generators** — `computer-vision/data_generator.py` creates test sensor data

## Key Files to Know

| File | Why It Matters |
|------|---------------|
| `requirements.txt` | Master dependency list — grouped by module |
| `.gitignore` | Excludes .env, *.db, *.pt, *.bin, logs/, vault_data/, baselines/ |
| `toolkit_starter_notebook.py` | Onboarding entry point |
| `computer-vision/config.yaml` | Representative YAML config pattern used across modules |
| `agentic-ai/rag_agent/agent.py` | Most complex code — LangGraph workflow with 4 nodes |
| `infrastructure-defense/file_vault/vault.py` | Envelope encryption reference implementation |

## Guidelines for AI Assistants

1. **Read before editing** — Each module is self-contained; understand its specific patterns before making changes.
2. **Preserve config-driven design** — Changes to behavior should go through YAML configs or Pydantic settings, not hardcoded values.
3. **No secrets in code** — Use `.env` files and `python-dotenv`. Never commit API keys, passwords, or credentials.
4. **Match existing style** — Use dataclasses for data records, Pydantic for validated models, YAML for config. Follow the module's existing patterns.
5. **Keep modules independent** — Cross-module imports should not be introduced. Each section directory is standalone.
6. **Respect the license** — Apache-2.0: redistribution and derivative works are permitted with attribution; retain the LICENSE and NOTICE files and the copyright notice.
7. **Documentation matters** — Each module has its own README/markdown docs. Update them when making structural changes.
8. **No unnecessary abstractions** — Code is intentionally straightforward and readable. Don't over-engineer.
9. **Security-first in digital-twin and infrastructure-defense** — These modules handle encryption, integrity, and network security. Be extra careful with changes that could weaken security guarantees.
10. **Sensitive data patterns** — The `.gitignore` is carefully configured. Never commit database files (*.db), model weights (*.pt, *.bin), encrypted data (*.encrypted), vault keys, or log directories.
