"""
Milestone and MilestoneDependency models for development tracking.
"""

from sqlalchemy import Column, Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Milestone(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "milestones"

    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(String(20), default="backlog")  # backlog, in_progress, review, done
    priority = Column(String(10), default="medium")  # low, medium, high, critical
    owner_email = Column(String(100))
    start_date = Column(Date, nullable=True)
    due_date = Column(Date, nullable=True)
    completed_date = Column(Date, nullable=True)
    sort_order = Column(Integer, default=0)

    project = relationship("Project", back_populates="milestones")
    dependencies = relationship(
        "MilestoneDependency",
        foreign_keys="MilestoneDependency.milestone_id",
        back_populates="milestone",
        cascade="all, delete-orphan",
    )


class MilestoneDependency(UUIDMixin, Base):
    __tablename__ = "milestone_dependencies"

    milestone_id = Column(String(36), ForeignKey("milestones.id"), nullable=False)
    depends_on_id = Column(String(36), ForeignKey("milestones.id"), nullable=False)
    dependency_type = Column(String(20), default="blocks")  # blocks, requires, related

    milestone = relationship("Milestone", foreign_keys=[milestone_id], back_populates="dependencies")
    depends_on = relationship("Milestone", foreign_keys=[depends_on_id])
