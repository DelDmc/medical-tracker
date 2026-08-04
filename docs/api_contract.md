# Medical Tracker Application — API Contract

## 1. Purpose

This document defines the JSON REST API contract between the Medical Tracker Application frontend and backend for the MVP.

The requirements specification is authoritative for required behavior. The application design specification and domain model define the accepted implementation and domain constraints represented by this contract.

Traceability to requirement and design-decision identifiers is maintained separately in `traceability_matrix.md`.

## 2. General Conventions

- Base path: `/api/v1/`.
- Request and response bodies use JSON unless the response has no body.
- JSON field names use `snake_case`.
- Calendar dates use ISO 8601 `YYYY-MM-DD` format.
- Times use ISO 8601 local-time format such as `10:30:00` and contain no timezone offset.
- Datetimes representing instants use ISO 8601 with timezone information.
- Date-only values are not converted through UTC.
- The authenticated user's configured IANA timezone determines current local date and time calculations.
- Bearer authentication is required by default. Registration, CSRF bootstrap, login, token refresh, logout, and health check do not require a bearer access token.
- Protected endpoints receive the access token through `Authorization: Bearer <access_token>`.
- Requests that set, send, rotate, or clear authentication or CSRF cookies include browser credentials.
- Login, token refresh, and logout require a matching `X-CSRFToken` header and CSRF cookie.
- User ownership is assigned by the backend and is never writable by clients.
- User-owned querysets are restricted to the authenticated user.
- A missing object and an object owned by another user return the same `404 Not Found` response structure.
- `null` represents an absent optional relationship or value.
- MVP list endpoints return JSON arrays. Pagination is not part of this contract.

## 3. Common Responses

### 3.1 Authentication failure

```http
401 Unauthorized
```

```json
{
  "detail": "Authentication credentials were not provided."
}
```

An expired or invalid access token uses the same status class. The frontend may attempt one token refresh before ending the session.

### 3.2 CSRF failure

```http
403 Forbidden
```

```json
{
  "detail": "CSRF verification failed."
}
```

This response is used when a CSRF-protected authentication request omits `X-CSRFToken` or the submitted token does not match the CSRF cookie. No authentication credentials are issued.

### 3.3 Not found

```http
404 Not Found
```

```json
{
  "detail": "Not found."
}
```

The same response is used when the requested object does not exist or belongs to another user.

### 3.4 Validation failure

```http
400 Bad Request
```

Field-level errors use field names:

```json
{
  "title": ["This field is required."],
  "scheduled_date": ["A scheduled date is required for this status."]
}
```

Rules involving multiple fields may use `non_field_errors`:

```json
{
  "non_field_errors": ["The submitted field combination is not valid."]
}
```

No universal custom response envelope is used.

## 4. Health Check

### `GET /api/v1/health/`

Authentication: not required.

Success:

```http
200 OK
```

```json
{
  "status": "ok"
}
```

No configuration, environment, database credential, or secret value is returned.

## 5. Authentication

### 5.1 Authentication matrix

| Operation | Bearer access token | Browser credentials | `X-CSRFToken` |
|---|---:|---:|---:|
| `POST /api/v1/auth/register/` | No | No | No |
| `GET /api/v1/auth/csrf/` | No | Yes | No |
| `POST /api/v1/auth/login/` | No | Yes | Yes |
| `POST /api/v1/auth/refresh/` | No | Yes | Yes |
| `POST /api/v1/auth/logout/` | No | Yes | Yes |
| Protected API operations | Yes | No | No |

For browser requests, browser credentials means that the frontend includes credentials so the browser can receive or send the applicable cookies. The frontend holds `access_token` and `csrf_token` only in application memory. It does not read the refresh-token or CSRF cookies directly.

### 5.2 Register

#### `POST /api/v1/auth/register/`

Authentication: bearer access token not required. Browser credentials and CSRF protection are not required.

Request:

```json
{
  "email": "person@example.com",
  "password": "example-password",
  "timezone": "Asia/Makassar"
}
```

Validation:

- `email` is required, must be valid, is normalized before comparison, and must be unique using case-insensitive comparison;
- `password` is required and must contain at least eight characters;
- `timezone` is required and must be a supported IANA timezone identifier;
- the password is write-only and is never returned.

Success:

```http
201 Created
```

```json
{
  "id": 42,
  "email": "person@example.com",
  "timezone": "Asia/Makassar"
}
```

### 5.3 Bootstrap CSRF protection

#### `GET /api/v1/auth/csrf/`

Authentication: bearer access token not required.

Request requirements:

- the request includes browser credentials;
- no `X-CSRFToken` header is required.

Success:

```http
200 OK
```

```json
{
  "csrf_token": "<csrf-token>"
}
```

The response sets or renews the Django CSRF cookie. The returned `csrf_token` corresponds to that cookie and is held only in frontend application memory.

CSRF cookie attributes:

| Environment | `HttpOnly` | `Secure` | `SameSite` | Path |
|---|---:|---:|---|---|
| Production | `true` | `true` | `None` | `/api/v1/` |
| Local HTTP development | `true` | `false` | `Lax` | `/api/v1/` |

### 5.4 Log in

#### `POST /api/v1/auth/login/`

Authentication: bearer access token not required.

Request requirements:

- the request includes browser credentials;
- the request includes `X-CSRFToken: <csrf_token>` using the token returned by the CSRF bootstrap endpoint;
- the request body is JSON.

Request:

```json
{
  "email": "person@example.com",
  "password": "example-password"
}
```

Success:

```http
200 OK
```

```json
{
  "access_token": "<access-token>"
}
```

The response sets the refresh token only in the backend-issued `refresh_token` cookie. The refresh token is not returned in JSON. The frontend stores `access_token` only in application memory.

Invalid credentials:

```http
401 Unauthorized
```

```json
{
  "detail": "Invalid credentials."
}
```

Unknown-email and incorrect-password attempts return the same status and response structure.

A missing or mismatched CSRF token returns the common `403 Forbidden` CSRF failure response and does not establish an authenticated session.

### 5.5 Refresh access token

#### `POST /api/v1/auth/refresh/`

Authentication: bearer access token not required.

Request requirements:

- the request includes browser credentials;
- the request includes `X-CSRFToken: <csrf_token>`;
- the refresh token is read only from the `refresh_token` cookie;
- the request has no JSON body.

Success:

```http
200 OK
```

```json
{
  "access_token": "<new-access-token>"
}
```

On success, the backend invalidates the submitted refresh token, issues a replacement refresh token, and replaces the `refresh_token` cookie. The frontend replaces its in-memory access token with the returned `access_token`.

Expired, revoked, malformed, missing, or otherwise invalid refresh token:

```http
401 Unauthorized
```

```json
{
  "detail": "Refresh token is invalid or expired."
}
```

The backend issues no new credentials and clears the stale `refresh_token` cookie.

A missing or mismatched CSRF token returns the common `403 Forbidden` CSRF failure response and issues no new credentials.

### 5.6 Log out

#### `POST /api/v1/auth/logout/`

Authentication: bearer access token not required.

Request requirements:

- the request includes browser credentials;
- the request includes `X-CSRFToken: <csrf_token>`;
- the refresh token is read from the `refresh_token` cookie when present;
- the request has no JSON body.

Success for a valid, expired, revoked, already invalid, or missing refresh token:

```http
204 No Content
```

The response body is empty. The backend invalidates a valid refresh token when present and always clears the `refresh_token` cookie. The response does not disclose the refresh-token state.

A missing or mismatched CSRF token returns the common `403 Forbidden` CSRF failure response.

### 5.7 Refresh-token cookie contract

The backend creates, replaces, and clears the `refresh_token` cookie using the following attributes:

| Environment | `HttpOnly` | Host-only | `Secure` | `SameSite` | Path | Expiration |
|---|---:|---:|---:|---|---|---|
| Production | `true` | `true` | `true` | `None` | `/api/v1/auth/` | Aligned with refresh-token expiry |
| Local HTTP development | `true` | `true` | `false` | `Lax` | `/api/v1/auth/` | Aligned with refresh-token expiry |

Cookie clearing uses the same cookie name, path, host-only scope, and applicable `Secure` and `SameSite` values as cookie creation. The refresh token is never returned in a JSON response and is not readable by frontend JavaScript.

## 6. Account

### 6.1 Retrieve account

#### `GET /api/v1/account/`

Authentication: required.

Success:

```http
200 OK
```

```json
{
  "id": 42,
  "email": "person@example.com",
  "timezone": "Asia/Makassar"
}
```

### 6.2 Update timezone

#### `PATCH /api/v1/account/`

Authentication: required.

Request:

```json
{
  "timezone": "Europe/Warsaw"
}
```

Only `timezone` is writable. The value must be a supported IANA timezone identifier.

Success:

```http
200 OK
```

```json
{
  "id": 42,
  "email": "person@example.com",
  "timezone": "Europe/Warsaw"
}
```

Changing the account timezone does not alter the stored instant represented by existing timezone-aware timestamps.

## 7. Categories

### `GET /api/v1/categories/`

Authentication: required.

The endpoint is read-only. No category create, update, or delete endpoints are provided.

Success:

```http
200 OK
```

```json
[
  {
    "id": 1,
    "name": "General medical appointment",
    "slug": "general-medical-appointment"
  },
  {
    "id": 2,
    "name": "Dental appointment",
    "slug": "dental-appointment"
  }
]
```

The complete response contains exactly these system-defined category names:

- General medical appointment;
- Dental appointment;
- Specialist consultation;
- Laboratory test;
- Vaccination;
- Preventive examination;
- Follow-up;
- Other.

Names and slugs are unique. `Uncategorized` is not a category resource; the API represents an unassigned category as `null`.

## 8. Examination Resource

### 8.1 Representation

```json
{
  "id": 184,
  "user_id": 42,
  "category": {
    "id": 2,
    "name": "Dental appointment",
    "slug": "dental-appointment"
  },
  "title": "Annual dental checkup",
  "medical_specialty": "Dentistry",
  "scheduled_date": "2026-08-15",
  "scheduled_time": "10:30:00",
  "completed_date": null,
  "status": "planned",
  "location": "Central Dental Clinic",
  "notes": "Routine appointment",
  "source_occurrence": null,
  "time_state": "upcoming",
  "created_at": "2026-07-21T04:10:00Z",
  "updated_at": "2026-07-21T04:10:00Z"
}
```

Field rules:

| Field | Type | Writable | Rule |
|---|---|---:|---|
| `id` | identifier | No | System generated. |
| `user_id` | identifier | No | Assigned from the authenticated user. |
| `category_id` | identifier or `null` | Yes | Request field used to assign one existing system category. |
| `category` | object or `null` | No | Response representation of the assigned category. |
| `title` | string | Yes | Required for every status. |
| `medical_specialty` | string or `null` | Yes | Optional organizational metadata. |
| `scheduled_date` | date or `null` | Yes | Required for `planned`, `cancelled`, and `missed`. |
| `scheduled_time` | time or `null` | Yes | Optional and stored separately from `scheduled_date`. |
| `completed_date` | date or `null` | Yes | Required for `completed`; must not be later than the authenticated user's current local date. |
| `status` | string | Yes | `draft`, `planned`, `completed`, `cancelled`, or `missed`. |
| `location` | string or `null` | Yes | Optional. |
| `notes` | string or `null` | Yes | Optional general organizational notes. |
| `source_occurrence` | identifier or `null` | No | Source record when generated through recurrence. Becomes `null` if the source record is later deleted. |
| `time_state` | string or `null` | No | `upcoming`, `overdue`, or `null`. |
| `created_at` | datetime | No | Timezone-aware system timestamp. |
| `updated_at` | datetime | No | Timezone-aware system timestamp. |

`category_id` is accepted in create and update requests but is not returned. `category` is returned but is not writable.

### 8.2 Status-dependent validation

- Every record requires `title`.
- `draft` requires no date field and may preserve any valid optional information.
- `planned`, `cancelled`, and `missed` require `scheduled_date`.
- `completed` requires `completed_date`.
- For a `completed` record, `completed_date` must not be later than the authenticated user's current local date; a future value returns a field-level validation error.
- `category_id` may be omitted or set to `null`.
- A supplied category identifier must exist.
- `scheduled_time` is optional for all statuses.
- Every create or update validates the complete resulting record, not only submitted fields.
- The API does not restrict status transitions beyond these resulting-state rules and the documented reminder and recurrence side effects.

## 9. Examination Collection

### 9.1 List examinations

#### `GET /api/v1/examinations/`

Authentication: required.

Returns only examinations owned by the authenticated user.

Supported query parameters:

| Parameter | Example | Behavior |
|---|---|---|
| `status` | `status=planned` | Exact stored-status filter. |
| `category` | `category=2` | Exact category-identifier filter. |
| `search` | `search=dental` | Case-insensitive containment search against `title`. |
| `ordering` | `ordering=scheduled_date` | Ascending scheduled-date order. |
| `ordering` | `ordering=-scheduled_date` | Descending scheduled-date order. |
| `time_state` | `time_state=past` | Past collection. |
| `time_state` | `time_state=upcoming` | Upcoming collection. |
| `time_state` | `time_state=overdue` | Overdue collection. |

Supplied `status` and `category` filters use AND semantics. Other supplied filters are applied to the same owned queryset. Invalid filter or ordering values return `400 Bad Request`.

Both scheduled-date ordering directions place records with `scheduled_date = null` after all dated records. Equal scheduled dates use identifier as a stable secondary ordering.

Success:

```http
200 OK
```

The response is a JSON array of examination representations.

### 9.2 Past collection

`time_state=past` includes:

```text
status = completed
AND completed_date <= user's current local date
```

or:

```text
status IN (cancelled, missed)
AND scheduled_date <= user's current local date
```

It excludes planned records, draft records, and records whose relevant date is in the future.

### 9.3 Upcoming collection

`time_state=upcoming` includes only planned records that are not overdue:

- records with a future `scheduled_date`;
- records on the user's current local date without `scheduled_time`;
- records on the user's current local date whose `scheduled_time` has not passed.

### 9.4 Overdue collection

`time_state=overdue` includes only planned records meeting either condition:

```text
scheduled_date < user's current local date
```

or:

```text
scheduled_date = user's current local date
AND scheduled_time is not null
AND scheduled_time < user's current local time
```

A current-date planned record without `scheduled_time` is not overdue. Draft, completed, cancelled, and missed records are never overdue.

## 10. Create Examination

### `POST /api/v1/examinations/`

Authentication: required.

Minimal draft request:

```json
{
  "title": "Annual eye examination",
  "status": "draft"
}
```

Draft with optional known information:

```json
{
  "title": "Annual eye examination",
  "status": "draft",
  "scheduled_date": "2026-09-10",
  "location": "City clinic"
}
```

Minimal planned request:

```json
{
  "title": "Annual eye examination",
  "status": "planned",
  "scheduled_date": "2026-09-10"
}
```

Complete planned request:

```json
{
  "category_id": 2,
  "title": "Annual dental checkup",
  "medical_specialty": "Dentistry",
  "scheduled_date": "2026-08-15",
  "scheduled_time": "10:30:00",
  "status": "planned",
  "location": "Central Dental Clinic",
  "notes": "Routine appointment"
}
```

The request must not accept `user_id`, `source_occurrence`, `time_state`, `created_at`, or `updated_at`.

Success:

```http
201 Created
```

The response contains the created examination representation.

## 11. Retrieve Examination

### `GET /api/v1/examinations/{id}/`

Authentication: required.

Responses:

- `200 OK` with the owned examination representation;
- `401 Unauthorized` when authentication is absent or invalid;
- `404 Not Found` when the record does not exist or belongs to another user.

## 12. Update Examination

### `PATCH /api/v1/examinations/{id}/`

Authentication: required.

`PATCH` performs a partial update, but validation is applied to the complete resulting record.

Draft-to-planned request:

```json
{
  "status": "planned",
  "scheduled_date": "2026-09-10"
}
```

Completion request:

```json
{
  "status": "completed",
  "completed_date": "2026-07-15"
}
```

Status-change side effects:

- changing a `planned` examination to `draft`, `completed`, `cancelled`, or `missed` deactivates its reminder in the same transaction;
- an existing recurrence rule remains attached and unchanged;
- changing an examination to `planned` does not reactivate an inactive reminder.

Success:

```http
200 OK
```

The response contains the updated examination representation.

## 13. Delete Examination

### `DELETE /api/v1/examinations/{id}/`

Authentication: required.

Deletion is permanent. The associated reminder and recurrence rule are deleted through cascading deletion. Any examination generated from the deleted examination through recurrence is not deleted and remains retrievable; its `source_occurrence` is set to `null`.

Success:

```http
204 No Content
```

The successful response has no body.

## 14. Reminder Resource

Each examination may have at most one reminder.

Reminder representation:

```json
{
  "id": 51,
  "examination": 184,
  "offset_days": 7,
  "due_date": "2026-08-08",
  "is_active": true,
  "created_at": "2026-07-21T04:15:00Z",
  "updated_at": "2026-07-21T04:15:00Z"
}
```

Rules:

- a reminder record may remain attached regardless of examination status;
- a reminder may be active only when the examination status is `planned`;
- reminder creation, offset updates, and reactivation are allowed only when the examination status is `planned`;
- disabling an existing reminder is allowed regardless of examination status;
- `offset_days` must be a positive whole number;
- `due_date` is read-only and equals `scheduled_date - offset_days` using calendar-date arithmetic;
- `due_date` is recalculated when `scheduled_date` or `offset_days` changes and is null when `scheduled_date` is absent;
- ownership is inherited from the examination;
- changing a `planned` examination to `draft`, `completed`, `cancelled`, or `missed` deactivates the reminder;
- changing an examination to `planned` does not reactivate the reminder automatically.

### 14.1 Retrieve reminder

#### `GET /api/v1/examinations/{id}/reminder/`

Returns the reminder attached to the owned examination.

Responses:

- `200 OK` with the reminder representation;
- `404 Not Found` when the examination is unavailable to the user or has no reminder.

### 14.2 Create reminder

#### `POST /api/v1/examinations/{id}/reminder/`

Request:

```json
{
  "offset_days": 7
}
```

Success:

```http
201 Created
```

A second reminder cannot be created while one already exists for the examination.

### 14.3 Update or disable reminder

#### `PATCH /api/v1/examinations/{id}/reminder/`

Update offset:

```json
{
  "offset_days": 3
}
```

Disable:

```json
{
  "is_active": false
}
```

Re-enable:

```json
{
  "is_active": true
}
```

Success:

```http
200 OK
```

### 14.4 List due reminders

#### `GET /api/v1/reminders/?state=due`

Returns reminders meeting:

```text
is_active = true
AND due_date <= user's current local date
```

Success is a JSON array of reminder representations.

## 15. Recurrence Resource

Each examination may have at most one recurrence rule. An existing rule remains attached when the examination status changes. Recurrence creation and update are allowed only while the examination is `planned`.

Recurrence representation:

```json
{
  "id": 61,
  "examination": 184,
  "interval": "yearly",
  "next_due_date": "2027-08-15",
  "created_at": "2026-07-21T04:20:00Z",
  "updated_at": "2026-07-21T04:20:00Z"
}
```

`next_due_date` is a read-only date or null. It is null when the source examination has no `scheduled_date`; otherwise, it is calculated using calendar-month arithmetic:

- `monthly`: add one calendar month;
- `six_months`: add six calendar months;
- `yearly`: add one calendar year.

When the target month lacks the source day, the result uses the target month's last valid day.

### 15.1 Retrieve recurrence

#### `GET /api/v1/examinations/{id}/recurrence/`

Responses:

- `200 OK` with the recurrence representation;
- `404 Not Found` when the examination is unavailable to the user or has no recurrence rule.

### 15.2 Create recurrence

#### `POST /api/v1/examinations/{id}/recurrence/`

Request:

```json
{
  "interval": "yearly"
}
```

Accepted intervals:

- `monthly`;
- `six_months`;
- `yearly`.

The source examination must be `planned` and have a `scheduled_date`.

Success:

```http
201 Created
```

### 15.3 Update recurrence

#### `PATCH /api/v1/examinations/{id}/recurrence/`

Request:

```json
{
  "interval": "six_months"
}
```

Success:

```http
200 OK
```

## 16. Create Next Occurrence

### `POST /api/v1/examinations/{id}/next-occurrence/`

Authentication: required.

The source examination must be owned by the authenticated user, have status `planned`, `completed`, `cancelled`, or `missed`, contain `scheduled_date`, and have a recurrence rule. A source examination with status `draft` is rejected with `400 Bad Request`.

The operation creates exactly one planned examination using the recurrence rule's calculated next due date and records the source examination in `source_occurrence`.

Success:

```http
201 Created
```

The response contains the generated examination representation.

Field values in the generated examination:

| Field | Value in the generated examination |
|---|---|
| `title` | Copied from the source examination. |
| `category` | Copied from the source examination. |
| `medical_specialty` | Copied from the source examination. |
| `scheduled_time` | Copied from the source examination. |
| `location` | Copied from the source examination. |
| `scheduled_date` | The recurrence rule's calculated next due date. |
| `status` | `planned`. |
| `source_occurrence` | The source examination identifier. |
| `notes` | `null`. |
| `completed_date` | `null`. |

No reminder and no recurrence rule is created for the generated examination. Configuring either one for the generated occurrence remains an explicit user action, which the API permits because the generated occurrence is `planned`.

Repeated request:

```http
200 OK
```

A repeated request that resolves to an existing generated occurrence for the same source examination and calculated due date does not create another record, and the response contains the existing generated examination representation. `201 Created` therefore indicates that the request created the occurrence and `200 OK` indicates that it already existed.

## 17. Calendar

### `GET /api/v1/calendar/?start_date={date}&end_date={date}`

Authentication: required.

Both query parameters are required and use `YYYY-MM-DD` format. `start_date` must not be later than `end_date`.

The response contains calendar entries for owned examinations whose status-specific display date falls within the inclusive range.

Calendar entry representation:

```json
{
  "calendar_date": "2026-08-15",
  "state": "overdue",
  "examination": {
    "id": 184,
    "title": "Annual dental checkup",
    "category": {
      "id": 2,
      "name": "Dental appointment",
      "slug": "dental-appointment"
    },
    "scheduled_date": "2026-08-15",
    "scheduled_time": "10:30:00",
    "completed_date": null,
    "status": "planned",
    "time_state": "overdue"
  }
}
```

Placement:

- `planned`, `cancelled`, and `missed` use `scheduled_date`;
- `completed` uses `completed_date`;
- drafts are excluded;
- records lacking the date required for their calendar status are excluded.

`state` is one of `planned`, `completed`, `cancelled`, `missed`, or `overdue`. A planned record satisfying the overdue rule uses `overdue`.

Success is a JSON array of calendar entries.

## 18. Dashboard

### `GET /api/v1/dashboard/`

Authentication: required.

Success:

```http
200 OK
```

```json
{
  "upcoming": [],
  "overdue": [],
  "recently_completed": [],
  "status_counts": {
    "draft": 0,
    "planned": 0,
    "completed": 0,
    "cancelled": 0,
    "missed": 0
  },
  "category_counts": [
    {
      "category": {
        "id": 1,
        "name": "General medical appointment",
        "slug": "general-medical-appointment"
      },
      "count": 0
    }
  ],
  "uncategorized_count": 0,
  "overdue_count": 0
}
```

Rules:

- `upcoming` uses the same shared calculation as `time_state=upcoming`;
- `overdue` uses the same shared calculation as `time_state=overdue`;
- `recently_completed` contains only owned records satisfying `status = completed`, `completed_date >= current local date - 29 days`, and `completed_date <= current local date`;
- `recently_completed` is ordered by `completed_date` descending and then by `id` descending;
- eligibility filtering and ordering are applied before the collection is limited to five records;
- `recently_completed` is a fixed dashboard preview collection and is not paginated;
- the current local date is calculated in the authenticated user's configured timezone;
- the upper-bound condition on `recently_completed` is retained defensively even though future completion dates are rejected during examination validation;
- `overdue_count` equals the number of records produced by the shared overdue query for the same current time;
- `status_counts` always contains all five status keys, including zero values;
- `category_counts` contains every system-defined category, including zero values;
- `uncategorized_count` counts records whose category is `null`.

## 19. Open Contract Points

None.

The repeated next-occurrence response and the field values of a generated next occurrence were previously unresolved. Both are now defined by accepted design decisions and specified in Section 16.
