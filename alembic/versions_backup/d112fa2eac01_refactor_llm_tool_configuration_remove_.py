"""refactor_llm_tool_configuration_remove_metric_id

Revision ID: d112fa2eac01
Revises: 1a21ef2e0fc8
Create Date: 2025-10-14 23:12:00.113870

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd112fa2eac01'
down_revision: Union[str, None] = '1a21ef2e0fc8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add metric_id to measurements table
    op.add_column('measurements', sa.Column('metric_id', sa.UUID(), nullable=True))
    op.create_foreign_key(
        'fk_measurements_metric_id', 'measurements', 'metrics', 
        ['metric_id'], ['id']
    )
    
    # Drop the foreign key constraint from llm_tool_configurations to metrics
    op.drop_constraint('llm_tool_configurations_metric_id_fkey', 'llm_tool_configurations', type_='foreignkey')
    
    # Drop metric_id column from llm_tool_configurations
    op.drop_column('llm_tool_configurations', 'metric_id')


def downgrade() -> None:
    # Add back metric_id to llm_tool_configurations
    op.add_column('llm_tool_configurations', sa.Column('metric_id', sa.UUID(), nullable=True))
    op.create_foreign_key(
        'llm_tool_configurations_metric_id_fkey', 'llm_tool_configurations', 'metrics',
        ['metric_id'], ['id']
    )
    
    # Remove metric_id from measurements
    op.drop_constraint('fk_measurements_metric_id', 'measurements', type_='foreignkey')
    op.drop_column('measurements', 'metric_id')
