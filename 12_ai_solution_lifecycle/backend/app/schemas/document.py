"""Document generation and CRUD schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class DocGenerateRequest(BaseModel):
    doc_type: str = Field(..., pattern="^(brd|trd|functional|design_schematic|user_schematic)$")
    prompt: str = Field(..., min_length=10, description="Natural language description of what to generate")
    title: Optional[str] = None


class DocCreate(BaseModel):
    doc_type: str
    title: str
    content: str
    status: str = "draft"


class DocUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    status: Optional[str] = None
    change_summary: Optional[str] = None


class DocResponse(BaseModel):
    id: str
    project_id: str
    doc_type: str
    title: str
    content: Optional[str]
    version: int
    status: str
    generated_by_prompt: Optional[str]
    llm_model_used: Optional[str]
    created_by: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


class DocVersionResponse(BaseModel):
    id: str
    document_id: str
    version: int
    content: str
    change_summary: Optional[str]
    created_by: Optional[str]
    created_at: Optional[datetime]

    model_config = {"from_attributes": True}
