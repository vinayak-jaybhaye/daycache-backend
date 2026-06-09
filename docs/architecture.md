# Architecture

This document describes how the DayCache backend is structured, how requests flow through the system, and the key design decisions behind it.

---

## High-Level Overview

DayCache is a **layered FastAPI application** that exposes a REST API for a personal diary. The backend is stateless — session state lives in a signed JWT stored in an HTTP-only cookie, not on the server.

```
┌──────────────┐     HTTP + Cookie      ┌─────────────────────────────┐
│   Frontend   │ ─────────────────────► │  FastAPI (app/main.py)      │
│  (React SPA) │                        │  ├── CORS middleware          │
└──────────────┘                        │  └── API router             │
                                        └──────────────┬──────────────┘
                                                       │
                    ┌──────────────────────────────────┼──────────────────────────┐
                    ▼                                  ▼                          ▼
             Route handlers                    Service layer              Integrations
         (app/api/routes/*)                 (app/services/*)          (Redis, SMTP, Gemini)
                    │                                  │                          │
                    ▼                                  ▼                          │
              Pydantic schemas                  SQLAlchemy ORM                     │
             (app/schemas/*)                  (app/db/models/*)                    │
                                                       │                          │
                                                       ▼                          │
                                                  PostgreSQL ◄─────────────────────┘
```

---

## Layer Responsibilities

### 1. Route Layer (`app/api/routes/`)

Thin HTTP handlers. Each route:

1. Validates input via Pydantic schemas
2. Resolves dependencies (`get_db`, `get_current_user`)
3. Delegates to a service function
4. Returns the response (and sets cookies for auth routes)

Routes do **not** contain business logic or direct complex queries.

### 2. Schema Layer (`app/schemas/`)

Pydantic models for request bodies, query parameters, and response shapes. Used for:

- Input validation (password length, email format, OTP digits)
- Serialization of API responses (`response_model`)
- Query parameter bundling (e.g. `ListDaysQuery`)

### 3. Service Layer (`app/services/`)

All business logic lives here. Services:

- Query and mutate the database via SQLAlchemy sessions
- Raise `HTTPException` for domain errors (404, 400, 401)
- Call external integrations (Redis OTP, SMTP, Gemini)
- Enforce user scoping — every query filters by `user.id`

| Service | Responsibility |
|---------|----------------|
| `auth_service.py` | Signup, login, Google OAuth, password reset |
| `redis_otp_service.py` | OTP generation, storage, verification in Redis |
| `email_services.py` | OTP email composition and dispatch |
| `user_services.py` | Profile, password change, account deletion |
| `entry_services.py` | Entry CRUD, search, cascade day cleanup |
| `day_service.py` | Active day listing, metadata, AI summary trigger |
| `ai_generation_service.py` | Gemini-powered summary and tag generation |

### 4. Data Layer (`app/db/`)

- **Models** (`models/`) — SQLAlchemy declarative models (`User`, `Day`, `Entry`)
- **Session** (`session.py`) — Engine, `SessionLocal`, `get_db` dependency
- **Seed** (`seed/`) — Development data generator (manual invocation)

No repository abstraction — services query models directly.

### 5. Core (`app/core/`)

Cross-cutting concerns:

| Module | Purpose |
|--------|---------|
| `config.py` | Pydantic Settings loaded from `.env` |
| `security.py` | Password hashing (Argon2), JWT encode/decode, cookie helpers |
| `dependencies.py` | `get_current_user` — decodes JWT from cookie, loads `User` |

### 6. Integrations (`app/integrations/`)

External service clients:

| Module | Purpose |
|--------|---------|
| `redis.py` | Singleton Redis client for OTP storage |
| `smtp.py` | Email sender (currently stubbed to `print`) |

---

## Request Flow

### Authenticated request example

```
GET /entries?q=morning
Cookie: access_token=<jwt>
```

1. **CORS middleware** — validates origin against `CORS_ORIGINS`
2. **Route** `list_entries` in `app/api/routes/entry.py`
3. **`get_current_user`** dependency:
   - Reads `access_token` cookie
   - Decodes JWT with `JWT_SECRET_KEY`
   - Loads `User` from DB by email (`sub` claim)
   - Raises 401 if missing/invalid
4. **`search_entries`** service:
   - Builds query: `entries` WHERE `user_id = current_user.id`
   - Applies `ilike` filter, date range, pagination
   - Returns list of `Entry` ORM objects
5. **FastAPI** serializes via `response_model=List[EntryResponse]`

### Auth flow (login)

```
POST /auth/login  { email, password }
```

1. Route calls `verify_and_login(db, email, password)`
2. Service looks up user, verifies Argon2 hash
3. Route calls `set_auth_cookie(response, user)` — encodes JWT, sets HTTP-only cookie
4. Returns `{ "message": "Login successful" }`

---

## Domain Model

DayCache separates **entries** (journal content) from **days** (optional metadata):

```
User
 ├── Entry (many)     ← source of truth for "what was written"
 └── Day (many)       ← optional enrichment (summary, tags)
```

- An **entry** belongs to a user and has an `entry_date`.
- A **day** row is optional metadata for a `(user_id, date)` pair.
- "Active days" are derived from distinct `entry_date` values in `entries`, optionally joined with `days` for summary/tags.
- Deleting the last entry for a date also removes the `Day` metadata row.
- Deleting a user cascades to all entries and days.

There are no SQLAlchemy `relationship()` definitions — links are FK columns only.

---

## Authentication Design

| Aspect | Choice |
|--------|--------|
| Token type | JWT (HS256) |
| Transport | HTTP-only cookie (`access_token`) |
| Header auth | Not supported |
| Server sessions | None (stateless) |
| Password hashing | Argon2 via passlib |
| Google auth | ID token verification against `GOOGLE_CLIENT_ID` |

JWT payload: `{ "sub": email, "id": user_id, "exp": timestamp }`

Cookie settings (production): `httponly=True`, `secure=True`, `samesite=none` — required for cross-origin SPA on Vercel talking to a separate API domain.

---

## OTP Flow (when enabled)

Signup and password reset use Redis-backed OTP:

```
POST /auth/get-otp  →  generate OTP, hash password, store in Redis (TTL 5 min), send email
POST /auth/signup   →  verify OTP + password match, create user, set cookie
```

Redis key: `signup:{email}` → JSON `{ "otp": "######", "password_hash": "<argon2>" }`

> **Current state:** `/auth/get-otp` returns early with a disabled message. OTP logic exists but is not reachable.

---

## AI Summary Generation

`GET /days/{date}/generate-summary` triggers `ai_generation_service.py`:

1. Loads all entries for the date
2. Concatenates content into a prompt
3. Calls Gemini (`models/gemini-2.5-flash`) for JSON `{ summary, tags }`
4. Upserts a `Day` row with the result

> **Current state:** An early `return` in the service returns stub data without calling Gemini.

---

## Error Handling

Services raise `fastapi.HTTPException` directly — there is no custom exception hierarchy or global error handler. FastAPI converts these to JSON responses with appropriate status codes.

Common patterns:

- `404` — entry/day/user not found
- `400` — validation failure, OTP mismatch, future entry date
- `401` — invalid credentials, expired/missing JWT
- `409` — email already registered

---

## Conventions

1. **Thin routes, fat services** — routes are 5–15 lines; logic is in services
2. **User scoping** — every data query includes `user_id = current_user.id`
3. **Dependency injection** — `Depends(get_db)` and `Depends(get_current_user)` everywhere
4. **Inline route comments** — routes document intent as `# email, password -> verify, return token`
5. **No global API prefix** — routes mount at `/auth`, `/users`, `/entries`, `/days`
6. **Template rendering** — simple `{{ key }}` string replacement, not Jinja2
