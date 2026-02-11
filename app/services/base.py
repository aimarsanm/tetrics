"""
Base service class with common business logic patterns.
"""
from abc import ABC
from typing import Dict, List, Optional, TypeVar, Generic
from uuid import UUID

from app.core.exceptions import NotFoundError, ConflictError, ValidationError
from app.schemas.base import PaginationParams, PaginatedResponse

# Type variables
RepositoryType = TypeVar("RepositoryType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")
ResponseSchemaType = TypeVar("ResponseSchemaType")


class BaseService(Generic[RepositoryType, CreateSchemaType, UpdateSchemaType, ResponseSchemaType], ABC):
    """Base service class with common business logic operations."""
    
    def __init__(self, repository: RepositoryType):
        """
        Initialize service with repository.
        
        Args:
            repository: Data access repository
        """
        self.repository = repository
    
    def get_by_id(self, id: UUID) -> Optional[ResponseSchemaType]:
        """
        Get entity by ID.
        
        Args:
            id: Entity ID
            
        Returns:
            Entity if found, None otherwise
            
        Raises:
            NotFoundError: If entity not found
        """
        entity = self.repository.get(id)
        if not entity:
            raise NotFoundError(f"Entity with ID {id} not found")
        return self._model_to_response(entity)
    
    def get_multi(
        self,
        pagination: PaginationParams,
        filters: Optional[Dict] = None
    ) -> PaginatedResponse:
        """
        Get multiple entities with pagination.
        
        Args:
            pagination: Pagination parameters
            filters: Optional filters
            
        Returns:
            Paginated response with entities
        """
        entities = self.repository.get_multi(
            skip=pagination.skip,
            limit=pagination.limit,
            filters=filters
        )
        total = self.repository.count(filters=filters)
        
        return PaginatedResponse(
            items=[self._model_to_response(entity) for entity in entities],
            total=total,
            skip=pagination.skip,
            limit=pagination.limit,
            has_next=pagination.skip + pagination.limit < total
        )
    
    def create(self, create_data: CreateSchemaType) -> ResponseSchemaType:
        """
        Create new entity.
        
        Args:
            create_data: Creation data
            
        Returns:
            Created entity
            
        Raises:
            ValidationError: If validation fails
            ConflictError: If entity already exists
        """
        # Validate creation data
        self._validate_create(create_data)
        
        # Check for conflicts
        self._check_create_conflicts(create_data)
        
        # Create entity
        entity = self.repository.create(create_data)
        return self._model_to_response(entity)
    
    def update(self, id: UUID, update_data: UpdateSchemaType) -> ResponseSchemaType:
        """
        Update existing entity.
        
        Args:
            id: Entity ID
            update_data: Update data
            
        Returns:
            Updated entity
            
        Raises:
            NotFoundError: If entity not found
            ValidationError: If validation fails
            ConflictError: If update conflicts
        """
        # Get existing entity
        entity = self.repository.get(id)
        if not entity:
            raise NotFoundError(f"Entity with ID {id} not found")
        
        # Validate update data
        self._validate_update(update_data, entity)
        
        # Check for conflicts
        self._check_update_conflicts(id, update_data)
        
        # Update entity
        updated_entity = self.repository.update(entity, update_data)
        return self._model_to_response(updated_entity)
    
    def delete(self, id: UUID) -> bool:
        """
        Delete entity by ID.
        
        Args:
            id: Entity ID
            
        Returns:
            True if deleted, False if not found
        """
        entity = self.repository.delete(id)
        return entity is not None
    
    def soft_delete(self, id: UUID) -> ResponseSchemaType:
        """
        Soft delete entity by ID.
        
        Args:
            id: Entity ID
            
        Returns:
            Soft deleted entity
            
        Raises:
            NotFoundError: If entity not found
        """
        entity = self.repository.soft_delete(id)
        if not entity:
            raise NotFoundError(f"Entity with ID {id} not found")
        return self._model_to_response(entity)
    
    def exists(self, id: UUID) -> bool:
        """
        Check if entity exists.
        
        Args:
            id: Entity ID
            
        Returns:
            True if exists, False otherwise
        """
        return self.repository.exists(id)
    
    # Abstract methods to be implemented by subclasses
    def _model_to_response(self, model) -> ResponseSchemaType:
        """Convert database model to response schema."""
        raise NotImplementedError("Subclasses must implement _model_to_response")
    
    def _validate_create(self, create_data: CreateSchemaType) -> None:
        """Validate creation data."""
        # Override in subclasses for specific validation
        pass
    
    def _validate_update(self, update_data: UpdateSchemaType, existing_model) -> None:
        """Validate update data."""
        # Override in subclasses for specific validation
        pass
    
    def _check_create_conflicts(self, create_data: CreateSchemaType) -> None:
        """Check for creation conflicts."""
        # Override in subclasses for specific conflict checks
        pass
    
    def _check_update_conflicts(self, id: UUID, update_data: UpdateSchemaType) -> None:
        """Check for update conflicts."""
        # Override in subclasses for specific conflict checks
        pass
