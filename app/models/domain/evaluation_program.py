"""
EvaluationProgram model - Root entity representing an evaluation program.
"""
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import String, DateTime, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.domain.constants import CASCADE_DELETE_ORPHAN

if TYPE_CHECKING:
    from app.models.domain.goal import Goal


class EvaluationProgram(BaseModel):
    """
    Root entity representing an evaluation program.
    Contains organizational context and time boundaries.
    """
    __tablename__ = "evaluation_programs"
    
    organization_context: Mapped[str] = mapped_column(String(255), nullable=False)
    time_period: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    responsible_team: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Ecosystem change management fields
    validity_period: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    reevaluation_triggers: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Relationships
    goals: Mapped[List["Goal"]] = relationship(
        "Goal", back_populates="evaluation_program", cascade=CASCADE_DELETE_ORPHAN
    )
