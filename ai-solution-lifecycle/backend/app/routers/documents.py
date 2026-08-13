"""Document generation and CRUD router."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models.document import Document, DocumentVersion
from app.schemas.document import DocCreate, DocGenerateRequest, DocResponse, DocUpdate, DocVersionResponse
from app.services.document_generator import generate_document
from app.services.llm_provider import get_llm_provider, LLMProvider

router = APIRouter(tags=["documents"])


@router.get("/api/v1/projects/{project_id}/documents", response_model=list[DocResponse])
async def list_documents(
    project_id: str,
    doc_type: str | None = None,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    query = db.query(Document).filter(Document.project_id == project_id)
    if doc_type:
        query = query.filter(Document.doc_type == doc_type)
    return query.order_by(Document.created_at.desc()).all()


@router.post("/api/v1/projects/{project_id}/documents/generate", response_model=DocResponse)
async def generate_doc(
    project_id: str,
    request: DocGenerateRequest,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
    llm: LLMProvider = Depends(get_llm_provider),
):
    from app.models.project import Project

    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    title, content, llm_response = await generate_document(
        doc_type=request.doc_type,
        user_prompt=request.prompt,
        llm=llm,
        project_name=project.name,
    )

    doc = Document(
        project_id=project_id,
        doc_type=request.doc_type,
        title=request.title or title,
        content=content,
        generated_by_prompt=request.prompt,
        llm_model_used=llm_response.model,
        created_by=user["email"],
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


@router.post("/api/v1/projects/{project_id}/documents", response_model=DocResponse)
async def create_document(
    project_id: str,
    data: DocCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    doc = Document(
        project_id=project_id,
        doc_type=data.doc_type,
        title=data.title,
        content=data.content,
        status=data.status,
        created_by=user["email"],
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


@router.get("/api/v1/documents/{doc_id}", response_model=DocResponse)
async def get_document(doc_id: str, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.put("/api/v1/documents/{doc_id}", response_model=DocResponse)
async def update_document(
    doc_id: str,
    data: DocUpdate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Save version before updating
    if data.content and data.content != doc.content:
        version = DocumentVersion(
            document_id=doc.id,
            version=doc.version,
            content=doc.content,
            change_summary=data.change_summary,
            created_by=user["email"],
            created_at=datetime.now(timezone.utc),
        )
        db.add(version)
        doc.version += 1

    for field, value in data.model_dump(exclude_unset=True, exclude={"change_summary"}).items():
        setattr(doc, field, value)

    db.commit()
    db.refresh(doc)
    return doc


@router.get("/api/v1/documents/{doc_id}/versions", response_model=list[DocVersionResponse])
async def list_versions(doc_id: str, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    return (
        db.query(DocumentVersion)
        .filter(DocumentVersion.document_id == doc_id)
        .order_by(DocumentVersion.version.desc())
        .all()
    )
