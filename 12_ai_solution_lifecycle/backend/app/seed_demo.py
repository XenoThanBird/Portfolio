"""
Seed the database with 3 fictional company projects and full cross-linked data.

Usage:
    cd backend
    python -m app.seed_demo
"""

import uuid
from datetime import datetime, timedelta, timezone

from app.database import SessionLocal, engine
from app.models import (
    AIModel,
    AlertEvent,
    AlertRule,
    Base,
    ChangeRequest,
    Document,
    Milestone,
    MilestoneDependency,
    ProjectMember,
    Project,
    PromptRun,
    PromptTemplate,
    RACIEntry,
    Risk,
    ROICalculation,
    SLADefinition,
    SLAMetric,
    UseCaseMapping,
    ValueAssessment,
)

now = datetime.now(timezone.utc)


def uid() -> str:
    return str(uuid.uuid4())


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Check if already seeded
        if db.query(Project).first():
            print("Database already seeded. Skipping.")
            return

        # ── AI Model Catalog (shared across projects) ──────────────────
        models = [
            AIModel(
                id=uid(), name="GPT-4o", provider="OpenAI", model_type="llm",
                description="Multimodal flagship model with vision and code capabilities.",
                capabilities=["text-generation", "code-generation", "vision", "function-calling"],
                cost_per_1k_tokens=0.005, max_context_length=128000,
                recommended_use_cases="Document generation, complex reasoning, code review",
                strengths="Broad knowledge, strong reasoning, multimodal",
                limitations="Higher cost, potential latency on long prompts",
            ),
            AIModel(
                id=uid(), name="Claude 3.5 Sonnet", provider="Anthropic", model_type="llm",
                description="High-capability model balancing performance with speed.",
                capabilities=["text-generation", "code-generation", "analysis", "structured-output"],
                cost_per_1k_tokens=0.003, max_context_length=200000,
                recommended_use_cases="Technical documentation, analysis, summarization",
                strengths="Large context window, nuanced analysis, safety",
                limitations="No native vision in older versions",
            ),
            AIModel(
                id=uid(), name="Llama 3.1 70B", provider="Meta", model_type="llm",
                description="Open-source large language model for on-premise deployment.",
                capabilities=["text-generation", "code-generation", "multilingual"],
                cost_per_1k_tokens=0.0, max_context_length=128000,
                recommended_use_cases="On-premise deployments, cost-sensitive applications",
                strengths="Open source, no API costs, customizable",
                limitations="Requires GPU infrastructure, no hosted API",
            ),
            AIModel(
                id=uid(), name="text-embedding-3-large", provider="OpenAI", model_type="embedding",
                description="High-dimensional text embedding model for semantic search.",
                capabilities=["embeddings", "semantic-search", "clustering"],
                cost_per_1k_tokens=0.00013, max_context_length=8191,
                recommended_use_cases="RAG pipelines, document similarity, search",
                strengths="High accuracy, dimension reduction support",
                limitations="Text only, no generation capability",
            ),
            AIModel(
                id=uid(), name="Whisper Large v3", provider="OpenAI", model_type="speech",
                description="Speech recognition model for audio transcription.",
                capabilities=["speech-to-text", "translation", "language-detection"],
                cost_per_1k_tokens=0.006, max_context_length=0,
                recommended_use_cases="Meeting transcription, voice interfaces, accessibility",
                strengths="Multilingual, robust to noise",
                limitations="Audio only, batch processing recommended",
            ),
        ]
        db.add_all(models)
        db.flush()

        # ── Project 1: Acme Corp — Customer Service AI ─────────────────
        p1_id = uid()
        p1 = Project(
            id=p1_id, name="Acme Corp — Customer Service AI",
            description="AI-powered customer support platform with intelligent routing, "
                        "sentiment analysis, and automated response generation.",
            status="active", owner_email="sarah.chen@demo.com",
            start_date=now - timedelta(days=45),
            target_end_date=now + timedelta(days=135),
            budget_millions=2.5, data_maturity_level=3,
        )
        db.add(p1)

        p1_members = [
            ProjectMember(id=uid(), project_id=p1_id, name="Sarah Chen", email="sarah.chen@demo.com", role="Project Lead", department="Engineering"),
            ProjectMember(id=uid(), project_id=p1_id, name="Marcus Rivera", email="marcus.rivera@demo.com", role="Data Scientist", department="AI/ML"),
            ProjectMember(id=uid(), project_id=p1_id, name="Priya Patel", email="priya.patel@demo.com", role="Product Owner", department="Product"),
            ProjectMember(id=uid(), project_id=p1_id, name="James Okafor", email="james.okafor@demo.com", role="Backend Engineer", department="Engineering"),
        ]
        db.add_all(p1_members)

        # Documents
        p1_docs = [
            Document(
                id=uid(), project_id=p1_id, doc_type="brd", title="Customer Service AI — Business Requirements",
                content="# Business Requirements Document\n\n## Executive Summary\nAcme Corp seeks to deploy an AI-powered customer service platform to reduce average handle time by 40% and improve CSAT scores by 15 points.\n\n## Business Objectives\n1. Reduce customer wait times from 8 minutes to under 2 minutes\n2. Automate 60% of Tier 1 support inquiries\n3. Improve first-contact resolution rate to 85%\n\n## Scope\n- Intelligent ticket routing based on intent classification\n- Automated response generation for common queries\n- Real-time sentiment analysis with escalation triggers\n- Agent assist with suggested responses and knowledge retrieval\n\n## Success Criteria\n- AHT reduction ≥ 40% within 6 months of deployment\n- CSAT improvement ≥ 15 points\n- Cost savings ≥ $1.2M annually",
                version=1, status="approved", generated_by_prompt=True, llm_model_used="gpt-4o",
            ),
            Document(
                id=uid(), project_id=p1_id, doc_type="trd", title="Customer Service AI — Technical Requirements",
                content="# Technical Requirements Document\n\n## Architecture Overview\nMicroservices architecture with event-driven communication.\n\n## Core Components\n1. **Intent Classifier** — Fine-tuned transformer model for 50+ intent categories\n2. **Response Generator** — RAG pipeline with company knowledge base\n3. **Sentiment Analyzer** — Real-time emotion detection with escalation logic\n4. **Routing Engine** — Skills-based routing with load balancing\n\n## Infrastructure\n- Kubernetes cluster (3 nodes minimum)\n- PostgreSQL for transactional data\n- Redis for caching and session state\n- Vector database (Pinecone) for knowledge embeddings\n\n## Performance Requirements\n- Response latency < 500ms (p95)\n- System uptime ≥ 99.9%\n- Concurrent users: 500+",
                version=1, status="approved", generated_by_prompt=True, llm_model_used="gpt-4o",
            ),
        ]
        db.add_all(p1_docs)

        # Milestones
        p1_m1_id, p1_m2_id, p1_m3_id, p1_m4_id = uid(), uid(), uid(), uid()
        p1_milestones = [
            Milestone(id=p1_m1_id, project_id=p1_id, title="Requirements & Design", status="done", priority="high", owner_email="priya.patel@demo.com", due_date=now - timedelta(days=15), sort_order=1),
            Milestone(id=p1_m2_id, project_id=p1_id, title="Intent Classifier Training", status="in_progress", priority="high", owner_email="marcus.rivera@demo.com", due_date=now + timedelta(days=20), sort_order=2),
            Milestone(id=p1_m3_id, project_id=p1_id, title="RAG Pipeline Integration", status="backlog", priority="medium", owner_email="james.okafor@demo.com", due_date=now + timedelta(days=60), sort_order=3),
            Milestone(id=p1_m4_id, project_id=p1_id, title="Production Deployment & Monitoring", status="backlog", priority="high", owner_email="sarah.chen@demo.com", due_date=now + timedelta(days=120), sort_order=4),
        ]
        db.add_all(p1_milestones)
        db.flush()

        db.add_all([
            MilestoneDependency(id=uid(), milestone_id=p1_m2_id, depends_on_id=p1_m1_id, dependency_type="requires"),
            MilestoneDependency(id=uid(), milestone_id=p1_m3_id, depends_on_id=p1_m2_id, dependency_type="blocks"),
            MilestoneDependency(id=uid(), milestone_id=p1_m4_id, depends_on_id=p1_m3_id, dependency_type="requires"),
        ])

        # RACI
        p1_raci = [
            RACIEntry(id=uid(), project_id=p1_id, deliverable="Requirements Document", milestone_id=p1_m1_id, person_name="Priya Patel", person_email="priya.patel@demo.com", role_type="R"),
            RACIEntry(id=uid(), project_id=p1_id, deliverable="Requirements Document", milestone_id=p1_m1_id, person_name="Sarah Chen", person_email="sarah.chen@demo.com", role_type="A"),
            RACIEntry(id=uid(), project_id=p1_id, deliverable="Intent Classifier", milestone_id=p1_m2_id, person_name="Marcus Rivera", person_email="marcus.rivera@demo.com", role_type="R"),
            RACIEntry(id=uid(), project_id=p1_id, deliverable="Intent Classifier", milestone_id=p1_m2_id, person_name="Sarah Chen", person_email="sarah.chen@demo.com", role_type="A"),
            RACIEntry(id=uid(), project_id=p1_id, deliverable="RAG Pipeline", milestone_id=p1_m3_id, person_name="James Okafor", person_email="james.okafor@demo.com", role_type="R"),
            RACIEntry(id=uid(), project_id=p1_id, deliverable="RAG Pipeline", milestone_id=p1_m3_id, person_name="Marcus Rivera", person_email="marcus.rivera@demo.com", role_type="C"),
        ]
        db.add_all(p1_raci)

        # SLAs
        p1_sla1_id, p1_sla2_id = uid(), uid()
        p1_slas = [
            SLADefinition(id=p1_sla1_id, project_id=p1_id, name="API Response Time", metric_type="response_time", target_value=500, target_unit="ms", warning_threshold=400, breach_threshold=500, measurement_window="1h"),
            SLADefinition(id=p1_sla2_id, project_id=p1_id, name="System Uptime", metric_type="uptime", target_value=99.9, target_unit="percent", warning_threshold=99.5, breach_threshold=99.0, measurement_window="24h"),
        ]
        db.add_all(p1_slas)
        db.flush()

        p1_sla_metrics = [
            SLAMetric(id=uid(), sla_id=p1_sla1_id, measured_value=320, is_compliant=True, measured_at=now - timedelta(hours=6)),
            SLAMetric(id=uid(), sla_id=p1_sla1_id, measured_value=445, is_compliant=True, measured_at=now - timedelta(hours=3)),
            SLAMetric(id=uid(), sla_id=p1_sla1_id, measured_value=510, is_compliant=False, measured_at=now - timedelta(hours=1)),
            SLAMetric(id=uid(), sla_id=p1_sla2_id, measured_value=99.95, is_compliant=True, measured_at=now - timedelta(hours=12)),
            SLAMetric(id=uid(), sla_id=p1_sla2_id, measured_value=99.92, is_compliant=True, measured_at=now - timedelta(hours=1)),
        ]
        db.add_all(p1_sla_metrics)

        # Alert Rules & Events
        p1_rule1_id = uid()
        p1_alerts = [
            AlertRule(
                id=p1_rule1_id, project_id=p1_id, alert_type="sla_breach", severity="critical",
                condition_config={"metric_type": "response_time", "threshold": 500},
                is_active=True, notify_emails=["sarah.chen@demo.com"], cooldown_minutes=30,
            ),
            AlertRule(
                id=uid(), project_id=p1_id, alert_type="milestone_delay", severity="warning",
                condition_config={"days_overdue": 3},
                is_active=True, notify_emails=["sarah.chen@demo.com", "priya.patel@demo.com"], cooldown_minutes=60,
            ),
        ]
        db.add_all(p1_alerts)
        db.flush()

        db.add(AlertEvent(
            id=uid(), rule_id=p1_rule1_id, project_id=p1_id,
            title="SLA Breach: API Response Time", severity="critical",
            message="API response time measured at 510ms, exceeding 500ms SLA target.",
            acknowledged=False, triggered_at=now - timedelta(hours=1),
        ))

        # Risks
        p1_risks = [
            Risk(
                id=uid(), project_id=p1_id, title="Training data quality insufficient",
                description="Historical support tickets may contain inconsistent labeling.",
                category="technical", probability="likely", impact="major",
                risk_score=32, classification="high",
                mitigation_plan="Implement data cleaning pipeline; manual review of 10% sample.",
                owner_email="marcus.rivera@demo.com", status="open",
            ),
            Risk(
                id=uid(), project_id=p1_id, title="API rate limiting from LLM provider",
                description="Production traffic may exceed provider rate limits during peak hours.",
                category="operational", probability="possible", impact="moderate",
                risk_score=18, classification="medium",
                mitigation_plan="Implement request queuing and caching layer; negotiate enterprise tier.",
                owner_email="james.okafor@demo.com", status="mitigated",
            ),
        ]
        db.add_all(p1_risks)

        db.add(ChangeRequest(
            id=uid(), project_id=p1_id, title="Add multilingual support to intent classifier",
            description="Expand intent classification to support Spanish and French.",
            justification="25% of customer base is non-English speaking.",
            impact_assessment="Adds 3-4 weeks to classifier training milestone. Requires additional training data.",
            status="under_review", priority="medium", requested_by="priya.patel@demo.com",
        ))

        # Use Case Mappings
        db.add(UseCaseMapping(
            id=uid(), project_id=p1_id,
            use_case_description="Automated customer support response generation",
            recommended_model_id=models[0].id, confidence_score=0.92,
            rationale="GPT-4o excels at natural language generation with nuanced tone control.",
        ))

        # Value Assessment
        p1_va_id = uid()
        db.add(ValueAssessment(
            id=p1_va_id, project_id=p1_id,
            financial_impact=82, operational_excellence=75, strategic_value=70,
            risk_mitigation=60, customer_impact=90, innovation_index=65,
            data_maturity=0.7, organizational_readiness=0.65, technical_capability=0.8,
            base_score=75.5, readiness_multiplier=0.72, final_score=54.4,
            classification="Strategic", recommended_action="Proceed with phased implementation",
            investment_range="$1M - $5M",
        ))
        db.flush()

        db.add(ROICalculation(
            id=uid(), assessment_id=p1_va_id,
            total_benefits=4.2, total_costs=2.5, time_horizon_years=3,
            discount_rate=0.08, roi_percent=68.0, npv_millions=1.42,
            payback_years=1.8, risk_adjusted_roi=48.96,
        ))

        # ── Project 2: GreenTech — Predictive Maintenance ──────────────
        p2_id = uid()
        p2 = Project(
            id=p2_id, name="GreenTech — Predictive Maintenance",
            description="IoT sensor-driven predictive maintenance system for wind turbine "
                        "fleet using anomaly detection and remaining useful life prediction.",
            status="active", owner_email="alex.wong@demo.com",
            start_date=now - timedelta(days=90),
            target_end_date=now + timedelta(days=90),
            budget_millions=5.0, data_maturity_level=4,
        )
        db.add(p2)

        p2_members = [
            ProjectMember(id=uid(), project_id=p2_id, name="Alex Wong", email="alex.wong@demo.com", role="Program Manager", department="Operations"),
            ProjectMember(id=uid(), project_id=p2_id, name="Elena Kowalski", email="elena.kowalski@demo.com", role="ML Engineer", department="AI/ML"),
            ProjectMember(id=uid(), project_id=p2_id, name="David Nakamura", email="david.nakamura@demo.com", role="IoT Architect", department="Engineering"),
            ProjectMember(id=uid(), project_id=p2_id, name="Fatima Al-Hassan", email="fatima.alhassan@demo.com", role="Data Engineer", department="Data Platform"),
        ]
        db.add_all(p2_members)

        p2_docs = [
            Document(
                id=uid(), project_id=p2_id, doc_type="brd", title="Predictive Maintenance — Business Requirements",
                content="# Business Requirements Document\n\n## Executive Summary\nGreenTech operates 200+ wind turbines across 12 sites. Unplanned downtime costs $15K/day per turbine. This project deploys predictive maintenance AI to reduce unplanned downtime by 60%.\n\n## Business Objectives\n1. Reduce unplanned downtime by 60%\n2. Extend component lifespan by 20% through optimized maintenance scheduling\n3. Reduce maintenance costs by $3.5M annually\n\n## Scope\n- Real-time anomaly detection on vibration, temperature, and power output sensors\n- Remaining Useful Life (RUL) prediction for critical components\n- Automated work order generation\n- Dashboard for fleet-wide health monitoring",
                version=1, status="approved", generated_by_prompt=True, llm_model_used="claude-3.5-sonnet",
            ),
            Document(
                id=uid(), project_id=p2_id, doc_type="trd", title="Predictive Maintenance — Technical Requirements",
                content="# Technical Requirements Document\n\n## Architecture\nEdge-cloud hybrid architecture for real-time sensor processing.\n\n## Components\n1. **Edge Gateway** — Raspberry Pi clusters at each site for initial signal processing\n2. **Streaming Pipeline** — Apache Kafka for sensor event ingestion (50K events/sec)\n3. **Anomaly Detector** — Isolation Forest + LSTM autoencoder ensemble\n4. **RUL Predictor** — Physics-informed neural network\n5. **Alert Service** — Priority-based notification with escalation\n\n## Data Requirements\n- 2 years historical sensor data (available)\n- 100+ labeled failure events for supervised training\n- Real-time ingestion at 1Hz per sensor (200 turbines × 12 sensors)",
                version=1, status="approved", generated_by_prompt=True, llm_model_used="claude-3.5-sonnet",
            ),
            Document(
                id=uid(), project_id=p2_id, doc_type="design_schematic", title="Edge-Cloud Data Flow",
                content="# Design Schematic: Edge-Cloud Data Flow\n\n## Data Flow\n```\nSensors → Edge Gateway → Kafka → Stream Processor → Feature Store\n                                                    ↓\n                                              Anomaly Detector → Alert Service\n                                                    ↓\n                                              RUL Predictor → Work Order System\n```\n\n## Edge Processing\n- Signal denoising (Butterworth filter)\n- Feature extraction (FFT, RMS, kurtosis)\n- Local anomaly pre-screening (reduces cloud traffic by 80%)",
                version=1, status="draft", generated_by_prompt=True, llm_model_used="claude-3.5-sonnet",
            ),
        ]
        db.add_all(p2_docs)

        # Milestones
        p2_m1_id, p2_m2_id, p2_m3_id, p2_m4_id, p2_m5_id = uid(), uid(), uid(), uid(), uid()
        p2_milestones = [
            Milestone(id=p2_m1_id, project_id=p2_id, title="Data Pipeline Setup", status="done", priority="high", owner_email="fatima.alhassan@demo.com", due_date=now - timedelta(days=60), sort_order=1),
            Milestone(id=p2_m2_id, project_id=p2_id, title="Anomaly Detection Model Training", status="done", priority="high", owner_email="elena.kowalski@demo.com", due_date=now - timedelta(days=30), sort_order=2),
            Milestone(id=p2_m3_id, project_id=p2_id, title="RUL Model Development", status="in_progress", priority="high", owner_email="elena.kowalski@demo.com", due_date=now + timedelta(days=15), sort_order=3),
            Milestone(id=p2_m4_id, project_id=p2_id, title="Edge Deployment", status="backlog", priority="medium", owner_email="david.nakamura@demo.com", due_date=now + timedelta(days=45), sort_order=4),
            Milestone(id=p2_m5_id, project_id=p2_id, title="Fleet Rollout & Monitoring", status="backlog", priority="high", owner_email="alex.wong@demo.com", due_date=now + timedelta(days=85), sort_order=5),
        ]
        db.add_all(p2_milestones)
        db.flush()

        db.add_all([
            MilestoneDependency(id=uid(), milestone_id=p2_m2_id, depends_on_id=p2_m1_id, dependency_type="requires"),
            MilestoneDependency(id=uid(), milestone_id=p2_m3_id, depends_on_id=p2_m2_id, dependency_type="requires"),
            MilestoneDependency(id=uid(), milestone_id=p2_m4_id, depends_on_id=p2_m3_id, dependency_type="blocks"),
            MilestoneDependency(id=uid(), milestone_id=p2_m5_id, depends_on_id=p2_m4_id, dependency_type="requires"),
        ])

        # RACI
        p2_raci = [
            RACIEntry(id=uid(), project_id=p2_id, deliverable="Data Pipeline", milestone_id=p2_m1_id, person_name="Fatima Al-Hassan", person_email="fatima.alhassan@demo.com", role_type="R"),
            RACIEntry(id=uid(), project_id=p2_id, deliverable="Data Pipeline", milestone_id=p2_m1_id, person_name="Alex Wong", person_email="alex.wong@demo.com", role_type="A"),
            RACIEntry(id=uid(), project_id=p2_id, deliverable="Anomaly Detection Model", milestone_id=p2_m2_id, person_name="Elena Kowalski", person_email="elena.kowalski@demo.com", role_type="R"),
            RACIEntry(id=uid(), project_id=p2_id, deliverable="Anomaly Detection Model", milestone_id=p2_m2_id, person_name="David Nakamura", person_email="david.nakamura@demo.com", role_type="C"),
            RACIEntry(id=uid(), project_id=p2_id, deliverable="Edge Deployment", milestone_id=p2_m4_id, person_name="David Nakamura", person_email="david.nakamura@demo.com", role_type="R"),
            RACIEntry(id=uid(), project_id=p2_id, deliverable="Edge Deployment", milestone_id=p2_m4_id, person_name="Alex Wong", person_email="alex.wong@demo.com", role_type="A"),
        ]
        db.add_all(p2_raci)

        # SLAs
        p2_sla1_id, p2_sla2_id = uid(), uid()
        p2_slas = [
            SLADefinition(id=p2_sla1_id, project_id=p2_id, name="Anomaly Detection Latency", metric_type="response_time", target_value=200, target_unit="ms", warning_threshold=150, breach_threshold=200, measurement_window="1h"),
            SLADefinition(id=p2_sla2_id, project_id=p2_id, name="Data Pipeline Throughput", metric_type="throughput", target_value=50000, target_unit="events/sec", warning_threshold=45000, breach_threshold=40000, measurement_window="1h"),
        ]
        db.add_all(p2_slas)
        db.flush()

        p2_sla_metrics = [
            SLAMetric(id=uid(), sla_id=p2_sla1_id, measured_value=145, is_compliant=True, measured_at=now - timedelta(hours=4)),
            SLAMetric(id=uid(), sla_id=p2_sla1_id, measured_value=160, is_compliant=True, measured_at=now - timedelta(hours=1)),
            SLAMetric(id=uid(), sla_id=p2_sla2_id, measured_value=52000, is_compliant=True, measured_at=now - timedelta(hours=4)),
            SLAMetric(id=uid(), sla_id=p2_sla2_id, measured_value=48000, is_compliant=True, measured_at=now - timedelta(hours=1)),
        ]
        db.add_all(p2_sla_metrics)

        # Alert Rules
        p2_rule1_id = uid()
        p2_alerts = [
            AlertRule(
                id=p2_rule1_id, project_id=p2_id, alert_type="risk_escalation", severity="critical",
                condition_config={"risk_score_threshold": 30},
                is_active=True, notify_emails=["alex.wong@demo.com"], cooldown_minutes=60,
            ),
            AlertRule(
                id=uid(), project_id=p2_id, alert_type="sla_breach", severity="warning",
                condition_config={"metric_type": "throughput", "threshold": 40000},
                is_active=True, notify_emails=["fatima.alhassan@demo.com"], cooldown_minutes=30,
            ),
        ]
        db.add_all(p2_alerts)

        # Risks
        p2_risks = [
            Risk(
                id=uid(), project_id=p2_id, title="Sensor data gaps during extreme weather",
                description="Severe storms can cause sensor communication dropouts.",
                category="operational", probability="likely", impact="moderate",
                risk_score=24, classification="high",
                mitigation_plan="Edge buffering with store-and-forward; interpolation for gaps < 5min.",
                owner_email="david.nakamura@demo.com", status="open",
            ),
            Risk(
                id=uid(), project_id=p2_id, title="Model drift due to aging turbine fleet",
                description="As turbines age, baseline vibration patterns shift, degrading model accuracy.",
                category="technical", probability="almost_certain", impact="moderate",
                risk_score=30, classification="high",
                mitigation_plan="Implement continuous learning pipeline with quarterly retraining.",
                owner_email="elena.kowalski@demo.com", status="open",
            ),
            Risk(
                id=uid(), project_id=p2_id, title="Edge compute hardware failures",
                description="Raspberry Pi clusters at remote sites may fail due to environmental conditions.",
                category="technical", probability="possible", impact="minor",
                risk_score=9, classification="low",
                mitigation_plan="Deploy redundant edge nodes; remote monitoring and auto-failover.",
                owner_email="david.nakamura@demo.com", status="mitigated",
            ),
        ]
        db.add_all(p2_risks)

        # Use Case Mappings
        db.add_all([
            UseCaseMapping(
                id=uid(), project_id=p2_id,
                use_case_description="Time-series anomaly detection for sensor data",
                recommended_model_id=models[2].id, confidence_score=0.85,
                rationale="On-premise Llama deployment enables real-time inference without cloud dependency.",
            ),
            UseCaseMapping(
                id=uid(), project_id=p2_id,
                use_case_description="Technical documentation generation for maintenance procedures",
                recommended_model_id=models[1].id, confidence_score=0.88,
                rationale="Claude excels at structured technical writing with long context support.",
            ),
        ])

        # Value Assessment
        p2_va_id = uid()
        db.add(ValueAssessment(
            id=p2_va_id, project_id=p2_id,
            financial_impact=90, operational_excellence=95, strategic_value=75,
            risk_mitigation=85, customer_impact=50, innovation_index=70,
            data_maturity=0.85, organizational_readiness=0.7, technical_capability=0.9,
            base_score=82.0, readiness_multiplier=0.82, final_score=67.2,
            classification="Transformational", recommended_action="Fast-track with full investment",
            investment_range="$5M - $10M",
        ))
        db.flush()

        db.add(ROICalculation(
            id=uid(), assessment_id=p2_va_id,
            total_benefits=8.5, total_costs=5.0, time_horizon_years=5,
            discount_rate=0.10, roi_percent=70.0, npv_millions=2.85,
            payback_years=2.1, risk_adjusted_roi=52.5,
        ))

        # ── Project 3: FinServ — Fraud Detection ───────────────────────
        p3_id = uid()
        p3 = Project(
            id=p3_id, name="FinServ — Fraud Detection Platform",
            description="Real-time transaction fraud detection system using graph neural networks "
                        "and behavioral analytics for a digital banking platform.",
            status="planning", owner_email="maria.garcia@demo.com",
            start_date=now - timedelta(days=10),
            target_end_date=now + timedelta(days=200),
            budget_millions=8.0, data_maturity_level=2,
        )
        db.add(p3)

        p3_members = [
            ProjectMember(id=uid(), project_id=p3_id, name="Maria Garcia", email="maria.garcia@demo.com", role="VP of AI", department="Technology"),
            ProjectMember(id=uid(), project_id=p3_id, name="Robert Kim", email="robert.kim@demo.com", role="Security Architect", department="Security"),
            ProjectMember(id=uid(), project_id=p3_id, name="Aisha Patel", email="aisha.patel@demo.com", role="ML Engineer", department="AI/ML"),
            ProjectMember(id=uid(), project_id=p3_id, name="Thomas Anderson", email="thomas.anderson@demo.com", role="Compliance Officer", department="Legal"),
        ]
        db.add_all(p3_members)

        p3_docs = [
            Document(
                id=uid(), project_id=p3_id, doc_type="brd", title="Fraud Detection — Business Requirements",
                content="# Business Requirements Document\n\n## Executive Summary\nFinServ processes 2M+ transactions daily. Current rule-based fraud detection catches only 65% of fraudulent transactions with a 3% false positive rate. This project will deploy ML-based fraud detection to achieve 95% detection with < 0.5% false positives.\n\n## Business Objectives\n1. Increase fraud detection rate from 65% to 95%\n2. Reduce false positive rate from 3% to < 0.5%\n3. Enable real-time decisioning (< 100ms per transaction)\n4. Reduce fraud losses by $12M annually\n\n## Regulatory Requirements\n- PCI DSS compliance for cardholder data\n- SOX audit trail for all model decisions\n- Explainable AI requirements for customer-facing decline reasons",
                version=1, status="draft", generated_by_prompt=True, llm_model_used="gpt-4o",
            ),
        ]
        db.add_all(p3_docs)

        # Milestones
        p3_m1_id, p3_m2_id, p3_m3_id = uid(), uid(), uid()
        p3_milestones = [
            Milestone(id=p3_m1_id, project_id=p3_id, title="Regulatory Assessment & Data Audit", status="in_progress", priority="critical", owner_email="thomas.anderson@demo.com", due_date=now + timedelta(days=20), sort_order=1),
            Milestone(id=p3_m2_id, project_id=p3_id, title="Feature Engineering & Model Selection", status="backlog", priority="high", owner_email="aisha.patel@demo.com", due_date=now + timedelta(days=60), sort_order=2),
            Milestone(id=p3_m3_id, project_id=p3_id, title="Security Architecture Review", status="backlog", priority="critical", owner_email="robert.kim@demo.com", due_date=now + timedelta(days=45), sort_order=3),
        ]
        db.add_all(p3_milestones)
        db.flush()

        db.add(MilestoneDependency(id=uid(), milestone_id=p3_m2_id, depends_on_id=p3_m1_id, dependency_type="requires"))

        # RACI
        p3_raci = [
            RACIEntry(id=uid(), project_id=p3_id, deliverable="Regulatory Assessment", milestone_id=p3_m1_id, person_name="Thomas Anderson", person_email="thomas.anderson@demo.com", role_type="R"),
            RACIEntry(id=uid(), project_id=p3_id, deliverable="Regulatory Assessment", milestone_id=p3_m1_id, person_name="Maria Garcia", person_email="maria.garcia@demo.com", role_type="A"),
            RACIEntry(id=uid(), project_id=p3_id, deliverable="Regulatory Assessment", milestone_id=p3_m1_id, person_name="Robert Kim", person_email="robert.kim@demo.com", role_type="C"),
            RACIEntry(id=uid(), project_id=p3_id, deliverable="Security Architecture", milestone_id=p3_m3_id, person_name="Robert Kim", person_email="robert.kim@demo.com", role_type="R"),
            RACIEntry(id=uid(), project_id=p3_id, deliverable="Security Architecture", milestone_id=p3_m3_id, person_name="Maria Garcia", person_email="maria.garcia@demo.com", role_type="A"),
        ]
        db.add_all(p3_raci)

        # SLAs
        p3_sla1_id = uid()
        db.add(SLADefinition(
            id=p3_sla1_id, project_id=p3_id, name="Transaction Decisioning Latency",
            metric_type="response_time", target_value=100, target_unit="ms",
            warning_threshold=80, breach_threshold=100, measurement_window="5m",
        ))
        db.flush()

        db.add(SLAMetric(id=uid(), sla_id=p3_sla1_id, measured_value=85, is_compliant=True, measured_at=now - timedelta(hours=2)))

        # Alert Rules
        db.add(AlertRule(
            id=uid(), project_id=p3_id, alert_type="doc_review_deadline", severity="warning",
            condition_config={"days_until_due": 7, "doc_status": "draft"},
            is_active=True, notify_emails=["maria.garcia@demo.com"], cooldown_minutes=120,
        ))

        # Risks
        p3_risks = [
            Risk(
                id=uid(), project_id=p3_id, title="PCI DSS compliance gaps",
                description="Current data infrastructure may not meet PCI DSS requirements for cardholder data.",
                category="compliance", probability="likely", impact="catastrophic",
                risk_score=48, classification="critical",
                mitigation_plan="Engage external PCI QSA for gap assessment; establish dedicated secure enclave.",
                owner_email="robert.kim@demo.com", status="open",
            ),
            Risk(
                id=uid(), project_id=p3_id, title="Insufficient labeled fraud data",
                description="Only 8 months of labeled transactions available; class imbalance ratio 1:1000.",
                category="technical", probability="almost_certain", impact="major",
                risk_score=40, classification="critical",
                mitigation_plan="Use SMOTE oversampling; acquire synthetic fraud data; implement active learning.",
                owner_email="aisha.patel@demo.com", status="open",
            ),
            Risk(
                id=uid(), project_id=p3_id, title="Model explainability for regulatory compliance",
                description="Graph neural networks are inherently opaque; regulators require explainable decisions.",
                category="compliance", probability="possible", impact="major",
                risk_score=24, classification="high",
                mitigation_plan="Implement SHAP-based explanations; hybrid approach with interpretable features.",
                owner_email="aisha.patel@demo.com", status="open",
            ),
        ]
        db.add_all(p3_risks)

        db.add(ChangeRequest(
            id=uid(), project_id=p3_id, title="Include account takeover detection in scope",
            description="Extend fraud detection scope beyond transaction fraud to include account takeover attempts.",
            justification="Account takeover losses increased 200% YoY; regulators flagged as emerging risk.",
            impact_assessment="Adds 6-8 weeks to timeline. Requires session behavior data integration.",
            status="submitted", priority="high", requested_by="robert.kim@demo.com",
        ))

        # Use Case Mappings
        db.add(UseCaseMapping(
            id=uid(), project_id=p3_id,
            use_case_description="Real-time transaction fraud scoring and explanation",
            recommended_model_id=models[2].id, confidence_score=0.78,
            rationale="On-premise Llama deployment satisfies data residency requirements for financial data.",
        ))

        # Value Assessment
        p3_va_id = uid()
        db.add(ValueAssessment(
            id=p3_va_id, project_id=p3_id,
            financial_impact=95, operational_excellence=60, strategic_value=85,
            risk_mitigation=90, customer_impact=70, innovation_index=80,
            data_maturity=0.45, organizational_readiness=0.5, technical_capability=0.6,
            base_score=83.5, readiness_multiplier=0.52, final_score=43.4,
            classification="High Potential", recommended_action="Invest in data maturity before full deployment",
            investment_range="$5M - $10M",
        ))
        db.flush()

        db.add(ROICalculation(
            id=uid(), assessment_id=p3_va_id,
            total_benefits=15.0, total_costs=8.0, time_horizon_years=4,
            discount_rate=0.12, roi_percent=87.5, npv_millions=4.2,
            payback_years=2.5, risk_adjusted_roi=45.5,
        ))

        # ── Global Prompt Templates (shared across projects) ───────────
        prompts = [
            PromptTemplate(
                id=uid(), project_id=None, name="BRD Generator",
                template="Generate a comprehensive Business Requirements Document for the following project:\n\nProject: {{project_name}}\nIndustry: {{industry}}\nKey Objectives: {{objectives}}\nBudget Range: {{budget}}\nTimeline: {{timeline}}",
                variables=["project_name", "industry", "objectives", "budget", "timeline"],
                category="document_generation", tags=["brd", "requirements", "business"],
                version=1, is_active=True, usage_count=24, avg_latency_ms=3200, success_rate=0.96,
            ),
            PromptTemplate(
                id=uid(), project_id=None, name="TRD Generator",
                template="Generate a Technical Requirements Document for:\n\nProject: {{project_name}}\nArchitecture Style: {{architecture}}\nTech Stack: {{tech_stack}}\nScale Requirements: {{scale}}\nSecurity Requirements: {{security}}",
                variables=["project_name", "architecture", "tech_stack", "scale", "security"],
                category="document_generation", tags=["trd", "technical", "architecture"],
                version=1, is_active=True, usage_count=18, avg_latency_ms=4100, success_rate=0.94,
            ),
            PromptTemplate(
                id=uid(), project_id=None, name="Risk Assessment Prompt",
                template="Analyze the following project context and identify the top {{num_risks}} risks:\n\nProject: {{project_name}}\nDomain: {{domain}}\nCurrent Phase: {{phase}}\nKnown Constraints: {{constraints}}",
                variables=["num_risks", "project_name", "domain", "phase", "constraints"],
                category="analysis", tags=["risk", "assessment", "analysis"],
                version=2, is_active=True, usage_count=12, avg_latency_ms=2800, success_rate=0.92,
            ),
            PromptTemplate(
                id=uid(), project_id=None, name="Executive Summary Writer",
                template="Write a concise executive summary (max {{max_words}} words) for the following content:\n\n{{content}}\n\nAudience: {{audience}}\nTone: {{tone}}",
                variables=["max_words", "content", "audience", "tone"],
                category="writing", tags=["summary", "executive", "communication"],
                version=1, is_active=True, usage_count=35, avg_latency_ms=1900, success_rate=0.98,
            ),
            PromptTemplate(
                id=uid(), project_id=p1_id, name="Customer Intent Classifier Prompt",
                template="Classify the following customer message into one of these categories: {{categories}}\n\nCustomer Message: {{message}}\n\nReturn JSON with 'category', 'confidence', and 'suggested_response'.",
                variables=["categories", "message"],
                category="classification", tags=["intent", "customer-service", "nlp"],
                version=3, is_active=True, usage_count=156, avg_latency_ms=850, success_rate=0.91,
            ),
        ]
        db.add_all(prompts)
        db.flush()

        # Sample prompt runs
        db.add_all([
            PromptRun(
                id=uid(), prompt_id=prompts[0].id, model="gpt-4o",
                inputs={"project_name": "Acme Customer AI", "industry": "SaaS", "objectives": "Reduce AHT 40%", "budget": "$2-3M", "timeline": "6 months"},
                output="# Business Requirements Document\n\n## Executive Summary\n...",
                latency_ms=3150, tokens=2800, cost=0.014, user_rating=5,
            ),
            PromptRun(
                id=uid(), prompt_id=prompts[4].id, model="gpt-4o",
                inputs={"categories": "billing, technical, account, general", "message": "My payment didn't go through and I was charged twice"},
                output='{"category": "billing", "confidence": 0.95, "suggested_response": "I apologize for the billing issue..."}',
                latency_ms=780, tokens=450, cost=0.002, user_rating=4,
            ),
            PromptRun(
                id=uid(), prompt_id=prompts[2].id, model="claude-3.5-sonnet",
                inputs={"num_risks": "5", "project_name": "GreenTech PdM", "domain": "Energy/IoT", "phase": "Development", "constraints": "Remote sites, limited connectivity"},
                output="## Top 5 Risks\n\n1. Sensor data reliability in extreme weather...",
                latency_ms=2650, tokens=1800, cost=0.005, user_rating=5,
            ),
        ])

        db.commit()
        print("Database seeded successfully with 3 projects and full demo data.")
        print("  - Acme Corp — Customer Service AI (active)")
        print("  - GreenTech — Predictive Maintenance (active)")
        print("  - FinServ — Fraud Detection Platform (planning)")
        print(f"  - {len(models)} AI models in catalog")
        print(f"  - {len(prompts)} prompt templates")

    except Exception as e:
        db.rollback()
        print(f"Seeding failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
