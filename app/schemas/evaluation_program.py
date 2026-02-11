"""
Schemas for Evaluation Program entity.

An Evaluation Program represents the root entity containing organizational
context and time boundaries for a measurement program.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import Field

from app.schemas.base import BaseCreateSchema, BaseResponseSchema, BaseSchema, BaseUpdateSchema


class EvaluationProgramBase(BaseSchema):
    """Shared fields for Evaluation Program operations."""
    
    organization_context: str = Field(
        ...,
        description="Organizational context for the evaluation",
        min_length=1,
        max_length=255
    )
    time_period: datetime = Field(
        ...,
        description="Time period when the evaluation takes place"
    )
    responsible_team: str = Field(
        ...,
        description="Team responsible for conducting the evaluation",
        min_length=1,
        max_length=255
    )
    
    # Ecosystem change management fields
    validity_period: Optional[int] = Field(
        None,
        description="Duration in days for which the evaluation program is valid"
    )
    reevaluation_triggers: Optional[List[str]] = Field(
        None,
        description="Conditions that trigger reevaluation (e.g., 'major tool release', 'significant user behavior changes')"
    )


class EvaluationProgramCreate(EvaluationProgramBase, BaseCreateSchema):
    """Schema for creating a new evaluation program."""
    pass


class EvaluationProgramUpdate(BaseUpdateSchema):
    """Schema for updating an existing evaluation program."""
    
    organization_context: Optional[str] = Field(
        None,
        description="Organizational context for the evaluation",
        min_length=1,
        max_length=255
    )
    time_period: Optional[datetime] = Field(
        None,
        description="Time period when the evaluation takes place"
    )
    responsible_team: Optional[str] = Field(
        None,
        description="Team responsible for conducting the evaluation",
        min_length=1,
        max_length=255
    )
    
    # Ecosystem change management fields
    validity_period: Optional[int] = Field(
        None,
        description="Duration in days for which the evaluation program is valid"
    )
    reevaluation_triggers: Optional[List[str]] = Field(
        None,
        description="Conditions that trigger reevaluation"
    )


class EvaluationProgramRead(EvaluationProgramBase, BaseResponseSchema):
    """Schema for reading an evaluation program with related entities."""
    
    goals: Optional[List["GoalRead"]] = Field(
        default=None,
        description="Goals associated with this evaluation program"
    )


# Import at the end to avoid circular imports
from app.schemas.goal import GoalRead  # noqa: E402
EvaluationProgramRead.model_rebuild()
