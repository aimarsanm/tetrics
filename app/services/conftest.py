"""
Shared fixtures for score aggregation service tests.

This module defines reusable fixtures for mocking dependencies,
creating sample entities, and providing test data.
"""
from datetime import datetime, timedelta, timezone
from typing import Dict, List
from unittest.mock import MagicMock
from uuid import UUID, uuid4

import pytest
from sqlalchemy.orm import Session

from app.models.domain import (
    AggregatedScore,
    AggregationStrategy,
    Direction,
    EvaluationCriterion,
    Measurement,
    Metric,
    MetricUnit,
)
from app.services.score_aggregation import ScoreAggregationService


# =============================================================================
# UUID Fixtures (Deterministic IDs for Tests)
# =============================================================================


@pytest.fixture
def sample_uuid_set():
    """
    Fixture providing a set of deterministic UUIDs for use in tests.
    
    Returns:
        Dict with named UUIDs for criterion, metrics, tool config, etc.
    """
    return {
        "criterion_id": UUID("11111111-1111-1111-1111-111111111111"),
        "metric_1_id": UUID("22222222-2222-2222-2222-222222222222"),
        "metric_2_id": UUID("33333333-3333-3333-3333-333333333333"),
        "metric_3_id": UUID("44444444-4444-4444-4444-444444444444"),
        "tool_config_id": UUID("55555555-5555-5555-5555-555555555555"),
        "aggregated_score_id": UUID("66666666-6666-6666-6666-666666666666"),
        "measurement_1_id": UUID("77777777-7777-7777-7777-777777777777"),
        "measurement_2_id": UUID("88888888-8888-8888-8888-888888888888"),
    }


# =============================================================================
# Mock Dependency Fixtures
# =============================================================================


@pytest.fixture
def mock_db_session():
    """
    Fixture providing a mocked SQLAlchemy Session.
    
    Returns:
        MagicMock simulating SQLAlchemy Session with configurable query methods
    """
    db = MagicMock(spec=Session)
    db.query = MagicMock(return_value=MagicMock())
    db.commit = MagicMock()
    db.refresh = MagicMock()
    return db


@pytest.fixture
def mock_criterion_repo():
    """
    Fixture providing a mocked EvaluationCriterionRepository.
    
    Returns:
        MagicMock with get_by_id method
    """
    repo = MagicMock()
    repo.get_by_id = MagicMock(return_value=None)
    return repo


@pytest.fixture
def mock_metric_repo():
    """
    Fixture providing a mocked MetricRepository.
    
    Returns:
        MagicMock with get_by_criterion method
    """
    repo = MagicMock()
    repo.get_by_criterion = MagicMock(return_value=[])
    return repo


@pytest.fixture
def mock_measurement_repo():
    """
    Fixture providing a mocked MeasurementRepository.
    
    Returns:
        MagicMock for measurement operations
    """
    repo = MagicMock()
    return repo


@pytest.fixture
def mock_score_repo():
    """
    Fixture providing a mocked AggregatedScoreRepository.
    
    Returns:
        MagicMock with get_by_criterion_and_tool, get_by_tool_configuration, create methods
    """
    repo = MagicMock()
    repo.get_by_criterion_and_tool = MagicMock(return_value=[])
    repo.get_by_tool_configuration = MagicMock(return_value=[])
    repo.create = MagicMock(return_value=None)
    return repo


@pytest.fixture
def mock_tool_config_repo():
    """
    Fixture providing a mocked LLMToolConfigurationRepository.
    
    Returns:
        MagicMock with update_total_score method
    """
    repo = MagicMock()
    repo.update_total_score = MagicMock()
    return repo


# =============================================================================
# Sample Entity Fixtures
# =============================================================================


@pytest.fixture
def sample_criterion_entity(sample_uuid_set):
    """
    Fixture providing a sample EvaluationCriterion mock.
    
    Returns:
        MagicMock simulating an EvaluationCriterion with typical attributes
    """
    criterion = MagicMock(spec=EvaluationCriterion)
    criterion.id = sample_uuid_set["criterion_id"]
    criterion.name = "Code Quality"
    criterion.aggregation_strategy = AggregationStrategy.WEIGHTED_AVERAGE
    criterion.weight = 1.0
    return criterion


@pytest.fixture
def sample_metric_entity(sample_uuid_set):
    """
    Fixture providing a sample Metric mock.
    
    Returns:
        MagicMock simulating a Metric with typical attributes
    """
    metric = MagicMock(spec=Metric)
    metric.id = sample_uuid_set["metric_1_id"]
    metric.name = "Test Coverage"
    metric.weight = 1.0
    metric.unit = MetricUnit.PERCENT
    metric.direction = Direction.HIGHER_IS_BETTER
    return metric


@pytest.fixture
def sample_measurement_entity(sample_uuid_set):
    """
    Fixture providing a sample Measurement mock.
    
    Returns:
        MagicMock simulating a Measurement with typical attributes
    """
    measurement = MagicMock(spec=Measurement)
    measurement.id = sample_uuid_set["measurement_1_id"]
    measurement.metric_id = sample_uuid_set["metric_1_id"]
    measurement.value = 75.0
    measurement.date = datetime.now(timezone.utc)
    measurement.is_active = True
    measurement.llm_tool_configuration_id = sample_uuid_set["tool_config_id"]
    measurement.aggregated_score_id = None
    return measurement


@pytest.fixture
def sample_aggregated_score_entity(sample_uuid_set):
    """
    Fixture providing a sample AggregatedScore mock.
    
    Returns:
        MagicMock simulating an AggregatedScore with typical attributes
    """
    score = MagicMock(spec=AggregatedScore)
    score.id = sample_uuid_set["aggregated_score_id"]
    score.criterion_id = sample_uuid_set["criterion_id"]
    score.tool_config_id = sample_uuid_set["tool_config_id"]
    score.score = 75.0
    score.timestamp = datetime.now(timezone.utc)
    score.component_metrics = {
        str(sample_uuid_set["metric_1_id"]): {
            "name": "Test Coverage",
            "value": 75.0,
            "weight": 1.0,
            "contribution": 75.0,
        }
    }
    return score


# =============================================================================
# Service with Mocks Fixture
# =============================================================================


@pytest.fixture
def service_with_mocks(
    mock_db_session,
    mock_criterion_repo,
    mock_metric_repo,
    mock_measurement_repo,
    mock_score_repo,
    mock_tool_config_repo,
    monkeypatch,
):
    """
    Fixture providing a ScoreAggregationService with all dependencies mocked.
    
    Returns:
        ScoreAggregationService instance with mocked repositories
    """
    service = ScoreAggregationService(mock_db_session)
    
    # Inject mocked repositories
    service.criterion_repo = mock_criterion_repo
    service.metric_repo = mock_metric_repo
    service.measurement_repo = mock_measurement_repo
    service.score_repo = mock_score_repo
    service.tool_config_repo = mock_tool_config_repo
    
    return service


# =============================================================================
# Helper Fixtures for Complex Test Scenarios
# =============================================================================


@pytest.fixture
def mock_query_chain():
    """
    Fixture providing a properly chained mock for db.query() operations.
    
    Returns:
        MagicMock configured for typical SQLAlchemy query chain patterns
    """
    mock_query_result = MagicMock()
    mock_query_result.filter.return_value.all.return_value = []
    mock_query_result.filter.return_value.scalar.return_value = 0.0
    mock_query_result.filter.return_value.distinct.return_value.all.return_value = []
    return mock_query_result
