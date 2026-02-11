"""
Measurement model - Individual measurement values.
"""
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, Text, DateTime, Float, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.domain.llm_tool_configuration import LLMToolConfiguration
    from app.models.domain.metric import Metric
    from app.models.domain.aggregated_score import AggregatedScore


class Measurement(BaseModel):
    """
    Individual measurement values linking a tool configuration to a specific metric.
    """
    __tablename__ = "measurements"
    
    value: Mapped[float] = mapped_column(Float, nullable=False)
    normalized_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
    evaluator: Mapped[str] = mapped_column(String(255), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Foreign keys
    llm_tool_configuration_id: Mapped[str] = mapped_column(
        PostgresUUID(as_uuid=True), ForeignKey("llm_tool_configurations.id"), nullable=False
    )
    metric_id: Mapped[str] = mapped_column(
        PostgresUUID(as_uuid=True), ForeignKey("metrics.id"), nullable=False
    )
    aggregated_score_id: Mapped[Optional[str]] = mapped_column(
        PostgresUUID(as_uuid=True), ForeignKey("aggregated_scores.id"), nullable=True
    )
    
    # Relationships
    llm_tool_configuration: Mapped["LLMToolConfiguration"] = relationship(
        "LLMToolConfiguration", back_populates="measurements"
    )
    metric: Mapped["Metric"] = relationship(
        "Metric", back_populates="measurements"
    )
    aggregated_score: Mapped[Optional["AggregatedScore"]] = relationship(
        "AggregatedScore", back_populates="measurements"
    )
