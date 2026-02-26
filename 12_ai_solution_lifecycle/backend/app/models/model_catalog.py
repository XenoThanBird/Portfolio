"""
AI Model catalog and use case mapping models.
"""

from sqlalchemy import Column, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class AIModel(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "ai_models"

    name = Column(String(100), nullable=False)
    provider = Column(String(50))  # openai, anthropic, huggingface, local, aws, google
    model_type = Column(String(50))  # llm, embedding, vision, classification, regression, speech
    description = Column(Text)
    capabilities = Column(JSON)  # String array
    cost_per_1k_tokens = Column(Float, nullable=True)
    max_context_length = Column(Integer, nullable=True)
    recommended_use_cases = Column(JSON)  # String array
    strengths = Column(JSON)  # String array
    limitations = Column(JSON)  # String array

    use_case_mappings = relationship("UseCaseMapping", back_populates="model")


class UseCaseMapping(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "use_case_mappings"

    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    use_case_description = Column(Text, nullable=False)
    recommended_model_id = Column(String(36), ForeignKey("ai_models.id"), nullable=False)
    confidence_score = Column(Float)  # 0-1
    rationale = Column(Text)

    project = relationship("Project", back_populates="use_case_mappings")
    model = relationship("AIModel", back_populates="use_case_mappings")
