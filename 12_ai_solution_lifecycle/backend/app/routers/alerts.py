"""Alert rules and events router."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models.alert import AlertEvent, AlertRule
from app.schemas.alert import AlertEventResponse, AlertRuleCreate, AlertRuleResponse, AlertRuleUpdate
from app.services.alert_engine import evaluate_alerts

router = APIRouter(tags=["alerts"])


@router.get("/api/v1/projects/{project_id}/alerts/rules", response_model=list[AlertRuleResponse])
async def list_rules(project_id: str, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    return db.query(AlertRule).filter(AlertRule.project_id == project_id).all()


@router.post("/api/v1/projects/{project_id}/alerts/rules", response_model=AlertRuleResponse)
async def create_rule(
    project_id: str, data: AlertRuleCreate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)
):
    rule = AlertRule(project_id=project_id, **data.model_dump())
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


@router.put("/api/v1/alerts/rules/{rule_id}", response_model=AlertRuleResponse)
async def update_rule(rule_id: str, data: AlertRuleUpdate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    rule = db.query(AlertRule).filter(AlertRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(rule, field, value)
    db.commit()
    db.refresh(rule)
    return rule


@router.delete("/api/v1/alerts/rules/{rule_id}")
async def delete_rule(rule_id: str, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    rule = db.query(AlertRule).filter(AlertRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    db.delete(rule)
    db.commit()
    return {"status": "deleted"}


@router.get("/api/v1/projects/{project_id}/alerts/events", response_model=list[AlertEventResponse])
async def list_events(
    project_id: str, limit: int = 50, db: Session = Depends(get_db), user: dict = Depends(get_current_user)
):
    return (
        db.query(AlertEvent)
        .filter(AlertEvent.project_id == project_id)
        .order_by(AlertEvent.triggered_at.desc())
        .limit(limit)
        .all()
    )


@router.put("/api/v1/alerts/events/{event_id}/acknowledge")
async def acknowledge_event(event_id: str, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    event = db.query(AlertEvent).filter(AlertEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    event.acknowledged = True
    event.acknowledged_by = user["email"]
    db.commit()
    return {"status": "acknowledged"}


@router.get("/api/v1/alerts/events/unacknowledged", response_model=list[AlertEventResponse])
async def unacknowledged_events(db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    return (
        db.query(AlertEvent)
        .filter(AlertEvent.acknowledged.is_(False))
        .order_by(AlertEvent.triggered_at.desc())
        .limit(50)
        .all()
    )


@router.post("/api/v1/projects/{project_id}/alerts/evaluate")
async def trigger_evaluation(project_id: str, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    new_events = evaluate_alerts(project_id, db)
    return {"events_created": len(new_events), "events": new_events}
