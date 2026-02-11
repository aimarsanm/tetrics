"""
Goal model - High-level measurement goal within an evaluation program.
"""
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.domain.constants import CASCADE_DELETE_ORPHAN

if TYPE_CHECKING:
    from app.models.domain.evaluation_program import EvaluationProgram
    from app.models.domain.evaluation_criterion import EvaluationCriterion


class Goal(BaseModel):
    """
    High-level measurement goal within an evaluation program.
    """
    __tablename__ = "goals"
    
    purpose: Mapped[str] = mapped_column(String(255), nullable=False)
    focus: Mapped[str] = mapped_column(String(255), nullable=False)
    viewpoint: Mapped[str] = mapped_column(String(255), nullable=False)
    context: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Foreign key
    evaluation_program_id: Mapped[str] = mapped_column(
        PostgresUUID(as_uuid=True), ForeignKey("evaluation_programs.id"), nullable=False
    )
    
    # Relationships
    evaluation_program: Mapped["EvaluationProgram"] = relationship(
        "EvaluationProgram", back_populates="goals"
    )
    evaluation_criteria: Mapped[List["EvaluationCriterion"]] = relationship(
        "EvaluationCriterion", back_populates="goal", cascade=CASCADE_DELETE_ORPHAN
    )
