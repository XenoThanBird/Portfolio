"""
Document and DocumentVersion models for auto-generated business documents.
"""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Document(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "documents"

    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    doc_type = Column(String(30), nullable=False)  # brd, trd, functional, design_schematic, user_schematic
    title = Column(String(200), nullable=False)
    content = Column(Text)  # Markdown content
    version = Column(Integer, default=1)
    status = Column(String(20), default="draft")  # draft, review, approved, archived
    generated_by_prompt = Column(Text)  # The NL prompt that generated it
    llm_model_used = Column(String(50))
    created_by = Column(String(100))

    project = relationship("Project", back_populates="documents")
    versions = relationship("DocumentVersion", back_populates="document", cascade="all, delete-orphan")


class DocumentVersion(UUIDMixin, Base):
    __tablename__ = "document_versions"

    document_id = Column(String(36), ForeignKey("documents.id"), nullable=False)
    version = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    change_summary = Column(Text)
    created_by = Column(String(100))
    created_at = Column(DateTime)

    document = relationship("Document", back_populates="versions")
