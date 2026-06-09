# API Reference

Base URL: no global prefix (e.g. `http://localhost:8000`)

Interactive docs: `/docs` (Swagger UI) and `/redoc` (ReDoc) when the server is running.

---

## Authentication

All protected endpoints require an `access_token` HTTP-only cookie set by login, signup, or Google auth routes.

| Property | Value |
|----------|-------|
| Cookie name | `access_token` |
| Algorithm | HS256 |
| Payload | `{ "sub": "<email>", "id": <user_id>, "exp": <timestamp> }` |
| Default expiry | 30 minutes (`ACCESS_TOKEN_EXPIRE_MINUTES`) |

There is no `Authorization: Bearer` header support.

---

## Auth — `/auth`

### `POST /auth/signup`

Create a new account after OTP verification.

**Auth:** Public

**Request body:**

```json
{
  "email": "user@example.com",
  "password": "secret12",
  "otp": "123456"
}
```

| Field | Constraints |
|-------|-------------|
| `email` | Valid email |
| `password` | 6–16 characters |
| `otp` | Exactly 6 digits |

**Response:** `200` — `{ "message": "Signup successful" }` + sets `access_token` cookie

**Errors:** `400` invalid OTP, `409` email already exists

---

### `POST /auth/login`

**Auth:** Public

**Request body:**

```json
{
  "email": "user@example.com",
  "password": "secret12"
}
```

**Response:** `200` — `{ "message": "Login successful" }` + sets cookie

**Errors:** `401` invalid credentials

---

### `POST /auth/google-auth`

Authenticate via Google ID token.

**Auth:** Public

**Request body:**

```json
{
  "google_token": "<Google ID token from frontend>"
}
```

**Response:** `200` — `{ "message": "Google authentication successful" }` + sets cookie

Creates a new user if the email does not exist (no password hash).

---

### `POST /auth/logout`

**Auth:** Public (no cookie required)

**Response:** `200` — `{ "message": "Logout successful" }` + clears cookie

---

### `POST /auth/get-otp`

Request an OTP for signup or password reset.

**Auth:** Public

**Request body:**

```json
{
  "email": "user@example.com",
  "password": "secret12",
  "purpose": "signup"
}
```

| `purpose` | Description |
|-----------|-------------|
| `"signup"` | Register new account |
| `"reset_password"` | Reset existing account password |

**Current behavior:** Returns `{ "message": "OTP service is currently disabled" }` without sending OTP.

**Intended behavior:** Stores OTP + password hash in Redis (5 min TTL), sends email.

---

### `POST /auth/reset-password`

Reset password using OTP.

**Auth:** Public

**Request body:**

```json
{
  "email": "user@example.com",
  "password": "newpass12",
  "otp": "123456"
}
```

**Response:** `200` — `{ "message": "Password reset successful" }`

---

## Users — `/users`

All routes require authentication.

### `GET /users/me`

Get the current user's profile.

**Response:**

```json
{
  "id": 1,
  "email": "user@example.com",
  "created_at": "2026-01-13T10:00:00Z",
  "updated_at": null
}
```

---

### `POST /users/me/change-password`

**Request body:**

```json
{
  "old_password": "secret12",
  "new_password": "newpass12"
}
```

**Response:** `200` — `{ "detail": "Password changed successfully" }`

---

### `DELETE /users/me`

Permanently delete the account and all associated data.

**Response:** `200` — `{ "detail": "User account deleted successfully" }` + clears cookie

---

## Entries — `/entries`

All routes require authentication. Entries are scoped to the authenticated user.

### `POST /entries/`

Create a new journal entry.

**Request body:**

```json
{
  "content": "Today was a good day.",
  "entry_date": "2026-06-09"
}
```

| Field | Notes |
|-------|-------|
| `content` | Required |
| `entry_date` | Optional; defaults to today. Cannot be a future date. |

**Response:** Entry object (no `response_model` — returns raw ORM shape)

---

### `GET /entries`

Search and list entries.

**Query parameters:**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `q` | string | — | Full-text search (`ilike` on content) |
| `start_date` | date | — | Filter entries on or after this date |
| `end_date` | date | — | Filter entries on or before this date |
| `limit` | int | 20 | Max 100 |
| `offset` | int | 0 | Pagination offset |

**Response:** `EntryResponse[]`

```json
[
  {
    "id": 1,
    "content": "Morning thoughts...",
    "entry_date": "2026-06-09",
    "created_at": "2026-06-09T08:00:00Z",
    "updated_at": null
  }
]
```

---

### `GET /entries/{entry_id}`

Get a single entry by ID.

**Response:** `EntryResponse`

**Errors:** `404` if not found or not owned by user

---

### `PATCH /entries/{entry_id}`

Update entry content.

**Request body:**

```json
{
  "content": "Updated text"
}
```

**Response:** `EntryResponse`

---

### `DELETE /entries/{entry_id}`

Delete an entry. If this was the last entry for that date, also removes day metadata.

**Response:** `200` — `{ "message": "Entry deleted" }`

---

## Days — `/days`

All routes require authentication.

### `GET /days/`

List dates that have at least one entry (active days).

**Query parameters:**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `start_date` | date | — | Range start |
| `end_date` | date | — | Range end |
| `limit` | int | 30 | Max 366 |
| `offset` | int | 0 | Pagination offset |
| `include_metadata` | bool | false | Return full metadata instead of dates only |

**Response (metadata=false):** `["2026-06-09", "2026-06-08", ...]`

**Response (metadata=true):** `DayResponse[]`

```json
[
  {
    "date": "2026-06-09",
    "summary": "A productive day",
    "tags": ["work", "exercise"]
  }
]
```

Days are returned in descending date order (newest first).

---

### `GET /days/{date}`

Get all entries for a specific date.

**Path param:** `date` — `YYYY-MM-DD`

**Response:** Array of Entry ORM objects (no `response_model`)

---

### `DELETE /days/{date}`

Delete all entries and day metadata for a date.

**Response:** `200` — `{ "detail": "Day entries deleted" }`

---

### `GET /days/{date}/metadata`

Get summary and tags for a day.

**Response:**

```json
{
  "date": "2026-06-09",
  "summary": "A productive day",
  "tags": ["work"],
  "created_at": "2026-06-09T12:00:00Z",
  "updated_at": null
}
```

**Errors:** `404` if no metadata exists for that date

---

### `DELETE /days/{date}/metadata`

Remove summary and tags without deleting entries.

**Response:** `200` — `{ "detail": "Day cleared" }`

---

### `GET /days/{date}/generate-summary`

Generate (or regenerate) AI summary and tags for a day, then return metadata.

**Response:** `DayMetadata` (same shape as `GET .../metadata`)

> **Note:** Currently returns stub data; Gemini API call is not active.

---

## Error Response Format

FastAPI returns errors as:

```json
{
  "detail": "Human-readable error message"
}
```

Or for validation errors:

```json
{
  "detail": [
    { "loc": ["body", "password"], "msg": "...", "type": "..." }
  ]
}
```
