"""Milestone schemas."""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class MilestoneCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = None
    status: str = "backlog"
    priority: str = "medium"
    owner_email: Optional[str] = None
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    sort_order: int = 0


class MilestoneUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    owner_email: Optional[str] = None
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    completed_date: Optional[date] = None
    sort_order: Optional[int] = None


class MilestoneResponse(BaseModel):
    id: str
    project_id: str
    title: str
    description: Optional[str]
    status: str
    priority: str
    owner_email: Optional[str]
    start_date: Optional[date]
    due_date: Optional[date]
    completed_date: Optional[date]
    sort_order: int
    created_at: Optional[datetime]

    model_config = {"from_attributes": True}


class DependencyCreate(BaseModel):
    depends_on_id: str
    dependency_type: str = "blocks"


class ReorderRequest(BaseModel):
    items: list[dict]  # [{"id": "...", "status": "...", "sort_order": 0}, ...]
