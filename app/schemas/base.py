"""
Base Pydantic schemas for API request/response validation.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_serializer


class BaseSchema(BaseModel):
    """Base schema with ORM mode enabled for SQLAlchemy integration."""
    
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        str_strip_whitespace=True,
    )


class BaseResponseSchema(BaseSchema):
    """Base response schema with common audit fields."""
    
    id: UUID
    created_at: datetime
    updated_at: datetime
    is_active: bool
    
    @field_serializer('id')
    def serialize_uuid(self, value: UUID, _info) -> str:
        """Convert UUID to string for JSON serialization."""
        return str(value)


class BaseCreateSchema(BaseSchema):
    """Base schema for create operations."""
    pass


class BaseUpdateSchema(BaseSchema):
    """Base schema for update operations."""
    pass


class PaginationParams(BaseSchema):
    """Pagination parameters."""
    skip: int = Field(default=0, ge=0, description="Number of items to skip")
    limit: int = Field(default=100, ge=1, le=1000, description="Number of items to return")


class PaginatedResponse(BaseSchema):
    """Paginated response wrapper."""
    items: list = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    skip: int = Field(..., description="Number of items skipped")
    limit: int = Field(..., description="Number of items returned")
    has_next: bool = Field(..., description="Whether there are more items")


class MessageResponse(BaseSchema):
    """Generic message response."""
    message: str = Field(..., description="Response message")
    success: bool = Field(default=True, description="Operation success status")


class ErrorResponse(BaseSchema):
    """Error response schema."""
    error: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    details: Optional[dict] = Field(None, description="Additional error details")


class HealthResponse(BaseSchema):
    """Health check response."""
    status: str = Field(..., description="Health status")
    timestamp: datetime = Field(..., description="Check timestamp")
    version: str = Field(..., description="Application version")
    environment: str = Field(..., description="Environment name")
