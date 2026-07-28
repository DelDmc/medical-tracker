# Medical Tracker Application — Initial API Contract

## 1. Purpose

This document defines the initial frontend-backend contract for authentication support and the examination-record vertical feature.

The requirements specification is authoritative. Authentication token transport remains unresolved in the Application Design Specification.

## 2. General Conventions

- Base path: `/api/`.
- Request and response bodies use JSON.
- JSON fields use `snake_case`.
- Datetimes use ISO 8601 with timezone information.
- User ownership is derived from authentication and is never accepted from the request body.
- User-owned object queries are restricted to the authenticated user.
- A request for another user's object returns `404 Not Found` rather than disclosing its existence.
- Validation errors use field-level messages where applicable.

## 3. Authentication Endpoints

Initial routes:

```http
POST /api/auth/register/
POST /api/auth/login/
POST /api/auth/refresh/
POST /api/auth/logout/
```

The final request and response details depend on the accepted JWT storage and transport design.

## 4. Category Endpoint

```http
GET /api/categories/
```

Behavior:

- authentication required;
- returns the fixed system-defined categories;
- read-only for the MVP;
- no create, update, or delete category endpoints.

## 5. Examination Endpoints

```http
GET    /api/examinations/
POST   /api/examinations/
GET    /api/examinations/{id}/
PATCH  /api/examinations/{id}/
DELETE /api/examinations/{id}/
```

Separate upcoming and overdue endpoints are not used.

## 6. Examination List

### Request

```http
GET /api/examinations/
```

Authentication: required.

### Supported query parameters

| Parameter | Example | Purpose |
|---|---|---|
| `status` | `status=draft` | Filter by stored lifecycle status. |
| `time_state` | `time_state=upcoming` | Filter by calculated time state. |
| `category` | `category=3` | Filter by category identifier. |
| `category_state` | `category_state=uncategorized` | Return records with no category. |
| `search` | `search=dentist` | Search supported text fields. |
| `ordering` | `ordering=scheduled_at` | Sort by an allowed field. |

Accepted `time_state` values:

- `upcoming`;
- `overdue`.

Invalid values return `400 Bad Request` with a clear validation error.

### Time-state behavior

`time_state=upcoming` returns records where:

```text
status = planned
scheduled_at is not null
scheduled_at >= current time
```

`time_state=overdue` returns records where:

```text
status = planned
scheduled_at is not null
scheduled_at < current time
```

## 7. Create Examination

### Request

```http
POST /api/examinations/
```

Example draft request:

```json
{
  "title": "Annual eye examination",
  "status": "draft"
}
```

Example unscheduled planned request:

```json
{
  "title": "Annual eye examination",
  "status": "planned",
  "category_id": null,
  "scheduled_at": null
}
```

Example scheduled planned request:

```json
{
  "title": "Annual dental checkup",
  "status": "planned",
  "category_id": 1,
  "medical_specialty": "Dentistry",
  "scheduled_at": "2026-08-15T10:30:00+08:00",
  "location": "Central Dental Clinic",
  "notes": "Routine appointment"
}
```

The request must not accept `user_id` as an ownership assignment.

### Success

```http
201 Created
```

Representative response:

```json
{
  "id": 184,
  "category": {
    "id": 1,
    "name": "Dentist"
  },
  "title": "Annual dental checkup",
  "medical_specialty": "Dentistry",
  "scheduled_at": "2026-08-15T10:30:00+08:00",
  "completed_at": null,
  "status": "planned",
  "location": "Central Dental Clinic",
  "notes": "Routine appointment",
  "time_state": "upcoming",
  "created_at": "2026-07-21T12:10:00+08:00",
  "updated_at": "2026-07-21T12:10:00+08:00"
}
```

For an unscheduled planned record, `time_state` is `null`.

## 8. Retrieve Examination

```http
GET /api/examinations/{id}/
```

Responses:

- `200 OK` for an owned record;
- `401 Unauthorized` when authentication is absent or invalid;
- `404 Not Found` when the record does not exist or belongs to another user.

## 9. Update Examination

```http
PATCH /api/examinations/{id}/
```

`PATCH` performs a partial update, but validation is applied to the resulting complete record.

Example completion request:

```json
{
  "status": "completed",
  "completed_at": "2026-08-15T11:15:00+08:00"
}
```

The API rejects a completed result without a valid completion date.

Allowed status transitions remain subject to an open application design decision.

## 10. Delete Examination

```http
DELETE /api/examinations/{id}/
```

Responses:

- `204 No Content` after successful deletion;
- `401 Unauthorized` when authentication is absent or invalid;
- `404 Not Found` when the record does not exist or belongs to another user.

## 11. Validation Error Format

Representative field-level response:

```json
{
  "title": ["This field is required."],
  "completed_at": ["A completion date is required when status is completed."]
}
```

A non-field error may be used for rules involving multiple fields:

```json
{
  "non_field_errors": ["The submitted field combination is not valid."]
}
```

A universal custom response envelope is not introduced unless an accepted requirement or design decision requires it.

## 12. Pagination

Pagination behavior and response shape remain to be finalized before list implementation. The selected form must be used consistently across list endpoints.