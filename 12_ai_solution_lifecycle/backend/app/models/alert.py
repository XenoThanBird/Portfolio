"""
Alert rule and event models for SLA breaches, milestone delays, and risk escalations.
"""

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class AlertRule(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "alert_rules"

    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    name = Column(String(100), nullable=False)
    alert_type = Column(String(30), nullable=False)  # sla_breach, milestone_delay, risk_escalation, doc_review_deadline
    condition_config = Column(JSON)  # Threshold/timing config
    severity = Column(String(10), default="warning")  # info, warning, critical
    is_active = Column(Boolean, default=True)
    notify_emails = Column(JSON)  # String array
    cooldown_minutes = Column(Integer, default=60)

    project = relationship("Project", back_populates="alert_rules")
    events = relationship("AlertEvent", back_populates="rule", cascade="all, delete-orphan")


class AlertEvent(UUIDMixin, Base):
    __tablename__ = "alert_events"

    rule_id = Column(String(36), ForeignKey("alert_rules.id"), nullable=False)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text)
    severity = Column(String(10), nullable=False)
    acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(String(100), nullable=True)
    triggered_at = Column(DateTime, nullable=False)

    rule = relationship("AlertRule", back_populates="events")
