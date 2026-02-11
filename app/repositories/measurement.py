"""
Repository for Measurement entity.

This repository handles measurement creation and updates with automatic
score recalculation logic based on metric type and value changes.
"""
from typing import List, Optional
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.domain import Measurement, Metric
from app.repositories.base_repository import BaseRepository
from app.schemas.measurement import MeasurementCreate, MeasurementUpdate


class MeasurementRepository(BaseRepository[Measurement]):
    """
    Repository for managing Measurement entities.
    
    Includes automatic score recalculation when measurements are created or updated.
    """
    
    def __init__(self, db: Session):
        """Initialize the repository."""
        super().__init__(Measurement, db)
    
    def create(
        self,
        schema: MeasurementCreate,
        auto_calculate_score: bool = True
    ) -> Measurement:
        """
        Create a new measurement with optional auto score calculation.
        
        When a new measurement is created:
        - If it's a cardinal metric and sets a new max value, recalculates all scores for the criterion
        - Otherwise, recalculates only the affected aggregated score
        
        Args:
            schema: Measurement creation data
            auto_calculate_score: Whether to automatically recalculate scores
            
        Returns:
            Created measurement
        """
        # Capture previous max for cardinal metrics
        metric_id = schema.metric_id
        metric = self.db.query(Metric).filter(Metric.id == metric_id).first()
        previous_max = None
        is_cardinal = False
        
        if metric:
            unit_value = metric.unit if isinstance(metric.unit, str) else metric.unit.value
            is_cardinal = unit_value.lower() == "cardinal"
            
            if is_cardinal:
                previous_max = self.db.query(func.max(Measurement.value)).filter(
                    Measurement.metric_id == metric_id,
                    Measurement.is_active == True
                ).scalar()
        
        # Create the measurement
        db_obj = Measurement(**schema.model_dump())
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        
        # Handle score recalculation
        if auto_calculate_score:
            self._handle_score_recalculation(
                db_obj, metric, is_cardinal, previous_max
            )
        
        return db_obj
    
    def get_by_id(self, id: UUID) -> Optional[Measurement]:
        """
        Get measurement by ID.
        
        Args:
            id: Measurement UUID
            
        Returns:
            Measurement if found, None otherwise
        """
        return self.get(id)
    
    def get_all(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Measurement]:
        """Get all measurements with pagination ordered by most recent first.

        The previous implementation delegated to the generic ``get_multi`` which
        had no ordering clause – meaning PostgreSQL could return arbitrary rows
        (often oldest first) once the table grew beyond the requested ``limit``.
        When more than ``limit`` active measurements existed, newly added ones
        could be excluded from the first page and the frontend (which only
        requested the first page) would not find a measurement for the metric,
        rendering "-".

        Ordering descending by ``date`` ensures the newest measurements are
        always included in the first page making the UI consistent and fixing
        the intermittent "-" display after add/edit.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of measurements ordered by date descending
        """
        return self.db.query(self.model).filter(
            self.model.is_active == True
        ).order_by(self.model.date.desc()).offset(skip).limit(limit).all()
    
    def get_by_llm_tool_configuration(
        self,
        llm_tool_configuration_id: UUID
    ) -> List[Measurement]:
        """
        Get measurements by LLM tool configuration ID.
        
        Args:
            llm_tool_configuration_id: LLM tool configuration UUID
            
        Returns:
            List of measurements for the configuration
        """
        return self.db.query(self.model).filter(
            self.model.llm_tool_configuration_id == llm_tool_configuration_id,
            self.model.is_active == True
        ).all()
    
    def update(
        self,
        id: UUID,
        schema: MeasurementUpdate,
        auto_calculate_score: bool = True
    ) -> Optional[Measurement]:
        """
        Update a measurement with optional auto score calculation.
        
        Args:
            id: Measurement UUID
            schema: Update data
            auto_calculate_score: Whether to automatically recalculate scores
            
        Returns:
            Updated measurement if found, None otherwise
        """
        db_obj = self.get(id)
        if not db_obj:
            return None
        
        # Capture previous max for cardinal metrics before update
        metric = self.db.query(Metric).filter(Metric.id == db_obj.metric_id).first()
        previous_max = None
        is_cardinal = False
        
        if metric:
            unit_value = metric.unit if isinstance(metric.unit, str) else metric.unit.value
            is_cardinal = unit_value.lower() == "cardinal"
            
            if is_cardinal:
                previous_max = self.db.query(func.max(Measurement.value)).filter(
                    Measurement.metric_id == metric.id,
                    Measurement.is_active == True
                ).scalar()
        
        # Update the measurement
        updated_measurement = super().update(db_obj, schema)
        
        if not updated_measurement:
            return None
        
        # Handle score recalculation
        if auto_calculate_score:
            self._handle_score_recalculation(
                updated_measurement, metric, is_cardinal, previous_max
            )
        
        return updated_measurement
    
    def delete(self, id: UUID) -> bool:
        """
        Delete a measurement and trigger score recalculation.
        
        Args:
            id: Measurement UUID
            
        Returns:
            True if deleted, False otherwise
        """
        # Get measurement before deletion to access its attributes
        measurement = self.get(id)
        if not measurement:
            return False
        
        # Store needed IDs before soft delete
        tool_config_id = measurement.llm_tool_configuration_id
        metric_id = measurement.metric_id
        
        # Get metric to find criterion
        metric = self.db.query(Metric).filter(Metric.id == metric_id).first()
        
        # Perform soft delete
        result = super().delete(id)
        
        if result and metric:
            # Trigger recalculation for the affected criterion/tool config
            try:
                from app.services.score_aggregation import ScoreAggregationService
                
                aggregation_service = ScoreAggregationService(self.db)
                print(
                    f"[AUTO-CALC] Measurement deleted, recalculating score for "
                    f"criterion {metric.evaluation_criterion_id}, tool {tool_config_id}"
                )
                
                # Try to recalculate the score (may fail if no measurements left)
                try:
                    aggregation_service.calculate_and_store_score(
                        criterion_id=metric.evaluation_criterion_id,
                        tool_config_id=tool_config_id
                    )
                except Exception:
                    # If no measurements left for this criterion/tool combo, that's OK
                    print(
                        f"[AUTO-CALC] No measurements left for criterion "
                        f"{metric.evaluation_criterion_id}, tool {tool_config_id}"
                    )
                
                # Update total score for the tool configuration
                aggregation_service.calculate_and_update_tool_total_score(tool_config_id)
                
            except Exception as e:
                print(f"[AUTO-CALC] Error during score recalculation after delete: {e}")
                import traceback
                traceback.print_exc()
        
        return result is not None
    
    # =========================================================================
    # Private Helper Methods
    # =========================================================================
    
    def _handle_score_recalculation(
        self,
        measurement: Measurement,
        metric: Optional[Metric],
        is_cardinal: bool,
        previous_max: Optional[float]
    ) -> None:
        """
        Handle score recalculation logic after measurement creation/update.
        
        Strategy:
        - For cardinal metrics with new max value: recalculate all scores for the criterion
        - For other cases: recalculate only the affected score
        
        Args:
            measurement: The created/updated measurement
            metric: Associated metric (if found)
            is_cardinal: Whether the metric is cardinal
            previous_max: Previous maximum value for cardinal metrics
        """
        if not metric:
            return
        
        performed_full_recalc = False
        
        # Check if we need full recalculation (new max for cardinal metric)
        if is_cardinal and self._is_new_maximum(measurement.value, previous_max):
            performed_full_recalc = self._recalculate_all_scores_for_criterion(
                metric.evaluation_criterion_id,
                metric.id,
                measurement.value
            )
        
        # If not full recalc, recalc only affected score
        if not performed_full_recalc:
            self._recalculate_single_score(measurement, metric)
    
    def _is_new_maximum(
        self,
        current_value: float,
        previous_max: Optional[float]
    ) -> bool:
        """Check if current value is a new maximum."""
        return previous_max is None or current_value > (previous_max or 0)
    
    def _recalculate_all_scores_for_criterion(
        self,
        criterion_id: UUID,
        metric_id: UUID,
        new_max_value: float
    ) -> bool:
        """
        Recalculate all scores for a criterion (full recalculation).
        
        Returns:
            True if successful, False otherwise
        """
        try:
            from app.services.score_aggregation import ScoreAggregationService
            
            aggregation_service = ScoreAggregationService(self.db)
            print(
                f"[AUTO-CALC] New max value {new_max_value} for metric {metric_id}; "
                f"full recalculation for criterion {criterion_id}"
            )
            recalculated_scores = aggregation_service.recalculate_all_scores_for_criterion(criterion_id)
            
            # Update total scores for all affected tool configurations
            affected_tool_configs = {score.tool_config_id for score in recalculated_scores}
            for tool_config_id in affected_tool_configs:
                aggregation_service.calculate_and_update_tool_total_score(tool_config_id)
            
            return True
        except Exception as e:
            print(f"[AUTO-CALC] Error during full recalculation: {e}")
            return False
    
    def _recalculate_single_score(
        self,
        measurement: Measurement,
        metric: Metric
    ) -> None:
        """
        Recalculate a single aggregated score for the measurement's configuration.
        
        Args:
            measurement: The measurement
            metric: Associated metric
        """
        try:
            from app.services.score_aggregation import ScoreAggregationService
            
            aggregation_service = ScoreAggregationService(self.db)
            print(
                f"[AUTO-CALC] Calculating score for criterion {metric.evaluation_criterion_id}, "
                f"tool {measurement.llm_tool_configuration_id}"
            )
            score = aggregation_service.calculate_and_store_score(
                criterion_id=metric.evaluation_criterion_id,
                tool_config_id=measurement.llm_tool_configuration_id
            )
            print(f"[AUTO-CALC] Successfully calculated score: {score.score}")
            
            # Update the total score for the tool configuration
            aggregation_service.calculate_and_update_tool_total_score(
                measurement.llm_tool_configuration_id
            )
        except Exception as e:
            # Log error but don't fail the measurement operation
            print(f"[AUTO-CALC] Error calculating aggregated score: {e}")
            import traceback
            traceback.print_exc()
