"""
AggregatedScore model - Aggregated scores calculated from multiple measurements.
"""
from datetime import datetime
from typing import List, TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, JSON, func
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.domain.evaluation_criterion import EvaluationCriterion
    from app.models.domain.llm_tool_configuration import LLMToolConfiguration
    from app.models.domain.measurement import Measurement


class AggregatedScore(BaseModel):
    """
    Aggregated scores calculated from multiple measurements.
    """
    __tablename__ = "aggregated_scores"
    
    criterion_id: Mapped[str] = mapped_column(
        PostgresUUID(as_uuid=True), ForeignKey("evaluation_criteria.id"), nullable=False
    )
    tool_config_id: Mapped[str] = mapped_column(
        PostgresUUID(as_uuid=True), ForeignKey("llm_tool_configurations.id"), nullable=False
    )
    score: Mapped[float] = mapped_column(Float, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
    component_metrics: Mapped[dict] = mapped_column(JSON, nullable=False)
    
    # Relationships
    criterion: Mapped["EvaluationCriterion"] = relationship(
        "EvaluationCriterion"
    )
    tool_configuration: Mapped["LLMToolConfiguration"] = relationship(
        "LLMToolConfiguration"
    )
    measurements: Mapped[List["Measurement"]] = relationship(
        "Measurement", back_populates="aggregated_score"
    )
