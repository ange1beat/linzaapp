"""Tests for app/s3_client.py — reconfigure(), thread safety, get_s3/get_bucket."""

import os
import threading

import app.s3_client as s3_module


_ORIGINAL_BUCKET = os.getenv("S3_BUCKET_NAME", "5aca33a6-7dff-49cb-8069-3442ccb455c3")
_ORIGINAL_REGION = os.getenv("S3_REGION", "ru-1")
_ORIGINAL_ENDPOINT = os.getenv("S3_ENDPOINT_URL", "https://s3.twcstorage.ru")


def _restore_defaults():
    s3_module.reconfigure(
        endpoint_url=_ORIGINAL_ENDPOINT,
        bucket_name=_ORIGINAL_BUCKET,
        region=_ORIGINAL_REGION,
        access_key_id=os.getenv("S3_ACCESS_KEY_ID", ""),
        secret_access_key=os.getenv("S3_SECRET_ACCESS_KEY", ""),
    )


class TestReconfigureBasic:
    """reconfigure() updates config and recreates the boto3 client."""

    def test_reconfigure_updates_bucket(self):
        s3_module.reconfigure(bucket_name="test-bucket-xyz")
        assert s3_module.get_bucket() == "test-bucket-xyz"
        _restore_defaults()

    def test_reconfigure_returns_new_client(self):
        old_client = s3_module.get_s3()
        s3_module.reconfigure(
            endpoint_url="https://s3.example.com",
            bucket_name="new-bucket",
            region="us-east-1",
            access_key_id="KEY123",
            secret_access_key="SECRET456",
        )
        new_client = s3_module.get_s3()
        assert new_client is not old_client
        _restore_defaults()

    def test_get_config_masks_secret_key(self):
        s3_module.reconfigure(
            access_key_id="ABCDEFGHIJ",
            secret_access_key="supersecret",
        )
        cfg = s3_module.get_config()
        assert "supersecret" not in str(cfg)
        assert cfg["access_key_id"].startswith("ABCDEFGH")
        assert cfg["access_key_id"].endswith("...")
        _restore_defaults()

    def test_partial_reconfigure_preserves_other_fields(self):
        s3_module.reconfigure(bucket_name="partial-bucket")
        cfg = s3_module.get_config()
        # Other fields not touched
        assert cfg["bucket_name"] == "partial-bucket"
        assert cfg["endpoint_url"] == _ORIGINAL_ENDPOINT
        _restore_defaults()


class TestReconfigureConcurrency:
    """reconfigure() is protected by a lock — concurrent calls must not corrupt state."""

    def test_concurrent_reconfigurations_no_errors(self):
        """Ten threads calling reconfigure() simultaneously — no exceptions."""
        errors = []

        def _reconfigure(i: int):
            try:
                s3_module.reconfigure(
                    bucket_name=f"bucket-{i}",
                    region="us-east-1",
                    endpoint_url="https://s3.example.com",
                    access_key_id=f"KEY{i:04d}",
                    secret_access_key=f"SECRET{i:04d}",
                )
            except Exception as exc:  # noqa: BLE001
                errors.append(exc)

        threads = [threading.Thread(target=_reconfigure, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=5)

        assert not errors, f"Errors during concurrent reconfigure: {errors}"
        # get_s3() must return a non-None client after all threads finish
        assert s3_module.get_s3() is not None
        _restore_defaults()

    def test_get_s3_during_reconfigure_always_returns_object(self):
        """get_s3() must never return None even while reconfigure() runs in another thread."""
        errors = []
        nones_seen = []

        def _reconfigurer():
            for i in range(30):
                try:
                    s3_module.reconfigure(
                        bucket_name=f"bucket-{i}",
                        region="us-east-1",
                        endpoint_url="https://s3.example.com",
                        access_key_id=f"KEY{i}",
                        secret_access_key=f"SECRET{i}",
                    )
                except Exception as exc:  # noqa: BLE001
                    errors.append(exc)

        def _reader():
            for _ in range(100):
                c = s3_module.get_s3()
                if c is None:
                    nones_seen.append(True)

        t1 = threading.Thread(target=_reconfigurer)
        t2 = threading.Thread(target=_reader)
        t1.start()
        t2.start()
        t1.join(timeout=5)
        t2.join(timeout=5)

        assert not errors
        assert not nones_seen, "get_s3() returned None during concurrent reconfigure"
        _restore_defaults()
