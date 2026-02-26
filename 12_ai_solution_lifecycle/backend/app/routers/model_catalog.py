"""AI model catalog and recommendation router."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models.model_catalog import AIModel, UseCaseMapping
from app.schemas.model_catalog import ModelCreate, ModelResponse, ModelUpdate, RecommendRequest, RecommendResponse
from app.services.llm_provider import get_llm_provider, LLMProvider
from app.services.model_recommender import recommend_models

router = APIRouter(prefix="/api/v1/models", tags=["model_catalog"])


@router.get("", response_model=list[ModelResponse])
async def list_models(db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    return db.query(AIModel).order_by(AIModel.name).all()


@router.post("", response_model=ModelResponse)
async def create_model(data: ModelCreate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    model = AIModel(**data.model_dump())
    db.add(model)
    db.commit()
    db.refresh(model)
    return model


@router.put("/{model_id}", response_model=ModelResponse)
async def update_model(
    model_id: str, data: ModelUpdate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)
):
    model = db.query(AIModel).filter(AIModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(model, field, value)
    db.commit()
    db.refresh(model)
    return model


@router.post("/recommend", response_model=RecommendResponse)
async def recommend(
    request: RecommendRequest,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
    llm: LLMProvider = Depends(get_llm_provider),
):
    recommendations = await recommend_models(
        use_case_description=request.use_case_description,
        db=db,
        llm=llm,
        project_id=request.project_id,
    )

    # Save mappings if project_id provided
    if request.project_id:
        for rec in recommendations:
            if rec.get("model_id"):
                mapping = UseCaseMapping(
                    project_id=request.project_id,
                    use_case_description=request.use_case_description,
                    recommended_model_id=rec["model_id"],
                    confidence_score=rec["confidence"],
                    rationale=rec["rationale"],
                )
                db.add(mapping)
        db.commit()

    return RecommendResponse(recommendations=recommendations)
