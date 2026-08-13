"""Project and ProjectMember schemas."""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class ProjectMemberCreate(BaseModel):
    name: str
    email: str
    role: Optional[str] = None
    department: Optional[str] = None


class ProjectMemberResponse(ProjectMemberCreate):
    id: str

    model_config = {"from_attributes": True}


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = None
    status: str = "draft"
    owner_email: Optional[str] = None
    start_date: Optional[date] = None
    target_end_date: Optional[date] = None
    budget_millions: Optional[float] = None
    data_maturity_level: int = Field(default=1, ge=1, le=5)
    members: list[ProjectMemberCreate] = []


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    owner_email: Optional[str] = None
    start_date: Optional[date] = None
    target_end_date: Optional[date] = None
    budget_millions: Optional[float] = None
    data_maturity_level: Optional[int] = None


class ProjectResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    status: str
    owner_email: Optional[str]
    start_date: Optional[date]
    target_end_date: Optional[date]
    budget_millions: Optional[float]
    data_maturity_level: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    members: list[ProjectMemberResponse] = []

    model_config = {"from_attributes": True}


class ProjectSummary(BaseModel):
    id: str
    name: str
    status: str
    milestone_count: int = 0
    milestones_done: int = 0
    document_count: int = 0
    open_risks: int = 0
    avg_risk_score: float = 0
    sla_compliance_pct: float = 0
    unacknowledged_alerts: int = 0
    value_score: Optional[float] = None
