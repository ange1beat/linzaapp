from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.s3_client import get_config, reconfigure, get_s3, get_bucket

router = APIRouter()


class S3ConfigUpdate(BaseModel):
    endpoint_url: str | None = None
    access_key_id: str | None = None
    secret_access_key: str | None = None
    bucket_name: str | None = None
    region: str | None = None


@router.get("/s3")
def current_config():
    return get_config()


@router.put("/s3")
def update_config(body: S3ConfigUpdate):
    reconfigure(
        endpoint_url=body.endpoint_url,
        access_key_id=body.access_key_id,
        secret_access_key=body.secret_access_key,
        bucket_name=body.bucket_name,
        region=body.region,
    )
    return {"status": "ok", "config": get_config()}


@router.post("/s3/test")
def test_connection():
    try:
        resp = get_s3().list_objects_v2(Bucket=get_bucket(), MaxKeys=1)
        return {"status": "ok", "bucket": get_bucket(), "objects": resp.get("KeyCount", 0)}
    except Exception as e:
        raise HTTPException(502, f"S3 connection failed: {e}")
