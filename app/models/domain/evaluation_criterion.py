"""
EvaluationCriterion model - Criteria that decompose a goal into measurable dimensions.
"""
from typing import List, TYPE_CHECKING

from sqlalchemy import String, Text, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.domain.constants import CASCADE_DELETE_ORPHAN
from app.models.domain.enums import AggregationStrategy

if TYPE_CHECKING:
    from app.models.domain.goal import Goal
    from app.models.domain.metric import Metric


class EvaluationCriterion(BaseModel):
    """
    Criteria that decompose a goal into measurable dimensions.
    """
    __tablename__ = "evaluation_criteria"
    
    dimension: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    weight: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    aggregation_strategy: Mapped[AggregationStrategy] = mapped_column(
        String(50), nullable=False, default=AggregationStrategy.WEIGHTED_AVERAGE
    )
    
    # Foreign key
    goal_id: Mapped[str] = mapped_column(
        PostgresUUID(as_uuid=True), ForeignKey("goals.id"), nullable=False
    )
    
    # Relationships
    goal: Mapped["Goal"] = relationship(
        "Goal", back_populates="evaluation_criteria"
    )
    metrics: Mapped[List["Metric"]] = relationship(
        "Metric", back_populates="evaluation_criterion", cascade=CASCADE_DELETE_ORPHAN
    )
