"""
SQLAlchemy models for the Personal Task Manager and Software Measurement Framework.
"""
from .base import Base, BaseModel
from .user import User

# Import domain models
from .domain import (
    ScaleType, CollectionMethod, Direction,
    EvaluationProgram, Goal, EvaluationCriterion, Metric,
    LLMToolConfiguration, Measurement, AggregatedScore
)


# Export all models for easy import
__all__ = [
    "Base",
    "BaseModel",
    "User",
    # Enums
    "ScaleType",
    "CollectionMethod",
    "Direction",
    # Domain Model
    "EvaluationProgram",
    "Goal",
    "EvaluationCriterion",
    "Metric",
    "LLMToolConfiguration",
    "Measurement",
    "AggregatedScore",
]
