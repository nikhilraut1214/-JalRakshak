"""Add unique constraint to readings (meter_id, timestamp)

Revision ID: b4f8a7c2e19d
Revises: 9a603d78e13c
Create Date: 2026-09-27 11:55:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b4f8a7c2e19d'
down_revision: Union[str, Sequence[str], None] = '9a603d78e13c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema to enforce reading uniqueness on (meter_id, timestamp)."""
    with op.batch_alter_table('readings', schema=None) as batch_op:
        batch_op.create_unique_constraint('uq_readings_meter_timestamp', ['meter_id', 'timestamp'])


def downgrade() -> None:
    """Downgrade schema removing reading uniqueness on (meter_id, timestamp)."""
    with op.batch_alter_table('readings', schema=None) as batch_op:
        batch_op.drop_constraint('uq_readings_meter_timestamp', type_='unique')
