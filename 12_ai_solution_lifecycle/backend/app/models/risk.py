"""
Risk register and change request models.
"""

from sqlalchemy import Column, Float, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

PROBABILITY_VALUES = {"Very Low": 0.1, "Low": 0.3, "Medium": 0.5, "High": 0.7, "Very High": 0.9}
IMPACT_VALUES = {"Minimal": 1, "Low": 2, "Medium": 3, "High": 4, "Critical": 5}


def calculate_risk_score(probability: str, impact: str) -> float:
    """Calculate risk score: probability_value * impact_value * 20."""
    prob_val = PROBABILITY_VALUES.get(probability, 0.5)
    impact_val = IMPACT_VALUES.get(impact, 3)
    return prob_val * impact_val * 20


def classify_risk(score: float) -> str:
    """Classify risk based on score."""
    if score >= 40:
        return "Critical"
    if score >= 30:
        return "High"
    if score >= 20:
        return "Medium"
    if score >= 10:
        return "Low"
    return "Minimal"


class Risk(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "risks"

    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(30))  # technical, business, regulatory, operational
    probability = Column(String(10), nullable=False)  # Very Low, Low, Medium, High, Very High
    impact = Column(String(10), nullable=False)  # Minimal, Low, Medium, High, Critical
    risk_score = Column(Float)  # Auto-calculated
    classification = Column(String(20))  # Critical, High, Medium, Low, Minimal
    mitigation_plan = Column(Text)
    owner_email = Column(String(100))
    status = Column(String(20), default="open")  # open, mitigating, accepted, closed

    project = relationship("Project", back_populates="risks")

    def compute_score(self) -> None:
        """Compute risk_score and classification from probability and impact."""
        self.risk_score = round(calculate_risk_score(self.probability, self.impact), 1)
        self.classification = classify_risk(self.risk_score)


class ChangeRequest(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "change_requests"

    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    justification = Column(Text)
    impact_assessment = Column(Text)
    requested_by = Column(String(100))
    status = Column(String(20), default="submitted")  # submitted, under_review, approved, rejected, implemented
    priority = Column(String(10), default="medium")  # low, medium, high, critical
    reviewed_by = Column(String(100), nullable=True)
    review_notes = Column(Text, nullable=True)

    project = relationship("Project", back_populates="change_requests")
