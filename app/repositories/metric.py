"""
Repository for Metric entity.
"""
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.domain import Metric
from app.repositories.base_repository import BaseRepository
from app.schemas.metric import MetricCreate, MetricUpdate


class MetricRepository(BaseRepository[Metric]):
    """Repository for managing Metric entities."""
    
    def __init__(self, db: Session):
        """Initialize the repository."""
        super().__init__(Metric, db)
    
    def create(self, schema: MetricCreate) -> Metric:
        """
        Create a new metric.
        
        Args:
            schema: Metric creation data
            
        Returns:
            Created metric
        """
        db_obj = Metric(**schema.model_dump())
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    def get_by_id(self, id: UUID) -> Optional[Metric]:
        """
        Get metric by ID.
        
        Args:
            id: Metric UUID
            
        Returns:
            Metric if found, None otherwise
        """
        return self.get(id)
    
    def get_all(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Metric]:
        """
        Get all metrics with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of metrics
        """
        return self.get_multi(skip=skip, limit=limit)
    
    def get_by_evaluation_criterion(
        self,
        evaluation_criterion_id: UUID
    ) -> List[Metric]:
        """
        Get metrics by evaluation criterion ID.
        
        Args:
            evaluation_criterion_id: Evaluation criterion UUID
            
        Returns:
            List of metrics for the criterion
        """
        return self.db.query(self.model).filter(
            self.model.evaluation_criterion_id == evaluation_criterion_id,
            self.model.is_active == True
        ).all()
    
    def get_by_criterion(self, criterion_id: UUID) -> List[Metric]:
        """
        Get metrics by criterion ID (alias for get_by_evaluation_criterion).
        
        Args:
            criterion_id: Criterion UUID
            
        Returns:
            List of metrics for the criterion
        """
        return self.get_by_evaluation_criterion(criterion_id)
    
    def update(
        self,
        id: UUID,
        schema: MetricUpdate
    ) -> Optional[Metric]:
        """
        Update a metric.
        
        Args:
            id: Metric UUID
            schema: Update data
            
        Returns:
            Updated metric if found, None otherwise
        """
        db_obj = self.get(id)
        if db_obj:
            return super().update(db_obj, schema)
        return None
    
    def delete(self, id: UUID) -> bool:
        """
        Delete a metric.
        
        Args:
            id: Metric UUID
            
        Returns:
            True if deleted, False otherwise
        """
        return super().delete(id) is not None
