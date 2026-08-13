"""PromptTemplate and PromptRun models."""

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class PromptTemplate(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "prompt_templates"

    project_id = Column(String(36), ForeignKey("projects.id"), nullable=True)  # null = global template
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    template = Column(Text, nullable=False)  # Contains {{variable}} placeholders
    variables = Column(JSON)  # Extracted variable list
    category = Column(String(50), index=True)  # analysis, generation, classification, etc.
    tags = Column(JSON)  # String array
    version = Column(Integer, default=1)
    parent_id = Column(String(36), ForeignKey("prompt_templates.id"), nullable=True)

    # Metrics
    created_by = Column(String(100))
    usage_count = Column(Integer, default=0)
    avg_latency_ms = Column(Float, nullable=True)
    avg_tokens = Column(Integer, nullable=True)
    success_rate = Column(Float, nullable=True)
    cost_per_run = Column(Float, nullable=True)

    runs = relationship("PromptRun", back_populates="prompt", cascade="all, delete-orphan")
    children = relationship("PromptTemplate", backref="parent", remote_side="PromptTemplate.id")


class PromptRun(UUIDMixin, Base):
    __tablename__ = "prompt_runs"

    prompt_id = Column(String(36), ForeignKey("prompt_templates.id"), nullable=False)
    model = Column(String(50))  # gpt-4, claude-3, mock
    inputs = Column(JSON)  # Variable values
    output = Column(Text)
    latency_ms = Column(Float)
    input_tokens = Column(Integer)
    output_tokens = Column(Integer)
    cost = Column(Float)
    user_rating = Column(Float, nullable=True)  # 1-5 stars
    feedback_text = Column(Text, nullable=True)
    run_by = Column(String(100))
    run_at = Column(DateTime)

    prompt = relationship("PromptTemplate", back_populates="runs")
