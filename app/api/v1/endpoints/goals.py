"""
API endpoints for Goals.
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.core.auth import get_current_user, requires_role, UserContext
from app.repositories import EvaluationCriterionRepository, EvaluationProgramRepository, GoalRepository
from app.schemas import EvaluationCriterionRead, GoalCreate, GoalRead, GoalUpdate

router = APIRouter()

GOAL_NOT_FOUND = "Goal not found"


@router.post("/", response_model=GoalRead)
def create_goal(
    schema: GoalCreate,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(requires_role("admin")),
):
    """Create a new goal. Admin only."""
    eval_program_repo = EvaluationProgramRepository(db)
    eval_program = eval_program_repo.get_by_id(schema.evaluation_program_id)
    if not eval_program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evaluation program with id {schema.evaluation_program_id} not found"
        )

    repo = GoalRepository(db)
    return repo.create(schema)


@router.get("/", response_model=List[GoalRead])
def get_goals(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
):
    """Get all goals."""
    repo = GoalRepository(db)
    return repo.get_all(skip=skip, limit=limit)


@router.get("/{goal_id}", response_model=GoalRead)
def get_goal(
    goal_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
):
    """Get goal by ID."""
    repo = GoalRepository(db)
    goal = repo.get_by_id(goal_id)
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=GOAL_NOT_FOUND
        )
    return goal


@router.put("/{goal_id}", response_model=GoalRead)
def update_goal(
    goal_id: UUID,
    schema: GoalUpdate,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(requires_role("admin")),
):
    """Update a goal. Admin only."""
    repo = GoalRepository(db)
    goal = repo.update(goal_id, schema)
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=GOAL_NOT_FOUND
        )
    return goal


@router.delete("/{goal_id}")
def delete_goal(
    goal_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(requires_role("admin")),
):
    """Delete a goal. Admin only."""
    repo = GoalRepository(db)
    success = repo.delete(goal_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=GOAL_NOT_FOUND
        )
    return {"message": "Goal deleted successfully"}


@router.get("/{goal_id}/evaluation-criteria", response_model=List[EvaluationCriterionRead])
def get_criteria_by_goal(
    goal_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
):
    """Get evaluation criteria by goal ID."""
    repo = EvaluationCriterionRepository(db)
    return repo.get_by_goal(goal_id)
