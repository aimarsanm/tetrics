"""
Repository for Evaluation Criterion entity.
"""
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.domain import AggregationStrategy, EvaluationCriterion
from app.repositories.base_repository import BaseRepository
from app.schemas.evaluation_criterion import (
    EvaluationCriterionCreate,
    EvaluationCriterionUpdate,
)


class EvaluationCriterionRepository(BaseRepository[EvaluationCriterion]):
    """Repository for managing Evaluation Criterion entities."""
    
    def __init__(self, db: Session):
        """Initialize the repository."""
        super().__init__(EvaluationCriterion, db)
    
    def create(self, schema: EvaluationCriterionCreate) -> EvaluationCriterion:
        """
        Create a new evaluation criterion.
        
        Args:
            schema: Evaluation criterion creation data
            
        Returns:
            Created evaluation criterion
        """
        data = schema.model_dump()
        
        # Normalize aggregation_strategy to enum
        if 'aggregation_strategy' in data and isinstance(data['aggregation_strategy'], str):
            try:
                data['aggregation_strategy'] = AggregationStrategy(data['aggregation_strategy'])
            except ValueError:
                raise ValueError(f"Invalid aggregation strategy: {data['aggregation_strategy']}")
        
        db_obj = EvaluationCriterion(**data)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    def get_by_id(self, id: UUID) -> Optional[EvaluationCriterion]:
        """
        Get evaluation criterion by ID.
        
        Args:
            id: Criterion UUID
            
        Returns:
            Evaluation criterion if found, None otherwise
        """
        return self.get(id)
    
    def get_all(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[EvaluationCriterion]:
        """
        Get all evaluation criteria with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of evaluation criteria
        """
        return self.get_multi(skip=skip, limit=limit)
    
    def get_by_goal(self, goal_id: UUID) -> List[EvaluationCriterion]:
        """
        Get evaluation criteria by goal ID.
        
        Args:
            goal_id: Goal UUID
            
        Returns:
            List of evaluation criteria for the goal
        """
        return self.db.query(self.model).filter(
            self.model.goal_id == goal_id,
            self.model.is_active == True
        ).all()
    
    def update(
        self,
        id: UUID,
        schema: EvaluationCriterionUpdate
    ) -> Optional[EvaluationCriterion]:
        """
        Update an evaluation criterion.
        
        Args:
            id: Criterion UUID
            schema: Update data
            
        Returns:
            Updated evaluation criterion if found, None otherwise
        """
        db_obj = self.get(id)
        if not db_obj:
            return None
        
        update_data = schema.model_dump(exclude_unset=True)
        
        # Normalize aggregation_strategy to enum if provided
        if 'aggregation_strategy' in update_data and update_data['aggregation_strategy'] is not None:
            if isinstance(update_data['aggregation_strategy'], str):
                try:
                    update_data['aggregation_strategy'] = AggregationStrategy(
                        update_data['aggregation_strategy']
                    )
                except ValueError:
                    raise ValueError(
                        f"Invalid aggregation strategy: {update_data['aggregation_strategy']}"
                    )
        
        return super().update(db_obj, update_data)
    
    def delete(self, id: UUID) -> bool:
        """
        Delete an evaluation criterion.
        
        Args:
            id: Criterion UUID
            
        Returns:
            True if deleted, False otherwise
        """
        return super().delete(id) is not None
