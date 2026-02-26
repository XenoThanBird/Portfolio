"""
RACI matrix entry model.
"""

from sqlalchemy import Column, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class RACIEntry(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "raci_entries"
    __table_args__ = (
        UniqueConstraint("project_id", "deliverable", "person_email", name="uq_raci_entry"),
    )

    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    deliverable = Column(String(200), nullable=False)  # Row label (task/deliverable)
    milestone_id = Column(String(36), ForeignKey("milestones.id"), nullable=True)
    person_name = Column(String(100), nullable=False)
    person_email = Column(String(100), nullable=False)
    role_type = Column(String(1), nullable=False)  # R, A, C, or I

    project = relationship("Project", back_populates="raci_entries")
