# Linza Board — Development Plan (devplan)

## Current State

- Branch: `natalia`
- Tests: 144/144 pass (E2E + unit)
- PR: [#3](https://github.com/BigDataQueen/-linza-app/pull/3) (natalia → main, NOT merged)

---

## A. Response Format Consistency (camelCase / snake_case)

**Status:** ⚠️ MEDIUM — mixed formats in API responses

**Problem:** Native endpoints use snake_case, compat endpoints use camelCase. MeResponse mixes both.

**Solution:** All backend responses in snake_case. Frontend `snakeToCamel` transform in `shared/api/apiInstance.ts` (afterResponse hook). Already partially implemented (`shared/api/transform.ts` exists).

**Files:**
- `Linza-admin/lm-web-develop/src/shared/api/apiInstance.ts` — add afterResponse hook
- `linza-board/backend/routes/auth.py` — unify MeResponse to snake_case
- `linza-board/backend/routes/users.py` — FullUserResponse to snake_case

**Effort:** 2–3 hours

---

## B. Pagination Consistency

**Status:** ⚠️ MEDIUM — inconsistent across endpoints

**Problem:**
| Endpoint | Pagination | Format |
|---|---|---|
| GET /api/projects/ | ✅ | PageSize/PageNumber |
| POST /api/users/search | ✅ | pageSize/pageNumber |
| GET /api/users/ | ❌ | Unlimited |
| GET /api/tenants/ | ❌ | Unlimited |
| GET /api/teams/ | ❌ | Unlimited |
| GET /api/reports/ | ❌ | Unlimited |

**Solution:** Add `page` + `page_size` params to all list endpoints with query aliases for backward compat.

**Files:**
- `backend/routes/users.py`, `tenants.py`, `teams.py`, `reports.py`

**Effort:** 1–2 hours

---

## C. Storage Endpoint Naming

**Status:** 💡 LOW — confusing but functional

**Problem:** `/api/settings/storage` (S3 profiles) vs `/api/storage` (quotas)

**Solution:** Rename `/api/storage` → `/api/storage-quotas`. Add 301 redirect from old path.

**Files:** `backend/main.py`, Vue + React composables/requests

**Effort:** 30 min

---

## D. Rate Limiting Expansion

**Status:** ⚠️ MEDIUM — only login is rate-limited

**Solution:** Add `@limiter.limit` to:
- `PUT /api/users/me/password` → 3/min
- `POST /api/users/` → 10/min
- `POST /api/errors/report` → 30/min

**Files:** `backend/routes/users.py`, `backend/routes/errors.py`

**Effort:** 15 min

---

## E. OTP Challenge Cleanup

**Status:** 💡 LOW — expired records accumulate

**Solution:** Background asyncio task in lifespan, runs every 30 min, deletes records where `expires_at < now() - 1h`.

**File:** `backend/main.py`

**Effort:** 30 min

---

## F. CSS Design System Update (Liquid Glass)

**Status:** 🔴 HIGH — new design system `linza-detector-design-system.css` added

### Token Mapping (old → new)

| Old (App.vue) | New (design-system) | Dark Value |
|---|---|---|
| `--c-bg` | `--bg` | `#050510` |
| `--c-surface` | `--glass` | `rgba(255,255,255,0.045)` |
| `--c-border` | `--glass-bd` | `rgba(255,255,255,0.08)` |
| `--c-blue` | `--bl` | `#5a9cf5` |
| `--c-teal` | `--gr` | `#3ee8b0` |
| `--c-err` | `--rd` | `#ff6b8a` |
| `--c-warn` | `--yl` | `#f0d060` |
| `--c-txt` | `--t` | `#dce0f4` |
| `--c-txt-2` | `--t2` | `#9da3c8` |

### Critical Changes

1. Theme via `data-theme="dark|light"` on `<html>` instead of `:root`
2. Font: DM Sans replaces Inter
3. Glass panels with `backdrop-filter: blur(24px)` replace flat borders
4. Pill buttons (`border-radius: 100px`) replace 6px radius
5. Mesh background + cursor glow effects
6. Scroll reveal animations

### Implementation Order

1. linza-board Vue.js (no UI library conflicts)
2. Connect `linza-detector-design-system.css` as base layer in `src/main.js`
3. Update `src/App.vue`: replace `:root` vars with `data-theme`, update global classes
4. Update all views: `.glass`/`.glass-card` instead of surface classes
5. Linza-admin React (CSS override layer for Gravity UI)

**Effort:** 8–12 hours (Vue) + 4–6 hours (React override)

---

## G. Missing Backend Endpoints (deferred)

| Priority | Endpoint | Purpose |
|----------|----------|---------|
| LOW | Folders CRUD | `/api/projects/{id}/folders` |
| LOW | Sources CRUD | `/api/importer/dataSourceItems` |
| LOW | Reports sharing | Already partially implemented |
| LOW | Registration by invitation | `/api/users/registration` |
| LOW | Password recovery | `/api/auth/recovery/password/*` |
| LOW | Email/Phone change with OTP | `/api/users/me/email`, `/api/users/me/phone` |

These require corresponding frontend implementation and are deferred to the next iteration.

---

## Timeline (recommended order)

| # | Task | Priority | Effort |
|---|------|----------|--------|
| 1 | F: CSS Design System (Vue.js) | HIGH | 8–12h |
| 2 | A: Response format unification | MEDIUM | 2–3h |
| 3 | B: Pagination consistency | MEDIUM | 1–2h |
| 4 | D: Rate limiting | MEDIUM | 15min |
| 5 | E: OTP cleanup | LOW | 30min |
| 6 | C: Storage naming | LOW | 30min |
| 7 | G: Missing endpoints | LOW | ongoing |
