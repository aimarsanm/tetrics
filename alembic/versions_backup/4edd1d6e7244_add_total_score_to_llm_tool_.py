"""add_total_score_to_llm_tool_configuration

Revision ID: 4edd1d6e7244
Revises: 33e7713440a5
Create Date: 2025-10-26 20:23:29.397080

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4edd1d6e7244'
down_revision: Union[str, None] = '33e7713440a5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add total_score column to llm_tool_configurations table
    op.add_column(
        'llm_tool_configurations',
        sa.Column('total_score', sa.Float(), nullable=True)
    )
    
    # Add total_score_updated_at column to llm_tool_configurations table
    op.add_column(
        'llm_tool_configurations',
        sa.Column('total_score_updated_at', sa.DateTime(), nullable=True)
    )


def downgrade() -> None:
    # Remove total_score_updated_at column
    op.drop_column('llm_tool_configurations', 'total_score_updated_at')
    
    # Remove total_score column
    op.drop_column('llm_tool_configurations', 'total_score')
