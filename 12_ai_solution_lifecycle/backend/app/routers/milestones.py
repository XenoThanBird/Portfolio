"""Milestone CRUD and Kanban board router."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models.milestone import Milestone, MilestoneDependency
from app.schemas.milestone import (
    DependencyCreate,
    MilestoneCreate,
    MilestoneResponse,
    MilestoneUpdate,
    ReorderRequest,
)

router = APIRouter(tags=["milestones"])


@router.get("/api/v1/projects/{project_id}/milestones")
async def list_milestones(
    project_id: str,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    milestones = (
        db.query(Milestone)
        .filter(Milestone.project_id == project_id)
        .order_by(Milestone.sort_order)
        .all()
    )
    # Group by status for Kanban view
    grouped = {"backlog": [], "in_progress": [], "review": [], "done": []}
    for m in milestones:
        status = m.status if m.status in grouped else "backlog"
        grouped[status].append(MilestoneResponse.model_validate(m))
    return grouped


@router.post("/api/v1/projects/{project_id}/milestones", response_model=MilestoneResponse)
async def create_milestone(
    project_id: str,
    data: MilestoneCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    milestone = Milestone(project_id=project_id, **data.model_dump())
    db.add(milestone)
    db.commit()
    db.refresh(milestone)
    return milestone


@router.put("/api/v1/milestones/{milestone_id}", response_model=MilestoneResponse)
async def update_milestone(
    milestone_id: str,
    data: MilestoneUpdate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    milestone = db.query(Milestone).filter(Milestone.id == milestone_id).first()
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(milestone, field, value)
    db.commit()
    db.refresh(milestone)
    return milestone


@router.delete("/api/v1/milestones/{milestone_id}")
async def delete_milestone(
    milestone_id: str,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    milestone = db.query(Milestone).filter(Milestone.id == milestone_id).first()
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")
    db.delete(milestone)
    db.commit()
    return {"status": "deleted"}


@router.post("/api/v1/milestones/{milestone_id}/dependencies")
async def add_dependency(
    milestone_id: str,
    data: DependencyCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    dep = MilestoneDependency(
        milestone_id=milestone_id,
        depends_on_id=data.depends_on_id,
        dependency_type=data.dependency_type,
    )
    db.add(dep)
    db.commit()
    return {"status": "dependency added"}


@router.put("/api/v1/milestones/reorder")
async def reorder_milestones(
    data: ReorderRequest,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    for item in data.items:
        milestone = db.query(Milestone).filter(Milestone.id == item["id"]).first()
        if milestone:
            milestone.status = item.get("status", milestone.status)
            milestone.sort_order = item.get("sort_order", milestone.sort_order)
    db.commit()
    return {"status": "reordered"}
