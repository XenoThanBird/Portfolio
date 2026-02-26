"""
SLA definition and metric tracking models.
"""

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class SLADefinition(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "sla_definitions"

    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    metric_type = Column(String(30), nullable=False)  # response_time, resolution_time, uptime, throughput
    target_value = Column(Float, nullable=False)
    target_unit = Column(String(20))  # hours, percent, count
    warning_threshold = Column(Float)
    breach_threshold = Column(Float)
    measurement_window = Column(String(20), default="weekly")  # daily, weekly, monthly

    project = relationship("Project", back_populates="sla_definitions")
    metrics = relationship("SLAMetric", back_populates="sla", cascade="all, delete-orphan")


class SLAMetric(UUIDMixin, Base):
    __tablename__ = "sla_metrics"

    sla_id = Column(String(36), ForeignKey("sla_definitions.id"), nullable=False)
    measured_value = Column(Float, nullable=False)
    is_compliant = Column(Boolean, nullable=False)
    measured_at = Column(DateTime, nullable=False)
    notes = Column(Text, nullable=True)

    sla = relationship("SLADefinition", back_populates="metrics")
