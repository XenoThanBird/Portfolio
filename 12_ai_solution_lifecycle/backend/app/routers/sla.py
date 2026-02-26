"""SLA definition and compliance tracking router."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models.sla import SLADefinition
from app.schemas.sla import ComplianceResponse, MetricRecord, SLACreate, SLAResponse, SLAUpdate
from app.services.sla_monitor import get_compliance_stats, get_project_sla_dashboard, record_metric

router = APIRouter(tags=["sla"])


@router.get("/api/v1/projects/{project_id}/slas", response_model=list[SLAResponse])
async def list_slas(project_id: str, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    return db.query(SLADefinition).filter(SLADefinition.project_id == project_id).all()


@router.post("/api/v1/projects/{project_id}/slas", response_model=SLAResponse)
async def create_sla(
    project_id: str, data: SLACreate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)
):
    sla = SLADefinition(project_id=project_id, **data.model_dump())
    db.add(sla)
    db.commit()
    db.refresh(sla)
    return sla


@router.put("/api/v1/slas/{sla_id}", response_model=SLAResponse)
async def update_sla(sla_id: str, data: SLAUpdate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    sla = db.query(SLADefinition).filter(SLADefinition.id == sla_id).first()
    if not sla:
        raise HTTPException(status_code=404, detail="SLA not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(sla, field, value)
    db.commit()
    db.refresh(sla)
    return sla


@router.delete("/api/v1/slas/{sla_id}")
async def delete_sla(sla_id: str, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    sla = db.query(SLADefinition).filter(SLADefinition.id == sla_id).first()
    if not sla:
        raise HTTPException(status_code=404, detail="SLA not found")
    db.delete(sla)
    db.commit()
    return {"status": "deleted"}


@router.post("/api/v1/slas/{sla_id}/metrics")
async def add_metric(sla_id: str, data: MetricRecord, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    metric = record_metric(sla_id, data.measured_value, db, data.notes)
    return {"id": metric.id, "is_compliant": metric.is_compliant, "measured_at": str(metric.measured_at)}


@router.get("/api/v1/slas/{sla_id}/compliance", response_model=ComplianceResponse)
async def get_compliance(sla_id: str, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    stats = get_compliance_stats(sla_id, db)
    if not stats:
        raise HTTPException(status_code=404, detail="SLA not found")
    return stats


@router.get("/api/v1/projects/{project_id}/slas/dashboard")
async def sla_dashboard(project_id: str, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    return get_project_sla_dashboard(project_id, db)
