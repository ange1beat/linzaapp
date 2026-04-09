"""video_analysis_queue: detector_job_id, report_id, error_message

Revision ID: c4a7b2d1e9f0
Revises: 8eb1dba86d7a
Create Date: 2026-04-04

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "c4a7b2d1e9f0"
down_revision: Union[str, None] = "8eb1dba86d7a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("video_analysis_queue", sa.Column("detector_job_id", sa.String(length=128), nullable=True))
    op.add_column("video_analysis_queue", sa.Column("report_id", sa.Integer(), nullable=True))
    op.add_column("video_analysis_queue", sa.Column("error_message", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("video_analysis_queue", "error_message")
    op.drop_column("video_analysis_queue", "report_id")
    op.drop_column("video_analysis_queue", "detector_job_id")
