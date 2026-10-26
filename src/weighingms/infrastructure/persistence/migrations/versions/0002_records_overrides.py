"""Immutable weighing records and supervisor overrides.

Revision ID: 0002
Revises: 0001
"""

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision: str | None = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "weighing_records",
        sa.Column("record_id", sa.String, primary_key=True),
        sa.Column(
            "session_id",
            sa.String,
            sa.ForeignKey("weighing_sessions.session_id"),
            nullable=False,
        ),
        sa.Column("batch_id", sa.String, nullable=False, index=True),
        sa.Column("component_id", sa.String, nullable=False),
        sa.Column("dyestuff_code", sa.String, nullable=False),
        sa.Column("dyestuff_name", sa.String, nullable=False),
        sa.Column("unit", sa.String, nullable=False),
        sa.Column("target_value", sa.String, nullable=False),
        sa.Column("actual_value", sa.String, nullable=False),
        sa.Column("tolerance_min", sa.String, nullable=False),
        sa.Column("tolerance_max", sa.String, nullable=False),
        sa.Column("result", sa.String, nullable=False),
        sa.Column("surplus_value", sa.String),
        sa.Column("operator_id", sa.String, nullable=False),
        sa.Column("lot_id", sa.String, nullable=False),
        sa.Column("container_id", sa.String, nullable=False),
        sa.Column("tare_value", sa.String, nullable=False),
        sa.Column("tare_unit", sa.String, nullable=False),
        sa.Column("scale_id", sa.String, nullable=False),
        sa.Column("confirmed_at", sa.String, nullable=False),
        sa.UniqueConstraint("session_id", "component_id", name="ux_one_record_per_component"),
    )
    op.create_table(
        "overrides",
        sa.Column("override_id", sa.String, primary_key=True),
        sa.Column(
            "record_id",
            sa.String,
            sa.ForeignKey("weighing_records.record_id"),
            nullable=False,
            unique=True,
        ),
        sa.Column("supervisor_id", sa.String, nullable=False),
        sa.Column("reason", sa.Text, nullable=False),
        sa.Column("authorised_at", sa.String, nullable=False),
    )


def downgrade() -> None:
    op.drop_table("overrides")
    op.drop_table("weighing_records")
