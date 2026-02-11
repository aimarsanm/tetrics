"""
Repository for LLM Tool Configuration entity.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.domain import LLMToolConfiguration
from app.repositories.base_repository import BaseRepository
from app.schemas.llm_tool_configuration import (
    LLMToolConfigurationCreate,
    LLMToolConfigurationUpdate,
)


class LLMToolConfigurationRepository(BaseRepository[LLMToolConfiguration]):
    """Repository for managing LLM Tool Configuration entities."""
    
    def __init__(self, db: Session):
        """Initialize the repository."""
        super().__init__(LLMToolConfiguration, db)
    
    def create(self, schema: LLMToolConfigurationCreate) -> LLMToolConfiguration:
        """
        Create a new LLM tool configuration.
        
        Args:
            schema: LLM tool configuration creation data
            
        Returns:
            Created LLM tool configuration
        """
        db_obj = LLMToolConfiguration(**schema.model_dump())
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    def get_by_id(self, id: UUID) -> Optional[LLMToolConfiguration]:
        """
        Get LLM tool configuration by ID.
        
        Args:
            id: Configuration UUID
            
        Returns:
            LLM tool configuration if found, None otherwise
        """
        return self.get(id)
    
    def get_all(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[LLMToolConfiguration]:
        """
        Get all LLM tool configurations with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of LLM tool configurations
        """
        return self.get_multi(skip=skip, limit=limit)
    
    def update(
        self,
        id: UUID,
        schema: LLMToolConfigurationUpdate
    ) -> Optional[LLMToolConfiguration]:
        """
        Update an LLM tool configuration.
        
        Args:
            id: Configuration UUID
            schema: Update data
            
        Returns:
            Updated LLM tool configuration if found, None otherwise
        """
        db_obj = self.get(id)
        if db_obj:
            return super().update(db_obj, schema)
        return None
    
    def delete(self, id: UUID) -> bool:
        """
        Delete an LLM tool configuration.
        
        Args:
            id: Configuration UUID
            
        Returns:
            True if deleted, False otherwise
        """
        return super().delete(id) is not None
    
    def update_total_score(
        self,
        id: UUID,
        total_score: float
    ) -> Optional[LLMToolConfiguration]:
        """
        Update the total aggregated score for an LLM tool configuration.
        
        This method updates the total_score and total_score_updated_at fields
        without triggering a full model update.
        
        Args:
            id: Configuration UUID
            total_score: New total score value
            
        Returns:
            Updated LLM tool configuration if found, None otherwise
        """
        db_obj = self.get(id)
        if db_obj:
            db_obj.total_score = total_score
            db_obj.total_score_updated_at = datetime.now()
            self.db.commit()
            self.db.refresh(db_obj)
        return db_obj
