"""
User schemas for external identity provider integration.

Note: User creation and deletion are handled by external identity provider (Keycloak).
These schemas are only for updating app-specific user data and retrieving user info.
"""
from typing import Optional
from pydantic import Field, ConfigDict
from uuid import UUID

from .base import BaseResponseSchema


# Schema for updating app-specific user data (the only user operation allowed)
class UserUpdate(BaseResponseSchema):
    """Schema for updating app-specific user preferences and data."""
    bio: Optional[str] = Field(
        None,
        max_length=1000,
        description="User biography or description"
    )
    notification_preferences: Optional[str] = Field(
        None,
        max_length=500,
        description="JSON string of notification preferences"
    )
    theme_preference: Optional[str] = Field(
        None,
        pattern="^(light|dark|system)$",
        description="UI theme preference: light, dark, or system"
    )


# Schema for user information responses
class UserResponse(BaseResponseSchema):
    """Schema for user information in API responses."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(description="User ID")
    external_id: str = Field(description="External identity provider user ID")
    email: str = Field(description="User email from identity provider")
    full_name: Optional[str] = Field(description="Full name from identity provider")
    bio: Optional[str] = Field(description="User biography")
    notification_preferences: Optional[str] = Field(description="Notification preferences")
    theme_preference: Optional[str] = Field(description="UI theme preference")
    is_active: bool = Field(description="Whether the user account is active")


# Schema for user profile (public view - minimal info)
class UserProfile(BaseResponseSchema):
    """Schema for public user profile information."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(description="User ID")
    full_name: Optional[str] = Field(description="Full name")
    bio: Optional[str] = Field(description="User biography")


# Schema for user creation (internal use only - for syncing with identity provider)
class UserCreate(BaseResponseSchema):
    """
    Schema for internal user creation when syncing with identity provider.
    This is NOT exposed via public API endpoints.
    """
    external_id: str = Field(
        min_length=1,
        max_length=255,
        description="External identity provider user ID"
    )
    email: str = Field(
        pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        description="User email from identity provider"
    )
    full_name: Optional[str] = Field(
        None,
        max_length=255,
        description="Full name from identity provider"
    )
