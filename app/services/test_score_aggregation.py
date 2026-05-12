"""
Unit tests for ScoreAggregationService.

This module contains comprehensive test coverage for score aggregation,
including white-box and black-box test cases covering all branches,
edge cases, and business logic requirements.

Test Organization:
- WHITE-BOX TESTS (WB-xxx): Branch coverage, flow analysis
- BLACK-BOX TESTS (BB-xxx): Equivalence partitioning, boundary value analysis

Framework: Pytest
Pattern: Arrange-Act-Assert (AAA)
"""
from datetime import datetime, timedelta, timezone
from typing import Dict, List
from unittest.mock import MagicMock, patch, call
from uuid import UUID, uuid4

import pytest

from app.core.exceptions import ValidationError
from app.models.domain import (
    AggregatedScore,
    AggregationStrategy,
    Direction,
    EvaluationCriterion,
    Measurement,
    Metric,
    MetricUnit,
)
from app.schemas.aggregated_score import AggregatedScoreCreate
from app.services.score_aggregation import (
    ScoreAggregationService,
    ZERO_TOLERANCE,
    PERCENT_UNIT_NORMALIZE_DIVISOR,
)


# =============================================================================
# WHITE-BOX TESTS: calculate_and_store_score() Method
# =============================================================================


class TestCalculateAndStoreScore:
    """WHITE-BOX tests for calculate_and_store_score() method."""

    def test_wb_001_happy_path_all_data_valid(
        self, service_with_mocks, sample_uuid_set, sample_criterion_entity,
        sample_metric_entity, sample_measurement_entity, sample_aggregated_score_entity
    ):
        """
        WB-001: Flujo normal - criterio existe, métricas existen, mediciones existen.
        
        Expected: AggregatedScore creado/actualizado + mediciones vinculadas
        """
        # Arrange
        service_with_mocks.criterion_repo.get_by_id.return_value = sample_criterion_entity
        service_with_mocks.metric_repo.get_by_criterion.return_value = [sample_metric_entity]
        service_with_mocks.db.query.return_value.filter.return_value.all.return_value = [
            sample_measurement_entity
        ]
        service_with_mocks.db.query.return_value.filter.return_value.scalar.return_value = 100.0
        service_with_mocks.score_repo.get_by_criterion_and_tool.return_value = []
        service_with_mocks.score_repo.create.return_value = sample_aggregated_score_entity

        # Act
        result = service_with_mocks.calculate_and_store_score(
            sample_uuid_set["criterion_id"],
            sample_uuid_set["tool_config_id"]
        )

        # Assert
        assert result is not None
        assert isinstance(result, MagicMock)
        service_with_mocks.score_repo.create.assert_called_once()
        service_with_mocks.db.commit.assert_called()

    def test_wb_002_criterion_not_found(self, service_with_mocks, sample_uuid_set):
        """
        WB-002: Rama - criterio NO existe.
        
        Expected: ValidationError("Criterion ... not found")
        """
        # Arrange
        service_with_mocks.criterion_repo.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ValidationError, match="Criterion.*not found"):
            service_with_mocks.calculate_and_store_score(
                sample_uuid_set["criterion_id"],
                sample_uuid_set["tool_config_id"]
            )

    def test_wb_003_no_metrics_found(
        self, service_with_mocks, sample_uuid_set, sample_criterion_entity
    ):
        """
        WB-003: Rama - métricas NO existen.
        
        Expected: ValidationError("No metrics found...")
        """
        # Arrange
        service_with_mocks.criterion_repo.get_by_id.return_value = sample_criterion_entity
        service_with_mocks.metric_repo.get_by_criterion.return_value = []

        # Act & Assert
        with pytest.raises(ValidationError, match="No metrics found"):
            service_with_mocks.calculate_and_store_score(
                sample_uuid_set["criterion_id"],
                sample_uuid_set["tool_config_id"]
            )

    def test_wb_004_no_measurements_found(
        self, service_with_mocks, sample_uuid_set, sample_criterion_entity, sample_metric_entity
    ):
        """
        WB-004: Rama - NO hay mediciones para ninguna métrica.
        
        Expected: ValidationError("No measurements found...")
        """
        # Arrange
        service_with_mocks.criterion_repo.get_by_id.return_value = sample_criterion_entity
        service_with_mocks.metric_repo.get_by_criterion.return_value = [sample_metric_entity]
        service_with_mocks.db.query.return_value.filter.return_value.all.return_value = []

        # Act & Assert
        with pytest.raises(ValidationError, match="No measurements found"):
            service_with_mocks.calculate_and_store_score(
                sample_uuid_set["criterion_id"],
                sample_uuid_set["tool_config_id"]
            )


# =============================================================================
# WHITE-BOX TESTS: recalculate_all_scores_for_criterion() Method
# =============================================================================


class TestRecalculateAllScoresForCriterion:
    """WHITE-BOX tests for recalculate_all_scores_for_criterion() method."""

    def test_wb_005_criterion_not_found_recalculate(
        self, service_with_mocks, sample_uuid_set
    ):
        """
        WB-005: Rama - criterio NO existe en recalculate.
        
        Expected: ValidationError("Criterion ... not found")
        """
        # Arrange
        service_with_mocks.criterion_repo.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ValidationError, match="Criterion.*not found"):
            service_with_mocks.recalculate_all_scores_for_criterion(
                sample_uuid_set["criterion_id"]
            )

    def test_wb_006_no_metrics_returns_empty_list(
        self, service_with_mocks, sample_uuid_set, sample_criterion_entity
    ):
        """
        WB-006: Rama - NO hay métricas + retorna lista vacía.
        
        Expected: [] (lista vacía)
        """
        # Arrange
        service_with_mocks.criterion_repo.get_by_id.return_value = sample_criterion_entity
        service_with_mocks.metric_repo.get_by_criterion.return_value = []

        # Act
        result = service_with_mocks.recalculate_all_scores_for_criterion(
            sample_uuid_set["criterion_id"]
        )

        # Assert
        assert result == []

    def test_wb_007_no_tool_configs_returns_empty_list(
        self, service_with_mocks, sample_uuid_set, sample_criterion_entity, sample_metric_entity
    ):
        """
        WB-007: Rama - NO hay tool_config_ids + retorna lista vacía.
        
        Expected: [] (lista vacía)
        """
        # Arrange
        service_with_mocks.criterion_repo.get_by_id.return_value = sample_criterion_entity
        service_with_mocks.metric_repo.get_by_criterion.return_value = [sample_metric_entity]
        # Query returns no tool_config_ids
        service_with_mocks.db.query.return_value.filter.return_value.distinct.return_value.all.return_value = []

        # Act
        result = service_with_mocks.recalculate_all_scores_for_criterion(
            sample_uuid_set["criterion_id"]
        )

        # Assert
        assert result == []

    def test_wb_008_partial_success_one_config_fails(
        self,
        service_with_mocks,
        sample_uuid_set,
        sample_criterion_entity,
        sample_metric_entity,
        sample_aggregated_score_entity,
    ):
        """
        WB-008: Rama - Éxito parcial (1/2 configs fallan).
        
        Expected: [AggregatedScore] solo para configs válidas
        """
        # Arrange
        tool_config_id_1 = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
        tool_config_id_2 = UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")

        service_with_mocks.criterion_repo.get_by_id.return_value = sample_criterion_entity
        service_with_mocks.metric_repo.get_by_criterion.return_value = [sample_metric_entity]

        # First config succeeds, second fails
        service_with_mocks.db.query.return_value.filter.return_value.distinct.return_value.all.return_value = [
            (tool_config_id_1,),
            (tool_config_id_2,),
        ]

        # Mock calculate_and_store_score to succeed for first, fail for second
        original_calc = service_with_mocks.calculate_and_store_score
        call_count = [0]

        def side_effect(crit_id, tool_id):
            call_count[0] += 1
            if call_count[0] == 1:
                return sample_aggregated_score_entity
            else:
                raise ValidationError("No measurements found")

        service_with_mocks.calculate_and_store_score = MagicMock(side_effect=side_effect)

        # Act
        result = service_with_mocks.recalculate_all_scores_for_criterion(
            sample_uuid_set["criterion_id"]
        )

        # Assert
        assert len(result) == 1
        assert result[0] == sample_aggregated_score_entity

    def test_wb_009_multiple_configs_all_success(
        self,
        service_with_mocks,
        sample_uuid_set,
        sample_criterion_entity,
        sample_metric_entity,
    ):
        """
        WB-009: Rama - Éxito total (múltiples configs).
        
        Expected: List[AggregatedScore] con 3 elementos
        """
        # Arrange
        tool_config_ids = [
            UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
            UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
            UUID("cccccccc-cccc-cccc-cccc-cccccccccccc"),
        ]

        service_with_mocks.criterion_repo.get_by_id.return_value = sample_criterion_entity
        service_with_mocks.metric_repo.get_by_criterion.return_value = [sample_metric_entity]
        service_with_mocks.db.query.return_value.filter.return_value.distinct.return_value.all.return_value = [
            (tid,) for tid in tool_config_ids
        ]

        scores = [MagicMock(spec=AggregatedScore) for _ in tool_config_ids]
        service_with_mocks.calculate_and_store_score = MagicMock(side_effect=scores)

        # Act
        result = service_with_mocks.recalculate_all_scores_for_criterion(
            sample_uuid_set["criterion_id"]
        )

        # Assert
        assert len(result) == 3
        assert service_with_mocks.calculate_and_store_score.call_count == 3


# =============================================================================
# WHITE-BOX TESTS: _apply_aggregation_strategy() Method
# =============================================================================


class TestApplyAggregationStrategy:
    """WHITE-BOX tests for _apply_aggregation_strategy() method."""

    def test_wb_010_strategy_weighted_average(
        self, service_with_mocks, sample_uuid_set, sample_criterion_entity,
        sample_metric_entity, sample_measurement_entity
    ):
        """
        WB-010: Rama - Estrategia = WEIGHTED_AVERAGE.
        
        Expected: Llama a _calculate_weighted_average()
        """
        # Arrange
        sample_criterion_entity.aggregation_strategy = AggregationStrategy.WEIGHTED_AVERAGE
        measurements_by_metric = {sample_uuid_set["metric_1_id"]: [sample_measurement_entity]}

        # Mock the calculation method
        service_with_mocks._calculate_weighted_average = MagicMock(
            return_value=(75.0, {})
        )

        # Act
        score, components = service_with_mocks._apply_aggregation_strategy(
            sample_criterion_entity,
            [sample_metric_entity],
            measurements_by_metric
        )

        # Assert
        service_with_mocks._calculate_weighted_average.assert_called_once()
        assert score == 75.0

    def test_wb_011_strategy_weighted_sum_normalized(
        self, service_with_mocks, sample_uuid_set, sample_criterion_entity,
        sample_metric_entity, sample_measurement_entity
    ):
        """
        WB-011: Rama - Estrategia = WEIGHTED_SUM_NORMALIZED.
        
        Expected: Llama a _calculate_weighted_sum_normalized()
        """
        # Arrange
        sample_criterion_entity.aggregation_strategy = AggregationStrategy.WEIGHTED_SUM_NORMALIZED
        measurements_by_metric = {sample_uuid_set["metric_1_id"]: [sample_measurement_entity]}

        service_with_mocks._calculate_weighted_sum_normalized = MagicMock(
            return_value=(50.0, {})
        )

        # Act
        score, components = service_with_mocks._apply_aggregation_strategy(
            sample_criterion_entity,
            [sample_metric_entity],
            measurements_by_metric
        )

        # Assert
        service_with_mocks._calculate_weighted_sum_normalized.assert_called_once()
        assert score == 50.0

    def test_wb_012_strategy_custom(
        self, service_with_mocks, sample_uuid_set, sample_criterion_entity,
        sample_metric_entity, sample_measurement_entity
    ):
        """
        WB-012: Rama - Estrategia = CUSTOM.
        
        Expected: Llama a _calculate_custom()
        """
        # Arrange
        sample_criterion_entity.aggregation_strategy = AggregationStrategy.CUSTOM
        measurements_by_metric = {sample_uuid_set["metric_1_id"]: [sample_measurement_entity]}

        service_with_mocks._calculate_custom = MagicMock(
            return_value=(60.0, {})
        )

        # Act
        score, components = service_with_mocks._apply_aggregation_strategy(
            sample_criterion_entity,
            [sample_metric_entity],
            measurements_by_metric
        )

        # Assert
        service_with_mocks._calculate_custom.assert_called_once()
        assert score == 60.0

    def test_wb_013_strategy_unknown(
        self, service_with_mocks, sample_uuid_set, sample_criterion_entity,
        sample_metric_entity
    ):
        """
        WB-013: Rama - Estrategia desconocida.
        
        Expected: ValidationError("Unknown aggregation strategy...")
        """
        # Arrange
        sample_criterion_entity.aggregation_strategy = "invalid_strategy"

        # Act & Assert
        with pytest.raises(ValidationError, match="Unknown aggregation strategy"):
            service_with_mocks._apply_aggregation_strategy(
                sample_criterion_entity,
                [sample_metric_entity],
                {}
            )


# =============================================================================
# WHITE-BOX TESTS: _parse_aggregation_strategy() Method
# =============================================================================


class TestParseAggregationStrategy:
    """WHITE-BOX tests for _parse_aggregation_strategy() method."""

    def test_wb_014_parse_enum_input(self, service_with_mocks):
        """
        WB-014: Rama - Input es AggregationStrategy enum.
        
        Expected: Retorna el mismo enum sin cambios
        """
        # Act
        result = service_with_mocks._parse_aggregation_strategy(
            AggregationStrategy.WEIGHTED_AVERAGE
        )

        # Assert
        assert result == AggregationStrategy.WEIGHTED_AVERAGE

    def test_wb_015_parse_valid_string(self, service_with_mocks):
        """
        WB-015: Rama - Input es string válido.
        
        Expected: AggregationStrategy.WEIGHTED_AVERAGE
        """
        # Act
        result = service_with_mocks._parse_aggregation_strategy("weighted_average")

        # Assert
        assert result == AggregationStrategy.WEIGHTED_AVERAGE

    def test_wb_016_parse_invalid_string(self, service_with_mocks):
        """
        WB-016: Rama - Input es string inválido.
        
        Expected: ValidationError("Invalid aggregation strategy...")
        """
        # Act & Assert
        with pytest.raises(ValidationError, match="Invalid aggregation strategy"):
            service_with_mocks._parse_aggregation_strategy("invalid_strategy")

    def test_wb_017_parse_unsupported_type(self, service_with_mocks):
        """
        WB-017: Rama - Input es tipo no soportado.
        
        Expected: ValidationError("Unknown aggregation strategy type...")
        """
        # Act & Assert
        with pytest.raises(ValidationError, match="Unknown aggregation strategy type"):
            service_with_mocks._parse_aggregation_strategy(123)


# =============================================================================
# WHITE-BOX TESTS: _calculate_weighted_average() Method
# =============================================================================


class TestCalculateWeightedAverage:
    """WHITE-BOX tests for _calculate_weighted_average() method."""

    def test_wb_018_all_metrics_have_measurements(
        self, service_with_mocks, sample_uuid_set, sample_criterion_entity
    ):
        """
        WB-018: Rama - Todas las métricas tienen mediciones.
        
        Expected: score = (Σ(value × weight) / Σ(weight)) × criterion_weight
        """
        # Arrange
        metric_1 = MagicMock(spec=Metric)
        metric_1.id = sample_uuid_set["metric_1_id"]
        metric_1.name = "Metric 1"
        metric_1.weight = 2.0

        metric_2 = MagicMock(spec=Metric)
        metric_2.id = sample_uuid_set["metric_2_id"]
        metric_2.name = "Metric 2"
        metric_2.weight = 3.0

        measurement_1 = MagicMock(spec=Measurement)
        measurement_1.value = 100.0
        measurement_1.date = datetime.now(timezone.utc)

        measurement_2 = MagicMock(spec=Measurement)
        measurement_2.value = 50.0
        measurement_2.date = datetime.now(timezone.utc)

        measurements_by_metric = {
            sample_uuid_set["metric_1_id"]: [measurement_1],
            sample_uuid_set["metric_2_id"]: [measurement_2],
        }

        sample_criterion_entity.weight = 1.0

        # Act
        score, components = service_with_mocks._calculate_weighted_average(
            sample_criterion_entity,
            [metric_1, metric_2],
            measurements_by_metric
        )

        # Assert
        # (100*2 + 50*3) / (2+3) * 1 = 350/5 = 70
        assert pytest.approx(score, rel=1e-6) == 70.0
        assert len(components) == 2

    def test_wb_019_metric_without_measurements_skipped(
        self, service_with_mocks, sample_uuid_set, sample_criterion_entity
    ):
        """
        WB-019: Rama - Métrica sin mediciones (skip).
        
        Expected: Métrica sin datos es ignorada, cálculo usa solo las otras
        """
        # Arrange
        metric_1 = MagicMock(spec=Metric)
        metric_1.id = sample_uuid_set["metric_1_id"]
        metric_1.weight = 2.0

        metric_2 = MagicMock(spec=Metric)
        metric_2.id = sample_uuid_set["metric_2_id"]
        metric_2.weight = 3.0

        measurement_1 = MagicMock(spec=Measurement)
        measurement_1.value = 100.0
        measurement_1.date = datetime.now(timezone.utc)

        # Only metric_1 has measurements
        measurements_by_metric = {
            sample_uuid_set["metric_1_id"]: [measurement_1],
        }

        sample_criterion_entity.weight = 1.0

        # Act
        score, components = service_with_mocks._calculate_weighted_average(
            sample_criterion_entity,
            [metric_1, metric_2],
            measurements_by_metric
        )

        # Assert
        # 100*2 / 2 * 1 = 100
        assert pytest.approx(score, rel=1e-6) == 100.0
        assert len(components) == 1

    def test_wb_020_total_weight_zero(
        self, service_with_mocks, sample_uuid_set, sample_criterion_entity
    ):
        """
        WB-020: Rama - Total weight = 0.
        
        Expected: ValidationError("Total metric weight is zero")
        """
        # Arrange
        metric_1 = MagicMock(spec=Metric)
        metric_1.id = sample_uuid_set["metric_1_id"]
        metric_1.weight = 0.0

        measurement_1 = MagicMock(spec=Measurement)
        measurement_1.value = 100.0
        measurement_1.date = datetime.now(timezone.utc)

        measurements_by_metric = {
            sample_uuid_set["metric_1_id"]: [measurement_1],
        }

        # Act & Assert
        with pytest.raises(ValidationError, match="Total metric weight is zero"):
            service_with_mocks._calculate_weighted_average(
                sample_criterion_entity,
                [metric_1],
                measurements_by_metric
            )

    def test_wb_021_total_weight_below_tolerance(
        self, service_with_mocks, sample_uuid_set, sample_criterion_entity
    ):
        """
        WB-021: Rama - Total weight < ZERO_TOLERANCE.
        
        Expected: ValidationError("Total metric weight is zero")
        """
        # Arrange
        metric_1 = MagicMock(spec=Metric)
        metric_1.id = sample_uuid_set["metric_1_id"]
        metric_1.weight = ZERO_TOLERANCE / 2  # Below tolerance

        measurement_1 = MagicMock(spec=Measurement)
        measurement_1.value = 100.0
        measurement_1.date = datetime.now(timezone.utc)

        measurements_by_metric = {
            sample_uuid_set["metric_1_id"]: [measurement_1],
        }

        # Act & Assert
        with pytest.raises(ValidationError, match="Total metric weight is zero"):
            service_with_mocks._calculate_weighted_average(
                sample_criterion_entity,
                [metric_1],
                measurements_by_metric
            )

    def test_wb_022_multiple_measurements_uses_latest(
        self, service_with_mocks, sample_uuid_set, sample_criterion_entity
    ):
        """
        WB-022: Rama - Múltiples mediciones, selecciona más reciente.
        
        Expected: Usa measurement con max(date)
        """
        # Arrange
        metric_1 = MagicMock(spec=Metric)
        metric_1.id = sample_uuid_set["metric_1_id"]
        metric_1.weight = 1.0

        # Older measurement
        measurement_old = MagicMock(spec=Measurement)
        measurement_old.value = 50.0
        measurement_old.date = datetime.now(timezone.utc) - timedelta(days=1)

        # Newer measurement
        measurement_new = MagicMock(spec=Measurement)
        measurement_new.value = 100.0
        measurement_new.date = datetime.now(timezone.utc)

        measurements_by_metric = {
            sample_uuid_set["metric_1_id"]: [measurement_old, measurement_new],
        }

        sample_criterion_entity.weight = 1.0

        # Act
        score, components = service_with_mocks._calculate_weighted_average(
            sample_criterion_entity,
            [metric_1],
            measurements_by_metric
        )

        # Assert
        # Should use value=100, not 50
        assert pytest.approx(score, rel=1e-6) == 100.0


# =============================================================================
# WHITE-BOX TESTS: _calculate_weighted_sum_normalized() Method
# =============================================================================


class TestCalculateWeightedSumNormalized:
    """WHITE-BOX tests for _calculate_weighted_sum_normalized() method."""

    def test_wb_023_all_metrics_have_measurements_wsn(
        self, service_with_mocks, sample_uuid_set, sample_criterion_entity
    ):
        """
        WB-023: Rama - Todas las métricas tienen mediciones (weighted_sum_normalized).
        
        Expected: Suma total de contribuciones normalizadas
        """
        # Arrange
        metric_1 = MagicMock(spec=Metric)
        metric_1.id = sample_uuid_set["metric_1_id"]
        metric_1.name = "Metric 1"
        metric_1.weight = 1.0
        metric_1.unit = MetricUnit.PERCENT
        metric_1.direction = Direction.HIGHER_IS_BETTER

        measurement_1 = MagicMock(spec=Measurement)
        measurement_1.value = 50.0  # 50%
        measurement_1.date = datetime.now(timezone.utc)

        measurements_by_metric = {
            sample_uuid_set["metric_1_id"]: [measurement_1],
        }

        service_with_mocks.db.query.return_value.filter.return_value.scalar.return_value = 100.0

        # Act
        score, components = service_with_mocks._calculate_weighted_sum_normalized(
            sample_criterion_entity,
            [metric_1],
            measurements_by_metric
        )

        # Assert
        # normalized = 50/100 = 0.5, weighted = 0.5 * 1.0 = 0.5
        assert pytest.approx(score, rel=1e-6) == 0.5

    def test_wb_024_metric_without_measurements_skipped_wsn(
        self, service_with_mocks, sample_uuid_set, sample_criterion_entity
    ):
        """
        WB-024: Rama - Métrica sin mediciones (skip) en weighted_sum_normalized.
        
        Expected: Métrica sin datos es ignorada
        """
        # Arrange
        metric_1 = MagicMock(spec=Metric)
        metric_1.id = sample_uuid_set["metric_1_id"]
        metric_1.weight = 1.0
        metric_1.unit = MetricUnit.PERCENT
        metric_1.direction = Direction.HIGHER_IS_BETTER

        metric_2 = MagicMock(spec=Metric)
        metric_2.id = sample_uuid_set["metric_2_id"]
        metric_2.weight = 1.0

        measurement_1 = MagicMock(spec=Measurement)
        measurement_1.value = 50.0
        measurement_1.date = datetime.now(timezone.utc)

        # Only metric_1 has measurements
        measurements_by_metric = {
            sample_uuid_set["metric_1_id"]: [measurement_1],
        }

        # Act
        score, components = service_with_mocks._calculate_weighted_sum_normalized(
            sample_criterion_entity,
            [metric_1, metric_2],
            measurements_by_metric
        )

        # Assert
        assert len(components) == 1  # Only one metric in breakdown


# =============================================================================
# WHITE-BOX TESTS: _calculate_custom() Method
# =============================================================================


class TestCalculateCustom:
    """WHITE-BOX tests for _calculate_custom() method."""

    def test_wb_025_custom_delegates_to_wsn(
        self, service_with_mocks, sample_uuid_set, sample_criterion_entity,
        sample_metric_entity, sample_measurement_entity
    ):
        """
        WB-025: Rama - Delega a weighted_sum_normalized.
        
        Expected: Retorna resultado de _calculate_weighted_sum_normalized()
        """
        # Arrange
        measurements_by_metric = {
            sample_uuid_set["metric_1_id"]: [sample_measurement_entity]
        }

        service_with_mocks._calculate_weighted_sum_normalized = MagicMock(
            return_value=(42.0, {})
        )

        # Act
        score, components = service_with_mocks._calculate_custom(
            sample_criterion_entity,
            [sample_metric_entity],
            measurements_by_metric
        )

        # Assert
        service_with_mocks._calculate_weighted_sum_normalized.assert_called_once()
        assert score == 42.0


# =============================================================================
# WHITE-BOX TESTS: _normalize_metric_value() Method
# =============================================================================


class TestNormalizeMetricValue:
    """WHITE-BOX tests for _normalize_metric_value() method."""

    def test_wb_026_normalize_percent_unit(self, service_with_mocks):
        """
        WB-026: Rama - Unit = "percent".
        
        Expected: normalized = 50 / 100.0 = 0.5
        """
        # Arrange
        metric = MagicMock(spec=Metric)
        metric.unit = MetricUnit.PERCENT

        # Act
        result = service_with_mocks._normalize_metric_value(metric, 50.0)

        # Assert
        assert pytest.approx(result, rel=1e-6) == 0.5

    def test_wb_027_normalize_cardinal_with_max_value(self, service_with_mocks, sample_uuid_set):
        """
        WB-027: Rama - Unit = "cardinal" + max_value > 0.
        
        Expected: normalized = 30 / 100 = 0.3
        """
        # Arrange
        metric = MagicMock(spec=Metric)
        metric.id = sample_uuid_set["metric_1_id"]
        metric.unit = MetricUnit.CARDINAL

        service_with_mocks.db.query.return_value.filter.return_value.scalar.return_value = 100.0

        # Act
        result = service_with_mocks._normalize_metric_value(metric, 30.0)

        # Assert
        assert pytest.approx(result, rel=1e-6) == 0.3

    def test_wb_028_normalize_cardinal_max_value_zero(
        self, service_with_mocks, sample_uuid_set
    ):
        """
        WB-028: Rama - Unit = "cardinal" + max_value = 0.
        
        Expected: normalized = 0.0
        """
        # Arrange
        metric = MagicMock(spec=Metric)
        metric.id = sample_uuid_set["metric_1_id"]
        metric.unit = MetricUnit.CARDINAL

        service_with_mocks.db.query.return_value.filter.return_value.scalar.return_value = 0.0

        # Act
        result = service_with_mocks._normalize_metric_value(metric, 50.0)

        # Assert
        assert pytest.approx(result, rel=1e-6) == 0.0

    def test_wb_029_normalize_cardinal_max_value_below_tolerance(
        self, service_with_mocks, sample_uuid_set
    ):
        """
        WB-029: Rama - Unit = "cardinal" + max_value < ZERO_TOLERANCE.
        
        Expected: normalized = 0.0
        """
        # Arrange
        metric = MagicMock(spec=Metric)
        metric.id = sample_uuid_set["metric_1_id"]
        metric.unit = MetricUnit.CARDINAL

        service_with_mocks.db.query.return_value.filter.return_value.scalar.return_value = ZERO_TOLERANCE / 2

        # Act
        result = service_with_mocks._normalize_metric_value(metric, 50.0)

        # Assert
        assert pytest.approx(result, rel=1e-6) == 0.0


# =============================================================================
# WHITE-BOX TESTS: _adjust_for_direction() Method
# =============================================================================


class TestAdjustForDirection:
    """WHITE-BOX tests for _adjust_for_direction() method."""

    def test_wb_030_lower_better_positive_weight_inverts(self, service_with_mocks):
        """
        WB-030: Rama - LOWER_IS_BETTER + weight > 0 (invierte).
        
        Expected: contribution = -10 (negativo)
        """
        # Act
        result = service_with_mocks._adjust_for_direction(
            10.0, 2.0, Direction.LOWER_IS_BETTER
        )

        # Assert
        assert pytest.approx(result, rel=1e-6) == -10.0

    def test_wb_031_higher_better_negative_weight_inverts(self, service_with_mocks):
        """
        WB-031: Rama - HIGHER_IS_BETTER + weight < 0 (invierte).
        
        Expected: contribution = -10 (negativo)
        """
        # Act
        result = service_with_mocks._adjust_for_direction(
            10.0, -2.0, Direction.HIGHER_IS_BETTER
        )

        # Assert
        assert pytest.approx(result, rel=1e-6) == -10.0

    def test_wb_032_higher_better_positive_weight_no_invert(self, service_with_mocks):
        """
        WB-032: Rama - HIGHER_IS_BETTER + weight > 0 (sin invertir).
        
        Expected: contribution = 10 (positivo)
        """
        # Act
        result = service_with_mocks._adjust_for_direction(
            10.0, 2.0, Direction.HIGHER_IS_BETTER
        )

        # Assert
        assert pytest.approx(result, rel=1e-6) == 10.0

    def test_wb_033_lower_better_negative_weight_no_invert(self, service_with_mocks):
        """
        WB-033: Rama - LOWER_IS_BETTER + weight < 0 (sin invertir).
        
        Expected: contribution = 10 (positivo)
        """
        # Act
        result = service_with_mocks._adjust_for_direction(
            10.0, -2.0, Direction.LOWER_IS_BETTER
        )

        # Assert
        assert pytest.approx(result, rel=1e-6) == 10.0

    def test_wb_034_target_value_treated_as_higher_better(self, service_with_mocks):
        """
        WB-034: Rama - TARGET_VALUE (se trata como HIGHER_IS_BETTER).
        
        Expected: contribution = 10 (sin invertir)
        """
        # Act
        result = service_with_mocks._adjust_for_direction(
            10.0, 2.0, Direction.TARGET_VALUE
        )

        # Assert
        assert pytest.approx(result, rel=1e-6) == 10.0


# =============================================================================
# WHITE-BOX TESTS: _upsert_aggregated_score() Method
# =============================================================================


class TestUpsertAggregatedScore:
    """WHITE-BOX tests for _upsert_aggregated_score() method."""

    def test_wb_035_existing_score_updated(
        self, service_with_mocks, sample_uuid_set, sample_aggregated_score_entity
    ):
        """
        WB-035: Rama - Score previo existe + actualización.
        
        Expected: Actualiza score, timestamp, component_metrics
        """
        # Arrange
        service_with_mocks.score_repo.get_by_criterion_and_tool.return_value = [
            sample_aggregated_score_entity
        ]

        # Act
        result = service_with_mocks._upsert_aggregated_score(
            sample_uuid_set["criterion_id"],
            sample_uuid_set["tool_config_id"],
            99.0,
            {"new": "metrics"}
        )

        # Assert
        assert sample_aggregated_score_entity.score == 99.0
        assert sample_aggregated_score_entity.component_metrics == {"new": "metrics"}
        service_with_mocks.db.commit.assert_called()
        service_with_mocks.db.refresh.assert_called()

    def test_wb_036_new_score_created(
        self, service_with_mocks, sample_uuid_set, sample_aggregated_score_entity
    ):
        """
        WB-036: Rama - Score previo NO existe + creación.
        
        Expected: Crea nuevo AggregatedScore via score_repo.create()
        """
        # Arrange
        service_with_mocks.score_repo.get_by_criterion_and_tool.return_value = []
        service_with_mocks.score_repo.create.return_value = sample_aggregated_score_entity

        # Act
        result = service_with_mocks._upsert_aggregated_score(
            sample_uuid_set["criterion_id"],
            sample_uuid_set["tool_config_id"],
            85.0,
            {"test": "data"}
        )

        # Assert
        service_with_mocks.score_repo.create.assert_called_once()
        call_args = service_with_mocks.score_repo.create.call_args[0][0]
        assert isinstance(call_args, AggregatedScoreCreate)
        assert call_args.score == 85.0


# =============================================================================
# WHITE-BOX TESTS: calculate_and_update_tool_total_score() Method
# =============================================================================


class TestCalculateAndUpdateToolTotalScore:
    """WHITE-BOX tests for calculate_and_update_tool_total_score() method."""

    def test_wb_037_no_scores_for_tool_config(
        self, service_with_mocks, sample_uuid_set
    ):
        """
        WB-037: Rama - NO hay scores para tool_config.
        
        Expected: total_score=0.0 almacenado, retorna None
        """
        # Arrange
        service_with_mocks.score_repo.get_by_tool_configuration.return_value = []

        # Act
        result = service_with_mocks.calculate_and_update_tool_total_score(
            sample_uuid_set["tool_config_id"]
        )

        # Assert
        assert result is None
        service_with_mocks.tool_config_repo.update_total_score.assert_called_once_with(
            sample_uuid_set["tool_config_id"], 0.0
        )

    def test_wb_038_multiple_scores_summed(
        self, service_with_mocks, sample_uuid_set
    ):
        """
        WB-038: Rama - Hay múltiples scores.
        
        Expected: total_score = 3.0 + 2.0 + 5.0 = 10.0
        """
        # Arrange
        score_1 = MagicMock()
        score_1.score = 3.0

        score_2 = MagicMock()
        score_2.score = 2.0

        score_3 = MagicMock()
        score_3.score = 5.0

        service_with_mocks.score_repo.get_by_tool_configuration.return_value = [
            score_1, score_2, score_3
        ]

        # Act
        result = service_with_mocks.calculate_and_update_tool_total_score(
            sample_uuid_set["tool_config_id"]
        )

        # Assert
        assert pytest.approx(result, rel=1e-6) == 10.0
        service_with_mocks.tool_config_repo.update_total_score.assert_called_once_with(
            sample_uuid_set["tool_config_id"], 10.0
        )


# =============================================================================
# WHITE-BOX TESTS: Other Utility Methods
# =============================================================================


class TestCollectMeasurements:
    """WHITE-BOX tests for _collect_measurements() method."""

    def test_wb_039_some_metrics_without_measurements(
        self, service_with_mocks, sample_uuid_set
    ):
        """
        WB-039: Rama - Algunas métricas sin mediciones.
        
        Expected: measurements_by_metric contiene solo las con datos
        """
        # Arrange
        metric_1 = MagicMock(spec=Metric)
        metric_1.id = sample_uuid_set["metric_1_id"]

        metric_2 = MagicMock(spec=Metric)
        metric_2.id = sample_uuid_set["metric_2_id"]

        metric_3 = MagicMock(spec=Metric)
        metric_3.id = sample_uuid_set["metric_3_id"]

        measurement = MagicMock(spec=Measurement)

        # Mock _get_measurements_for_metric_and_tool to return data for first two
        def get_measurements(metric_id, tool_id):
            if metric_id == sample_uuid_set["metric_1_id"]:
                return [measurement]
            elif metric_id == sample_uuid_set["metric_2_id"]:
                return [measurement]
            else:
                return []

        service_with_mocks._get_measurements_for_metric_and_tool = MagicMock(
            side_effect=get_measurements
        )

        # Act
        result = service_with_mocks._collect_measurements(
            [metric_1, metric_2, metric_3],
            sample_uuid_set["tool_config_id"]
        )

        # Assert
        assert len(result) == 2  # Only 2 metrics have measurements
        assert sample_uuid_set["metric_1_id"] in result
        assert sample_uuid_set["metric_2_id"] in result


class TestGetMeasurementsForMetricAndTool:
    """WHITE-BOX tests for _get_measurements_for_metric_and_tool() method."""

    def test_wb_040_filters_is_active_true(
        self, service_with_mocks, sample_uuid_set
    ):
        """
        WB-040: Rama - Filtra is_active=True.
        
        Expected: Solo retorna mediciones activas
        """
        # Arrange
        active_measurement = MagicMock(spec=Measurement)
        active_measurement.is_active = True

        service_with_mocks.db.query.return_value.filter.return_value.all.return_value = [
            active_measurement
        ]

        # Act
        result = service_with_mocks._get_measurements_for_metric_and_tool(
            sample_uuid_set["metric_1_id"],
            sample_uuid_set["tool_config_id"]
        )

        # Assert
        assert len(result) == 1
        service_with_mocks.db.query.assert_called()


# =============================================================================
# BLACK-BOX TESTS: Equivalence Partitioning & Boundary Value Analysis
# =============================================================================


class TestBlackBoxEquivalencePartitioning:
    """BLACK-BOX tests using equivalence partitioning."""

    def test_bb_001_mixed_metric_units(
        self, service_with_mocks, sample_uuid_set, sample_criterion_entity
    ):
        """
        BB-001: Equivalence Partition - Métricas mezcladas (Percent + Cardinal).
        
        Expected: Score agregado correcto con normalización diferenciada
        """
        # Arrange
        percent_metric = MagicMock(spec=Metric)
        percent_metric.id = sample_uuid_set["metric_1_id"]
        percent_metric.weight = 1.0
        percent_metric.unit = MetricUnit.PERCENT
        percent_metric.direction = Direction.HIGHER_IS_BETTER

        cardinal_metric = MagicMock(spec=Metric)
        cardinal_metric.id = sample_uuid_set["metric_2_id"]
        cardinal_metric.weight = 1.0
        cardinal_metric.unit = MetricUnit.CARDINAL
        cardinal_metric.direction = Direction.HIGHER_IS_BETTER

        percent_measurement = MagicMock(spec=Measurement)
        percent_measurement.value = 80.0  # 80%
        percent_measurement.date = datetime.now(timezone.utc)

        cardinal_measurement = MagicMock(spec=Measurement)
        cardinal_measurement.value = 50.0
        cardinal_measurement.date = datetime.now(timezone.utc)

        measurements_by_metric = {
            sample_uuid_set["metric_1_id"]: [percent_measurement],
            sample_uuid_set["metric_2_id"]: [cardinal_measurement],
        }

        # Mock max value for cardinal
        service_with_mocks.db.query.return_value.filter.return_value.scalar.return_value = 100.0

        # Act
        score, components = service_with_mocks._calculate_weighted_sum_normalized(
            sample_criterion_entity,
            [percent_metric, cardinal_metric],
            measurements_by_metric
        )

        # Assert
        # Percent: 80/100 = 0.8, Cardinal: 50/100 = 0.5
        # Score = 0.8 + 0.5 = 1.3
        assert pytest.approx(score, rel=1e-6) == 1.3
        assert len(components) == 2

    def test_bb_002_mixed_directions(
        self, service_with_mocks, sample_uuid_set, sample_criterion_entity
    ):
        """
        BB-002: Equivalence Partition - Direcciones mixtas.
        
        Expected: Cada métrica ajustada según su dirección
        """
        # Arrange
        higher_metric = MagicMock(spec=Metric)
        higher_metric.id = sample_uuid_set["metric_1_id"]
        higher_metric.weight = 1.0
        higher_metric.unit = MetricUnit.PERCENT
        higher_metric.direction = Direction.HIGHER_IS_BETTER

        lower_metric = MagicMock(spec=Metric)
        lower_metric.id = sample_uuid_set["metric_2_id"]
        lower_metric.weight = 1.0
        lower_metric.unit = MetricUnit.PERCENT
        lower_metric.direction = Direction.LOWER_IS_BETTER

        measurement_1 = MagicMock(spec=Measurement)
        measurement_1.value = 50.0
        measurement_1.date = datetime.now(timezone.utc)

        measurement_2 = MagicMock(spec=Measurement)
        measurement_2.value = 50.0
        measurement_2.date = datetime.now(timezone.utc)

        measurements_by_metric = {
            sample_uuid_set["metric_1_id"]: [measurement_1],
            sample_uuid_set["metric_2_id"]: [measurement_2],
        }

        # Act
        score, components = service_with_mocks._calculate_weighted_sum_normalized(
            sample_criterion_entity,
            [higher_metric, lower_metric],
            measurements_by_metric
        )

        # Assert
        # Higher: 0.5, Lower (inverted): -0.5 -> total = 0.0
        assert pytest.approx(score, rel=1e-6) == 0.0

    def test_bb_003_metric_weight_zero(self, service_with_mocks, sample_uuid_set):
        """
        BB-003: Boundary Value Analysis - Métrica weight = 0.
        
        Expected: Métrica contribuye 0 al cálculo
        """
        # Arrange
        metric = MagicMock(spec=Metric)
        metric.id = sample_uuid_set["metric_1_id"]
        metric.name = "Zero Weight Metric"
        metric.weight = 0.0

        measurement = MagicMock(spec=Measurement)
        measurement.value = 100.0
        measurement.date = datetime.now(timezone.utc)

        measurements_by_metric = {
            sample_uuid_set["metric_1_id"]: [measurement]
        }

        criterion = MagicMock(spec=EvaluationCriterion)
        criterion.weight = 1.0

        # Act
        score, components = service_with_mocks._calculate_weighted_average(
            criterion,
            [metric],
            measurements_by_metric
        )

        # Assert
        # (100 * 0) / 0 -> zero tolerance -> ValidationError
        # This should trigger the zero weight validation

    def test_bb_004_metric_weight_negative(
        self, service_with_mocks, sample_uuid_set, sample_criterion_entity
    ):
        """
        BB-004: Boundary Value Analysis - Métrica weight negativo.
        
        Expected: Score incluye contribución negativa
        """
        # Arrange
        metric = MagicMock(spec=Metric)
        metric.id = sample_uuid_set["metric_1_id"]
        metric.weight = -1.5
        metric.unit = MetricUnit.PERCENT
        metric.direction = Direction.HIGHER_IS_BETTER

        measurement = MagicMock(spec=Measurement)
        measurement.value = 50.0
        measurement.date = datetime.now(timezone.utc)

        measurements_by_metric = {
            sample_uuid_set["metric_1_id"]: [measurement]
        }

        # Act
        score, components = service_with_mocks._calculate_weighted_sum_normalized(
            sample_criterion_entity,
            [metric],
            measurements_by_metric
        )

        # Assert
        # normalized = 0.5, weighted = -1.5 * 0.5 = -0.75, higher+negative -> -0.75
        assert pytest.approx(score, rel=1e-6) == -0.75

    def test_bb_005_measurement_value_zero(
        self, service_with_mocks, sample_uuid_set, sample_criterion_entity
    ):
        """
        BB-005: Boundary Value Analysis - Measurement value = 0.
        
        Expected: Score incluye 0 como contribución válida
        """
        # Arrange
        metric = MagicMock(spec=Metric)
        metric.id = sample_uuid_set["metric_1_id"]
        metric.weight = 1.0
        metric.unit = MetricUnit.PERCENT
        metric.direction = Direction.HIGHER_IS_BETTER

        measurement = MagicMock(spec=Measurement)
        measurement.value = 0.0
        measurement.date = datetime.now(timezone.utc)

        measurements_by_metric = {
            sample_uuid_set["metric_1_id"]: [measurement]
        }

        # Act
        score, components = service_with_mocks._calculate_weighted_sum_normalized(
            sample_criterion_entity,
            [metric],
            measurements_by_metric
        )

        # Assert
        assert pytest.approx(score, rel=1e-6) == 0.0

    def test_bb_006_measurement_value_negative(
        self, service_with_mocks, sample_uuid_set, sample_criterion_entity
    ):
        """
        BB-006: Boundary Value Analysis - Measurement value negativo.
        
        Expected: Score incluye valor negativo
        """
        # Arrange
        metric = MagicMock(spec=Metric)
        metric.id = sample_uuid_set["metric_1_id"]
        metric.weight = 1.0
        metric.unit = MetricUnit.PERCENT
        metric.direction = Direction.HIGHER_IS_BETTER

        measurement = MagicMock(spec=Measurement)
        measurement.value = -50.0
        measurement.date = datetime.now(timezone.utc)

        measurements_by_metric = {
            sample_uuid_set["metric_1_id"]: [measurement]
        }

        # Act
        score, components = service_with_mocks._calculate_weighted_sum_normalized(
            sample_criterion_entity,
            [metric],
            measurements_by_metric
        )

        # Assert
        # normalized = -50/100 = -0.5
        assert pytest.approx(score, rel=1e-6) == -0.5

    def test_bb_007_cardinal_max_value_zero_prevents_division_error(
        self, service_with_mocks, sample_uuid_set
    ):
        """
        BB-007: Boundary Value Analysis - Cardinal max_value = 0.
        
        Expected: Normalización retorna 0.0 (previene división por cero)
        """
        # Arrange
        metric = MagicMock(spec=Metric)
        metric.id = sample_uuid_set["metric_1_id"]
        metric.unit = MetricUnit.CARDINAL

        service_with_mocks.db.query.return_value.filter.return_value.scalar.return_value = 0.0

        # Act
        result = service_with_mocks._normalize_metric_value(metric, 100.0)

        # Assert
        assert pytest.approx(result, rel=1e-6) == 0.0

    def test_bb_008_percent_value_at_upper_limit(self, service_with_mocks):
        """
        BB-008: Boundary Value Analysis - PERCENT value = 100.
        
        Expected: normalized = 1.0
        """
        # Act
        result = service_with_mocks._normalize_metric_value(
            MagicMock(unit=MetricUnit.PERCENT),
            100.0
        )

        # Assert
        assert pytest.approx(result, rel=1e-6) == 1.0

    def test_bb_009_percent_value_above_100(self, service_with_mocks):
        """
        BB-009: Boundary Value Analysis - PERCENT value > 100.
        
        Expected: normalized = 1.5 (permite valores > 1.0)
        """
        # Act
        result = service_with_mocks._normalize_metric_value(
            MagicMock(unit=MetricUnit.PERCENT),
            150.0
        )

        # Assert
        assert pytest.approx(result, rel=1e-6) == 1.5

    def test_bb_010_percent_value_negative(self, service_with_mocks):
        """
        BB-010: Boundary Value Analysis - PERCENT value < 0.
        
        Expected: normalized = -0.5 (permite negativos)
        """
        # Act
        result = service_with_mocks._normalize_metric_value(
            MagicMock(unit=MetricUnit.PERCENT),
            -50.0
        )

        # Assert
        assert pytest.approx(result, rel=1e-6) == -0.5

    def test_bb_011_criterion_weight_zero(
        self, service_with_mocks, sample_uuid_set
    ):
        """
        BB-011: Boundary Value Analysis - Criterion weight = 0.
        
        Expected: Score final = 0 (multiplicar por 0)
        """
        # Arrange
        criterion = MagicMock(spec=EvaluationCriterion)
        criterion.weight = 0.0

        metric = MagicMock(spec=Metric)
        metric.id = sample_uuid_set["metric_1_id"]
        metric.weight = 1.0

        measurement = MagicMock(spec=Measurement)
        measurement.value = 100.0
        measurement.date = datetime.now(timezone.utc)

        measurements_by_metric = {
            sample_uuid_set["metric_1_id"]: [measurement]
        }

        # Act
        score, components = service_with_mocks._calculate_weighted_average(
            criterion,
            [metric],
            measurements_by_metric
        )

        # Assert
        assert pytest.approx(score, rel=1e-6) == 0.0

    def test_bb_012_multiple_tool_configs(
        self,
        service_with_mocks,
        sample_uuid_set,
        sample_criterion_entity,
        sample_metric_entity,
        sample_aggregated_score_entity
    ):
        """
        BB-012: Equivalence Partition - Tool configs múltiples.
        
        Expected: 5 scores retornados, cada uno correcto
        """
        # Arrange
        tool_config_ids = [
            UUID(f"{'0' * (8 - len(str(i)))}{i}{'1' * (24 - (8 - len(str(i))))}-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
            for i in range(1, 6)
        ]

        service_with_mocks.criterion_repo.get_by_id.return_value = sample_criterion_entity
        service_with_mocks.metric_repo.get_by_criterion.return_value = [sample_metric_entity]
        service_with_mocks.db.query.return_value.filter.return_value.distinct.return_value.all.return_value = [
            (tid,) for tid in tool_config_ids
        ]

        scores = [MagicMock(spec=AggregatedScore) for _ in tool_config_ids]
        service_with_mocks.calculate_and_store_score = MagicMock(side_effect=scores)

        # Act
        result = service_with_mocks.recalculate_all_scores_for_criterion(
            sample_uuid_set["criterion_id"]
        )

        # Assert
        assert len(result) == 5

    def test_bb_013_error_partial_in_recalculate(
        self,
        service_with_mocks,
        sample_uuid_set,
        sample_criterion_entity,
        sample_metric_entity,
        sample_aggregated_score_entity
    ):
        """
        BB-013: Equivalence Partition - Error parcial en recalculate.
        
        Expected: 2 scores retornados, 1 silenciosamente ignorado
        """
        # Arrange
        tool_config_ids = [
            UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
            UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
            UUID("cccccccc-cccc-cccc-cccc-cccccccccccc"),
        ]

        service_with_mocks.criterion_repo.get_by_id.return_value = sample_criterion_entity
        service_with_mocks.metric_repo.get_by_criterion.return_value = [sample_metric_entity]
        service_with_mocks.db.query.return_value.filter.return_value.distinct.return_value.all.return_value = [
            (tid,) for tid in tool_config_ids
        ]

        scores = [sample_aggregated_score_entity, sample_aggregated_score_entity]
        errors = [None, None, ValidationError("No measurements")]

        def side_effect(crit_id, tool_id):
            if len(scores) > 0:
                return scores.pop(0)
            else:
                raise errors.pop(0)

        service_with_mocks.calculate_and_store_score = MagicMock(side_effect=side_effect)

        # Act
        result = service_with_mocks.recalculate_all_scores_for_criterion(
            sample_uuid_set["criterion_id"]
        )

        # Assert
        assert len(result) == 2

    def test_bb_014_multiple_measurements_latest_used(
        self, service_with_mocks, sample_uuid_set, sample_criterion_entity
    ):
        """
        BB-014: Equivalence Partition - Mediciones múltiples, usa más reciente.
        
        Expected: Usa measurement con max(date)
        """
        # Arrange
        metric = MagicMock(spec=Metric)
        metric.id = sample_uuid_set["metric_1_id"]
        metric.weight = 1.0

        # Create measurements with different timestamps
        measurement_1 = MagicMock(spec=Measurement)
        measurement_1.value = 50.0
        measurement_1.date = datetime(2026, 5, 1, tzinfo=timezone.utc)

        measurement_2 = MagicMock(spec=Measurement)
        measurement_2.value = 75.0
        measurement_2.date = datetime(2026, 5, 10, tzinfo=timezone.utc)

        measurement_3 = MagicMock(spec=Measurement)
        measurement_3.value = 100.0
        measurement_3.date = datetime(2026, 5, 12, tzinfo=timezone.utc)

        measurements_by_metric = {
            sample_uuid_set["metric_1_id"]: [measurement_1, measurement_2, measurement_3]
        }

        sample_criterion_entity.weight = 1.0

        # Act
        score, components = service_with_mocks._calculate_weighted_average(
            sample_criterion_entity,
            [metric],
            measurements_by_metric
        )

        # Assert
        # Should use value=100 (most recent)
        assert pytest.approx(score, rel=1e-6) == 100.0

    def test_bb_015_measurement_timestamp_now(
        self, service_with_mocks, sample_uuid_set, sample_criterion_entity
    ):
        """
        BB-015: Boundary Value Analysis - Medición timestamp = now.
        
        Expected: Se reconoce como más reciente correctamente
        """
        # Arrange
        metric = MagicMock(spec=Metric)
        metric.id = sample_uuid_set["metric_1_id"]
        metric.weight = 1.0

        now = datetime.now(timezone.utc)

        measurement_old = MagicMock(spec=Measurement)
        measurement_old.value = 50.0
        measurement_old.date = now - timedelta(hours=1)

        measurement_now = MagicMock(spec=Measurement)
        measurement_now.value = 100.0
        measurement_now.date = now

        measurements_by_metric = {
            sample_uuid_set["metric_1_id"]: [measurement_old, measurement_now]
        }

        sample_criterion_entity.weight = 1.0

        # Act
        score, components = service_with_mocks._calculate_weighted_average(
            sample_criterion_entity,
            [metric],
            measurements_by_metric
        )

        # Assert
        assert pytest.approx(score, rel=1e-6) == 100.0

    def test_bb_016_strategies_produce_different_scores(
        self, service_with_mocks, sample_uuid_set, sample_criterion_entity,
        sample_metric_entity, sample_measurement_entity
    ):
        """
        BB-016: Equivalence Partition - Estrategias producen scores diferentes.
        
        Expected: 2 scores diferentes para el mismo dataset
        """
        # Arrange
        measurements_by_metric = {
            sample_uuid_set["metric_1_id"]: [sample_measurement_entity]
        }

        # Mock different results for different strategies
        service_with_mocks._calculate_weighted_average = MagicMock(
            return_value=(75.0, {})
        )
        service_with_mocks._calculate_weighted_sum_normalized = MagicMock(
            return_value=(50.0, {})
        )

        # Act - strategy 1
        score_1, _ = service_with_mocks._apply_aggregation_strategy(
            MagicMock(aggregation_strategy=AggregationStrategy.WEIGHTED_AVERAGE),
            [sample_metric_entity],
            measurements_by_metric
        )

        # Act - strategy 2
        score_2, _ = service_with_mocks._apply_aggregation_strategy(
            MagicMock(aggregation_strategy=AggregationStrategy.WEIGHTED_SUM_NORMALIZED),
            [sample_metric_entity],
            measurements_by_metric
        )

        # Assert
        assert score_1 != score_2

    def test_bb_017_component_metrics_breakdown(
        self, service_with_mocks, sample_uuid_set, sample_criterion_entity,
        sample_metric_entity, sample_measurement_entity
    ):
        """
        BB-017: Equivalence Partition - Component metrics breakdown.
        
        Expected: component_metrics dict contiene todas las métricas
        """
        # Arrange
        measurements_by_metric = {
            sample_uuid_set["metric_1_id"]: [sample_measurement_entity]
        }

        service_with_mocks._calculate_weighted_average = MagicMock(
            return_value=(75.0, {
                str(sample_uuid_set["metric_1_id"]): {
                    "name": "Metric 1",
                    "value": 75.0,
                    "weight": 1.0,
                    "contribution": 75.0
                }
            })
        )

        # Act
        score, components = service_with_mocks._apply_aggregation_strategy(
            sample_criterion_entity,
            [sample_metric_entity],
            measurements_by_metric
        )

        # Assert
        assert len(components) == 1
        assert str(sample_uuid_set["metric_1_id"]) in components

    def test_bb_018_floating_point_precision(self, service_with_mocks):
        """
        BB-018: Boundary Value Analysis - Floating point precision.
        
        Expected: Resultado dentro de tolerancia aceptable
        """
        # Arrange
        metric = MagicMock(spec=Metric)
        metric.id = UUID("11111111-1111-1111-1111-111111111111")
        metric.weight = 0.1

        measurement = MagicMock(spec=Measurement)
        measurement.value = 0.3
        measurement.date = datetime.now(timezone.utc)

        measurements_by_metric = {
            metric.id: [measurement]
        }

        criterion = MagicMock(spec=EvaluationCriterion)
        criterion.weight = 1.0

        # Act
        score, components = service_with_mocks._calculate_weighted_average(
            criterion,
            [metric],
            measurements_by_metric
        )

        # Assert
        # 0.3 * 0.1 / 0.1 * 1 = 0.3 (within FP tolerance)
        assert pytest.approx(score, rel=1e-6) == pytest.approx(0.3, rel=1e-6)

    def test_bb_019_tool_total_score_zero(
        self, service_with_mocks, sample_uuid_set
    ):
        """
        BB-019: Equivalence Partition - Tool total score = 0.
        
        Expected: total_score=0.0
        """
        # Arrange
        score_1 = MagicMock()
        score_1.score = 0.0

        score_2 = MagicMock()
        score_2.score = 0.0

        service_with_mocks.score_repo.get_by_tool_configuration.return_value = [
            score_1, score_2
        ]

        # Act
        result = service_with_mocks.calculate_and_update_tool_total_score(
            sample_uuid_set["tool_config_id"]
        )

        # Assert
        assert pytest.approx(result, rel=1e-6) == 0.0

    def test_bb_020_tool_total_score_large_sum(
        self, service_with_mocks, sample_uuid_set
    ):
        """
        BB-020: Equivalence Partition - Tool total score suma grande.
        
        Expected: total_score=450
        """
        # Arrange
        scores = [MagicMock(score=val) for val in [100.0, 200.0, 150.0]]

        service_with_mocks.score_repo.get_by_tool_configuration.return_value = scores

        # Act
        result = service_with_mocks.calculate_and_update_tool_total_score(
            sample_uuid_set["tool_config_id"]
        )

        # Assert
        assert pytest.approx(result, rel=1e-6) == 450.0

    def test_bb_021_inactive_measurement_excluded(
        self, service_with_mocks, sample_uuid_set
    ):
        """
        BB-021: Equivalence Partition - Medición inactiva excluida.
        
        Expected: Excluida de cálculo (query filtra)
        """
        # Arrange
        inactive_measurement = MagicMock(spec=Measurement)
        inactive_measurement.is_active = False

        # Query should filter out inactive
        service_with_mocks.db.query.return_value.filter.return_value.all.return_value = []

        # Act
        result = service_with_mocks._get_measurements_for_metric_and_tool(
            sample_uuid_set["metric_1_id"],
            sample_uuid_set["tool_config_id"]
        )

        # Assert
        assert len(result) == 0

    def test_bb_023_enum_parsing_case_insensitive_attempt(self, service_with_mocks):
        """
        BB-023: Equivalence Partition - Enum parsing con case mismatch.
        
        Expected: ValidationError or case-insensitive parsing
        """
        # Act & Assert
        # Python enum is case-sensitive, so this should fail
        with pytest.raises(ValidationError):
            service_with_mocks._parse_aggregation_strategy("WeIgHeD_AvErAgE")

    def test_bb_024_direction_enum_vs_string(
        self, service_with_mocks, sample_uuid_set
    ):
        """
        BB-024: Equivalence Partition - Direction enum vs string.
        
        Expected: Ambos manejados equivalentemente
        """
        # Arrange
        metric_enum = MagicMock(spec=Metric)
        metric_enum.id = sample_uuid_set["metric_1_id"]
        metric_enum.direction = Direction.HIGHER_IS_BETTER

        metric_string = MagicMock(spec=Metric)
        metric_string.id = sample_uuid_set["metric_2_id"]
        metric_string.direction = "higher_is_better"

        # Act
        direction_enum_str = service_with_mocks._get_direction_string(metric_enum.direction)
        direction_string_str = service_with_mocks._get_direction_string(metric_string.direction)

        # Assert
        # Both should produce the same string representation
        assert direction_enum_str.lower() == direction_string_str.lower()
