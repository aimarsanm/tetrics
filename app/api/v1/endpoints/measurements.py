"""
API endpoints for Measurements.
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.core.auth import get_current_user, requires_role, UserContext
from app.repositories import MeasurementRepository
from app.schemas import MeasurementCreate, MeasurementRead, MeasurementUpdate

router = APIRouter()

MEASUREMENT_NOT_FOUND = "Measurement not found"


@router.post("/", response_model=MeasurementRead)
def create_measurement(
    schema: MeasurementCreate,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
):
    """Create a new measurement. Any authenticated user can add measures."""
    repo = MeasurementRepository(db)
    return repo.create(schema)


@router.get("/", response_model=List[MeasurementRead])
def get_measurements(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
):
    """Get all measurements."""
    repo = MeasurementRepository(db)
    return repo.get_all(skip=skip, limit=limit)


@router.get("/{measurement_id}", response_model=MeasurementRead)
def get_measurement(
    measurement_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
):
    """Get measurement by ID."""
    repo = MeasurementRepository(db)
    measurement = repo.get_by_id(measurement_id)
    if not measurement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=MEASUREMENT_NOT_FOUND
        )
    return measurement


@router.put("/{measurement_id}", response_model=MeasurementRead)
def update_measurement(
    measurement_id: UUID,
    schema: MeasurementUpdate,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(requires_role("admin")),
):
    """Update a measurement. Admin only."""
    repo = MeasurementRepository(db)
    measurement = repo.update(measurement_id, schema)
    if not measurement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=MEASUREMENT_NOT_FOUND
        )
    return measurement


@router.delete("/{measurement_id}")
def delete_measurement(
    measurement_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(requires_role("admin")),
):
    """Delete a measurement. Admin only."""
    repo = MeasurementRepository(db)
    success = repo.delete(measurement_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=MEASUREMENT_NOT_FOUND
        )
    return {"message": "Measurement deleted successfully"}
