"""Core session tables: sessions, session components, station state, audit events.

Revision ID: 0001
Revises:
"""

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision: str | None = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "weighing_sessions",
        sa.Column("session_id", sa.String, primary_key=True),
        sa.Column("batch_id", sa.String, nullable=False),
        sa.Column("station_id", sa.String, nullable=False),
        sa.Column("status", sa.String, nullable=False),
        sa.Column("started_by", sa.String, nullable=False),
        sa.Column("started_at", sa.String, nullable=False),
        sa.Column("completed_at", sa.String),
        sa.Column("sync_status", sa.String, nullable=False),
        sa.Column("synced_at", sa.String),
        sa.Column("consumption_id", sa.String),
        sa.Column("recipe", sa.Text, nullable=False),
    )
    op.create_index(
        "ux_open_session_per_batch",
        "weighing_sessions",
        ["batch_id"],
        unique=True,
        sqlite_where=sa.text("status = 'IN_PROGRESS'"),
    )
    op.create_table(
        "session_components",
        sa.Column(
            "session_id",
            sa.String,
            sa.ForeignKey("weighing_sessions.session_id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("component_id", sa.String, primary_key=True),
        sa.Column("sequence", sa.Integer, nullable=False),
        sa.Column("state", sa.String, nullable=False),
        sa.Column("container_id", sa.String),
        sa.Column("tare_value", sa.String),
        sa.Column("tare_unit", sa.String),
        sa.Column("activated_at", sa.String),
        sa.Column("record_id", sa.String),
        sa.Column("actual_value", sa.String),
        sa.Column("actual_unit", sa.String),
    )
    op.create_table(
        "station_state",
        sa.Column("key", sa.String, primary_key=True),
        sa.Column("value", sa.String, nullable=False),
    )
    op.create_table(
        "audit_events",
        sa.Column("event_id", sa.String, primary_key=True),
        sa.Column("session_id", sa.String),
        sa.Column("type", sa.String, nullable=False),
        sa.Column("actor_id", sa.String, nullable=False),
        sa.Column("detail", sa.Text, nullable=False),
        sa.Column("occurred_at", sa.String, nullable=False),
    )


def downgrade() -> None:
    op.drop_table("audit_events")
    op.drop_table("station_state")
    op.drop_table("session_components")
    op.drop_index("ux_open_session_per_batch", table_name="weighing_sessions")
    op.drop_table("weighing_sessions")
