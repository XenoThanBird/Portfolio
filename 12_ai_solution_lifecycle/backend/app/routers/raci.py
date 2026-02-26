"""RACI matrix CRUD router."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models.raci import RACIEntry
from app.schemas.raci import RACICreate, RACIMatrixResponse, RACIResponse, RACIUpdate

router = APIRouter(tags=["raci"])


@router.get("/api/v1/projects/{project_id}/raci", response_model=RACIMatrixResponse)
async def get_raci_matrix(
    project_id: str,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    entries = db.query(RACIEntry).filter(RACIEntry.project_id == project_id).all()

    deliverables = sorted(set(e.deliverable for e in entries))
    people_set = {}
    for e in entries:
        people_set[e.person_email] = {"name": e.person_name, "email": e.person_email}

    matrix = {}
    for e in entries:
        if e.deliverable not in matrix:
            matrix[e.deliverable] = {}
        matrix[e.deliverable][e.person_email] = e.role_type

    return RACIMatrixResponse(
        deliverables=deliverables,
        people=list(people_set.values()),
        matrix=matrix,
    )


@router.post("/api/v1/projects/{project_id}/raci", response_model=RACIResponse)
async def create_or_update_raci(
    project_id: str,
    data: RACICreate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    existing = (
        db.query(RACIEntry)
        .filter(
            RACIEntry.project_id == project_id,
            RACIEntry.deliverable == data.deliverable,
            RACIEntry.person_email == data.person_email,
        )
        .first()
    )

    if existing:
        existing.role_type = data.role_type
        existing.person_name = data.person_name
        existing.milestone_id = data.milestone_id
        db.commit()
        db.refresh(existing)
        return existing

    entry = RACIEntry(project_id=project_id, **data.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.put("/api/v1/raci/{entry_id}", response_model=RACIResponse)
async def update_raci(
    entry_id: str,
    data: RACIUpdate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    entry = db.query(RACIEntry).filter(RACIEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="RACI entry not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(entry, field, value)
    db.commit()
    db.refresh(entry)
    return entry


@router.delete("/api/v1/raci/{entry_id}")
async def delete_raci(entry_id: str, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    entry = db.query(RACIEntry).filter(RACIEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="RACI entry not found")
    db.delete(entry)
    db.commit()
    return {"status": "deleted"}
