# Matthan Bird, JD – AI Portfolio

AI strategy and solutions leader with end-to-end ownership of enterprise AI transformation — opportunity discovery, business-case development, technical architecture, production delivery, governance, and value realization. Currently PMC Lead Data Scientist, Enterprise Solution Architect & Decision Intelligence Consultant at Duke Energy, designing governed decision-intelligence and multi-agent AI capabilities for enterprise portfolio management. Previously Lead Experimental AI Scientist in Duke Energy's Emerging Technologies R&D lab — multi-agent automation frameworks, battery anomaly detection, autonomous robotics, computer vision, and enterprise GenAI enablement.

Before that, led Conversational AI at Spectrum (Charter Communications), scaling platforms to 18M+ monthly interactions in a regulated, high-volume service environment. J.D. in business and environmental law; U.S. Navy submarine electronics & intelligence veteran.

This repository showcases selected projects across AI/ML engineering, prompt design, NLP tooling, governance strategy, and automation.

---

## Table of Contents

- [Featured Projects](#featured-projects)
  - [Conversational AI](#conversational-ai)
  - [AI Governance & Enterprise Strategy](#ai-governance--enterprise-strategy)
  - [Computer Vision & Anomaly Detection](#computer-vision--anomaly-detection)
  - [Robotics & Autonomous Systems](#robotics--autonomous-systems)
  - [Agentic AI & Enterprise Tooling](#agentic-ai--enterprise-tooling)
  - [Digital Twin Architecture](#digital-twin-architecture)
  - [AI Sentinel — Infrastructure Defense](#ai-sentinel--infrastructure-defense)
  - [AI Solution Lifecycle Platform](#ai-solution-lifecycle-platform)
- [Technical Skills](#technical-skills)
- [Certifications](#certifications)
- [Getting Started](#getting-started)
- [Get in Touch](#get-in-touch)

---

## Featured Projects

### Conversational AI

*End-to-end conversational AI engineering — IVR intent routing, prompt design, NLP analytics, and speech-recognition optimization. See the [section README](conversational-ai/README.md) for the full picture.*

- [`ivr-routing/`](conversational-ai/ivr-routing/) – Confidence-based IVR routing with LLM fallback, batch accuracy evaluation, and utterance clustering
- [`prompt-engineering/`](conversational-ai/prompt-engineering/) – Enterprise GPT-4o prompt sets, OpenAI function calling schema, few-shot examples, and a Jupyter test runner
- [`nlp-tools/`](conversational-ai/nlp-tools/) – Streamlit cosine-similarity scorer, LLM performance analytics dashboard, and libpostal address pipeline
- [`asr-lab/`](conversational-ai/asr-lab/) – ASR configuration batch testing, sensitivity optimization, and cross-engine comparison (Azure Speech, Deepgram, Speechmatics)

### AI Governance & Enterprise Strategy

*Responsible AI documentation and implementation strategies tailored to enterprise environments, including NERC CIP, FERC, and NIST AI RMF compliance.*

- [`ai_governance_policy_template.md`](ai-governance/ai_governance_policy_template.md) – Enterprise governance policy
- [`ai_raci_matrix_template.xlsx`](ai-governance/ai_raci_matrix_template.xlsx) – RACI matrix for AI governance
- [`responsible_llm_guidelines_readme.md`](ai-governance/responsible_llm_guidelines_readme.md) – Safety and compliance guidelines
- [`llm_deployment_best_practices_readme.md`](ai-governance/llm_deployment_best_practices_readme.md) – Operational best practices
- [`llm_deployment_business_strategy_readme.md`](ai-governance/llm_deployment_business_strategy_readme.md) – Business alignment strategy
- [`llm_training_plan.md`](ai-governance/llm_training_plan.md) – Detailed LLM training plan

### Computer Vision & Anomaly Detection

*Multi-modal computer vision, time-series anomaly detection, and GPU-accelerated monitoring systems for critical infrastructure.*

- [`computer-vision/README.md`](computer-vision/README.md) – Module overview
- [`vision_monitor.py`](computer-vision/vision_monitor.py) – YOLOv8 + BLIP-2 monitoring pipeline
- [`alert_pipeline.py`](computer-vision/alert_pipeline.py) – Multi-level alert system with cooldowns
- [`anomaly_detector.py`](computer-vision/anomaly_detector.py) – Time-series anomaly detection (threshold, z-score, isolation forest)
- [`data_generator.py`](computer-vision/data_generator.py) – Synthetic sensor data generator
- [`metrics_exporter.py`](computer-vision/metrics_exporter.py) – Prometheus-format exporter for Grafana

### Robotics & Autonomous Systems

*AI/ML integration for autonomous inspection robots in industrial environments using the public Boston Dynamics Spot SDK.*

- [`robotics/README.md`](robotics/README.md) – Module overview
- [`mission_orchestrator.py`](robotics/mission_orchestrator.py) – Mission scheduling and execution loop
- [`spot_client.py`](robotics/spot_client.py) – Lightweight Spot SDK wrapper
- [`report_generator.py`](robotics/report_generator.py) – Post-mission Markdown + JSON reports
- [`inspection_config.yaml`](robotics/inspection_config.yaml) – Configurable checkpoint definitions

### Agentic AI & Enterprise Tooling

*End-to-end agentic architectures for RAG, MCP servers, and multi-agent orchestration.*

- [`agentic-ai/README.md`](agentic-ai/README.md) – Module overview
- [`rag_agent/`](agentic-ai/rag_agent/) – LangGraph RAG agent with FAISS, tool integration, and structured output
- [`mcp_server/`](agentic-ai/mcp_server/) – MCP server template with tool registration and async client
- [`multi_agent/`](agentic-ai/multi_agent/) – Multi-agent orchestrator with audit logging and API key management

### Digital Twin Architecture

*Privacy-first multi-database digital twin framework with encrypted vector search, knowledge graph analysis, and metadata lineage tracking.*

- [`digital-twin/README.md`](digital-twin/README.md) – Module overview
- [`storage/vector_db.py`](digital-twin/storage/vector_db.py) – ChromaDB wrapper with encryption-aware add/query
- [`storage/knowledge_graph.py`](digital-twin/storage/knowledge_graph.py) – NetworkX graph with centrality analysis and community detection
- [`storage/metadata_db.py`](digital-twin/storage/metadata_db.py) – SQLAlchemy ORM for data lineage and sync tracking
- [`storage/encryptor.py`](digital-twin/storage/encryptor.py) – Fernet (AES-256) encryption with sensitivity classifier
- [`config.py`](digital-twin/config.py) – Pydantic BaseSettings configuration management
- [`example.py`](digital-twin/example.py) – Five runnable examples demonstrating the full stack
- [`architecture.md`](digital-twin/architecture.md) – Detailed architecture documentation

### AI Sentinel — Infrastructure Defense

*Defensive tooling for critical-infrastructure environments — file integrity monitoring, network visibility, deception-based early warning, envelope encryption, and TLS compliance verification.*

- [`infrastructure-defense/README.md`](infrastructure-defense/README.md) – Module overview
- **Sentinel FIM** — File integrity monitor with SHA-256 hashing, baseline comparison, and real-time watch modes
- **Network Inventory & Audit** — Device discovery, port scanning, OS fingerprinting, and topology visualization
- **Threat Intelligence Honeypot** — Async service listeners with JSONL logging, threat analysis, and Streamlit dashboard
- **Envelope Encryption File Vault** — AES-256-GCM envelope encryption with key rotation and HMAC integrity
- **TLS Handshake Analyzer** — Certificate inspection, cipher validation, and compliance reporting

### AI Solution Lifecycle Platform

*Full-stack platform for evaluating, planning, and managing AI solution deployments — from value assessment through production monitoring. FastAPI + Vue 3 + PostgreSQL.*

- [`ai-solution-lifecycle/README.md`](ai-solution-lifecycle/README.md) – Module overview
- **AI Document Generation** — Auto-generate BRDs, TRDs, functional specs from natural language via pluggable LLM providers (OpenAI, Anthropic, Mock)
- **Prompt Library & Playground** — Versioned prompt templates with variable extraction, execution metrics, and interactive testing
- **Milestone Tracking** — Kanban-style project milestones with dependency graph
- **RACI Matrix Builder** — Interactive Responsible/Accountable/Consulted/Informed matrix per deliverable
- **SLA Monitoring & Alerts** — Define, measure, and track SLA compliance with rule-based alerting and cooldown deduplication
- **Risk Register** — 5×5 probability × impact heat map with classification, mitigation tracking, and change request workflow
- **AI Model Catalog** — Registry with LLM-powered use case recommendation engine
- **Value Assessment Engine** — 6-dimension weighted scoring, readiness multiplier, ROI/NPV calculator, and implementation roadmap generation

---

## Technical Skills

| Category | Technologies |
| -------- | ------------ |
| **AI/ML** | AWS Bedrock, SageMaker, Azure AI, OpenAI, HuggingFace, TensorFlow, Computer Vision, NLP, Anomaly Detection, RAG, Agentic AI |
| **Cloud & Infrastructure** | AWS (Lambda, S3, OpenSearch, GuardDuty), Azure, Docker, PostgreSQL, TimescaleDB, NATS JetStream, Grafana |
| **Development** | Python, SQL, JavaScript, FastAPI, MCP, Git/GitHub, Power BI, ServiceNow |
| **Frameworks & Libraries** | Streamlit, Pandas, NumPy, scikit-learn, Sentence Transformers, Plotly, Seaborn, Matplotlib |

---

## Certifications

- AWS Certified AI Practitioner (AIF-C01) — 2026
- Developing Generative AI Solutions on AWS — 2026
- Developing Machine Learning Solutions on AWS — 2026
- Security, Compliance, and Governance for AI Solutions — 2026
- Microsoft Certified: Azure AI Fundamentals (AI-900)
- US Naval Nuclear Submarine Program Advanced Technical Training

---

## Getting Started

**Requirements:** Python 3.9+

```bash
# Clone the repository
git clone https://github.com/XenoThanBird/Portfolio.git
cd Portfolio

# Create a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate    # macOS/Linux
.venv\Scripts\activate       # Windows

# Install dependencies
pip install -r requirements.txt
```

To run any Streamlit dashboard:

```bash
streamlit run conversational-ai/nlp-tools/streamlit_cosine_tool.py
```

---

## Get in Touch

For collaboration, consulting, or just a great conversation about agentic AI systems, reach out:

- **LinkedIn**: [linkedin.com/in/matthan-bird-jd-mdb28173](https://www.linkedin.com/in/matthan-bird-jd-mdb28173)
- **Email**: [bird.matthan@gmail.com](mailto:bird.matthan@gmail.com)

---

> "The future belongs to those who design it."
> — Matthan Bird
