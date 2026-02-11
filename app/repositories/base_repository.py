"""
Base repository class with common CRUD operations.
"""
from typing import Generic, List, Optional, Type, TypeVar
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.base import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    """
    Base repository providing common CRUD operations.
    
    This class implements the Repository pattern, providing a clean
    abstraction layer between the domain/business logic and data access.
    """
    
    def __init__(self, model: Type[ModelType], db: Session):
        """
        Initialize repository with model class and database session.
        
        Args:
            model: SQLAlchemy model class
            db: Database session
        """
        self.model = model
        self.db = db
    
    def get(self, id: UUID) -> Optional[ModelType]:
        """
        Get a single entity by ID.
        
        Args:
            id: Entity UUID
            
        Returns:
            Entity if found and active, None otherwise
        """
        return self.db.query(self.model).filter(
            self.model.id == id,
            self.model.is_active == True
        ).first()
    
    def get_multi(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """
        Get multiple entities with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of entities
        """
        return self.db.query(self.model).filter(
            self.model.is_active == True
        ).offset(skip).limit(limit).all()
    
    def create(self, obj_in: dict) -> ModelType:
        """
        Create a new entity.
        
        Args:
            obj_in: Dictionary of entity attributes
            
        Returns:
            Created entity
        """
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    def update(
        self,
        db_obj: ModelType,
        obj_in: dict
    ) -> ModelType:
        """
        Update an existing entity.
        
        Args:
            db_obj: Database entity to update
            obj_in: Dictionary of fields to update
            
        Returns:
            Updated entity
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    def delete(self, id: UUID) -> Optional[ModelType]:
        """
        Soft delete an entity by setting is_active to False.
        
        Args:
            id: Entity UUID
            
        Returns:
            Deleted entity if found, None otherwise
        """
        db_obj = self.get(id)
        if db_obj:
            db_obj.is_active = False
            self.db.add(db_obj)
            self.db.commit()
            self.db.refresh(db_obj)
        return db_obj
