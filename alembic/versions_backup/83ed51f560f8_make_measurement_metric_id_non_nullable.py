"""make_measurement_metric_id_non_nullable

Revision ID: 83ed51f560f8
Revises: d112fa2eac01
Create Date: 2025-10-14 23:19:54.007752

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '83ed51f560f8'
down_revision: Union[str, None] = 'd112fa2eac01'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Make metric_id non-nullable in measurements
    op.alter_column('measurements', 'metric_id',
                    existing_type=sa.UUID(),
                    nullable=False)


def downgrade() -> None:
    # Make metric_id nullable again
    op.alter_column('measurements', 'metric_id',
                    existing_type=sa.UUID(),
                    nullable=True)
