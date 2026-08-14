# Matthan Bird, JD — AI Portfolio

[![CI](https://github.com/XenoThanBird/Portfolio/actions/workflows/ci.yml/badge.svg)](https://github.com/XenoThanBird/Portfolio/actions/workflows/ci.yml)

AI strategy and solutions leader with end-to-end ownership of enterprise AI
transformation — opportunity discovery, business-case development, technical
architecture, production delivery, governance, and value realization.
Currently PMC Lead Data Scientist, Enterprise Solution Architect & Decision
Intelligence Consultant at Duke Energy; previously Lead Experimental AI
Scientist in Duke Energy's Emerging Technologies R&D lab, and before that led
Conversational AI at Spectrum (Charter Communications) at 18M+ monthly
interactions. J.D.; U.S. Navy submarine electronics & intelligence veteran.

The through-line of this portfolio is **governed AI**: systems that ship with
their audit trail, their evidence standards, and their human-accountability
structures built in — not bolted on. Both installable packages are CI-tested
with enforced coverage floors, the value-registry engine refuses to report a
figure without declared provenance, and every dataset here is synthetic.

---

## Capabilities

### Agent Governance — *the flagship*

[`packages/agent-governance-kit/`](packages/agent-governance-kit/) — an
installable, zero-dependency Python package of governance primitives for
agentic systems: a hash-chained tamper-evident audit log, redaction and
policy-as-code check stages, a three-outcome failure state machine whose
*startover* path is human-only and verified against a persisted approval
boundary, and a cross-process human-in-the-loop gate. 60 tests, mypy strict,
demo in under a second. [`agentic-ai/`](agentic-ai/) demonstrates the
architectures it governs — LangGraph RAG, MCP server, multi-agent
orchestration — and [`ai-governance/`](ai-governance/) holds the policy and
strategy documentation layer.

### Value Engineering & Decision Intelligence

[`packages/value-registry/`](packages/value-registry/) — an AI opportunity
value model and model-risk registry sharing one data model: the
evidence-classed figure. Every number declares how it was known
(`documented` / `estimated` / `modeled`) and with what confidence; the engine
refuses unclassified figures, aggregates inherit their weakest input's class,
and lifecycle gates can forbid scaling on modeled money.
[`ai-solution-lifecycle/`](ai-solution-lifecycle/) is the full-stack
expression: a FastAPI + Vue 3 platform for evaluating and managing AI
deployments — value scoring, risk registers, RACI, SLAs, and LLM-backed
document generation.

### Conversational & Speech AI

[`conversational-ai/`](conversational-ai/) — the full lifecycle of a
production voice channel: confidence-based IVR intent routing with LLM
fallback, enterprise prompt engineering with function-calling schemas, NLP
analytics dashboards, and an ASR optimization lab that batch-tests speech
recognition configurations against background-noise scenarios across Azure
Speech, Deepgram, and Speechmatics.

### Critical-Infrastructure Defense

[`infrastructure-defense/`](infrastructure-defense/) — defensive tooling
built around the constraints of regulated infrastructure environments:
file-integrity monitoring, network inventory and exposure auditing,
deception-based early warning, envelope encryption with key rotation, and
TLS compliance verification. Passive-first, cloud-free, auditable by default.

### Vision, Robotics & Autonomy

[`computer-vision/`](computer-vision/) — YOLOv8 + BLIP-2 monitoring with
time-series anomaly detection and multi-level alerting.
[`robotics/`](robotics/) — mission orchestration for Boston Dynamics Spot:
checkpoint-based inspection scheduling with post-mission reporting.

### Data Foundations

[`digital-twin/`](digital-twin/) — privacy-first multi-database architecture:
encrypted vector search, knowledge-graph analysis, and metadata lineage
tracking with sensitivity-classified encryption.

---

## Getting Started

```bash
git clone https://github.com/XenoThanBird/Portfolio.git && cd Portfolio
python -m venv .venv && source .venv/bin/activate   # .venv\Scripts\activate on Windows
pip install -r requirements.txt

# Fastest end-to-end demos (each < 60s):
pip install -e packages/agent-governance-kit && python packages/agent-governance-kit/examples/demo.py
pip install -e packages/value-registry && cd packages/value-registry && make demo
```

Each section's README carries its own file guide, runnable examples, and
module-specific requirements. Python 3.9+. The CI workflow runs a 3.9/3.11
matrix with compile checks, package test suites, lint, and secret scanning;
GitHub code scanning (CodeQL, repository default setup) runs alongside it.

## License & Contact

Licensed under [Apache-2.0](LICENSE) — use it, learn from it, build on it.
No real operational data, credentials, or employer-internal content appears
anywhere in this repository; every dataset is synthetic.

- **LinkedIn**: [linkedin.com/in/matthan-bird-jd-mdb28173](https://www.linkedin.com/in/matthan-bird-jd-mdb28173)
- **Email**: [bird.matthan@gmail.com](mailto:bird.matthan@gmail.com)

> "The future belongs to those who design it." — Matthan Bird
