# Development Guide

Conventions, workflows, and known gaps for contributing to the DayCache backend.

---

## Development Workflow

### 1. Start services

```bash
docker compose up -d
```

### 2. Activate virtual environment

```bash
source .venv/bin/activate
pip install -r requirements.txt
pip install google-auth
```

### 3. Configure and migrate

```bash
cp .env.sample .env
# Edit .env — fix DATABASE_URL scheme and JWT_SECRET_KEY
alembic upgrade head
```

### 4. (Optional) Seed data

```bash
python -m app.db.seed.seed_dev_data
```

### 5. Run with hot reload

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Test endpoints

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- Login with seeded user: `dev1@example.com` / `devpassword`

---

## Adding a New Endpoint

1. **Schema** — define request/response models in `app/schemas/`
2. **Service** — implement business logic in `app/services/`
3. **Route** — add a thin handler in `app/api/routes/`
4. **Router** — if adding a new resource, register in `app/api/router.py`

Example pattern:

```python
# app/api/routes/example.py
@router.get("/{id}", response_model=ExampleResponse)
def get_example(
    id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return get_example_service(db, user, id)
```

---

## Adding a Database Migration

1. Modify models in `app/db/models/`
2. Ensure the model is imported in `app/db/models/__init__.py`
3. Generate migration:

```bash
alembic revision --autogenerate -m "add column to entries"
```

4. Review the generated file in `alembic/versions/`
5. Apply:

```bash
alembic upgrade head
```

---

## Code Conventions

| Convention | Detail |
|------------|--------|
| Route comments | Document intent inline: `# email, password -> verify, return token` |
| User scoping | Every query must filter by `user.id` from `get_current_user` |
| Error handling | Raise `HTTPException` in services, not custom exception classes |
| Password rules | 6–16 characters (enforced in Pydantic schemas) |
| Date format | ISO `YYYY-MM-DD` for all date fields |
| Template rendering | `{{ key }}` replacement via `app/utils/template_renderer.py` |

---

## File Reference

| Path | Purpose |
|------|---------|
| `app/main.py` | App factory, CORS, router mount |
| `app/api/router.py` | Combines route modules with prefixes |
| `app/api/routes/auth.py` | Authentication endpoints |
| `app/api/routes/user.py` | User profile endpoints |
| `app/api/routes/entry.py` | Entry CRUD and search |
| `app/api/routes/day.py` | Day listing, metadata, AI summary |
| `app/core/config.py` | Settings from environment |
| `app/core/security.py` | Hashing, JWT, cookies |
| `app/core/dependencies.py` | `get_current_user` |
| `app/db/session.py` | Database engine and session |
| `app/db/models/user.py` | User model |
| `app/db/models/entry.py` | Entry model |
| `app/db/models/day.py` | Day metadata model |
| `app/services/auth_service.py` | Auth business logic |
| `app/services/entry_services.py` | Entry CRUD and search |
| `app/services/day_service.py` | Day listing and metadata |
| `app/services/ai_generation_service.py` | Gemini integration |
| `app/services/redis_otp_service.py` | OTP storage in Redis |
| `app/services/email_services.py` | Email composition |
| `app/integrations/redis.py` | Redis client singleton |
| `app/integrations/smtp.py` | Email sender (stubbed) |
| `app/templates/emails/otp_verification.txt` | OTP email template |

---

## Known Gaps and TODOs

From `TODO` file and code review:

### High priority

| Gap | Location | Impact |
|-----|----------|--------|
| OTP endpoint disabled | `app/api/routes/auth.py` | Signup and password reset non-functional |
| SMTP stubbed | `app/integrations/smtp.py` | No real email delivery |
| AI summary stubbed | `app/services/ai_generation_service.py` | Gemini never called |
| `google-auth` missing from requirements | `requirements.txt` | Google auth import fails without manual install |

### Medium priority

| Gap | Location | Impact |
|-----|----------|--------|
| `.env.sample` naming mismatches | `.env.sample` vs `config.py` | Misconfiguration risk |
| Prod cookie settings in dev | `app/core/security.py` | Local HTTP auth friction |
| Reset OTP shares signup key | `redis_otp_service.py` | Signup/reset collision risk |
| `PATCH /users/me` commented out | `app/api/routes/user.py` | No email update API |
| Google users lack password | `auth_service.py` | Cannot password-login Google accounts |

### Low priority

| Gap | Impact |
|-----|--------|
| No `response_model` on some routes | Leaks internal ORM shape |
| No tests or CI | No automated verification |
| No app Docker image | Infra-only docker-compose |
| No health check endpoint | No liveness probe |
| No API versioning | Breaking changes affect all clients |

---

## Enabling Disabled Features

### OTP service

In `app/api/routes/auth.py`, remove the early return in `get_otp`:

```python
# Remove these lines:
return {
  "message": "OTP service is currently disabled"
}
```

Ensure Redis is running and `REDIS_URL` is set.

### SMTP email

Uncomment the real SMTP implementation in `app/integrations/smtp.py` and configure SMTP variables.

### AI summaries

Remove the early `return` stub in `app/services/ai_generation_service.py` and set `GEMINI_API_KEY`.

### Local dev cookies

In `app/core/security.py`, comment out the production cookie settings and uncomment the dev block (`secure=False`, `samesite=lax`).

---

## Security Notes

- OTP uses `random.randint` (6 digits) — not cryptographically strong; acceptable for short-lived codes with rate limiting
- Entry search uses parameterized `ilike` — no SQL injection risk via ORM
- JWT secret must be strong and unique per environment
- `samesite=none` + `secure=True` is correct for cross-origin production but requires HTTPS
