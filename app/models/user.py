"""
User model for external identity provider integration.
Users are managed by Keycloak - this model stores only app-specific data.
"""
from sqlalchemy import String, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional

from .base import BaseModel


class User(BaseModel):
    """
    User model for storing app-specific user data.
    
    Note: Authentication and core user management is handled by external
    identity provider (Keycloak). This model only stores application-specific
    user preferences and metadata.
    """
    __tablename__ = "users"
    
    # External identity provider user ID (Keycloak sub claim)
    external_id: Mapped[str] = mapped_column(
        String(255), 
        unique=True, 
        nullable=False,
        index=True,
        comment="External identity provider user ID (Keycloak sub)"
    )
    
    # User email from identity provider (for reference and display)
    email: Mapped[str] = mapped_column(
        String(320), 
        unique=True, 
        nullable=False,
        index=True,
        comment="User email from identity provider"
    )
    
    # Display name from identity provider
    full_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Full name from identity provider"
    )
    
    # App-specific user preferences and data
    bio: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="User biography/description (app-specific)"
    )
    
    # App-specific settings
    notification_preferences: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="JSON string of notification preferences"
    )
    
    theme_preference: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        default="system",
        comment="UI theme preference: light, dark, system"
    )
    
    def __repr__(self) -> str:
        return f"<User(external_id='{self.external_id}', email='{self.email}')>"
