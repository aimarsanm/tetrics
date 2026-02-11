"""
API endpoints for Aggregated Scores.
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.repositories import AggregatedScoreRepository
from app.schemas import AggregatedScoreCreate, AggregatedScoreRead, AggregatedScoreUpdate

router = APIRouter()

AGGREGATED_SCORE_NOT_FOUND = "Aggregated score not found"


@router.post("/", response_model=AggregatedScoreRead)
def create_aggregated_score(
    schema: AggregatedScoreCreate,
    db: Session = Depends(get_db)
):
    """Create a new aggregated score."""
    repo = AggregatedScoreRepository(db)
    return repo.create(schema)


@router.get("/", response_model=List[AggregatedScoreRead])
def get_aggregated_scores(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all aggregated scores."""
    repo = AggregatedScoreRepository(db)
    return repo.get_all(skip=skip, limit=limit)


@router.get("/{score_id}", response_model=AggregatedScoreRead)
def get_aggregated_score(
    score_id: UUID,
    db: Session = Depends(get_db)
):
    """Get aggregated score by ID."""
    repo = AggregatedScoreRepository(db)
    score = repo.get_by_id(score_id)
    if not score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=AGGREGATED_SCORE_NOT_FOUND
        )
    return score


@router.put("/{score_id}", response_model=AggregatedScoreRead)
def update_aggregated_score(
    score_id: UUID,
    schema: AggregatedScoreUpdate,
    db: Session = Depends(get_db)
):
    """Update an aggregated score."""
    repo = AggregatedScoreRepository(db)
    score = repo.update(score_id, schema)
    if not score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=AGGREGATED_SCORE_NOT_FOUND
        )
    return score


@router.delete("/{score_id}")
def delete_aggregated_score(
    score_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete an aggregated score."""
    repo = AggregatedScoreRepository(db)
    success = repo.delete(score_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=AGGREGATED_SCORE_NOT_FOUND
        )
    return {"message": "Aggregated score deleted successfully"}
