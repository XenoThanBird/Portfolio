"""
Alert evaluation engine.
Checks alert rules against project state and creates alert events.
"""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.alert import AlertEvent, AlertRule
from app.models.milestone import Milestone
from app.models.risk import Risk
from app.models.sla import SLADefinition, SLAMetric


def evaluate_alerts(project_id: str, db: Session) -> list[dict]:
    """
    Evaluate all active alert rules for a project and create events for triggered rules.

    Returns:
        List of newly created alert event summaries.
    """
    rules = (
        db.query(AlertRule)
        .filter(AlertRule.project_id == project_id, AlertRule.is_active.is_(True))
        .all()
    )

    new_events = []
    now = datetime.now(timezone.utc)

    for rule in rules:
        triggered = False
        title = ""
        message = ""

        if rule.alert_type == "milestone_delay":
            triggered, title, message = _check_milestone_delays(project_id, rule, db, now)
        elif rule.alert_type == "sla_breach":
            triggered, title, message = _check_sla_breaches(project_id, rule, db)
        elif rule.alert_type == "risk_escalation":
            triggered, title, message = _check_risk_escalations(project_id, rule, db)
        elif rule.alert_type == "doc_review_deadline":
            triggered, title, message = _check_doc_deadlines(project_id, rule, db, now)

        if triggered:
            # Check cooldown
            latest_event = (
                db.query(AlertEvent)
                .filter(AlertEvent.rule_id == rule.id)
                .order_by(AlertEvent.triggered_at.desc())
                .first()
            )
            if latest_event:
                elapsed = (now - latest_event.triggered_at).total_seconds() / 60
                if elapsed < rule.cooldown_minutes:
                    continue

            event = AlertEvent(
                rule_id=rule.id,
                project_id=project_id,
                title=title,
                message=message,
                severity=rule.severity,
                triggered_at=now,
            )
            db.add(event)
            new_events.append({"title": title, "severity": rule.severity, "message": message})

    if new_events:
        db.commit()

    return new_events


def _check_milestone_delays(
    project_id: str, rule: AlertRule, db: Session, now: datetime
) -> tuple[bool, str, str]:
    """Check for overdue milestones."""
    threshold_days = (rule.condition_config or {}).get("overdue_days", 3)
    overdue = (
        db.query(Milestone)
        .filter(
            Milestone.project_id == project_id,
            Milestone.status.in_(["backlog", "in_progress", "review"]),
            Milestone.due_date.isnot(None),
        )
        .all()
    )

    overdue_items = []
    for m in overdue:
        if m.due_date and (now.date() - m.due_date).days > threshold_days:
            overdue_items.append(m.title)

    if overdue_items:
        return (
            True,
            f"{len(overdue_items)} milestone(s) overdue",
            f"Overdue milestones: {', '.join(overdue_items[:5])}",
        )
    return False, "", ""


def _check_sla_breaches(
    project_id: str, rule: AlertRule, db: Session
) -> tuple[bool, str, str]:
    """Check for SLA breaches."""
    slas = db.query(SLADefinition).filter(SLADefinition.project_id == project_id).all()

    breaches = []
    for sla in slas:
        latest = (
            db.query(SLAMetric)
            .filter(SLAMetric.sla_id == sla.id)
            .order_by(SLAMetric.measured_at.desc())
            .first()
        )
        if latest and not latest.is_compliant:
            breaches.append(sla.name)

    if breaches:
        return (
            True,
            f"{len(breaches)} SLA breach(es) detected",
            f"Breached SLAs: {', '.join(breaches[:5])}",
        )
    return False, "", ""


def _check_risk_escalations(
    project_id: str, rule: AlertRule, db: Session
) -> tuple[bool, str, str]:
    """Check for critical/high risks."""
    threshold = (rule.condition_config or {}).get("min_score", 40)
    critical_risks = (
        db.query(Risk)
        .filter(
            Risk.project_id == project_id,
            Risk.status == "open",
            Risk.risk_score >= threshold,
        )
        .all()
    )

    if critical_risks:
        return (
            True,
            f"{len(critical_risks)} high-severity risk(s)",
            f"Critical risks: {', '.join(r.title for r in critical_risks[:5])}",
        )
    return False, "", ""


def _check_doc_deadlines(
    project_id: str, rule: AlertRule, db: Session, now: datetime
) -> tuple[bool, str, str]:
    """Check for documents stuck in review status."""
    from app.models.document import Document

    max_review_hours = (rule.condition_config or {}).get("max_review_hours", 48)
    docs_in_review = (
        db.query(Document)
        .filter(Document.project_id == project_id, Document.status == "review")
        .all()
    )

    stale = []
    for doc in docs_in_review:
        if doc.updated_at:
            hours = (now - doc.updated_at).total_seconds() / 3600
            if hours > max_review_hours:
                stale.append(doc.title)

    if stale:
        return (
            True,
            f"{len(stale)} document(s) pending review > {max_review_hours}h",
            f"Stale reviews: {', '.join(stale[:5])}",
        )
    return False, "", ""
