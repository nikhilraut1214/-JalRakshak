"""Initial schema

Revision ID: 9a603d78e13c
Revises: 
Create Date: 2026-09-26 23:23:08.358648

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9a603d78e13c'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'audit_events',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('entity_type', sa.String(), nullable=False),
        sa.Column('entity_id', sa.String(), nullable=False),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('from_state', sa.String(), nullable=True),
        sa.Column('to_state', sa.String(), nullable=True),
        sa.Column('performed_by', sa.String(), nullable=False),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audit_events_entity_id'), 'audit_events', ['entity_id'], unique=False)

    op.create_table(
        'users',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('organization_id', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_organization_id'), 'users', ['organization_id'], unique=False)

    op.create_table(
        'meters',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('location_label', sa.String(), nullable=False),
        sa.Column('meter_type', sa.String(), nullable=False),
        sa.Column('owner_id', sa.String(), nullable=True),
        sa.Column('organization_id', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_meters_organization_id'), 'meters', ['organization_id'], unique=False)
    op.create_index(op.f('ix_meters_owner_id'), 'meters', ['owner_id'], unique=False)

    op.create_table(
        'alerts',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('meter_id', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('severity', sa.String(), nullable=False),
        sa.Column('risk_score', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['meter_id'], ['meters.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_alerts_meter_id'), 'alerts', ['meter_id'], unique=False)

    op.create_table(
        'readings',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('meter_id', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('reading_liters', sa.Float(), nullable=False),
        sa.Column('raw_or_derived', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['meter_id'], ['meters.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_meter_timestamp', 'readings', ['meter_id', 'timestamp'], unique=False)
    op.create_index(op.f('ix_readings_meter_id'), 'readings', ['meter_id'], unique=False)
    op.create_index(op.f('ix_readings_timestamp'), 'readings', ['timestamp'], unique=False)

    op.create_table(
        'alert_evidence',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('alert_id', sa.String(), nullable=False),
        sa.Column('current_usage_liters', sa.Float(), nullable=False),
        sa.Column('baseline_liters', sa.Float(), nullable=False),
        sa.Column('deviation_pct', sa.Float(), nullable=False),
        sa.Column('persistence_intervals', sa.Integer(), nullable=False),
        sa.Column('trend', sa.String(), nullable=False),
        sa.Column('estimated_excess_liters', sa.Float(), nullable=False),
        sa.Column('risk_score', sa.Float(), nullable=False),
        sa.Column('severity', sa.String(), nullable=False),
        sa.Column('verification_required', sa.Boolean(), nullable=False),
        sa.Column('raw_evidence_json', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['alert_id'], ['alerts.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_alert_evidence_alert_id'), 'alert_evidence', ['alert_id'], unique=True)

    op.create_table(
        'explanations',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('alert_id', sa.String(), nullable=False),
        sa.Column('language', sa.String(), nullable=False),
        sa.Column('explanation', sa.Text(), nullable=False),
        sa.Column('source', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['alert_id'], ['alerts.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_explanations_alert_id'), 'explanations', ['alert_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_explanations_alert_id'), table_name='explanations')
    op.drop_table('explanations')
    op.drop_index(op.f('ix_alert_evidence_alert_id'), table_name='alert_evidence')
    op.drop_table('alert_evidence')
    op.drop_index(op.f('ix_readings_timestamp'), table_name='readings')
    op.drop_index(op.f('ix_readings_meter_id'), table_name='readings')
    op.drop_index('idx_meter_timestamp', table_name='readings')
    op.drop_table('readings')
    op.drop_index(op.f('ix_alerts_meter_id'), table_name='alerts')
    op.drop_table('alerts')
    op.drop_index(op.f('ix_meters_owner_id'), table_name='meters')
    op.drop_index(op.f('ix_meters_organization_id'), table_name='meters')
    op.drop_table('meters')
    op.drop_index(op.f('ix_users_organization_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_audit_events_entity_id'), table_name='audit_events')
    op.drop_table('audit_events')
