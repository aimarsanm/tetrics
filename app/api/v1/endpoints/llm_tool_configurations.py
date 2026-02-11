"""
API endpoints for LLM Tool Configurations.
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.repositories import AggregatedScoreRepository, LLMToolConfigurationRepository, MeasurementRepository
from app.schemas import (
    AggregatedScoreRead,
    LLMToolConfigurationCreate,
    LLMToolConfigurationRead,
    LLMToolConfigurationUpdate,
    MeasurementRead,
)

router = APIRouter()

LLM_TOOL_CONFIG_NOT_FOUND = "LLM tool configuration not found"


@router.post("/", response_model=LLMToolConfigurationRead)
def create_llm_tool_configuration(
    schema: LLMToolConfigurationCreate,
    db: Session = Depends(get_db)
):
    """Create a new LLM tool configuration."""
    repo = LLMToolConfigurationRepository(db)
    return repo.create(schema)


@router.get("/", response_model=List[LLMToolConfigurationRead])
def get_llm_tool_configurations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all LLM tool configurations."""
    repo = LLMToolConfigurationRepository(db)
    return repo.get_all(skip=skip, limit=limit)


@router.get("/{config_id}", response_model=LLMToolConfigurationRead)
def get_llm_tool_configuration(
    config_id: UUID,
    db: Session = Depends(get_db)
):
    """Get LLM tool configuration by ID."""
    repo = LLMToolConfigurationRepository(db)
    config = repo.get_by_id(config_id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=LLM_TOOL_CONFIG_NOT_FOUND
        )
    return config


@router.put("/{config_id}", response_model=LLMToolConfigurationRead)
def update_llm_tool_configuration(
    config_id: UUID,
    schema: LLMToolConfigurationUpdate,
    db: Session = Depends(get_db)
):
    """Update an LLM tool configuration."""
    repo = LLMToolConfigurationRepository(db)
    config = repo.update(config_id, schema)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=LLM_TOOL_CONFIG_NOT_FOUND
        )
    return config


@router.delete("/{config_id}")
def delete_llm_tool_configuration(
    config_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete an LLM tool configuration."""
    repo = LLMToolConfigurationRepository(db)
    success = repo.delete(config_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=LLM_TOOL_CONFIG_NOT_FOUND
        )
    return {"message": "LLM tool configuration deleted successfully"}


@router.get("/{config_id}/measurements", response_model=List[MeasurementRead])
def get_measurements_by_configuration(
    config_id: UUID,
    db: Session = Depends(get_db)
):
    """Get measurements by LLM tool configuration ID."""
    repo = MeasurementRepository(db)
    return repo.get_by_llm_tool_configuration(config_id)


@router.get("/{config_id}/aggregated-scores", response_model=List[AggregatedScoreRead])
def get_scores_by_configuration(
    config_id: UUID,
    db: Session = Depends(get_db)
):
    """Get aggregated scores by tool configuration ID."""
    repo = AggregatedScoreRepository(db)
    return repo.get_by_tool_configuration(config_id)
