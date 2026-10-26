"""Print log: every successful ticket print (original or reprint).

Revision ID: 0003
Revises: 0002
"""

import sqlalchemy as sa
from alembic import op

revision = "0003"
down_revision: str | None = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "print_jobs",
        sa.Column("print_id", sa.String, primary_key=True),
        sa.Column("session_id", sa.String, nullable=False, index=True),
        sa.Column("ticket_id", sa.String, nullable=False),
        sa.Column("reprint", sa.Boolean, nullable=False),
        sa.Column("operator_id", sa.String, nullable=False),
        sa.Column("printed_at", sa.String, nullable=False),
    )


def downgrade() -> None:
    op.drop_table("print_jobs")
