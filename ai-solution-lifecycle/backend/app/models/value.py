"""
Value assessment and ROI calculation models.
"""

from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class ValueAssessment(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "value_assessments"

    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, unique=True)

    # Value components (0-100)
    financial_impact = Column(Float, default=0)
    operational_excellence = Column(Float, default=0)
    strategic_value = Column(Float, default=0)
    risk_mitigation = Column(Float, default=0)
    customer_impact = Column(Float, default=0)
    innovation_index = Column(Float, default=0)

    # Readiness scores (0-1)
    data_maturity = Column(Float, default=0)
    organizational_readiness = Column(Float, default=0)
    technical_capability = Column(Float, default=0)

    # Calculated scores
    base_score = Column(Float, default=0)
    readiness_multiplier = Column(Float, default=0)
    final_score = Column(Float, default=0)
    classification = Column(String(20))  # Transformational, Strategic, Tactical, Experimental, Monitor
    recommended_action = Column(String(100))
    investment_range = Column(String(50))

    project = relationship("Project", back_populates="value_assessment")
    roi_calculations = relationship("ROICalculation", back_populates="assessment", cascade="all, delete-orphan")


class ROICalculation(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "roi_calculations"

    assessment_id = Column(String(36), ForeignKey("value_assessments.id"), nullable=False)
    total_benefits = Column(Float)  # Millions
    total_costs = Column(Float)  # Millions
    time_horizon_years = Column(Integer, default=3)
    discount_rate = Column(Float, default=0.10)
    roi_percent = Column(Float)
    npv_millions = Column(Float)
    payback_years = Column(Float)
    risk_adjusted_roi = Column(Float)

    assessment = relationship("ValueAssessment", back_populates="roi_calculations")
