"""Risk register and change request router."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models.risk import ChangeRequest, Risk, PROBABILITY_VALUES, IMPACT_VALUES
from app.schemas.risk import (
    ChangeRequestCreate, ChangeRequestResponse, ChangeRequestUpdate,
    RiskCreate, RiskMatrixResponse, RiskResponse, RiskUpdate,
)

router = APIRouter(tags=["risks"])


@router.get("/api/v1/projects/{project_id}/risks", response_model=list[RiskResponse])
async def list_risks(project_id: str, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    return db.query(Risk).filter(Risk.project_id == project_id).order_by(Risk.risk_score.desc()).all()


@router.post("/api/v1/projects/{project_id}/risks", response_model=RiskResponse)
async def create_risk(
    project_id: str, data: RiskCreate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)
):
    risk = Risk(project_id=project_id, **data.model_dump())
    risk.compute_score()
    db.add(risk)
    db.commit()
    db.refresh(risk)
    return risk


@router.put("/api/v1/risks/{risk_id}", response_model=RiskResponse)
async def update_risk(risk_id: str, data: RiskUpdate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    risk = db.query(Risk).filter(Risk.id == risk_id).first()
    if not risk:
        raise HTTPException(status_code=404, detail="Risk not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(risk, field, value)
    risk.compute_score()
    db.commit()
    db.refresh(risk)
    return risk


@router.delete("/api/v1/risks/{risk_id}")
async def delete_risk(risk_id: str, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    risk = db.query(Risk).filter(Risk.id == risk_id).first()
    if not risk:
        raise HTTPException(status_code=404, detail="Risk not found")
    db.delete(risk)
    db.commit()
    return {"status": "deleted"}


@router.get("/api/v1/projects/{project_id}/risks/matrix", response_model=RiskMatrixResponse)
async def risk_matrix(project_id: str, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    risks = db.query(Risk).filter(Risk.project_id == project_id, Risk.status == "open").all()
    matrix = {p: {i: 0 for i in IMPACT_VALUES} for p in PROBABILITY_VALUES}
    for r in risks:
        if r.probability in matrix and r.impact in matrix.get(r.probability, {}):
            matrix[r.probability][r.impact] += 1
    avg_score = round(sum(r.risk_score or 0 for r in risks) / len(risks), 1) if risks else 0
    return RiskMatrixResponse(matrix=matrix, total_risks=len(risks), avg_score=avg_score)


# Change Requests
@router.get("/api/v1/projects/{project_id}/change-requests", response_model=list[ChangeRequestResponse])
async def list_change_requests(project_id: str, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    return db.query(ChangeRequest).filter(ChangeRequest.project_id == project_id).order_by(ChangeRequest.created_at.desc()).all()


@router.post("/api/v1/projects/{project_id}/change-requests", response_model=ChangeRequestResponse)
async def create_change_request(
    project_id: str, data: ChangeRequestCreate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)
):
    cr = ChangeRequest(project_id=project_id, requested_by=user["email"], **data.model_dump())
    db.add(cr)
    db.commit()
    db.refresh(cr)
    return cr


@router.put("/api/v1/change-requests/{cr_id}", response_model=ChangeRequestResponse)
async def update_change_request(
    cr_id: str, data: ChangeRequestUpdate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)
):
    cr = db.query(ChangeRequest).filter(ChangeRequest.id == cr_id).first()
    if not cr:
        raise HTTPException(status_code=404, detail="Change request not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(cr, field, value)
    db.commit()
    db.refresh(cr)
    return cr
