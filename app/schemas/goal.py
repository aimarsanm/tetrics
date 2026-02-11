"""
Schemas for Goal entity.

A Goal represents a high-level measurement objective within an evaluation program.
"""
from typing import List, Optional
from uuid import UUID

from pydantic import Field

from app.schemas.base import BaseCreateSchema, BaseResponseSchema, BaseSchema, BaseUpdateSchema


class GoalBase(BaseSchema):
    """Shared fields for Goal operations."""
    
    purpose: str = Field(
        ...,
        description="The purpose of this goal",
        min_length=1,
        max_length=255
    )
    focus: str = Field(
        ...,
        description="The focus area of this goal",
        min_length=1,
        max_length=255
    )
    viewpoint: str = Field(
        ...,
        description="The viewpoint from which this goal is evaluated",
        min_length=1,
        max_length=255
    )
    context: Optional[str] = Field(
        None,
        description="Additional context in Markdown format"
    )


class GoalCreate(GoalBase, BaseCreateSchema):
    """Schema for creating a new goal."""
    
    evaluation_program_id: UUID = Field(
        ...,
        description="ID of the parent evaluation program"
    )


class GoalUpdate(BaseUpdateSchema):
    """Schema for updating an existing goal."""
    
    purpose: Optional[str] = Field(
        None,
        description="The purpose of this goal",
        min_length=1,
        max_length=255
    )
    focus: Optional[str] = Field(
        None,
        description="The focus area of this goal",
        min_length=1,
        max_length=255
    )
    viewpoint: Optional[str] = Field(
        None,
        description="The viewpoint from which this goal is evaluated",
        min_length=1,
        max_length=255
    )
    context: Optional[str] = Field(
        None,
        description="Additional context in Markdown format"
    )


class GoalRead(GoalBase, BaseResponseSchema):
    """Schema for reading a goal with related entities."""
    
    evaluation_program_id: UUID
    evaluation_criteria: Optional[List["EvaluationCriterionRead"]] = Field(
        default=None,
        description="Evaluation criteria associated with this goal"
    )


# Import at the end to avoid circular imports
from app.schemas.evaluation_criterion import EvaluationCriterionRead  # noqa: E402
GoalRead.model_rebuild()
