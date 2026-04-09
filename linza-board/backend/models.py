"""SQLAlchemy models for Linza Board.

Defines the database schema for all entities:
- User: system users with role-based access
- StorageProfile: S3 storage connection profiles
- AccessCredential: credentials for external data sources
- DataSource: configured data source endpoints
- AnalysisReport: stored video analysis results
- ErrorRecord: centralized error tracking records
"""

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func

from backend.database import Base


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
