"""
LLMToolConfiguration model - Configuration for LLM tools.
"""
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import String, Text, DateTime, JSON, Float, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.domain.constants import CASCADE_DELETE_ORPHAN

if TYPE_CHECKING:
    from app.models.domain.measurement import Measurement


class LLMToolConfiguration(BaseModel):
    """
    Configuration for LLM tools that can be evaluated across multiple metrics.
    """
    __tablename__ = "llm_tool_configurations"
    
    tool_name: Mapped[str] = mapped_column(String(255), nullable=False)
    model_version: Mapped[str] = mapped_column(String(255), nullable=False)
    prompt_strategy: Mapped[str] = mapped_column(Text, nullable=False)
    parameters: Mapped[dict] = mapped_column(JSON, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
    total_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    total_score_updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Ecosystem context fields
    toolchain: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    ide: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    ide_plugins: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Prompt strategy enhancements
    conversation_history: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    skills_used: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Relationships
    measurements: Mapped[List["Measurement"]] = relationship(
        "Measurement", back_populates="llm_tool_configuration", cascade=CASCADE_DELETE_ORPHAN
    )
