# Database

DayCache uses **PostgreSQL 16** with **SQLAlchemy** ORM and **Alembic** for migrations.

---

## Schema Overview

```
users
  id            BIGINT PK
  email         VARCHAR(255) UNIQUE
  password_hash VARCHAR(255) NULLABLE
  created_at    TIMESTAMPTZ
  updated_at    TIMESTAMPTZ

entries
  id            BIGINT PK
  user_id       BIGINT FK → users.id ON DELETE CASCADE
  content       TEXT
  entry_date    DATE
  created_at    TIMESTAMPTZ
  updated_at    TIMESTAMPTZ

days
  id            BIGINT PK
  user_id       BIGINT FK → users.id ON DELETE CASCADE
  date          DATE
  summary       TEXT NULLABLE
  tags          VARCHAR[] NULLABLE
  created_at    TIMESTAMPTZ
  updated_at    TIMESTAMPTZ
  UNIQUE(user_id, date)
```

---

## Tables

### `users`

| Column | Type | Notes |
|--------|------|-------|
| `id` | BigInteger | Primary key |
| `email` | String(255) | Unique, indexed |
| `password_hash` | String(255) | Nullable — Google-only users have no password |
| `created_at` | TIMESTAMPTZ | Server default `now()` |
| `updated_at` | TIMESTAMPTZ | Updated on change |

**Model:** `app/db/models/user.py`

### `entries`

| Column | Type | Notes |
|--------|------|-------|
| `id` | BigInteger | Primary key |
| `user_id` | BigInteger | FK → `users.id`, indexed |
| `content` | Text | Journal entry text |
| `entry_date` | Date | The calendar date this entry belongs to, indexed |
| `created_at` | TIMESTAMPTZ | Server default `now()` |
| `updated_at` | TIMESTAMPTZ | Updated on change |

**Indexes:**
- `user_id`
- `entry_date`
- Composite `(user_id, entry_date)`

**Model:** `app/db/models/entry.py`

### `days`

| Column | Type | Notes |
|--------|------|-------|
| `id` | BigInteger | Primary key |
| `user_id` | BigInteger | FK → `users.id`, indexed |
| `date` | Date | Calendar date |
| `summary` | Text | AI-generated or manual summary |
| `tags` | ARRAY(String) | GIN-indexed (`ix_days_tags`) |
| `created_at` | TIMESTAMPTZ | Server default `now()` |
| `updated_at` | TIMESTAMPTZ | Updated on change |

**Constraints:** `UNIQUE(user_id, date)` — one metadata row per user per date

**Model:** `app/db/models/day.py`

---

## Relationships

There are no SQLAlchemy `relationship()` definitions. Logical relationships:

```
User 1 ──< Entry     (via entries.user_id)
User 1 ──< Day       (via days.user_id)
```

Entries and days are correlated by `(user_id, date)` but not FK-linked. A day can exist without entries (after metadata generation) and entries can exist without a day row.

---

## Cascade Behavior

| Action | Effect |
|--------|--------|
| Delete user | DB cascades to all entries and days |
| Delete last entry for a date | Application deletes the `Day` metadata row |
| `DELETE /days/{date}` | Deletes all entries + day metadata for that date |
| `DELETE /days/{date}/metadata` | Removes metadata only; entries remain |

---

## Migrations

### Configuration

- **Alembic config:** `alembic.ini` — `script_location = alembic`, `prepend_sys_path = .`
- **Runtime:** `alembic/env.py` reads `DATABASE_URL` from app settings and sets `target_metadata = Base.metadata`
- **Model discovery:** `app/db/models/__init__.py` imports all models so Alembic detects them

### Commands

```bash
# Apply all pending migrations
alembic upgrade head

# Create a new migration after model changes
alembic revision --autogenerate -m "describe change"

# View current revision
alembic current

# Roll back one revision
alembic downgrade -1
```

### Existing migrations

| Revision | File | Description |
|----------|------|-------------|
| `16748e401501` | `alembic/versions/16748e401501_initial_schema.py` | Initial schema — users, days, entries with indexes |

---

## Seeding

Development seed script: `app/db/seed/seed_dev_data.py`

```bash
python -m app.db.seed.seed_dev_data
```

**What it does:**
1. Deletes all existing users, entries, and days
2. Creates 5 users: `dev1@example.com` … `dev5@example.com` (password: `devpassword`)
3. Generates random entries from 2024-01-01 to today (~500–700 days per user)
4. ~90% of days get pre-built summaries and tags

Not integrated into Alembic or app startup — run manually.

---

## Connection Setup

`app/db/session.py`:

```python
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

The `get_db` dependency yields a session per request and closes it in a `finally` block.

**Connection string format** (psycopg3):

```
postgresql+psycopg://diary_user:diary_password@localhost:5432/diary_db
```

Docker Compose credentials match these defaults.
