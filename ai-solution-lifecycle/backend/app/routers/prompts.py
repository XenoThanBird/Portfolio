"""Prompt library CRUD, search, and execution router."""

import re
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models.prompt import PromptRun, PromptTemplate
from app.schemas.prompt import FeedbackRequest, PromptCreate, PromptResponse, PromptUpdate, RunRequest, RunResponse
from app.services.llm_provider import LLMProviderFactory

router = APIRouter(prefix="/api/v1/prompts", tags=["prompts"])


def extract_variables(template: str) -> list[str]:
    """Extract {{variable}} placeholders from template."""
    return list(set(re.findall(r"\{\{(\w+)\}\}", template)))


@router.get("", response_model=list[PromptResponse])
async def list_prompts(
    project_id: str | None = None,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    query = db.query(PromptTemplate)
    if project_id:
        query = query.filter(
            (PromptTemplate.project_id == project_id) | (PromptTemplate.project_id.is_(None))
        )
    return query.order_by(PromptTemplate.usage_count.desc()).all()


@router.get("/search")
async def search_prompts(
    q: str | None = None,
    category: str | None = None,
    sort_by: str = Query("usage_count", pattern="^(created_at|usage_count|success_rate)$"),
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    query = db.query(PromptTemplate)
    if q:
        query = query.filter(
            PromptTemplate.name.ilike(f"%{q}%") | PromptTemplate.description.ilike(f"%{q}%")
        )
    if category:
        query = query.filter(PromptTemplate.category == category)

    if sort_by == "usage_count":
        query = query.order_by(PromptTemplate.usage_count.desc())
    elif sort_by == "success_rate":
        query = query.order_by(PromptTemplate.success_rate.desc())
    else:
        query = query.order_by(PromptTemplate.created_at.desc())

    prompts = query.limit(limit).all()
    categories = (
        db.query(PromptTemplate.category, db.query(PromptTemplate).filter(PromptTemplate.category == PromptTemplate.category).count())
        .group_by(PromptTemplate.category)
        .all()
    ) if False else []  # Simplified for demo

    return {"prompts": prompts, "total": len(prompts), "categories": categories}


@router.post("", response_model=PromptResponse)
async def create_prompt(
    data: PromptCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    variables = data.variables or extract_variables(data.template)
    prompt = PromptTemplate(
        project_id=data.project_id,
        name=data.name,
        description=data.description,
        template=data.template,
        variables=variables,
        category=data.category,
        tags=data.tags,
        created_by=user["email"],
    )
    db.add(prompt)
    db.commit()
    db.refresh(prompt)
    return prompt


@router.get("/{prompt_id}", response_model=PromptResponse)
async def get_prompt(prompt_id: str, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    prompt = db.query(PromptTemplate).filter(PromptTemplate.id == prompt_id).first()
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompt


@router.put("/{prompt_id}", response_model=PromptResponse)
async def update_prompt(
    prompt_id: str,
    data: PromptUpdate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    prompt = db.query(PromptTemplate).filter(PromptTemplate.id == prompt_id).first()
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(prompt, field, value)
    if data.template:
        prompt.variables = extract_variables(data.template)
    db.commit()
    db.refresh(prompt)
    return prompt


@router.delete("/{prompt_id}")
async def delete_prompt(prompt_id: str, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    prompt = db.query(PromptTemplate).filter(PromptTemplate.id == prompt_id).first()
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    db.delete(prompt)
    db.commit()
    return {"status": "deleted"}


@router.post("/{prompt_id}/run", response_model=RunResponse)
async def run_prompt(
    prompt_id: str,
    request: RunRequest,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    prompt = db.query(PromptTemplate).filter(PromptTemplate.id == prompt_id).first()
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")

    # Substitute variables
    filled = prompt.template
    for var, value in request.inputs.items():
        filled = filled.replace(f"{{{{{var}}}}}", value)

    # Call LLM
    llm = LLMProviderFactory.create(request.model if request.model != "mock" else None)
    response = await llm.generate(prompt=filled)

    # Record run
    run = PromptRun(
        prompt_id=prompt_id,
        model=response.model,
        inputs=request.inputs,
        output=response.content,
        latency_ms=response.latency_ms,
        input_tokens=response.input_tokens,
        output_tokens=response.output_tokens,
        cost=response.cost,
        run_by=user["email"],
        run_at=datetime.now(timezone.utc),
    )
    db.add(run)

    # Update prompt metrics
    prompt.usage_count += 1
    prev_avg = prompt.avg_latency_ms or 0
    prompt.avg_latency_ms = (prev_avg * (prompt.usage_count - 1) + response.latency_ms) / prompt.usage_count

    db.commit()
    db.refresh(run)

    return RunResponse(
        run_id=run.id,
        output=response.content,
        metrics={
            "latency_ms": response.latency_ms,
            "tokens": {"input": response.input_tokens, "output": response.output_tokens},
            "cost": response.cost,
        },
    )


@router.post("/runs/{run_id}/feedback")
async def submit_feedback(
    run_id: str,
    request: FeedbackRequest,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    run = db.query(PromptRun).filter(PromptRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    run.user_rating = request.rating
    run.feedback_text = request.feedback_text
    db.commit()
    return {"status": "feedback recorded"}
