"""
User endpoints using UserService.
"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.core.auth import get_current_user, requires_role, UserContext
from app.services.user import UserService
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.core.exceptions import NotFoundError, ConflictError, ValidationError

router = APIRouter()


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """Dependency to get UserService instance."""
    return UserService(db)


@router.get("/{user_id}", response_model=UserResponse)
def get_user_profile(
    user_id: UUID,
    service: UserService = Depends(get_user_service),
    current_user: UserContext = Depends(get_current_user),
):
    """Get user profile by ID."""
    try:
        user = service.get_user_profile(user_id)
        return user
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/external/{external_id}", response_model=UserResponse)
def get_user_by_external_id(
    external_id: str,
    service: UserService = Depends(get_user_service),
    current_user: UserContext = Depends(get_current_user),
):
    """Get user by external identity provider ID."""
    user = service.get_by_external_id(external_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.get("/email/{email}", response_model=UserResponse)
def get_user_by_email(
    email: str,
    service: UserService = Depends(get_user_service),
    current_user: UserContext = Depends(get_current_user),
):
    """Get user by email address."""
    user = service.get_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.post("/sync", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def sync_user_from_idp(
    external_id: str,
    email: str,
    full_name: Optional[str] = None,
    service: UserService = Depends(get_user_service),
    current_user: UserContext = Depends(get_current_user),
):
    """
    Sync user data from identity provider.
    Creates or updates a user record based on data from the identity provider.
    """
    try:
        user = service.sync_user_from_idp(external_id, email, full_name)
        return user
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/{user_id}/preferences", response_model=UserResponse)
def update_user_preferences(
    user_id: UUID,
    user_update: UserUpdate,
    service: UserService = Depends(get_user_service),
    current_user: UserContext = Depends(get_current_user),
):
    """Update user preferences."""
    try:
        user = service.update_user_preferences(user_id, user_update)
        return user
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/{user_id}/deactivate", response_model=UserResponse)
def deactivate_user(
    user_id: UUID,
    service: UserService = Depends(get_user_service),
    current_user: UserContext = Depends(requires_role("admin")),
):
    """Deactivate a user account. Admin only."""
    try:
        user = service.deactivate_user(user_id)
        return user
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/{user_id}/reactivate", response_model=UserResponse)
def reactivate_user(
    user_id: UUID,
    service: UserService = Depends(get_user_service),
    current_user: UserContext = Depends(requires_role("admin")),
):
    """Reactivate a user account. Admin only."""
    try:
        user = service.reactivate_user(user_id)
        return user
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
