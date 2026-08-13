"""Project CRUD router."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models.project import Project, ProjectMember
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectSummary, ProjectUpdate

router = APIRouter(prefix="/api/v1/projects", tags=["projects"])


@router.get("", response_model=list[ProjectResponse])
async def list_projects(
    status: str | None = None,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    query = db.query(Project)
    if status:
        query = query.filter(Project.status == status)
    return query.order_by(Project.created_at.desc()).all()


@router.post("", response_model=ProjectResponse)
async def create_project(
    data: ProjectCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    project = Project(
        name=data.name,
        description=data.description,
        status=data.status,
        owner_email=data.owner_email or user["email"],
        start_date=data.start_date,
        target_end_date=data.target_end_date,
        budget_millions=data.budget_millions,
        data_maturity_level=data.data_maturity_level,
    )
    for m in data.members:
        project.members.append(ProjectMember(name=m.name, email=m.email, role=m.role, department=m.department))
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    data: ProjectUpdate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}")
async def archive_project(project_id: str, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    project.status = "archived"
    db.commit()
    return {"status": "archived"}


@router.get("/{project_id}/summary", response_model=ProjectSummary)
async def get_project_summary(project_id: str, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    from app.models.alert import AlertEvent
    from app.models.document import Document
    from app.models.milestone import Milestone
    from app.models.risk import Risk
    from app.models.value import ValueAssessment

    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    milestones = db.query(Milestone).filter(Milestone.project_id == project_id).all()
    docs = db.query(Document).filter(Document.project_id == project_id).count()
    risks = db.query(Risk).filter(Risk.project_id == project_id, Risk.status == "open").all()
    alerts = db.query(AlertEvent).filter(AlertEvent.project_id == project_id, AlertEvent.acknowledged.is_(False)).count()
    va = db.query(ValueAssessment).filter(ValueAssessment.project_id == project_id).first()

    return ProjectSummary(
        id=project.id,
        name=project.name,
        status=project.status,
        milestone_count=len(milestones),
        milestones_done=sum(1 for m in milestones if m.status == "done"),
        document_count=docs,
        open_risks=len(risks),
        avg_risk_score=round(sum(r.risk_score or 0 for r in risks) / len(risks), 1) if risks else 0,
        unacknowledged_alerts=alerts,
        value_score=va.final_score if va else None,
    )
