"""Value assessment, ROI calculator, and roadmap router."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models.value import ROICalculation, ValueAssessment
from app.schemas.value import (
    ROIRequest, ROIResponse, RoadmapResponse, UseCasePriorityRequest,
    ValueAssessmentCreate, ValueResponse,
)
from app.services.value_engine import ValueEngine

router = APIRouter(tags=["value"])

engine = ValueEngine()


@router.get("/api/v1/projects/{project_id}/value", response_model=ValueResponse)
async def get_value(project_id: str, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    va = db.query(ValueAssessment).filter(ValueAssessment.project_id == project_id).first()
    if not va:
        raise HTTPException(status_code=404, detail="No value assessment found")
    return va


@router.post("/api/v1/projects/{project_id}/value", response_model=ValueResponse)
async def create_or_update_value(
    project_id: str,
    data: ValueAssessmentCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    va = db.query(ValueAssessment).filter(ValueAssessment.project_id == project_id).first()

    components = {
        "financial_impact": data.financial_impact,
        "operational_excellence": data.operational_excellence,
        "strategic_value": data.strategic_value,
        "risk_mitigation": data.risk_mitigation,
        "customer_impact": data.customer_impact,
        "innovation_index": data.innovation_index,
    }
    readiness = {
        "data_maturity": data.data_maturity,
        "organizational_readiness": data.organizational_readiness,
        "technical_capability": data.technical_capability,
    }

    score = engine.calculate_value_score(components, readiness)

    if va:
        for field, value in data.model_dump().items():
            setattr(va, field, value)
    else:
        va = ValueAssessment(project_id=project_id, **data.model_dump())
        db.add(va)

    va.base_score = score["base_score"]
    va.readiness_multiplier = score["readiness_multiplier"]
    va.final_score = score["final_score"]
    va.classification = score["classification"]
    va.recommended_action = score["recommended_action"]
    va.investment_range = score["investment_range"]

    db.commit()
    db.refresh(va)
    return va


@router.post("/api/v1/projects/{project_id}/value/roi", response_model=ROIResponse)
async def calculate_roi(
    project_id: str,
    data: ROIRequest,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    va = db.query(ValueAssessment).filter(ValueAssessment.project_id == project_id).first()
    if not va:
        raise HTTPException(status_code=404, detail="Create a value assessment first")

    roi = engine.calculate_roi(
        benefits=data.total_benefits,
        costs=data.total_costs,
        years=data.time_horizon_years,
        discount_rate=data.discount_rate,
    )

    calc = ROICalculation(
        assessment_id=va.id,
        total_benefits=data.total_benefits,
        total_costs=data.total_costs,
        time_horizon_years=data.time_horizon_years,
        discount_rate=data.discount_rate,
        roi_percent=roi["roi_percent"],
        npv_millions=roi["npv_millions"],
        payback_years=roi["payback_years"],
        risk_adjusted_roi=roi["risk_adjusted_roi"],
    )
    db.add(calc)
    db.commit()
    db.refresh(calc)
    return calc


@router.get("/api/v1/projects/{project_id}/value/roadmap", response_model=RoadmapResponse)
async def get_roadmap(
    project_id: str,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    from app.models.project import Project

    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    va = db.query(ValueAssessment).filter(ValueAssessment.project_id == project_id).first()
    current = project.data_maturity_level or 1
    target = min(current + 2, 5)
    budget = project.budget_millions or 10

    return engine.generate_roadmap(current, target, budget)


@router.post("/api/v1/projects/{project_id}/value/use-cases")
async def prioritize_use_cases(
    project_id: str,
    data: UseCasePriorityRequest,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    return engine.prioritize_use_cases(data.use_cases)
