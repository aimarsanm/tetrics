"""
API endpoints for Evaluation Criteria.
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.core.auth import get_current_user, requires_role, UserContext
from app.repositories import AggregatedScoreRepository, EvaluationCriterionRepository, MetricRepository
from app.schemas import (
    AggregatedScoreRead,
    EvaluationCriterionCreate,
    EvaluationCriterionRead,
    EvaluationCriterionUpdate,
    MetricRead,
)

router = APIRouter()

EVALUATION_CRITERION_NOT_FOUND = "Evaluation criterion not found"


@router.post("/", response_model=EvaluationCriterionRead)
def create_evaluation_criterion(
    schema: EvaluationCriterionCreate,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(requires_role("admin")),
):
    """Create a new evaluation criterion. Admin only."""
    repo = EvaluationCriterionRepository(db)
    return repo.create(schema)


@router.get("/", response_model=List[EvaluationCriterionRead])
def get_evaluation_criteria(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
):
    """Get all evaluation criteria."""
    repo = EvaluationCriterionRepository(db)
    return repo.get_all(skip=skip, limit=limit)


@router.get("/{criterion_id}", response_model=EvaluationCriterionRead)
def get_evaluation_criterion(
    criterion_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
):
    """Get evaluation criterion by ID."""
    repo = EvaluationCriterionRepository(db)
    criterion = repo.get_by_id(criterion_id)
    if not criterion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=EVALUATION_CRITERION_NOT_FOUND
        )
    return criterion


@router.put("/{criterion_id}", response_model=EvaluationCriterionRead)
def update_evaluation_criterion(
    criterion_id: UUID,
    schema: EvaluationCriterionUpdate,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(requires_role("admin")),
):
    """Update an evaluation criterion. Admin only."""
    repo = EvaluationCriterionRepository(db)
    criterion = repo.update(criterion_id, schema)
    if not criterion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=EVALUATION_CRITERION_NOT_FOUND
        )
    try:
        print(f"[UPDATE] Criterion {criterion_id} aggregation_strategy now: {criterion.aggregation_strategy}")
    except Exception as _e:
        print(f"[UPDATE] Failed to print aggregation_strategy for {criterion_id}: {_e}")
    return criterion


@router.delete("/{criterion_id}")
def delete_evaluation_criterion(
    criterion_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(requires_role("admin")),
):
    """Delete an evaluation criterion. Admin only."""
    repo = EvaluationCriterionRepository(db)
    success = repo.delete(criterion_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=EVALUATION_CRITERION_NOT_FOUND
        )
    return {"message": "Evaluation criterion deleted successfully"}


@router.get("/{criterion_id}/metrics", response_model=List[MetricRead])
def get_metrics_by_criterion(
    criterion_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
):
    """Get metrics by evaluation criterion ID."""
    repo = MetricRepository(db)
    return repo.get_by_evaluation_criterion(criterion_id)


@router.get("/{criterion_id}/aggregated-scores", response_model=List[AggregatedScoreRead])
def get_scores_by_criterion(
    criterion_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
):
    """Get aggregated scores by criterion ID."""
    repo = AggregatedScoreRepository(db)
    return repo.get_by_criterion(criterion_id)


@router.post("/{criterion_id}/recalculate-scores", response_model=List[AggregatedScoreRead])
def recalculate_criterion_scores(
    criterion_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(requires_role("admin")),
):
    """
    Recalculate all aggregated scores for a specific criterion across all tool configurations.
    Admin only.
    """
    from app.services.score_aggregation import ScoreAggregationService

    print(f"[RECALC] Recalculating scores for criterion {criterion_id}")
    service = ScoreAggregationService(db)
    try:
        recalculated_scores = service.recalculate_all_scores_for_criterion(criterion_id)
        print(f"[RECALC] Successfully recalculated {len(recalculated_scores)} scores")
        return recalculated_scores
    except Exception as e:
        print(f"[RECALC] Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to recalculate scores: {str(e)}"
        )
