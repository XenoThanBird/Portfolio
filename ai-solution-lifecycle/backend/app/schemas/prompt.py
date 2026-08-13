"""Prompt library schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PromptCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None
    template: str = Field(..., min_length=10)
    category: str
    tags: list[str] = []
    variables: Optional[list[str]] = None
    project_id: Optional[str] = None


class PromptUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    template: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[list[str]] = None


class PromptResponse(BaseModel):
    id: str
    project_id: Optional[str]
    name: str
    description: Optional[str]
    template: str
    variables: Optional[list[str]]
    category: Optional[str]
    tags: Optional[list[str]]
    version: int
    created_by: Optional[str]
    created_at: Optional[datetime]
    usage_count: int
    avg_latency_ms: Optional[float]
    success_rate: Optional[float]
    cost_per_run: Optional[float]

    model_config = {"from_attributes": True}


class RunRequest(BaseModel):
    inputs: dict[str, str]
    model: str = "mock"


class RunResponse(BaseModel):
    run_id: str
    output: str
    metrics: dict


class FeedbackRequest(BaseModel):
    rating: float = Field(..., ge=1, le=5)
    feedback_text: Optional[str] = None
