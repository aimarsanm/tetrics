"""
Schemas for Evaluation Criterion entity.

An Evaluation Criterion decomposes a goal into measurable dimensions.
"""
from typing import List, Optional
from uuid import UUID

from pydantic import Field

from app.schemas.base import BaseCreateSchema, BaseResponseSchema, BaseSchema, BaseUpdateSchema


class EvaluationCriterionBase(BaseSchema):
    """Shared fields for Evaluation Criterion operations."""
    
    dimension: str = Field(
        ...,
        description="The dimension being evaluated (e.g., 'Accuracy', 'Performance')",
        min_length=1,
        max_length=255
    )
    description: str = Field(
        ...,
        description="Detailed description of what this criterion measures",
        min_length=1
    )
    weight: float = Field(
        default=1.0,
        description="Weight of this criterion in the overall evaluation (can be negative for penalties)"
    )
    aggregation_strategy: str = Field(
        default="weighted_average",
        description="Strategy used to aggregate metric measurements into a criterion score"
    )


class EvaluationCriterionCreate(EvaluationCriterionBase, BaseCreateSchema):
    """Schema for creating a new evaluation criterion."""
    
    goal_id: UUID = Field(
        ...,
        description="ID of the parent goal"
    )


class EvaluationCriterionUpdate(BaseUpdateSchema):
    """Schema for updating an existing evaluation criterion."""
    
    dimension: Optional[str] = Field(
        None,
        description="The dimension being evaluated",
        min_length=1,
        max_length=255
    )
    description: Optional[str] = Field(
        None,
        description="Detailed description of what this criterion measures",
        min_length=1
    )
    weight: Optional[float] = Field(
        None,
        description="Weight of this criterion in the overall evaluation (can be negative for penalties)"
    )
    aggregation_strategy: Optional[str] = Field(
        None,
        description="Strategy used to aggregate metric measurements"
    )


class EvaluationCriterionRead(EvaluationCriterionBase, BaseResponseSchema):
    """Schema for reading an evaluation criterion with related entities."""
    
    goal_id: UUID
    metrics: Optional[List["MetricRead"]] = Field(
        default=None,
        description="Metrics associated with this criterion"
    )


# Import at the end to avoid circular imports
from app.schemas.metric import MetricRead  # noqa: E402
EvaluationCriterionRead.model_rebuild()
