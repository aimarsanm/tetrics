"""
Schemas for Aggregated Score entity.

An Aggregated Score represents the calculated score for a criterion
based on multiple metric measurements.
"""
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import Field

from app.schemas.base import BaseCreateSchema, BaseResponseSchema, BaseSchema, BaseUpdateSchema


class AggregatedScoreBase(BaseSchema):
    """Shared fields for Aggregated Score operations."""
    
    criterion_id: UUID = Field(
        ...,
        description="ID of the evaluation criterion"
    )
    tool_config_id: UUID = Field(
        ...,
        description="ID of the LLM tool configuration"
    )
    score: float = Field(
        ...,
        description="The aggregated score value"
    )
    component_metrics: Dict[str, Any] = Field(
        ...,
        description="Breakdown of how individual metrics contributed to the score"
    )


class AggregatedScoreCreate(AggregatedScoreBase, BaseCreateSchema):
    """Schema for creating a new aggregated score."""
    pass


class AggregatedScoreUpdate(BaseUpdateSchema):
    """Schema for updating an existing aggregated score."""
    
    score: Optional[float] = Field(
        None,
        description="The aggregated score value"
    )
    component_metrics: Optional[Dict[str, Any]] = Field(
        None,
        description="Breakdown of component metrics"
    )


class AggregatedScoreRead(AggregatedScoreBase, BaseResponseSchema):
    """Schema for reading an aggregated score."""
    
    timestamp: datetime
