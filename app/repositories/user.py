"""
User repository implementation.
"""
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from .base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User operations."""
    
    def __init__(self, db: Session):
        super().__init__(User, db)
    
    def create(self, obj_in: UserCreate) -> User:
        """Create a new user."""
        db_obj = User(**obj_in.model_dump())
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    def get_by_external_id(self, external_id: str) -> Optional[User]:
        """Get user by external identity provider ID."""
        return self.db.query(User).filter(User.external_id == external_id).first()
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email address."""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        return self.db.query(User).filter(User.username == username).first()
    
    def get_active_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all active users."""
        return (
            self.db.query(User)
            .filter(User.is_active == True)
            .order_by(User.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def search_users(
        self, 
        search_term: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[User]:
        """Search users by name, email, or username."""
        return (
            self.db.query(User)
            .filter(
                or_(
                    User.full_name.ilike(f"%{search_term}%"),
                    User.email.ilike(f"%{search_term}%"),
                    User.username.ilike(f"%{search_term}%")
                )
            )
            .filter(User.is_active == True)
            .order_by(User.full_name)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def count_active_users(self) -> int:
        """Count active users."""
        return self.db.query(User).filter(User.is_active == True).count()
    
    def count_total_users(self) -> int:
        """Count total users (including inactive)."""
        return self.db.query(User).count()
    
    def deactivate(self, user_id: UUID) -> Optional[User]:
        """Deactivate a user (soft delete)."""
        user = self.get(user_id)
        if user:
            user.is_active = False
            user.updated_at = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(user)
        return user
    
    def activate(self, user_id: UUID) -> Optional[User]:
        """Activate a user."""
        user = self.get(user_id)
        if user:
            user.is_active = True
            user.updated_at = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(user)
        return user
    
    def update_last_login(self, user_id: UUID) -> Optional[User]:
        """Update user's last login timestamp."""
        user = self.get(user_id)
        if user:
            user.last_login = datetime.now(timezone.utc)
            user.updated_at = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(user)
        return user
    

    
    def get_users_by_role(self, role: str, skip: int = 0, limit: int = 100) -> List[User]:
        """Get users by role (if role field exists)."""
        query = self.db.query(User).filter(User.is_active == True)
        
        # Check if the User model has a role field
        if hasattr(User, 'role'):
            query = query.filter(User.role == role)
        
        return (
            query
            .order_by(User.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_recently_registered_users(self, days: int = 7, skip: int = 0, limit: int = 100) -> List[User]:
        """Get users registered in the last N days."""
        from datetime import timedelta
        
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        return (
            self.db.query(User)
            .filter(User.created_at >= cutoff_date)
            .filter(User.is_active == True)
            .order_by(User.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    

    
    def check_email_exists(self, email: str, exclude_user_id: Optional[UUID] = None) -> bool:
        """Check if email already exists, optionally excluding a specific user."""
        query = self.db.query(User).filter(User.email == email)
        
        if exclude_user_id:
            query = query.filter(User.id != exclude_user_id)
        
        return query.first() is not None
    
    def check_username_exists(self, username: str, exclude_user_id: Optional[UUID] = None) -> bool:
        """Check if username already exists, optionally excluding a specific user."""
        query = self.db.query(User).filter(User.username == username)
        
        if exclude_user_id:
            query = query.filter(User.id != exclude_user_id)
        
        return query.first() is not None
    
    def get_user_statistics(self) -> Dict[str, Any]:
        """Get user statistics."""
        total_users = self.count_total_users()
        active_users = self.count_active_users()
        inactive_users = total_users - active_users
        
        # Users registered in last 30 days
        from datetime import timedelta
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        recent_registrations = (
            self.db.query(User)
            .filter(User.created_at >= thirty_days_ago)
            .count()
        )
        
        # Users with recent activity (last login in 30 days)
        recent_activity = 0
        if hasattr(User, 'last_login'):
            recent_activity = (
                self.db.query(User)
                .filter(User.last_login >= thirty_days_ago)
                .filter(User.is_active == True)
                .count()
            )
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "inactive_users": inactive_users,
            "recent_registrations": recent_registrations,
            "recent_activity": recent_activity,
            "activity_rate": (recent_activity / active_users * 100) if active_users > 0 else 0
        }
