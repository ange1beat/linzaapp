"""analysis_reports: content_marking, revision_done, escalated

Revision ID: a1b2c3d4e5f6
Revises: f0e1d2c3b4a5
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "f0e1d2c3b4a5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("analysis_reports", sa.Column("content_marking", sa.String(length=32), nullable=True))
    op.add_column(
        "analysis_reports",
        sa.Column("revision_done", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    op.add_column(
        "analysis_reports",
        sa.Column("escalated", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )


def downgrade() -> None:
    op.drop_column("analysis_reports", "escalated")
    op.drop_column("analysis_reports", "revision_done")
    op.drop_column("analysis_reports", "content_marking")
