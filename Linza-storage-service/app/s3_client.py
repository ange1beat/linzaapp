import os
import threading
import boto3
from botocore.config import Config

_lock = threading.Lock()

_config = {
    "aws_access_key_id": os.getenv("S3_ACCESS_KEY_ID", ""),
    "aws_secret_access_key": os.getenv("S3_SECRET_ACCESS_KEY", ""),
    "endpoint_url": os.getenv("S3_ENDPOINT_URL", "https://s3.twcstorage.ru"),
    "bucket_name": os.getenv("S3_BUCKET_NAME", "5aca33a6-7dff-49cb-8069-3442ccb455c3"),
    "region": os.getenv("S3_REGION", "ru-1"),
}


def _int_env(name: str, default: int) -> int:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        return max(1, int(raw))
    except ValueError:
        return default


def _create_client():
    # Стриминг get_object (видео, Range) — между chunk'ами S3 может «молчать» дольше дефолтных ~60 с.
    read_to = _int_env("S3_READ_TIMEOUT", 600)
    conn_to = _int_env("S3_CONNECT_TIMEOUT", 60)
    return boto3.client(
        "s3",
        aws_access_key_id=_config["aws_access_key_id"],
        aws_secret_access_key=_config["aws_secret_access_key"],
        endpoint_url=_config["endpoint_url"],
        region_name=_config["region"],
        config=Config(
            signature_version="s3v4",
            connect_timeout=conn_to,
            read_timeout=read_to,
            retries={"max_attempts": 8, "mode": "adaptive"},
        ),
    )

_client = _create_client()

def get_s3():
    return _client

def get_bucket():
    return _config["bucket_name"]

def get_config():
    """Return current config (without secret key)."""
    return {
        "endpoint_url": _config["endpoint_url"],
        "access_key_id": _config["aws_access_key_id"][:8] + "..." if _config["aws_access_key_id"] else "",
        "bucket_name": _config["bucket_name"],
        "region": _config["region"],
    }

def reconfigure(endpoint_url=None, access_key_id=None, secret_access_key=None, bucket_name=None, region=None):
    """Hot-reload S3 configuration and recreate boto3 client."""
    global _client
    with _lock:
        if endpoint_url is not None:
            _config["endpoint_url"] = endpoint_url
        if access_key_id is not None:
            _config["aws_access_key_id"] = access_key_id
        if secret_access_key is not None:
            _config["aws_secret_access_key"] = secret_access_key
        if bucket_name is not None:
            _config["bucket_name"] = bucket_name
        if region is not None:
            _config["region"] = region
        _client = _create_client()
