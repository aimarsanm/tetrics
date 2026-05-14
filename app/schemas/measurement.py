"""
Schemas for Measurement entity.

A Measurement links a tool configuration to a specific metric value.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import Field

from app.schemas.base import BaseCreateSchema, BaseResponseSchema, BaseSchema, BaseUpdateSchema


class MeasurementBase(BaseSchema):
    """Shared fields for Measurement operations."""
    
    value: float = Field(
        ...,
        description="The measured value"
    )
    normalized_value: Optional[float] = Field(
        None,
        description="Normalized value for comparison purposes"
    )
    evaluator: Optional[str] = Field(
        None,
        description="Person or system that performed the evaluation",
        min_length=1,
        max_length=255
    )
    notes: Optional[str] = Field(
        None,
        description="Additional notes or context about this measurement"
    )


class MeasurementCreate(MeasurementBase, BaseCreateSchema):
    """Schema for creating a new measurement."""
    
    llm_tool_configuration_id: UUID = Field(
        ...,
        description="ID of the LLM tool configuration being measured"
    )
    metric_id: UUID = Field(
        ...,
        description="ID of the metric being measured"
    )


class MeasurementUpdate(BaseUpdateSchema):
    """Schema for updating an existing measurement."""
    
    value: Optional[float] = Field(
        None,
        description="The measured value"
    )
    normalized_value: Optional[float] = Field(
        None,
        description="Normalized value for comparison"
    )
    evaluator: Optional[str] = Field(
        None,
        description="Person or system that performed the evaluation",
        min_length=1,
        max_length=255
    )
    notes: Optional[str] = Field(
        None,
        description="Additional notes or context"
    )


class MeasurementRead(MeasurementBase, BaseResponseSchema):
    """Schema for reading a measurement."""
    
    llm_tool_configuration_id: UUID
    metric_id: UUID
    date: datetime
