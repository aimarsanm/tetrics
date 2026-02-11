"""
Main API router for version 1.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    aggregated_scores,
    evaluation_criteria,
    evaluation_programs,
    goals,
    llm_tool_configurations,
    measurements,
    metrics,
    users,
)

api_router = APIRouter()

# User endpoints
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["users"]
)

# Domain endpoints
api_router.include_router(
    evaluation_programs.router,
    prefix="/domain/evaluation-programs",
    tags=["Evaluation Programs"]
)

api_router.include_router(
    goals.router,
    prefix="/domain/goals",
    tags=["Goals"]
)

api_router.include_router(
    evaluation_criteria.router,
    prefix="/domain/evaluation-criteria",
    tags=["Evaluation Criteria"]
)

api_router.include_router(
    metrics.router,
    prefix="/domain/metrics",
    tags=["Metrics"]
)

api_router.include_router(
    llm_tool_configurations.router,
    prefix="/domain/llm-tool-configurations",
    tags=["LLM Tool Configurations"]
)

api_router.include_router(
    measurements.router,
    prefix="/domain/measurements",
    tags=["Measurements"]
)

api_router.include_router(
    aggregated_scores.router,
    prefix="/domain/aggregated-scores",
    tags=["Aggregated Scores"]
)
