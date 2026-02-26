"""AI model catalog schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ModelCreate(BaseModel):
    name: str
    provider: Optional[str] = None
    model_type: Optional[str] = None
    description: Optional[str] = None
    capabilities: list[str] = []
    cost_per_1k_tokens: Optional[float] = None
    max_context_length: Optional[int] = None
    recommended_use_cases: list[str] = []
    strengths: list[str] = []
    limitations: list[str] = []


class ModelUpdate(BaseModel):
    name: Optional[str] = None
    provider: Optional[str] = None
    model_type: Optional[str] = None
    description: Optional[str] = None
    capabilities: Optional[list[str]] = None
    cost_per_1k_tokens: Optional[float] = None
    max_context_length: Optional[int] = None
    recommended_use_cases: Optional[list[str]] = None
    strengths: Optional[list[str]] = None
    limitations: Optional[list[str]] = None


class ModelResponse(BaseModel):
    id: str
    name: str
    provider: Optional[str]
    model_type: Optional[str]
    description: Optional[str]
    capabilities: Optional[list[str]]
    cost_per_1k_tokens: Optional[float]
    max_context_length: Optional[int]
    recommended_use_cases: Optional[list[str]]
    strengths: Optional[list[str]]
    limitations: Optional[list[str]]
    created_at: Optional[datetime]

    model_config = {"from_attributes": True}


class RecommendRequest(BaseModel):
    use_case_description: str
    project_id: Optional[str] = None


class RecommendResponse(BaseModel):
    recommendations: list[dict]  # [{model_id, model_name, confidence, rationale}]
