# Linza Platform — Administrator Guide (SuperAdmin)

## 1. Roles and Access Control

### System Roles (legacy)

| Role | Code | Access |
|------|------|--------|
| **SuperAdmin** | `superadmin` | Full access. All operations unrestricted. |
| **Admin** | `admin` | Manage own users, settings access. |
| **User** | `user` | Read-only, basic operations. |

### Portal Roles (PRD)

| Role | Code | Purpose | Auto-mapping |
|------|------|---------|-------------|
| Administrator | `administrator` | Org config, users, teams, storage | superadmin → ✅, admin → ✅ |
| Operator | `operator` | Files, analysis, queue | superadmin → ✅, admin → ✅, user → ✅ |
| Lawyer | `lawyer` | Escalated content review | superadmin → ✅ |
| Chief Editor | `chief_editor` | Team metrics, content marking | superadmin → ✅ |

**SuperAdmin** automatically receives **all 4 portal roles**.

---

## 2. JWT Tokens

### Payload Structure

```json
{
  "sub": "admin", "role": "superadmin",
  "pr": ["administrator", "operator", "lawyer", "chief_editor"],
  "ar": "administrator", "tid": 1, "gid": null, "exp": 1744820400
}
```

| Field | Description |
|-------|------------|
| `sub` | User login |
| `role` | Legacy role |
| `pr` | Portal roles array |
| `ar` | Active portal role |
| `tid` | Tenant ID |
| `gid` | Team ID |
| `exp` | Expiration (Unix timestamp) |

### Configuration

| Parameter | Env Var | Default |
|-----------|---------|---------|
| Secret key | `AUTH_SECRET_KEY` | `linza-board-secret-key-change-in-production` |
| Algorithm | — | HS256 |
| TTL | `AUTH_TOKEN_EXPIRE_MINUTES` | 480 min (8 hours) |

---

## 3. Tenant Management

Tenants represent organizations. All users, teams, and projects belong to a tenant. A **Default Organization** (slug: `default`) is created on first launch.

| Operation | Method | Path | Access |
|-----------|--------|------|--------|
| My tenant | GET | `/api/tenants/my` | Any authenticated |
| List all | GET | `/api/tenants/` | Admin+ |
| Create | POST | `/api/tenants/` | Admin+ |
| Update | PATCH | `/api/tenants/{id}` | Admin+ |
| Delete | DELETE | `/api/tenants/{id}` | **SuperAdmin only** |

---

## 4. User Management

### Creating Users

```bash
curl -X POST http://localhost:8000/api/users/ \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"first_name":"John","last_name":"Doe","login":"jdoe",
       "password":"SecurePass123!","email":"john@company.com",
       "role":"user","portal_roles":["operator"]}'
```

- Only **SuperAdmin** can create users with role `admin`
- Passwords are hashed with bcrypt (truncated to 72 bytes)

### Search

```bash
curl -X POST http://localhost:8000/api/users/search \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"searchTerm":"John","pageSize":10,"pageNumber":1}'
```

---

## 5. Team Management

Teams belong to a tenant. Create, add members, remove members via `/api/teams/`.

---

## 6. Project Management

### Access Control Hierarchy

1. **SuperAdmin** → access to all projects
2. **Owner** (created_by) → full access
3. **Member** (project_members) → by role (owner/editor/viewer)
4. **User share** (project_shares type=user)
5. **Team share** (project_shares type=team)
6. **Tenant share** (project_shares type=tenant)
7. **Same tenant** → read access

### Sharing

```bash
curl -X POST http://localhost:8000/api/projects/1/share \
  -d '{"share_type":"team","share_target_id":2,"permission":"view"}'
```

---

## 7. Storage Quotas

### Hierarchy: tenant > team > user

All three levels are checked before file upload. If any level is exceeded → HTTP 413.

```bash
# Set tenant quota: 10 GB
curl -X POST http://localhost:8000/api/storage/quotas \
  -d '{"scope_type":"tenant","scope_id":1,"quota_bytes":10737418240}'
```

---

## 8. Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AUTH_SECRET_KEY` | `linza-board-secret-key...` | JWT secret key |
| `AUTH_TOKEN_EXPIRE_MINUTES` | `480` | Token TTL (minutes) |
| `AUTH_ADMIN_LOGIN` | `admin` | SuperAdmin login |
| `AUTH_ADMIN_PASSWORD` | `admin` | SuperAdmin password |
| `AUTH_ADMIN_EMAIL` | `admin@linza.local` | SuperAdmin email |
| `DATABASE_URL` | `sqlite:///./linza_board.db` | Database connection |
| `CORS_ORIGINS` | `http://localhost:5173` | Allowed CORS origins |
| `ERROR_TRACKER_URL` | — | Linza Debug URL |
| `SERVICE_API_KEY` | — | Inter-service auth key |

---

## 9. Database Migrations

**PostgreSQL:** `python -m alembic upgrade head`
**SQLite (dev):** auto via `Base.metadata.create_all()`
**Rollback:** `python -m alembic downgrade -1`

---

## 10. Production Security Checklist

- [ ] Change `AUTH_SECRET_KEY` to random ≥ 32 chars
- [ ] Change `AUTH_ADMIN_PASSWORD` to strong password
- [ ] Set `DATABASE_URL` to PostgreSQL
- [ ] Configure `CORS_ORIGINS` (remove localhost)
- [ ] Enable HTTPS via reverse proxy
- [ ] Connect email/SMS service for OTP
- [ ] Set `ERROR_TRACKER_URL` for Linza Debug
- [ ] Verify bcrypt==4.0.1 in requirements.txt
