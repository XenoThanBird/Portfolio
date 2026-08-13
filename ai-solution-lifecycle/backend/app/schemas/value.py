"""Value assessment and ROI schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ValueAssessmentCreate(BaseModel):
    financial_impact: float = Field(default=0, ge=0, le=100)
    operational_excellence: float = Field(default=0, ge=0, le=100)
    strategic_value: float = Field(default=0, ge=0, le=100)
    risk_mitigation: float = Field(default=0, ge=0, le=100)
    customer_impact: float = Field(default=0, ge=0, le=100)
    innovation_index: float = Field(default=0, ge=0, le=100)
    data_maturity: float = Field(default=0, ge=0, le=1)
    organizational_readiness: float = Field(default=0, ge=0, le=1)
    technical_capability: float = Field(default=0, ge=0, le=1)


class ValueResponse(BaseModel):
    id: str
    project_id: str
    financial_impact: float
    operational_excellence: float
    strategic_value: float
    risk_mitigation: float
    customer_impact: float
    innovation_index: float
    data_maturity: float
    organizational_readiness: float
    technical_capability: float
    base_score: float
    readiness_multiplier: float
    final_score: float
    classification: Optional[str]
    recommended_action: Optional[str]
    investment_range: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


class ROIRequest(BaseModel):
    total_benefits: float = Field(..., description="Total expected benefits in $M")
    total_costs: float = Field(..., description="Total implementation costs in $M")
    time_horizon_years: int = Field(default=3, ge=1, le=10)
    discount_rate: float = Field(default=0.10, ge=0, le=1)


class ROIResponse(BaseModel):
    id: str
    roi_percent: float
    npv_millions: float
    payback_years: float
    risk_adjusted_roi: float
    total_benefits: float
    total_costs: float

    model_config = {"from_attributes": True}


class UseCasePriorityRequest(BaseModel):
    use_cases: list[dict]  # [{use_case, value_potential, complexity, time_months, data_readiness, risk_level}]


class RoadmapResponse(BaseModel):
    phases: list[dict]
    total_duration_months: int
    total_budget_millions: float
    maturity_progression: str
    success_probability: str


class ExecutiveSummaryResponse(BaseModel):
    summary_text: str
    value_assessment: Optional[ValueResponse]
    roi: Optional[ROIResponse]
