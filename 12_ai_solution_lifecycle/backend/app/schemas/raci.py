"""RACI matrix schemas."""

from typing import Optional

from pydantic import BaseModel, Field


class RACICreate(BaseModel):
    deliverable: str = Field(..., min_length=2, max_length=200)
    milestone_id: Optional[str] = None
    person_name: str
    person_email: str
    role_type: str = Field(..., pattern="^[RACI]$")


class RACIUpdate(BaseModel):
    role_type: Optional[str] = Field(None, pattern="^[RACI]$")
    deliverable: Optional[str] = None
    person_name: Optional[str] = None
    person_email: Optional[str] = None


class RACIResponse(BaseModel):
    id: str
    project_id: str
    deliverable: str
    milestone_id: Optional[str]
    person_name: str
    person_email: str
    role_type: str

    model_config = {"from_attributes": True}


class RACIMatrixResponse(BaseModel):
    deliverables: list[str]
    people: list[dict]  # [{"name": "...", "email": "..."}]
    matrix: dict[str, dict[str, str]]  # deliverable -> {email -> role_type}
