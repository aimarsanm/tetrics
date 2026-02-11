"""
User service for external identity provider integration.

This service handles syncing user data from external identity provider (Keycloak)
and managing app-specific user preferences.
"""
from typing import Optional
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.repositories.user import UserRepository
from app.core.exceptions import NotFoundError, ConflictError


class UserService:
    """
    User service for external identity provider integration.
    
    Note: This service does NOT handle user authentication or registration.
    Those are handled by the external identity provider (Keycloak).
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
    
    def get_by_external_id(self, external_id: str) -> Optional[User]:
        """Get user by external identity provider ID."""
        return self.user_repo.get_by_external_id(external_id)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email address."""
        return self.user_repo.get_by_email(email)
    
    def sync_user_from_idp(self, external_id: str, email: str, full_name: Optional[str] = None) -> User:
        """
        Sync user data from identity provider.
        
        This method creates or updates a user record based on data from the identity provider.
        Called when a user logs in or when user data is updated in the identity provider.
        """
        # Check if user already exists
        existing_user = self.get_by_external_id(external_id)
        
        if existing_user:
            # Update existing user data from identity provider
            if existing_user.email != email:
                existing_user.email = email
            if existing_user.full_name != full_name:
                existing_user.full_name = full_name
            
            self.db.commit()
            self.db.refresh(existing_user)
            return existing_user
        else:
            # Check if email is already used by another user
            email_user = self.get_by_email(email)
            if email_user:
                raise ConflictError(f"Email {email} is already associated with another user")
            
            # Create new user record
            user_data = UserCreate(
                external_id=external_id,
                email=email,
                full_name=full_name
            )
            return self.user_repo.create(user_data)
    
    def update_user_preferences(self, user_id: UUID, user_update: UserUpdate) -> User:
        """
        Update app-specific user preferences and data.
        
        This is the main user update operation available to end users.
        """
        user = self.user_repo.get(user_id)
        if not user:
            raise NotFoundError(f"User with ID {user_id} not found")
        
        # Update only the app-specific fields
        update_data = user_update.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            if hasattr(user, field):
                setattr(user, field, value)
        
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_user_profile(self, user_id: UUID) -> User:
        """Get user profile information."""
        user = self.user_repo.get(user_id)
        if not user:
            raise NotFoundError(f"User with ID {user_id} not found")
        return user
    
    def deactivate_user(self, user_id: UUID) -> User:
        """
        Deactivate a user account (soft delete).
        
        Note: This only deactivates the local app record. The user account
        in the identity provider must be managed separately.
        """
        user = self.user_repo.get(user_id)
        if not user:
            raise NotFoundError(f"User with ID {user_id} not found")
        
        user.is_active = False
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def reactivate_user(self, user_id: UUID) -> User:
        """Reactivate a deactivated user account."""
        user = self.user_repo.get(user_id)
        if not user:
            raise NotFoundError(f"User with ID {user_id} not found")
        
        user.is_active = True
        self.db.commit()
        self.db.refresh(user)
        return user
