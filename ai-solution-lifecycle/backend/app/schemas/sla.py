"""SLA schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SLACreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    metric_type: str  # response_time, resolution_time, uptime, throughput
    target_value: float
    target_unit: Optional[str] = None
    warning_threshold: Optional[float] = None
    breach_threshold: Optional[float] = None
    measurement_window: str = "weekly"


class SLAUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    target_value: Optional[float] = None
    warning_threshold: Optional[float] = None
    breach_threshold: Optional[float] = None


class SLAResponse(BaseModel):
    id: str
    project_id: str
    name: str
    description: Optional[str]
    metric_type: str
    target_value: float
    target_unit: Optional[str]
    warning_threshold: Optional[float]
    breach_threshold: Optional[float]
    measurement_window: str
    created_at: Optional[datetime]

    model_config = {"from_attributes": True}


class MetricRecord(BaseModel):
    measured_value: float
    notes: Optional[str] = None


class ComplianceResponse(BaseModel):
    sla_id: str
    sla_name: str
    total_measurements: int
    compliant_count: int
    compliance_pct: float
    latest_value: Optional[float]
    trend: str  # improving, stable, declining
