"""
SLA compliance monitoring service.
"""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.sla import SLADefinition, SLAMetric


def record_metric(
    sla_id: str,
    measured_value: float,
    db: Session,
    notes: str | None = None,
) -> SLAMetric:
    """Record a new SLA metric measurement and determine compliance."""
    sla = db.query(SLADefinition).filter(SLADefinition.id == sla_id).first()
    if not sla:
        raise ValueError(f"SLA {sla_id} not found")

    # Determine compliance based on metric type
    # For response_time/resolution_time: lower is better (value <= target = compliant)
    # For uptime/throughput: higher is better (value >= target = compliant)
    if sla.metric_type in ("response_time", "resolution_time"):
        is_compliant = measured_value <= sla.target_value
    else:
        is_compliant = measured_value >= sla.target_value

    metric = SLAMetric(
        sla_id=sla_id,
        measured_value=measured_value,
        is_compliant=is_compliant,
        measured_at=datetime.now(timezone.utc),
        notes=notes,
    )
    db.add(metric)
    db.commit()
    db.refresh(metric)
    return metric


def get_compliance_stats(sla_id: str, db: Session) -> dict:
    """Calculate compliance statistics for an SLA."""
    sla = db.query(SLADefinition).filter(SLADefinition.id == sla_id).first()
    if not sla:
        return {}

    metrics = (
        db.query(SLAMetric)
        .filter(SLAMetric.sla_id == sla_id)
        .order_by(SLAMetric.measured_at.desc())
        .all()
    )

    if not metrics:
        return {
            "sla_id": sla_id,
            "sla_name": sla.name,
            "total_measurements": 0,
            "compliant_count": 0,
            "compliance_pct": 0.0,
            "latest_value": None,
            "trend": "stable",
        }

    total = len(metrics)
    compliant = sum(1 for m in metrics if m.is_compliant)
    compliance_pct = round((compliant / total) * 100, 1)

    # Determine trend from last 5 measurements
    recent = metrics[:5]
    if len(recent) >= 3:
        recent_compliance = sum(1 for m in recent if m.is_compliant) / len(recent)
        older = metrics[5:10] if len(metrics) > 5 else metrics
        older_compliance = sum(1 for m in older if m.is_compliant) / len(older) if older else 0.5
        if recent_compliance > older_compliance + 0.1:
            trend = "improving"
        elif recent_compliance < older_compliance - 0.1:
            trend = "declining"
        else:
            trend = "stable"
    else:
        trend = "stable"

    return {
        "sla_id": sla_id,
        "sla_name": sla.name,
        "total_measurements": total,
        "compliant_count": compliant,
        "compliance_pct": compliance_pct,
        "latest_value": metrics[0].measured_value if metrics else None,
        "trend": trend,
    }


def get_project_sla_dashboard(project_id: str, db: Session) -> list[dict]:
    """Get SLA compliance overview for all SLAs in a project."""
    slas = db.query(SLADefinition).filter(SLADefinition.project_id == project_id).all()
    return [get_compliance_stats(sla.id, db) for sla in slas]
