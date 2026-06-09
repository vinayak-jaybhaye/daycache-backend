# Configuration

All settings are loaded from environment variables (and optionally a `.env` file) via Pydantic Settings in `app/core/config.py`.

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | **Yes** | — | SQLAlchemy connection string |
| `JWT_SECRET_KEY` | **Yes** | — | Secret for signing JWTs |
| `JWT_ALGORITHM` | No | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `30` | Token and cookie max-age in minutes |
| `ENV` | No | `development` | Environment label (not used in code paths) |
| `CORS_ORIGINS` | No | `None` | JSON list of allowed origins |
| `REDIS_URL` | No | `None` | Redis connection URL for OTP storage |
| `GEMINI_API_KEY` | No | `None` | Google Gemini API key for AI summaries |
| `SMTP_SERVER` | No | `None` | SMTP server hostname |
| `SMTP_PORT` | No | `None` | SMTP port (e.g. 587) |
| `SMTP_USERNAME` | No | `None` | SMTP auth username |
| `SMTP_PASSWORD` | No | `None` | SMTP auth password |
| `GOOGLE_CLIENT_ID` | No | `None` | Google OAuth client ID for ID token verification |

---

## Example `.env`

```env
DATABASE_URL=postgresql+psycopg://diary_user:diary_password@localhost:5432/diary_db
REDIS_URL=redis://localhost:6379/0

JWT_SECRET_KEY=change-me-to-a-random-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=

GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GEMINI_API_KEY=your-gemini-api-key

CORS_ORIGINS=["http://localhost:5173"]
```

---

## `.env.sample` Mismatches

The checked-in `.env.sample` has naming inconsistencies with `config.py`:

| Sample file | Correct name |
|-------------|--------------|
| `ALGORITHM` | `JWT_ALGORITHM` |
| `postgresql+psycopg2://` | `postgresql+psycopg://` (psycopg3 driver) |

Quoted values with leading spaces (e.g. `JWT_SECRET_KEY= secret-key`) may cause parsing issues depending on the env loader.

---

## CORS

`CORS_ORIGINS` must be a JSON array string when set via `.env`:

```env
CORS_ORIGINS=["http://localhost:5173","https://daycache-fe.vercel.app"]
```

The frontend must be listed here for cookie-based auth to work cross-origin. `allow_credentials=True` is set in `app/main.py`.

---

## Cookie Settings

Defined in `app/core/security.py`:

| Setting | Production | Dev (commented out) |
|---------|------------|---------------------|
| `httponly` | `True` | `True` |
| `secure` | `True` | `False` |
| `samesite` | `none` | `lax` |

Production settings require HTTPS. For local HTTP development with the frontend on a different port, uncomment the dev cookie block in `security.py`.

---

## Docker Compose Services

`docker-compose.yml` provides infrastructure only (no app container):

| Service | Image | Port | Credentials |
|---------|-------|------|-------------|
| PostgreSQL | `postgres:16` | 5432 | `diary_user` / `diary_password` / `diary_db` |
| Redis | `redis:7` | 6379 | No auth |
