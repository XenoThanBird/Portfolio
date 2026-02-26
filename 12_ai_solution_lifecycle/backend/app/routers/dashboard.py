"""Dashboard aggregation router."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models.alert import AlertEvent
from app.models.document import Document
from app.models.milestone import Milestone
from app.models.project import Project
from app.models.risk import Risk
from app.models.value import ValueAssessment

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])


@router.get("")
async def global_dashboard(db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    projects = db.query(Project).filter(Project.status != "archived").all()
    active_count = sum(1 for p in projects if p.status == "active")
    unack_alerts = db.query(AlertEvent).filter(AlertEvent.acknowledged.is_(False)).count()

    # Aggregate value scores
    assessments = db.query(ValueAssessment).all()
    avg_value = round(sum(a.final_score for a in assessments) / len(assessments), 1) if assessments else 0

    # SLA compliance
    from app.models.sla import SLAMetric
    total_metrics = db.query(SLAMetric).count()
    compliant_metrics = db.query(SLAMetric).filter(SLAMetric.is_compliant.is_(True)).count()
    sla_compliance = round((compliant_metrics / total_metrics) * 100, 1) if total_metrics > 0 else 100

    return {
        "total_projects": len(projects),
        "active_projects": active_count,
        "unacknowledged_alerts": unack_alerts,
        "avg_value_score": avg_value,
        "sla_compliance_pct": sla_compliance,
        "projects": [
            {
                "id": p.id,
                "name": p.name,
                "status": p.status,
                "owner_email": p.owner_email,
            }
            for p in projects[:10]
        ],
    }


@router.get("/projects/{project_id}")
async def project_dashboard(project_id: str, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    milestones = db.query(Milestone).filter(Milestone.project_id == project_id).all()
    docs = db.query(Document).filter(Document.project_id == project_id).count()
    risks = db.query(Risk).filter(Risk.project_id == project_id, Risk.status == "open").all()
    alerts = db.query(AlertEvent).filter(AlertEvent.project_id == project_id, AlertEvent.acknowledged.is_(False)).all()
    va = db.query(ValueAssessment).filter(ValueAssessment.project_id == project_id).first()

    milestone_stats = {"backlog": 0, "in_progress": 0, "review": 0, "done": 0}
    for m in milestones:
        status = m.status if m.status in milestone_stats else "backlog"
        milestone_stats[status] += 1

    return {
        "milestones": milestone_stats,
        "total_milestones": len(milestones),
        "document_count": docs,
        "open_risks": len(risks),
        "avg_risk_score": round(sum(r.risk_score or 0 for r in risks) / len(risks), 1) if risks else 0,
        "critical_risks": sum(1 for r in risks if (r.risk_score or 0) >= 40),
        "unacknowledged_alerts": len(alerts),
        "recent_alerts": [
            {"title": a.title, "severity": a.severity, "triggered_at": str(a.triggered_at)}
            for a in alerts[:5]
        ],
        "value_score": va.final_score if va else None,
        "value_classification": va.classification if va else None,
    }
