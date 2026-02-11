"""
API endpoints for Evaluation Programs.
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.repositories import EvaluationProgramRepository, GoalRepository
from app.schemas import EvaluationProgramCreate, EvaluationProgramRead, EvaluationProgramUpdate, GoalRead

router = APIRouter()

EVALUATION_PROGRAM_NOT_FOUND = "Evaluation program not found"


@router.post("/", response_model=EvaluationProgramRead)
def create_evaluation_program(
    schema: EvaluationProgramCreate,
    db: Session = Depends(get_db)
):
    """Create a new evaluation program."""
    repo = EvaluationProgramRepository(db)
    return repo.create(schema)


@router.get("/", response_model=List[EvaluationProgramRead])
def get_evaluation_programs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all evaluation programs."""
    repo = EvaluationProgramRepository(db)
    return repo.get_all(skip=skip, limit=limit)


@router.get("/{program_id}", response_model=EvaluationProgramRead)
def get_evaluation_program(
    program_id: UUID,
    db: Session = Depends(get_db)
):
    """Get evaluation program by ID."""
    repo = EvaluationProgramRepository(db)
    program = repo.get_by_id(program_id)
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=EVALUATION_PROGRAM_NOT_FOUND
        )
    return program


@router.put("/{program_id}", response_model=EvaluationProgramRead)
def update_evaluation_program(
    program_id: UUID,
    schema: EvaluationProgramUpdate,
    db: Session = Depends(get_db)
):
    """Update an evaluation program."""
    repo = EvaluationProgramRepository(db)
    program = repo.update(program_id, schema)
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=EVALUATION_PROGRAM_NOT_FOUND
        )
    return program


@router.delete("/{program_id}")
def delete_evaluation_program(
    program_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete an evaluation program."""
    repo = EvaluationProgramRepository(db)
    success = repo.delete(program_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=EVALUATION_PROGRAM_NOT_FOUND
        )
    return {"message": "Evaluation program deleted successfully"}


@router.get("/{program_id}/goals", response_model=List[GoalRead])
def get_goals_by_program(
    program_id: UUID,
    db: Session = Depends(get_db)
):
    """Get goals by evaluation program ID."""
    repo = GoalRepository(db)
    return repo.get_by_evaluation_program(program_id)
