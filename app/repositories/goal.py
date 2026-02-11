"""
Repository for Goal entity.
"""
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.domain import Goal
from app.repositories.base_repository import BaseRepository
from app.schemas.goal import GoalCreate, GoalUpdate


class GoalRepository(BaseRepository[Goal]):
    """Repository for managing Goal entities."""
    
    def __init__(self, db: Session):
        """Initialize the repository."""
        super().__init__(Goal, db)
    
    def create(self, schema: GoalCreate) -> Goal:
        """
        Create a new goal.
        
        Args:
            schema: Goal creation data
            
        Returns:
            Created goal
        """
        db_obj = Goal(**schema.model_dump())
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    def get_by_id(self, id: UUID) -> Optional[Goal]:
        """
        Get goal by ID.
        
        Args:
            id: Goal UUID
            
        Returns:
            Goal if found, None otherwise
        """
        return self.get(id)
    
    def get_all(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Goal]:
        """
        Get all goals with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of goals
        """
        return self.get_multi(skip=skip, limit=limit)
    
    def get_by_evaluation_program(
        self,
        evaluation_program_id: UUID
    ) -> List[Goal]:
        """
        Get goals by evaluation program ID.
        
        Args:
            evaluation_program_id: Evaluation program UUID
            
        Returns:
            List of goals for the program
        """
        return self.db.query(self.model).filter(
            self.model.evaluation_program_id == evaluation_program_id,
            self.model.is_active == True
        ).all()
    
    def update(
        self,
        id: UUID,
        schema: GoalUpdate
    ) -> Optional[Goal]:
        """
        Update a goal.
        
        Args:
            id: Goal UUID
            schema: Update data
            
        Returns:
            Updated goal if found, None otherwise
        """
        db_obj = self.get(id)
        if db_obj:
            return super().update(db_obj, schema)
        return None
    
    def delete(self, id: UUID) -> bool:
        """
        Delete a goal.
        
        Args:
            id: Goal UUID
            
        Returns:
            True if deleted, False otherwise
        """
        return super().delete(id) is not None
