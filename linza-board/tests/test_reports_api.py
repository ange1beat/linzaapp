"""Integration tests for /api/reports endpoints (board#28)."""


REPORT_DATA = {
    "filename": "video_001.mp4",
    "report_name": "Analysis #1",
    "source": "cdn.example.com",
    "started_at": "2026-04-03T10:00:00",
    "finished_at": "2026-04-03T10:05:00",
    "match_count": 3,
    "status": "success",
    "report_json": '{"detections": []}',
}


def test_list_reports_requires_auth(client):
    resp = client.get("/api/reports/")
    assert resp.status_code == 401


def test_list_reports_empty(client, auth_headers):
    resp = client.get("/api/reports/", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []


def test_create_report(client, auth_headers):
    resp = client.post("/api/reports/", json=REPORT_DATA, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["filename"] == "video_001.mp4"
    assert "id" in data


def test_get_report_detail(client, auth_headers):
    create = client.post("/api/reports/", json=REPORT_DATA, headers=auth_headers)
    rid = create.json()["id"]

    resp = client.get(f"/api/reports/{rid}", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["filename"] == "video_001.mp4"
    assert data["report_json"] == '{"detections": []}'
    assert data["match_count"] == 3


def test_get_report_not_found(client, auth_headers):
    resp = client.get("/api/reports/99999", headers=auth_headers)
    assert resp.status_code == 404


def test_patch_report_filename(client, auth_headers):
    create = client.post("/api/reports/", json=REPORT_DATA, headers=auth_headers)
    rid = create.json()["id"]

    resp = client.patch(
        f"/api/reports/{rid}",
        json={"filename": "uploads/new-key/video.mp4"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["filename"] == "uploads/new-key/video.mp4"

    detail = client.get(f"/api/reports/{rid}", headers=auth_headers).json()
    assert detail["filename"] == "uploads/new-key/video.mp4"
    assert detail["report_json"] == '{"detections": []}'


def test_patch_report_not_found(client, auth_headers):
    resp = client.patch(
        "/api/reports/99999",
        json={"filename": "x.mp4"},
        headers=auth_headers,
    )
    assert resp.status_code == 404


def test_delete_report(client, auth_headers):
    create = client.post("/api/reports/", json=REPORT_DATA, headers=auth_headers)
    rid = create.json()["id"]

    resp = client.delete(f"/api/reports/{rid}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "deleted"

    # Verify it's gone
    resp = client.get(f"/api/reports/{rid}", headers=auth_headers)
    assert resp.status_code == 404


def test_delete_report_not_found(client, auth_headers):
    resp = client.delete("/api/reports/99999", headers=auth_headers)
    assert resp.status_code == 404


def _token_active_role(client, role: str) -> str:
    r = client.post("/api/auth/login", json={"login": "admin", "password": "admin"})
    assert r.status_code == 200
    t = r.json()["access_token"]
    r2 = client.post(
        "/api/auth/switch-role",
        json={"active_role": role},
        headers={"Authorization": f"Bearer {t}"},
    )
    assert r2.status_code == 200
    return r2.json()["access_token"]


def test_operator_cannot_patch_marking_after_revision(client, auth_headers):
    """Суперадмин по умолчанию в контексте «оператор» — маркировка запрещена после revision_done."""
    create = client.post("/api/reports/", json=REPORT_DATA, headers=auth_headers)
    rid = create.json()["id"]
    r1 = client.patch(f"/api/reports/{rid}", json={"revision_done": True}, headers=auth_headers)
    assert r1.status_code == 200
    r2 = client.patch(
        f"/api/reports/{rid}",
        json={"content_marking": "age_12"},
        headers=auth_headers,
    )
    assert r2.status_code == 403


def test_administrator_can_patch_marking_after_revision(client):
    op_t = _token_active_role(client, "operator")
    adm_t = _token_active_role(client, "administrator")
    op_h = {"Authorization": f"Bearer {op_t}"}
    adm_h = {"Authorization": f"Bearer {adm_t}"}
    create = client.post("/api/reports/", json=REPORT_DATA, headers=op_h)
    rid = create.json()["id"]
    assert client.patch(f"/api/reports/{rid}", json={"revision_done": True}, headers=op_h).status_code == 200
    r2 = client.patch(
        f"/api/reports/{rid}",
        json={"content_marking": "age_16"},
        headers=adm_h,
    )
    assert r2.status_code == 200
    assert r2.json()["content_marking"] == "age_16"


def test_operator_cannot_patch_marking_when_escalated(client, auth_headers):
    create = client.post("/api/reports/", json=REPORT_DATA, headers=auth_headers)
    rid = create.json()["id"]
    assert client.patch(f"/api/reports/{rid}", json={"escalated": True}, headers=auth_headers).status_code == 200
    r2 = client.patch(
        f"/api/reports/{rid}",
        json={"content_marking": "clean"},
        headers=auth_headers,
    )
    assert r2.status_code == 403


def test_operator_cannot_deescalate(client, auth_headers):
    create = client.post("/api/reports/", json=REPORT_DATA, headers=auth_headers)
    rid = create.json()["id"]
    assert client.patch(f"/api/reports/{rid}", json={"escalated": True}, headers=auth_headers).status_code == 200
    r2 = client.patch(f"/api/reports/{rid}", json={"escalated": False}, headers=auth_headers)
    assert r2.status_code == 403


def test_lawyer_can_deescalate(client):
    op_t = _token_active_role(client, "operator")
    law_t = _token_active_role(client, "lawyer")
    op_h = {"Authorization": f"Bearer {op_t}"}
    law_h = {"Authorization": f"Bearer {law_t}"}
    create = client.post("/api/reports/", json=REPORT_DATA, headers=op_h)
    rid = create.json()["id"]
    assert client.patch(f"/api/reports/{rid}", json={"escalated": True}, headers=op_h).status_code == 200
    r2 = client.patch(f"/api/reports/{rid}", json={"escalated": False}, headers=law_h)
    assert r2.status_code == 200
    assert r2.json()["escalated"] is False


def test_operator_cannot_clear_revision_done(client, auth_headers):
    create = client.post("/api/reports/", json=REPORT_DATA, headers=auth_headers)
    rid = create.json()["id"]
    assert client.patch(f"/api/reports/{rid}", json={"revision_done": True}, headers=auth_headers).status_code == 200
    r2 = client.patch(f"/api/reports/{rid}", json={"revision_done": False}, headers=auth_headers)
    assert r2.status_code == 403


def test_chief_editor_can_clear_revision_done(client):
    op_t = _token_active_role(client, "operator")
    ed_t = _token_active_role(client, "chief_editor")
    op_h = {"Authorization": f"Bearer {op_t}"}
    ed_h = {"Authorization": f"Bearer {ed_t}"}
    create = client.post("/api/reports/", json=REPORT_DATA, headers=op_h)
    rid = create.json()["id"]
    assert client.patch(f"/api/reports/{rid}", json={"revision_done": True}, headers=op_h).status_code == 200
    r2 = client.patch(f"/api/reports/{rid}", json={"revision_done": False}, headers=ed_h)
    assert r2.status_code == 200
    assert r2.json()["revision_done"] is False
