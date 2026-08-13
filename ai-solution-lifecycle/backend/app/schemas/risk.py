"""Risk and change request schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class RiskCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = None
    probability: str  # Very Low, Low, Medium, High, Very High
    impact: str  # Minimal, Low, Medium, High, Critical
    mitigation_plan: Optional[str] = None
    owner_email: Optional[str] = None


class RiskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    probability: Optional[str] = None
    impact: Optional[str] = None
    mitigation_plan: Optional[str] = None
    owner_email: Optional[str] = None
    status: Optional[str] = None


class RiskResponse(BaseModel):
    id: str
    project_id: str
    title: str
    description: Optional[str]
    category: Optional[str]
    probability: str
    impact: str
    risk_score: Optional[float]
    classification: Optional[str]
    mitigation_plan: Optional[str]
    owner_email: Optional[str]
    status: str
    created_at: Optional[datetime]

    model_config = {"from_attributes": True}


class RiskMatrixResponse(BaseModel):
    matrix: dict[str, dict[str, int]]  # probability -> {impact -> count}
    total_risks: int
    avg_score: float


class ChangeRequestCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = None
    justification: Optional[str] = None
    impact_assessment: Optional[str] = None
    priority: str = "medium"


class ChangeRequestUpdate(BaseModel):
    status: Optional[str] = None
    reviewed_by: Optional[str] = None
    review_notes: Optional[str] = None
    priority: Optional[str] = None


class ChangeRequestResponse(BaseModel):
    id: str
    project_id: str
    title: str
    description: Optional[str]
    justification: Optional[str]
    impact_assessment: Optional[str]
    requested_by: Optional[str]
    status: str
    priority: str
    reviewed_by: Optional[str]
    review_notes: Optional[str]
    created_at: Optional[datetime]

    model_config = {"from_attributes": True}
