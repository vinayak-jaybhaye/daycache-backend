# DayCache Backend

REST API for [DayCache](https://daycache-fe.vercel.app) — a personal diary application. This service handles authentication, journal entry CRUD, day browsing, and (planned) AI-powered day summaries.

**Related repository:** [daycache-fe](https://github.com/vinayak-jaybhaye/daycache-fe) (React frontend)

---

## Features

| Feature | Status |
|---------|--------|
| Email/password login | Working |
| Google OAuth (ID token) | Working |
| Email/password signup with OTP | Implemented; OTP endpoint disabled |
| Password reset via OTP | Service logic exists; OTP disabled |
| JWT auth via HTTP-only cookie | Working |
| Journal entry CRUD | Working |
| Full-text entry search | Working |
| Active day listing (dates with entries) | Working |
| Day metadata (summary + tags) | Schema ready; AI generation stubbed |
| SMTP email delivery | Stubbed (prints to stdout) |

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Framework | FastAPI |
| Server | Uvicorn (ASGI) |
| ORM | SQLAlchemy |
| Migrations | Alembic |
| Database | PostgreSQL 16 |
| Cache / OTP | Redis 7 |
| Auth | JWT (python-jose) + Argon2 (passlib) |
| AI | Google Gemini (`google-genai`) |
| Validation | Pydantic v2 |

---

## Quick Start

### Prerequisites

- Python 3.11+
- Docker and Docker Compose (for PostgreSQL and Redis)

### 1. Start infrastructure

```bash
docker compose up -d
```

This starts PostgreSQL (`localhost:5432`) and Redis (`localhost:6379`) with credentials defined in `docker-compose.yml`.

### 2. Set up Python environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install google-auth   # required for Google OAuth; not yet in requirements.txt
```

### 3. Configure environment

```bash
cp .env.sample .env
```

Edit `.env` — see [docs/configuration.md](docs/configuration.md) for all variables. At minimum, set `DATABASE_URL` and `JWT_SECRET_KEY`.

> **Note:** Use `postgresql+psycopg://` (psycopg3) in `DATABASE_URL`, not `postgresql+psycopg2://` as shown in the sample file.

### 4. Run migrations

```bash
alembic upgrade head
```

### 5. (Optional) Seed development data

```bash
python -m app.db.seed.seed_dev_data
```

Creates 5 users (`dev1@example.com` … `dev5@example.com`, password `devpassword`) with sample entries.

### 6. Start the API server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Interactive API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Project Structure

```
daycache-backend/
├── app/
│   ├── main.py                 # FastAPI app, CORS, router mount
│   ├── api/
│   │   ├── router.py           # Route aggregation
│   │   └── routes/             # HTTP handlers (thin layer)
│   ├── core/                   # Config, security, auth dependencies
│   ├── db/
│   │   ├── models/             # SQLAlchemy ORM models
│   │   ├── session.py          # Engine and session factory
│   │   └── seed/               # Development data seeder
│   ├── schemas/                # Pydantic request/response models
│   ├── services/               # Business logic
│   ├── integrations/           # Redis, SMTP clients
│   ├── utils/                  # Template rendering helpers
│   └── templates/emails/       # Email templates
├── alembic/                    # Database migrations
├── docker-compose.yml          # PostgreSQL + Redis (no app container)
├── requirements.txt
└── docs/                       # Detailed documentation
```

---

## Documentation

| Document | Description |
|----------|-------------|
| [Architecture](docs/architecture.md) | Layers, request flow, design decisions |
| [API Reference](docs/api.md) | All endpoints, auth, request/response shapes |
| [Database](docs/database.md) | Schema, relationships, migration guide |
| [Configuration](docs/configuration.md) | Environment variables and settings |
| [Development Guide](docs/development.md) | Local dev, conventions, known gaps |

---

## API Overview

All endpoints are mounted at the root (no `/api` prefix). Authentication uses an HTTP-only `access_token` cookie set by login/signup routes.

| Prefix | Description |
|--------|-------------|
| `/auth` | Signup, login, logout, Google OAuth, OTP, password reset |
| `/users` | Profile, change password, delete account |
| `/entries` | Create, read, update, delete, search journal entries |
| `/days` | List active days, get entries for a date, day metadata, AI summary |

See [docs/api.md](docs/api.md) for the complete reference.

---

## Local Development Notes

- **CORS:** Set `CORS_ORIGINS` to your frontend origin (e.g. `["http://localhost:5173"]`).
- **Cookies:** Production cookie settings (`secure=True`, `samesite=none`) require HTTPS. For plain HTTP local dev, uncomment the dev cookie block in `app/core/security.py`.
- **OTP:** The `/auth/get-otp` route returns a disabled message. Remove the early return in `app/api/routes/auth.py` to enable signup and password reset flows.
- **AI summaries:** `ai_generation_service.py` currently returns a stub; the Gemini API call is unreachable.

---

## License

See repository for license details.
