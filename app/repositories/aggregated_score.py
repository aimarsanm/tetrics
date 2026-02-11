"""
Repository for Aggregated Score entity.
"""
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.domain import AggregatedScore
from app.repositories.base_repository import BaseRepository
from app.schemas.aggregated_score import (
    AggregatedScoreCreate,
    AggregatedScoreUpdate,
)


class AggregatedScoreRepository(BaseRepository[AggregatedScore]):
    """Repository for managing Aggregated Score entities."""
    
    def __init__(self, db: Session):
        """Initialize the repository."""
        super().__init__(AggregatedScore, db)
    
    def create(self, schema: AggregatedScoreCreate) -> AggregatedScore:
        """
        Create a new aggregated score.
        
        Args:
            schema: Aggregated score creation data
            
        Returns:
            Created aggregated score
        """
        db_obj = AggregatedScore(**schema.model_dump())
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    def get_by_id(self, id: UUID) -> Optional[AggregatedScore]:
        """
        Get aggregated score by ID.
        
        Args:
            id: Aggregated score UUID
            
        Returns:
            Aggregated score if found, None otherwise
        """
        return self.get(id)
    
    def get_all(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[AggregatedScore]:
        """
        Get all aggregated scores with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of aggregated scores
        """
        return self.get_multi(skip=skip, limit=limit)
    
    def get_by_criterion(self, criterion_id: UUID) -> List[AggregatedScore]:
        """
        Get aggregated scores by criterion ID.
        
        Args:
            criterion_id: Criterion UUID
            
        Returns:
            List of aggregated scores for the criterion
        """
        return self.db.query(self.model).filter(
            self.model.criterion_id == criterion_id,
            self.model.is_active == True
        ).all()
    
    def get_by_tool_configuration(
        self,
        tool_config_id: UUID
    ) -> List[AggregatedScore]:
        """
        Get aggregated scores by tool configuration ID.
        
        Args:
            tool_config_id: Tool configuration UUID
            
        Returns:
            List of aggregated scores for the configuration
        """
        return self.db.query(self.model).filter(
            self.model.tool_config_id == tool_config_id,
            self.model.is_active == True
        ).all()
    
    def get_by_criterion_and_tool(
        self,
        criterion_id: UUID,
        tool_config_id: UUID
    ) -> List[AggregatedScore]:
        """
        Get aggregated scores by criterion and tool configuration ID.
        
        Returns scores ordered by timestamp (most recent first).
        
        Args:
            criterion_id: Criterion UUID
            tool_config_id: Tool configuration UUID
            
        Returns:
            List of aggregated scores matching both criteria
        """
        return self.db.query(self.model).filter(
            self.model.criterion_id == criterion_id,
            self.model.tool_config_id == tool_config_id,
            self.model.is_active == True
        ).order_by(self.model.timestamp.desc()).all()
    
    def update(
        self,
        id: UUID,
        schema: AggregatedScoreUpdate
    ) -> Optional[AggregatedScore]:
        """
        Update an aggregated score.
        
        Args:
            id: Aggregated score UUID
            schema: Update data
            
        Returns:
            Updated aggregated score if found, None otherwise
        """
        db_obj = self.get(id)
        if db_obj:
            return super().update(db_obj, schema)
        return None
    
    def delete(self, id: UUID) -> bool:
        """
        Delete an aggregated score.
        
        Args:
            id: Aggregated score UUID
            
        Returns:
            True if deleted, False otherwise
        """
        return super().delete(id) is not None
