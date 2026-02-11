"""
Schemas for LLM Tool Configuration entity.

An LLM Tool Configuration represents a specific setup of an LLM tool
that can be evaluated across multiple metrics.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import Field

from app.schemas.base import BaseCreateSchema, BaseResponseSchema, BaseSchema, BaseUpdateSchema


class LLMToolConfigurationBase(BaseSchema):
    """Shared fields for LLM Tool Configuration operations."""
    
    tool_name: str = Field(
        ...,
        description="Name of the LLM tool",
        min_length=1,
        max_length=255
    )
    model_version: str = Field(
        ...,
        description="Version of the model being used",
        min_length=1,
        max_length=255
    )
    prompt_strategy: str = Field(
        ...,
        description="Description of the prompt strategy employed",
        min_length=1
    )
    parameters: Dict[str, Any] = Field(
        ...,
        description="Configuration parameters for the tool"
    )
    
    # Ecosystem context fields
    toolchain: Optional[str] = Field(
        None,
        description="Specific tools and technologies used (e.g., 'Node.js, npm, Jest')",
        max_length=500
    )
    ide: Optional[str] = Field(
        None,
        description="Integrated development environment used (e.g., 'VS Code')",
        max_length=255
    )
    ide_plugins: Optional[List[str]] = Field(
        None,
        description="IDE plugins or extensions used (e.g., ['GitHub Copilot', 'ESLint'])"
    )
    
    # Prompt strategy enhancements
    conversation_history: Optional[List[Dict[str, str]]] = Field(
        None,
        description="Conversation history with role/content pairs for multi-turn dialogues"
    )
    skills_used: Optional[List[str]] = Field(
        None,
        description="Skills or techniques used in prompting (e.g., ['open-ended questioning', 'contextual framing'])"
    )


class LLMToolConfigurationCreate(LLMToolConfigurationBase, BaseCreateSchema):
    """Schema for creating a new LLM tool configuration."""
    # Allow client to supply a timestamp instead of always using server default
    # This supports editing historical configurations or importing past data.
    timestamp: Optional[datetime] = Field(
        None,
        description="Explicit timestamp for the configuration (defaults to server time if omitted)"
    )


class LLMToolConfigurationUpdate(BaseUpdateSchema):
    """Schema for updating an existing LLM tool configuration."""
    
    tool_name: Optional[str] = Field(
        None,
        description="Name of the LLM tool",
        min_length=1,
        max_length=255
    )
    model_version: Optional[str] = Field(
        None,
        description="Version of the model being used",
        min_length=1,
        max_length=255
    )
    prompt_strategy: Optional[str] = Field(
        None,
        description="Description of the prompt strategy employed",
        min_length=1
    )
    parameters: Optional[Dict[str, Any]] = Field(
        None,
        description="Configuration parameters for the tool"
    )
    timestamp: Optional[datetime] = Field(
        None,
        description="Timestamp of the configuration; allows manual adjustment when re-dating entries"
    )
    
    # Ecosystem context fields
    toolchain: Optional[str] = Field(
        None,
        description="Specific tools and technologies used",
        max_length=500
    )
    ide: Optional[str] = Field(
        None,
        description="Integrated development environment used",
        max_length=255
    )
    ide_plugins: Optional[List[str]] = Field(
        None,
        description="IDE plugins or extensions used"
    )
    
    # Prompt strategy enhancements
    conversation_history: Optional[List[Dict[str, str]]] = Field(
        None,
        description="Conversation history with role/content pairs"
    )
    skills_used: Optional[List[str]] = Field(
        None,
        description="Skills or techniques used in prompting"
    )


class LLMToolConfigurationRead(LLMToolConfigurationBase, BaseResponseSchema):
    """Schema for reading an LLM tool configuration with related entities."""
    
    timestamp: datetime
    total_score: Optional[float] = Field(
        default=None,
        description="Total aggregated score across all evaluation criteria"
    )
    total_score_updated_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when the total score was last updated"
    )
    measurements: Optional[List["MeasurementRead"]] = Field(
        default=None,
        description="Measurements associated with this configuration"
    )


# Import at the end to avoid circular imports
from app.schemas.measurement import MeasurementRead  # noqa: E402
LLMToolConfigurationRead.model_rebuild()
