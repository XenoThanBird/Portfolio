"""Alert schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AlertRuleCreate(BaseModel):
    name: str
    alert_type: str  # sla_breach, milestone_delay, risk_escalation, doc_review_deadline
    condition_config: Optional[dict] = None
    severity: str = "warning"
    is_active: bool = True
    notify_emails: list[str] = []
    cooldown_minutes: int = 60


class AlertRuleUpdate(BaseModel):
    name: Optional[str] = None
    condition_config: Optional[dict] = None
    severity: Optional[str] = None
    is_active: Optional[bool] = None
    notify_emails: Optional[list[str]] = None


class AlertRuleResponse(BaseModel):
    id: str
    project_id: str
    name: str
    alert_type: str
    condition_config: Optional[dict]
    severity: str
    is_active: bool
    notify_emails: Optional[list[str]]
    cooldown_minutes: int
    created_at: Optional[datetime]

    model_config = {"from_attributes": True}


class AlertEventResponse(BaseModel):
    id: str
    rule_id: str
    project_id: str
    title: str
    message: Optional[str]
    severity: str
    acknowledged: bool
    acknowledged_by: Optional[str]
    triggered_at: Optional[datetime]

    model_config = {"from_attributes": True}
