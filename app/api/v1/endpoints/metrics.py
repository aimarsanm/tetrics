"""
API endpoints for Metrics.
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.core.auth import get_current_user, requires_role, UserContext
from app.repositories import MetricRepository
from app.schemas import MetricCreate, MetricRead, MetricUpdate

router = APIRouter()

METRIC_NOT_FOUND = "Metric not found"


@router.post("/", response_model=MetricRead)
def create_metric(
    schema: MetricCreate,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(requires_role("admin")),
):
    """Create a new metric. Admin only."""
    repo = MetricRepository(db)
    return repo.create(schema)


@router.get("/", response_model=List[MetricRead])
def get_metrics(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
):
    """Get all metrics."""
    repo = MetricRepository(db)
    return repo.get_all(skip=skip, limit=limit)


@router.get("/{metric_id}", response_model=MetricRead)
def get_metric(
    metric_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
):
    """Get metric by ID."""
    repo = MetricRepository(db)
    metric = repo.get_by_id(metric_id)
    if not metric:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=METRIC_NOT_FOUND
        )
    return metric


@router.put("/{metric_id}", response_model=MetricRead)
def update_metric(
    metric_id: UUID,
    schema: MetricUpdate,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(requires_role("admin")),
):
    """Update a metric. Admin only."""
    repo = MetricRepository(db)
    metric = repo.update(metric_id, schema)
    if not metric:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=METRIC_NOT_FOUND
        )
    return metric


@router.delete("/{metric_id}")
def delete_metric(
    metric_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(requires_role("admin")),
):
    """Delete a metric. Admin only."""
    repo = MetricRepository(db)
    success = repo.delete(metric_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=METRIC_NOT_FOUND
        )
    return {"message": "Metric deleted successfully"}
