"""
Repository for Evaluation Program entity.
"""
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.domain import EvaluationProgram
from app.repositories.base_repository import BaseRepository
from app.schemas.evaluation_program import (
    EvaluationProgramCreate,
    EvaluationProgramUpdate,
)


class EvaluationProgramRepository(BaseRepository[EvaluationProgram]):
    """Repository for managing Evaluation Program entities."""
    
    def __init__(self, db: Session):
        """Initialize the repository."""
        super().__init__(EvaluationProgram, db)
    
    def create(self, schema: EvaluationProgramCreate) -> EvaluationProgram:
        """
        Create a new evaluation program.
        
        Args:
            schema: Evaluation program creation data
            
        Returns:
            Created evaluation program
        """
        db_obj = EvaluationProgram(**schema.model_dump())
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    def get_by_id(self, id: UUID) -> Optional[EvaluationProgram]:
        """
        Get evaluation program by ID.
        
        Args:
            id: Program UUID
            
        Returns:
            Evaluation program if found, None otherwise
        """
        return self.get(id)
    
    def get_all(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[EvaluationProgram]:
        """
        Get all evaluation programs with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of evaluation programs
        """
        return self.get_multi(skip=skip, limit=limit)
    
    def update(
        self,
        id: UUID,
        schema: EvaluationProgramUpdate
    ) -> Optional[EvaluationProgram]:
        """
        Update an evaluation program.
        
        Args:
            id: Program UUID
            schema: Update data
            
        Returns:
            Updated evaluation program if found, None otherwise
        """
        db_obj = self.get(id)
        if db_obj:
            return super().update(db_obj, schema)
        return None
    
    def delete(self, id: UUID) -> bool:
        """
        Delete an evaluation program.
        
        Args:
            id: Program UUID
            
        Returns:
            True if deleted, False otherwise
        """
        return super().delete(id) is not None
