# AI Solution Lifecycle Platform

End-to-end platform for evaluating, planning, and managing AI solution deployments — from initial value assessment through production monitoring.

By Matthan Bird with assistance from GitHub Copilot, Claude Anthropic, & Microsoft Copilot.

## Overview

This platform enables organizations to evaluate micro-SaaS AI solutions through a natural language interface with:

- **AI Document Generation** — Auto-generate BRDs, TRDs, functional specs, design schematics, and user schematics from natural language prompts using configurable LLM providers (OpenAI, Anthropic, or mock)
- **Prompt Library** — Create, version, test, and track reusable prompt templates with variable extraction, execution metrics, and a testing playground
- **Milestone Tracking** — Kanban-style project milestone management with dependencies and priority-based sorting
- **RACI Matrix** — Interactive Responsible/Accountable/Consulted/Informed matrix builder per project deliverable
- **SLA Monitoring** — Define, measure, and track SLA compliance with automated breach detection
- **Alert Engine** — Rule-based alerting for SLA breaches, milestone delays, risk escalations, and document deadlines with cooldown deduplication
- **Risk Register** — Probability × Impact risk scoring with 5×5 heat map matrix, classification, and mitigation tracking
- **Change Request Management** — Formal change request workflow (submitted → review → approved/rejected → implemented)
- **AI Model Catalog** — Registry of AI models with capabilities, costs, and LLM-powered use case recommendations
- **Value Assessment** — 6-dimension weighted scoring engine with readiness multiplier, ROI calculator (NPV, payback, risk-adjusted), and implementation roadmap generation

## Architecture

```
┌─────────────────────────────────────────────────────┐
│  Vue 3 + Tailwind SPA                               │
│  14 views · 30 components · Pinia state management  │
│  Axios API client · Vue Router with auth guards     │
├─────────────────────────────────────────────────────┤
│  FastAPI Backend                                     │
│  70 endpoints · 12 routers · 6 services             │
│  SQLAlchemy ORM · Pydantic v2 schemas               │
│  JWT auth · LLM strategy pattern                    │
├─────────────────────────────────────────────────────┤
│  PostgreSQL 16                                       │
│  15+ tables · UUID primary keys · Timestamp mixins  │
└─────────────────────────────────────────────────────┘
```

### LLM Provider Strategy

```
LLMProvider (Abstract)
├── OpenAIProvider    → gpt-4 / gpt-4o via openai SDK
├── AnthropicProvider → Claude via anthropic SDK
└── MockProvider      → Deterministic template responses (no API key needed)
```

Set `LLM_PROVIDER=mock` (default) for demo mode, or `openai`/`anthropic` with a valid API key.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Vue 3, Composition API, Tailwind CSS, Pinia, Vue Router, Chart.js |
| Backend | Python 3.11, FastAPI, SQLAlchemy 2.0, Pydantic v2 |
| Database | PostgreSQL 16 |
| LLM | OpenAI / Anthropic / Mock (pluggable) |
| Infrastructure | Docker, docker-compose, Nginx |

## Quick Start

### Docker (recommended)

```bash
# Clone and navigate
cd 12_ai_solution_lifecycle

# Copy environment config
cp .env.template .env

# Launch all services
docker-compose up --build

# Seed demo data (in another terminal)
docker-compose exec backend python -m app.seed_demo
```

- Frontend: http://localhost
- API docs: http://localhost:8000/docs
- Login: any `@demo.com` email with any password

### Local Development

```bash
# Backend
cd backend
pip install -r requirements.txt
cp ../.env.template .env
python -m app.seed_demo          # seed demo data
uvicorn app.main:app --reload    # API at :8000

# Frontend (in another terminal)
cd frontend
npm install
npm run dev                      # SPA at :5173
```

### CLI Demo (no server needed)

```bash
python example.py
```

## API Endpoints (70 routes)

| Module | Endpoints | Description |
|--------|-----------|-------------|
| Auth | 1 | Mock JWT login |
| Projects | 6 | CRUD + summary aggregation |
| Documents | 6 | CRUD + AI generation + versioning |
| Prompts | 8 | CRUD + search + run + feedback |
| Milestones | 6 | CRUD + dependencies + batch reorder |
| RACI | 4 | Matrix view + CRUD |
| SLA | 7 | Definitions + metrics + compliance + dashboard |
| Alerts | 8 | Rules + events + acknowledge + evaluate |
| Risks | 5 | CRUD + 5×5 matrix view |
| Change Requests | 3 | CRUD with status workflow |
| Model Catalog | 4 | CRUD + LLM recommendation |
| Value | 5 | Assessment + ROI + roadmap + use case prioritization |
| Dashboard | 2 | Global + per-project aggregation |
| Health | 1 | Status check |

## Data Model

15+ tables across 11 domain modules:

- **projects** / **project_members** — Core project tracking with team membership
- **documents** / **document_versions** — AI-generated docs with full version history
- **prompt_templates** / **prompt_runs** — Reusable prompts with execution metrics
- **milestones** / **milestone_dependencies** — Kanban tasks with dependency graph
- **raci_entries** — Deliverable × person responsibility matrix
- **sla_definitions** / **sla_metrics** — Service level tracking with compliance history
- **alert_rules** / **alert_events** — Configurable alerting with acknowledgment
- **risks** / **change_requests** — Risk register with formal change management
- **ai_models** / **use_case_mappings** — Model catalog with project recommendations
- **value_assessments** / **roi_calculations** — Scoring engine with financial analysis

## Demo Data

The seeder (`seed_demo.py`) creates 3 fictional projects:

1. **Acme Corp — Customer Service AI** (active) — Intent classification, RAG pipeline, sentiment analysis
2. **GreenTech — Predictive Maintenance** (active) — IoT sensors, anomaly detection, RUL prediction
3. **FinServ — Fraud Detection Platform** (planning) — Graph neural networks, real-time scoring, PCI compliance

Each project includes team members, documents, milestones with dependencies, RACI entries, SLAs with metrics, alert rules, risks, change requests, use case mappings, and value assessments with ROI calculations. The catalog includes 5 AI models and 5 prompt templates.

## Project Structure

```
12_ai_solution_lifecycle/
├── README.md
├── config.yaml                 # Scoring weights, risk matrix, SLA defaults
├── .env.template
├── example.py                  # CLI demo
├── docker-compose.yml
├── requirements.txt
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py             # FastAPI app entry
│       ├── config.py           # Pydantic BaseSettings
│       ├── database.py         # SQLAlchemy engine
│       ├── auth.py             # Mock JWT
│       ├── models/             # 11 SQLAlchemy model files
│       ├── schemas/            # 11 Pydantic schema files
│       ├── routers/            # 12 API routers
│       ├── services/           # 6 service modules
│       └── seed_demo.py        # Demo data seeder
└── frontend/
    ├── Dockerfile
    ├── package.json
    └── src/
        ├── api/                # 12 API modules
        ├── stores/             # 8 Pinia stores
        ├── router/             # Routes + auth guards
        ├── views/              # 14 page-level views
        └── components/         # 30 reusable components
            ├── layout/         # Sidebar, Topbar
            ├── dashboard/      # KPI, ProjectHealth, Alerts, ValueChart
            ├── documents/      # DocGenerator, DocViewer, DocVersions
            ├── prompts/        # PromptCard, PromptEditor, MetricCard
            ├── milestones/     # KanbanColumn, MilestoneCard
            ├── raci/           # RACIMatrix, RACICell
            ├── risk/           # RiskMatrix, RiskCard, ChangeRequestModal
            ├── value/          # ROICalculator, RadarChart, ReadinessGauge, RoadmapTimeline
            └── shared/         # Modal, DataTable, StatusBadge, ConfirmDialog, LoadingSpinner
```
