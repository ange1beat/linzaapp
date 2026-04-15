"""E2E test: full user journey from login to project management.

Simulates the linza-admin frontend flow:
1. Login (POST /api/auth) → get stateToken
2. OTP challenge → resend email
3. OTP verify → confirm code
4. Sign-in → get accessToken (camelCase)
5. Get current user (/api/auth/me)
6. Get tenant (/api/tenants/my)
7. Create project
8. List projects
9. Toggle favorite
10. Add member to project
11. Share project with team
12. Create team
13. View storage quotas
14. Switch portal role
15. Update profile (name, telegram)
"""
import json

from backend.auth import hash_password
from backend.models import OtpChallenge, User


def _get_otp_code(db_session, state_token: str) -> str:
    """Get OTP challenge from DB and set a known code for testing."""
    challenge = db_session.query(OtpChallenge).filter(
        OtpChallenge.state_token == state_token
    ).first()
    assert challenge is not None, "OTP challenge not found in DB"
    # Set a known OTP code for testing
    challenge.otp_code = hash_password("123456")
    db_session.commit()
    return "123456"


def test_e2e_login_to_projects(client, db_session):
    """Full E2E: login → OTP → dashboard → projects → team → storage."""

    # =============================================
    # STEP 1: Login (compat endpoint, stateToken flow)
    # =============================================
    login_resp = client.post("/api/auth", json={
        "login": "admin",
        "password": "admin",
    })
    assert login_resp.status_code == 200, f"Login failed: {login_resp.json()}"
    login_data = login_resp.json()

    assert "stateToken" in login_data, "Missing stateToken in login response"
    assert "user" in login_data, "Missing user in login response"
    assert login_data["user"]["email"] == "admin@linza.local"
    assert isinstance(login_data["user"]["id"], str), "user.id should be string"

    state_token = login_data["stateToken"]
    print(f"  ✓ Step 1: Login OK, stateToken received")

    # =============================================
    # STEP 2: OTP Challenge (resend via email)
    # =============================================
    resend_resp = client.post("/api/auth/factors/otp/challenge/email", json={
        "stateToken": state_token,
    })
    assert resend_resp.status_code == 200
    print(f"  ✓ Step 2: OTP challenge email sent")

    # =============================================
    # STEP 3: OTP Verify
    # =============================================
    otp_code = _get_otp_code(db_session, state_token)

    verify_resp = client.post("/api/auth/factors/otp/verify", json={
        "stateToken": state_token,
        "passcode": otp_code,
    })
    assert verify_resp.status_code == 200, f"OTP verify failed: {verify_resp.json()}"
    verify_data = verify_resp.json()
    assert "stateToken" in verify_data
    assert "user" in verify_data
    print(f"  ✓ Step 3: OTP verified")

    # =============================================
    # STEP 4: Sign-in (exchange stateToken for accessToken)
    # =============================================
    signin_resp = client.post("/api/auth/sign-in", json={
        "stateToken": state_token,
    })
    assert signin_resp.status_code == 200, f"Sign-in failed: {signin_resp.json()}"
    signin_data = signin_resp.json()
    assert "accessToken" in signin_data, "Missing accessToken (camelCase) in sign-in response"

    access_token = signin_data["accessToken"]
    headers = {"Authorization": f"Bearer {access_token}"}
    print(f"  ✓ Step 4: Signed in, got accessToken")

    # =============================================
    # STEP 5: Get current user (/api/auth/me)
    # =============================================
    me_resp = client.get("/api/auth/me", headers=headers)
    assert me_resp.status_code == 200
    me_data = me_resp.json()

    assert me_data["login"] == "admin"
    assert me_data["role"] == "superadmin"
    assert me_data["first_name"] == "Super"
    assert me_data["last_name"] == "Admin"
    assert isinstance(me_data["portal_roles"], list)
    assert len(me_data["portal_roles"]) >= 1
    assert me_data["active_role"] in me_data["portal_roles"]
    assert me_data["tenant_id"] is not None, "User should have a tenant"
    assert isinstance(me_data.get("storage_quota_bytes"), int)
    assert isinstance(me_data.get("storage_used_bytes"), int)
    print(f"  ✓ Step 5: /me OK — {me_data['first_name']} {me_data['last_name']}, tenant={me_data['tenant_id']}, roles={me_data['portal_roles']}")

    # =============================================
    # STEP 6: Get tenant (/api/tenants/my)
    # =============================================
    tenant_resp = client.get("/api/tenants/my", headers=headers)
    assert tenant_resp.status_code == 200
    tenant_data = tenant_resp.json()
    assert tenant_data["name"] == "Default Organization"
    assert tenant_data["slug"] == "default"
    print(f"  ✓ Step 6: Tenant OK — {tenant_data['name']}")

    # =============================================
    # STEP 7: Create project
    # =============================================
    create_proj_resp = client.post("/api/projects/", headers=headers, json={
        "name": "E2E Test Project",
    })
    assert create_proj_resp.status_code == 201, f"Create project failed: {create_proj_resp.json()}"
    project = create_proj_resp.json()
    project_id = project["id"]
    assert project["name"] == "E2E Test Project"
    assert project["tenant_id"] == me_data["tenant_id"]
    print(f"  ✓ Step 7: Project created — id={project_id}")

    # =============================================
    # STEP 8: List projects
    # =============================================
    list_resp = client.get("/api/projects/", headers=headers)
    assert list_resp.status_code == 200
    list_data = list_resp.json()
    assert list_data["total"] >= 1
    found = any(p["id"] == project_id for p in list_data["projects"])
    assert found, "Created project not in list"
    print(f"  ✓ Step 8: Projects listed — total={list_data['total']}")

    # =============================================
    # STEP 9: Toggle favorite
    # =============================================
    fav_resp = client.post(f"/api/projects/{project_id}/favorite", headers=headers)
    assert fav_resp.status_code == 200
    assert fav_resp.json()["is_favorite"] is True

    favs_resp = client.get("/api/projects/favorites", headers=headers)
    assert favs_resp.status_code == 200
    assert any(p["id"] == project_id for p in favs_resp.json())
    print(f"  ✓ Step 9: Favorite toggled — is_favorite=True")

    # =============================================
    # STEP 10: Create a test user and add as project member
    # =============================================
    test_user = User(
        first_name="Test", last_name="Member", login="e2e_member",
        password_hash=hash_password("TestPass123!"), email="e2e@test.com",
        role="user", tenant_id=me_data["tenant_id"],
    )
    db_session.add(test_user)
    db_session.commit()
    db_session.refresh(test_user)

    add_member_resp = client.post(f"/api/projects/{project_id}/members", headers=headers, json={
        "user_ids": [test_user.id],
        "role": "editor",
    })
    assert add_member_resp.status_code == 200
    assert add_member_resp.json()["added"] == 1

    members_resp = client.get(f"/api/projects/{project_id}/members", headers=headers)
    assert members_resp.status_code == 200
    member_ids = [m["user_id"] for m in members_resp.json()]
    assert test_user.id in member_ids
    print(f"  ✓ Step 10: Member added — user_id={test_user.id}")

    # =============================================
    # STEP 11: Create team and share project with team
    # =============================================
    team_resp = client.post("/api/teams/", headers=headers, json={"name": "E2E Team"})
    assert team_resp.status_code == 201
    team_id = team_resp.json()["id"]

    share_resp = client.post(f"/api/projects/{project_id}/share", headers=headers, json={
        "share_type": "team",
        "share_target_id": team_id,
        "permission": "view",
    })
    assert share_resp.status_code == 201
    print(f"  ✓ Step 11: Project shared with team {team_id}")

    # =============================================
    # STEP 12: Storage quotas
    # =============================================
    # Create a quota
    quota_resp = client.post("/api/storage/quotas", headers=headers, json={
        "scope_type": "tenant",
        "scope_id": me_data["tenant_id"],
        "quota_bytes": 10737418240,  # 10 GB
    })
    assert quota_resp.status_code == 201

    # Check usage
    usage_resp = client.get("/api/storage/usage", headers=headers)
    assert usage_resp.status_code == 200
    usage = usage_resp.json()
    assert usage["tenant"] is not None
    assert usage["tenant"]["quota_bytes"] == 10737418240
    print(f"  ✓ Step 12: Storage quota set — tenant 10 GB")

    # =============================================
    # STEP 13: Switch portal role
    # =============================================
    switch_resp = client.post("/api/auth/switch-role", headers=headers, json={
        "active_role": "lawyer",
    })
    assert switch_resp.status_code == 200
    new_token = switch_resp.json()["access_token"]

    me2 = client.get("/api/auth/me", headers={"Authorization": f"Bearer {new_token}"})
    assert me2.json()["active_role"] == "lawyer"
    print(f"  ✓ Step 13: Role switched to lawyer")

    # =============================================
    # STEP 14: Update profile
    # =============================================
    name_resp = client.put("/api/users/me/name", headers=headers, json={
        "firstName": "Наталия",
        "lastName": "Администратор",
    })
    assert name_resp.status_code == 200
    assert name_resp.json()["first_name"] == "Наталия"

    tg_resp = client.put("/api/users/me/telegram", headers=headers, json={
        "username": "@linza_admin",
    })
    assert tg_resp.status_code == 200
    assert tg_resp.json()["telegram_username"] == "linza_admin"
    print(f"  ✓ Step 14: Profile updated")

    # =============================================
    # STEP 15: User search (members page)
    # =============================================
    search_resp = client.post("/api/users/search", headers=headers, json={
        "searchTerm": "Test",
        "pageSize": 10,
        "pageNumber": 1,
    })
    assert search_resp.status_code == 200
    search_data = search_resp.json()
    assert search_data["total"] >= 1
    found_member = any(u["email"] == "e2e@test.com" for u in search_data["users"])
    assert found_member
    print(f"  ✓ Step 15: User search OK — found {search_data['total']} results")

    # =============================================
    # STEP 16: Token refresh
    # =============================================
    refresh_resp = client.post("/api/auth/token", headers=headers)
    assert refresh_resp.status_code == 200
    assert "accessToken" in refresh_resp.json()
    print(f"  ✓ Step 16: Token refreshed")

    # =============================================
    # STEP 17: Sign out
    # =============================================
    signout_resp = client.post("/api/auth/sign-out", headers=headers)
    assert signout_resp.status_code == 200
    print(f"  ✓ Step 17: Signed out")

    print(f"\n  ══════════════════════════════════════")
    print(f"  ✓ E2E TEST PASSED: Full user journey OK")
    print(f"  ══════════════════════════════════════")
