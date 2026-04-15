"""SQLAlchemy models for Linza Board.

Defines the database schema for all entities:
- User: system users with role-based access
- StorageProfile: S3 storage connection profiles
- AccessCredential: credentials for external data sources
- DataSource: configured data source endpoints
- AnalysisReport: stored video analysis results
- ErrorRecord: centralized error tracking records
"""

from sqlalchemy import (
    BigInteger, Boolean, Column, DateTime, ForeignKey, Integer, String, Text,
    UniqueConstraint,
)
from sqlalchemy.sql import func

from backend.database import Base


class Tenant(Base):
    """Organization / company. Top-level entity for multi-tenancy."""
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Team(Base):
    """Team within a tenant (e.g. department, market segment group)."""
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class User(Base):
    """System user account.

    Roles: superadmin (full access), admin (settings access), user (read-only).
    Created by another user (created_by FK) except the seed superadmin.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    login = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)  # bcrypt hash, input truncated to 72 chars
    email = Column(String, nullable=False)
    role = Column(String, nullable=False, default="user")  # superadmin, admin, user
    # JSON array of portal roles: administrator, operator, lawyer, chief_editor (PRD)
    portal_roles = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # Multi-tenancy: user belongs to a tenant and optionally a team
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True, index=True)
    # Extended profile fields
    phone_number = Column(String, nullable=True)
    telegram_username = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    # Storage quota tracking (bytes)
    storage_quota_bytes = Column(BigInteger, default=0)
    storage_used_bytes = Column(BigInteger, default=0)
    last_login_at = Column(DateTime(timezone=True), nullable=True)


class YandexOAuthState(Base):
    """Временная привязка state → user для OAuth callback (одноразовая, ~10 мин)."""

    __tablename__ = "yandex_oauth_states"

    state = Column(String(128), primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    # Origin из Referer при POST /start — редирект после Яндекса сюда (Docker: :8000, не :5173 из .env).
    frontend_base = Column(String(512), default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class UserYandexDiskToken(Base):
    """OAuth-токен Яндекс.Диска пользователя (личный импорт файлов)."""

    __tablename__ = "user_yandex_disk_tokens"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True, index=True)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, default="")
    expires_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class GoogleOAuthState(Base):
    """Временная привязка state → user для Google OAuth callback."""

    __tablename__ = "google_oauth_states"

    state = Column(String(128), primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    frontend_base = Column(String(512), default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class UserGoogleDriveToken(Base):
    """OAuth-токен Google Drive пользователя (личный импорт файлов)."""

    __tablename__ = "user_google_drive_tokens"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True, index=True)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, default="")
    expires_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class StorageProfile(Base):
    """S3-compatible storage connection profile.

    Two types: 'source' (read files from) and 'destination' (write results to).
    Only one profile per type can be active at a time (is_active flag).
    """
    __tablename__ = "storage_profiles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    profile_type = Column(String, nullable=False)  # "source" or "destination"
    s3_endpoint_url = Column(String, default="")    # S3-compatible endpoint URL
    s3_access_key_id = Column(String, default="")   # AWS access key
    s3_secret_access_key = Column(String, default="")  # AWS secret key
    s3_bucket_name = Column(String, default="")     # target bucket
    s3_region = Column(String, default="")           # AWS region
    s3_tenant_id = Column(String, default="")        # multi-tenant identifier
    is_active = Column(Boolean, default=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class AccessCredential(Base):
    """Credentials for accessing external data sources (SMB shares, HTTP endpoints)."""
    __tablename__ = "access_credentials"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)           # human-readable name
    domain = Column(String, default="")             # network domain
    login = Column(String, default="")              # username
    password_encrypted = Column(String, default="") # stored as plaintext (known limitation)
    workspace = Column(String, default="Default workspace")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class DataSource(Base):
    """Configured data source for video file discovery.

    Supports S3, HTTP, and SMB protocols. Links to AccessCredential
    for authentication when needed.
    """
    __tablename__ = "data_sources"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    path_type = Column(String, default="http")  # s3, http, smb
    path_url = Column(String, default="")       # source URL or path
    file_extensions = Column(String, default="mp4,avi,mkv,mov")  # comma-separated
    priority = Column(String, default="Normal")  # Normal, High, Low
    access_credential_id = Column(Integer, ForeignKey("access_credentials.id"), nullable=True)
    workspace = Column(String, default="Default workspace")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class VideoAnalysisQueueItem(Base):
    """Pending intent to run analysis on a file already in storage (mostly sources/)."""

    __tablename__ = "video_analysis_queue"

    id = Column(Integer, primary_key=True, index=True)
    storage_key = Column(String, nullable=False)
    origin = Column(String, default="source")
    status = Column(String, default="pending")
    detector_job_id = Column(String(128), nullable=True)
    report_id = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AnalysisReport(Base):
    """Stored result of video analysis.

    Contains the full JSON report with detected violations,
    linked to the source video file and data source.
    """
    __tablename__ = "analysis_reports"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)      # analyzed video filename
    report_name = Column(String, default="")       # JSON report file name
    source = Column(String, default="")            # originating data source name
    started_at = Column(String, default="")        # analysis start timestamp (ISO string)
    finished_at = Column(String, default="")       # analysis end timestamp (ISO string)
    match_count = Column(Integer, default=0)       # number of detected violations
    status = Column(String, default="processing")  # success, error, processing
    report_json = Column(Text, default="{}")       # full JSON report body
    # Портал PRD: маркировка контента, ревизия оператора, эскалация юристу
    content_marking = Column(String, nullable=True)  # clean | age_12 | age_16 | age_18 | banned
    revision_done = Column(Boolean, default=False)
    escalated = Column(Boolean, default=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class AppSetting(Base):
    """Key-value настройки приложения (конфиг мастера администратора и т.п.)."""

    __tablename__ = "app_settings"

    key = Column(String(64), primary_key=True, index=True)
    value = Column(Text, nullable=False)


class ErrorRecord(Base):
    """Centralized error tracking record.

    Errors are captured automatically by ErrorReporterMiddleware (HTTP 4xx/5xx
    responses and unhandled exceptions) and can also be reported manually
    through the API. Each error can be submitted as a GitHub Issue to the
    Linza-debug repository (https://github.com/BigDataQueen/Linza-debug/issues).

    Severity levels: critical, error, warning, info.
    Categories: ui, api, storage, auth, player, analytics, network.
    Status: 'new' (just recorded) or 'submitted' (sent to GitHub Issues).
    """
    __tablename__ = "error_records"

    id = Column(Integer, primary_key=True, index=True)
    service = Column(String, nullable=False, default="unknown")    # source service name
    severity = Column(String, nullable=False, default="error")     # critical/error/warning/info
    category = Column(String, default="")                          # ui/api/storage/auth/player/analytics/network
    message = Column(Text, nullable=False)                         # human-readable error description
    traceback = Column(Text, default=None)                         # full Python traceback if available
    endpoint = Column(String, default=None)                        # HTTP endpoint path (e.g. /api/reports)
    method = Column(String, default=None)                          # HTTP method (GET/POST/PUT/DELETE)
    status_code = Column(Integer, default=None)                    # HTTP response status code
    request_id = Column(String, default=None)                      # unique request identifier for tracing
    extra = Column(Text, default=None)                             # additional JSON context
    github_issue_url = Column(String, default=None)                # URL of created GitHub Issue (if submitted)
    status = Column(String, default="new")                         # 'new' or 'submitted'
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ---------------------------------------------------------------------------
# Phase 1: Multi-tenancy, teams, projects, sharing, storage quotas, OTP
# ---------------------------------------------------------------------------


class StorageQuota(Base):
    """Hierarchical storage quotas: tenant > team > user.

    scope_type determines what scope_id refers to:
      - "tenant" → tenants.id
      - "team"   → teams.id
      - "user"   → users.id
    """
    __tablename__ = "storage_quotas"
    __table_args__ = (
        UniqueConstraint("scope_type", "scope_id", name="uq_storage_quota_scope"),
    )

    id = Column(Integer, primary_key=True, index=True)
    scope_type = Column(String, nullable=False)   # "tenant" | "team" | "user"
    scope_id = Column(Integer, nullable=False)
    quota_bytes = Column(BigInteger, nullable=False)
    used_bytes = Column(BigInteger, default=0)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Project(Base):
    """Project with tenant scope, member management, and sharing."""
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    avatar_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ProjectMember(Base):
    """User membership in a project with a role."""
    __tablename__ = "project_members"
    __table_args__ = (
        UniqueConstraint("project_id", "user_id", name="uq_project_member"),
    )

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String, nullable=False, default="viewer")  # owner | editor | viewer
    added_at = Column(DateTime(timezone=True), server_default=func.now())


class ProjectShare(Base):
    """Polymorphic project sharing: share with user, team, or entire tenant."""
    __tablename__ = "project_shares"
    __table_args__ = (
        UniqueConstraint("project_id", "share_type", "share_target_id", name="uq_project_share"),
    )

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    share_type = Column(String, nullable=False)       # "user" | "team" | "tenant"
    share_target_id = Column(Integer, nullable=False)  # user.id | team.id | tenant.id
    permission = Column(String, nullable=False, default="view")  # "view" | "edit"
    shared_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ReportShare(Base):
    """Share an analysis report with another user."""
    __tablename__ = "report_shares"
    __table_args__ = (
        UniqueConstraint("report_id", "user_id", name="uq_report_share"),
    )

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("analysis_reports.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    permission = Column(String, nullable=False, default="view")  # "view" | "comment"
    shared_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class UserFavoriteProject(Base):
    """User's favorite projects."""
    __tablename__ = "user_favorite_projects"
    __table_args__ = (
        UniqueConstraint("user_id", "project_id", name="uq_user_fav_project"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class OtpChallenge(Base):
    """OTP challenge for multi-factor authentication (linza-admin compatibility)."""
    __tablename__ = "otp_challenges"

    id = Column(Integer, primary_key=True, index=True)
    state_token = Column(String, unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    otp_code = Column(String, nullable=False)  # hashed with bcrypt
    channel = Column(String, nullable=False)   # "email" | "sms"
    expires_at = Column(DateTime(timezone=True), nullable=False)
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
