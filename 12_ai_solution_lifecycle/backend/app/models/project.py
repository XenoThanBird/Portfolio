"""
Project and ProjectMember models.
"""

from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Project(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "projects"

    name = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    status = Column(String(20), default="draft")  # draft, active, on_hold, completed, archived
    owner_email = Column(String(100))
    start_date = Column(Date, nullable=True)
    target_end_date = Column(Date, nullable=True)
    budget_millions = Column(Float, nullable=True)
    data_maturity_level = Column(Integer, default=1)  # 1-5

    members = relationship("ProjectMember", back_populates="project", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="project", cascade="all, delete-orphan")
    milestones = relationship("Milestone", back_populates="project", cascade="all, delete-orphan")
    raci_entries = relationship("RACIEntry", back_populates="project", cascade="all, delete-orphan")
    sla_definitions = relationship("SLADefinition", back_populates="project", cascade="all, delete-orphan")
    alert_rules = relationship("AlertRule", back_populates="project", cascade="all, delete-orphan")
    risks = relationship("Risk", back_populates="project", cascade="all, delete-orphan")
    change_requests = relationship("ChangeRequest", back_populates="project", cascade="all, delete-orphan")
    use_case_mappings = relationship("UseCaseMapping", back_populates="project", cascade="all, delete-orphan")
    value_assessment = relationship("ValueAssessment", back_populates="project", uselist=False, cascade="all, delete-orphan")


class ProjectMember(UUIDMixin, Base):
    __tablename__ = "project_members"

    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    role = Column(String(50))  # PM, Tech Lead, Analyst, Sponsor, etc.
    department = Column(String(100))

    project = relationship("Project", back_populates="members")
