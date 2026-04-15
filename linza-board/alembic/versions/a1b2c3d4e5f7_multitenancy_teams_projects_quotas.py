"""Multi-tenancy: tenants, teams, projects, sharing, storage quotas, OTP

Revision ID: a1b2c3d4e5f7
Revises: f0e1d2c3b4a5
Create Date: 2026-04-15
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a1b2c3d4e5f7"
down_revision: Union[str, None] = "f0e1d2c3b4a5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- New tables ---

    op.create_table(
        "tenants",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_tenants_id", "tenants", ["id"])
    op.create_index("ix_tenants_slug", "tenants", ["slug"], unique=True)

    op.create_table(
        "teams",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_teams_id", "teams", ["id"])
    op.create_index("ix_teams_tenant_id", "teams", ["tenant_id"])

    op.create_table(
        "storage_quotas",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("scope_type", sa.String(), nullable=False),
        sa.Column("scope_id", sa.Integer(), nullable=False),
        sa.Column("quota_bytes", sa.BigInteger(), nullable=False),
        sa.Column("used_bytes", sa.BigInteger(), server_default="0"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("scope_type", "scope_id", name="uq_storage_quota_scope"),
    )
    op.create_index("ix_storage_quotas_id", "storage_quotas", ["id"])

    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("avatar_url", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_projects_id", "projects", ["id"])
    op.create_index("ix_projects_tenant_id", "projects", ["tenant_id"])

    op.create_table(
        "project_members",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("project_id", sa.Integer(), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", sa.String(), nullable=False, server_default="viewer"),
        sa.Column("added_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("project_id", "user_id", name="uq_project_member"),
    )
    op.create_index("ix_project_members_id", "project_members", ["id"])
    op.create_index("ix_project_members_project_id", "project_members", ["project_id"])
    op.create_index("ix_project_members_user_id", "project_members", ["user_id"])

    op.create_table(
        "project_shares",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("project_id", sa.Integer(), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("share_type", sa.String(), nullable=False),
        sa.Column("share_target_id", sa.Integer(), nullable=False),
        sa.Column("permission", sa.String(), nullable=False, server_default="view"),
        sa.Column("shared_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("project_id", "share_type", "share_target_id", name="uq_project_share"),
    )
    op.create_index("ix_project_shares_id", "project_shares", ["id"])
    op.create_index("ix_project_shares_project_id", "project_shares", ["project_id"])

    op.create_table(
        "report_shares",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("report_id", sa.Integer(), sa.ForeignKey("analysis_reports.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("permission", sa.String(), nullable=False, server_default="view"),
        sa.Column("shared_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("report_id", "user_id", name="uq_report_share"),
    )
    op.create_index("ix_report_shares_id", "report_shares", ["id"])
    op.create_index("ix_report_shares_report_id", "report_shares", ["report_id"])
    op.create_index("ix_report_shares_user_id", "report_shares", ["user_id"])

    op.create_table(
        "user_favorite_projects",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("project_id", sa.Integer(), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "project_id", name="uq_user_fav_project"),
    )
    op.create_index("ix_user_favorite_projects_id", "user_favorite_projects", ["id"])
    op.create_index("ix_user_favorite_projects_user_id", "user_favorite_projects", ["user_id"])
    op.create_index("ix_user_favorite_projects_project_id", "user_favorite_projects", ["project_id"])

    op.create_table(
        "otp_challenges",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("state_token", sa.String(), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("otp_code", sa.String(), nullable=False),
        sa.Column("channel", sa.String(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("verified", sa.Boolean(), server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_otp_challenges_id", "otp_challenges", ["id"])
    op.create_index("ix_otp_challenges_state_token", "otp_challenges", ["state_token"], unique=True)

    # --- Extend users table ---

    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(sa.Column("tenant_id", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("team_id", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("phone_number", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("telegram_username", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("avatar_url", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("storage_quota_bytes", sa.BigInteger(), server_default="0"))
        batch_op.add_column(sa.Column("storage_used_bytes", sa.BigInteger(), server_default="0"))
        batch_op.add_column(sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True))
        batch_op.create_index("ix_users_tenant_id", ["tenant_id"])
        batch_op.create_index("ix_users_team_id", ["team_id"])
        batch_op.create_foreign_key("fk_users_tenant_id", "tenants", ["tenant_id"], ["id"])
        batch_op.create_foreign_key("fk_users_team_id", "teams", ["team_id"], ["id"])

    # --- Seed default tenant ---
    tenants = sa.table("tenants",
        sa.column("id", sa.Integer),
        sa.column("name", sa.String),
        sa.column("slug", sa.String),
    )
    op.bulk_insert(tenants, [{"id": 1, "name": "Default Organization", "slug": "default"}])

    # Assign all existing users to the default tenant
    op.execute("UPDATE users SET tenant_id = 1 WHERE tenant_id IS NULL")


def downgrade() -> None:
    op.execute("UPDATE users SET tenant_id = NULL")

    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_constraint("fk_users_team_id", type_="foreignkey")
        batch_op.drop_constraint("fk_users_tenant_id", type_="foreignkey")
        batch_op.drop_index("ix_users_team_id")
        batch_op.drop_index("ix_users_tenant_id")
        batch_op.drop_column("last_login_at")
        batch_op.drop_column("storage_used_bytes")
        batch_op.drop_column("storage_quota_bytes")
        batch_op.drop_column("avatar_url")
        batch_op.drop_column("telegram_username")
        batch_op.drop_column("phone_number")
        batch_op.drop_column("team_id")
        batch_op.drop_column("tenant_id")

    op.drop_table("otp_challenges")
    op.drop_table("user_favorite_projects")
    op.drop_table("report_shares")
    op.drop_table("project_shares")
    op.drop_table("project_members")
    op.drop_table("projects")
    op.drop_table("storage_quotas")
    op.drop_table("teams")
    op.drop_table("tenants")
