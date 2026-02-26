# Matthan Bird, JD – AI Portfolio

Experimental AI Specialist and Emerging Technology Innovation Lab Lead with 20+ years of leadership experience spanning production AI systems, computer vision, robotics integration, NLP, and enterprise AI governance. Currently architecting and deploying AI solutions for critical infrastructure at Duke Energy's ETO Innovation Lab — from battery anomaly detection and autonomous robotics to multi-modal computer vision and cybersecurity frameworks.

Previously led Conversational AI at Spectrum (Charter Communications), scaling platforms to 18M+ monthly interactions with $3.53B+ in documented business value.

This repository showcases selected projects across AI/ML engineering, prompt design, NLP tooling, governance strategy, and automation.

---

## Table of Contents

- [Featured Projects](#featured-projects)
  - [1. Conversational IVR & NLP Optimization](#1-conversational-ivr--nlp-optimization)
  - [2. Prompt Engineering & GPT Fine-Tuning](#2-prompt-engineering--gpt-fine-tuning)
  - [3. AI Governance & Enterprise Strategy](#3-ai-governance--enterprise-strategy)
  - [4. NLP Tools & Dashboards](#4-nlp-tools--dashboards)
  - [5. Wealth Building through AI Automation](#5-wealth-building-through-ai-automation)
  - [6. Computer Vision & Anomaly Detection](#6-computer-vision--anomaly-detection)
  - [7. Robotics & Autonomous Systems](#7-robotics--autonomous-systems)
  - [8. Agentic AI & Enterprise Tooling](#8-agentic-ai--enterprise-tooling)
  - [9. Digital Twin Architecture](#9-digital-twin-architecture)
- [Technical Skills](#technical-skills)
- [Certifications](#certifications)
- [Getting Started](#getting-started)
- [Get in Touch](#get-in-touch)

---

## Featured Projects

### 1. Conversational IVR & NLP Optimization

*Redesigning legacy IVR systems using Kore.ai with integrated LLM routing, Few-Shot intent mapping, and AI-first NLU analytics.*

- [`top_of_ivr_llm_router_readme.md`](01_conversational_ivr/top_of_ivr_llm_router_readme.md) – Top-of-IVR LLM router design
- [`router_logic.py`](01_conversational_ivr/router_logic.py) – Confidence-based routing with fallback logic
- [`batch_evaluator.py`](01_conversational_ivr/batch_evaluator.py) – Batch evaluation of router accuracy
- [`cosine_similarity.md`](01_conversational_ivr/cosine_similarity.md) – Utterance clustering using cosine similarity
- [`example_utterance_clustering_cosine_similarity.py`](01_conversational_ivr/example_utterance_clustering_cosine_similarity.py) – Clustering example script

### 2. Prompt Engineering & GPT Fine-Tuning

*Custom GPT-4o prompt sets for enterprise bots, billing routers, and zero-shot model training in Kore.ai.*

- [`prompt_engineering_readme.md`](02_prompt_engineering/prompt_engineering_readme.md) – Module overview
- [`billing_router_prompt_1.md`](02_prompt_engineering/billing_router_prompt_1.md) – Cable/Mobile billing router prompt
- [`cable_billing_router_prompt_2.md`](02_prompt_engineering/cable_billing_router_prompt_2.md) – Specialized cable billing prompt
- [`few_shot_prompt_examples.md`](02_prompt_engineering/few_shot_prompt_examples.md) – Few-shot examples for function calling
- [`function_calling_schema.json`](02_prompt_engineering/function_calling_schema.json) – OpenAI function calling schema
- [`prompt_test_runner.ipynb`](02_prompt_engineering/prompt_test_runner.ipynb) – Jupyter notebook for prompt validation

### 3. AI Governance & Enterprise Strategy

*Responsible AI documentation and implementation strategies tailored to enterprise environments, including NERC CIP, FERC, and NIST AI RMF compliance.*

- [`ai_governance_policy_template.md`](03_ai_governance/ai_governance_policy_template.md) – Enterprise governance policy
- [`ai_raci_matrix_template.xlsx`](03_ai_governance/ai_raci_matrix_template.xlsx) – RACI matrix for AI governance
- [`responsible_llm_guidelines_readme.md`](03_ai_governance/responsible_llm_guidelines_readme.md) – Safety and compliance guidelines
- [`llm_deployment_best_practices_readme.md`](03_ai_governance/llm_deployment_best_practices_readme.md) – Operational best practices
- [`llm_deployment_business_strategy_readme.md`](03_ai_governance/llm_deployment_business_strategy_readme.md) – Business alignment strategy
- [`llm_training_plan.md`](03_ai_governance/llm_training_plan.md) – Detailed LLM training plan

### 4. NLP Tools & Dashboards

*Python & Streamlit apps for sentence similarity scoring, semantic clustering, and LLM performance analytics.*

- [`nlp_tools_readme.md`](04_nlp_tools/nlp_tools_readme.md) – Module overview
- [`streamlit_cosine_tool.py`](04_nlp_tools/streamlit_cosine_tool.py) – Cosine similarity UI tool
- [`llm_analytics_dashboard.py`](04_nlp_tools/llm_analytics_dashboard.py) – LLM performance analytics dashboard
- [`address_training_pipeline.py`](04_nlp_tools/address_training_pipeline.py) – Address recognition pipeline for IVRs

### 5. Wealth Building through AI Automation

*Personal experiments in building recession-resistant, passive-income systems powered by AI.*

- [`wealth_building_ai_readme.md`](05_wealth_building/wealth_building_ai_readme.md) – Module overview
- [`24_month_wealth_building_strategy.md`](05_wealth_building/24_month_wealth_building_strategy.md) – 24-month financial freedom roadmap
- [`automation_model_framework.md`](05_wealth_building/automation_model_framework.md) – Project scoring framework
- [`passive_income_dashboard.py`](05_wealth_building/passive_income_dashboard.py) – Income tracking dashboard

### 6. Computer Vision & Anomaly Detection

*Multi-modal computer vision, time-series anomaly detection, and GPU-accelerated monitoring systems for critical infrastructure.*

- [`06_computer_vision/README.md`](06_computer_vision/README.md) – Module overview
- [`vision_monitor.py`](06_computer_vision/vision_monitor.py) – YOLOv8 + BLIP-2 monitoring pipeline
- [`alert_pipeline.py`](06_computer_vision/alert_pipeline.py) – Multi-level alert system with cooldowns
- [`anomaly_detector.py`](06_computer_vision/anomaly_detector.py) – Time-series anomaly detection (threshold, z-score, isolation forest)
- [`data_generator.py`](06_computer_vision/data_generator.py) – Synthetic sensor data generator
- [`metrics_exporter.py`](06_computer_vision/metrics_exporter.py) – Prometheus-format exporter for Grafana

### 7. Robotics & Autonomous Systems

*AI/ML integration for autonomous inspection robots in industrial environments using the public Boston Dynamics Spot SDK.*

- [`07_robotics/README.md`](07_robotics/README.md) – Module overview
- [`mission_orchestrator.py`](07_robotics/mission_orchestrator.py) – Mission scheduling and execution loop
- [`spot_client.py`](07_robotics/spot_client.py) – Lightweight Spot SDK wrapper
- [`report_generator.py`](07_robotics/report_generator.py) – Post-mission Markdown + JSON reports
- [`inspection_config.yaml`](07_robotics/inspection_config.yaml) – Configurable checkpoint definitions

### 8. Agentic AI & Enterprise Tooling

*End-to-end agentic architectures for RAG, MCP servers, and multi-agent orchestration.*

- [`08_agentic_ai/README.md`](08_agentic_ai/README.md) – Module overview
- [`rag_agent/`](08_agentic_ai/rag_agent/) – LangGraph RAG agent with FAISS, tool integration, and structured output
- [`mcp_server/`](08_agentic_ai/mcp_server/) – MCP server template with tool registration and async client
- [`multi_agent/`](08_agentic_ai/multi_agent/) – Multi-agent orchestrator with audit logging and API key management

### 9. Digital Twin Architecture

*Privacy-first multi-database digital twin framework with encrypted vector search, knowledge graph analysis, and metadata lineage tracking.*

- [`09_digital_twin/README.md`](09_digital_twin/README.md) – Module overview
- [`storage/vector_db.py`](09_digital_twin/storage/vector_db.py) – ChromaDB wrapper with encryption-aware add/query
- [`storage/knowledge_graph.py`](09_digital_twin/storage/knowledge_graph.py) – NetworkX graph with centrality analysis and community detection
- [`storage/metadata_db.py`](09_digital_twin/storage/metadata_db.py) – SQLAlchemy ORM for data lineage and sync tracking
- [`storage/encryptor.py`](09_digital_twin/storage/encryptor.py) – Fernet (AES-256) encryption with sensitivity classifier
- [`config.py`](09_digital_twin/config.py) – Pydantic BaseSettings configuration management
- [`example.py`](09_digital_twin/example.py) – Five runnable examples demonstrating the full stack
- [`architecture.md`](09_digital_twin/architecture.md) – Detailed architecture documentation

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
streamlit run 04_nlp_tools/streamlit_cosine_tool.py
```

---

## Get in Touch

For collaboration, consulting, or just a great conversation about agentic AI systems, reach out:

- **LinkedIn**: [linkedin.com/in/matthan-bird-jd-mdb28173](https://www.linkedin.com/in/matthan-bird-jd-mdb28173)
- **Email**: [bird.matthan@gmail.com](mailto:bird.matthan@gmail.com)

---

> "The future belongs to those who design it."
> — Matthan Bird
