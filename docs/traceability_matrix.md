# Medical Tracker Application — Traceability Matrix

## 1. Purpose

This document maintains traceability between requirements, accepted application design decisions, and API operations. Implementation tasks and tests maintain their requirement references in their own artifacts.

It is an administrative mapping document. It does not define product behavior, domain rules, or API behavior. When a mapped source changes, the source document remains authoritative and the affected detailed artifacts must be reviewed.

## 2. Maintenance Rules

- Requirement identifiers and design-decision identifiers are recorded only in this matrix where practical.
- The API contract describes the interface without reproducing these identifiers.
- Reordering document sections does not require changing this matrix when identifiers remain unchanged.
- When a requirement or decision is added, removed, superseded, or materially changed, affected rows must be updated.
- One API operation may map to several requirements and decisions.
- Requirements that are purely frontend, deployment, documentation, or internal persistence concerns may have no direct API-operation row.
- A mapped design decision may be accepted or proposed; `design_specification.md` remains authoritative for design-decision status.

## 3. API Traceability

| API area or operation | Requirement references | Design-decision references |
|---|---|---|
| General versioned JSON API under `/api/v1/` | TECH-001 | ADS-TECH-001-01 |
| Authentication required by default | SEC-001 | ADS-SEC-001-01 |
| Owner-scoped examinations, reminders, and recurrence | SEC-002 | ADS-SEC-002-01 |
| Explicit CORS origin allowlist | SEC-005 | ADS-SEC-005-01 |
| Credentialed CORS requests and allowed headers | SEC-005 | ADS-SEC-005-02 |
| Django CSRF trusted origins | SEC-005 | ADS-SEC-005-03 |
| Refresh-token cookie attributes | SEC-005 | ADS-SEC-005-04 |
| CSRF-token bootstrap behavior | SEC-005 | ADS-SEC-005-05 |
| Frontend CSRF-token handling | SEC-005 | ADS-SEC-005-06 |
| CSRF-cookie `HttpOnly` attribute | SEC-005 | ADS-SEC-005-07 |
| CSRF-cookie environment attributes | SEC-005 | ADS-SEC-005-08 |
| Uniform not-found response | SEC-006 | ADS-SEC-006-01 |
| Date, time, and timestamp representations | TECH-002 | ADS-TECH-002-01 |
| `GET /api/v1/health/` | TECH-004 | ADS-TECH-004-01 |
| `POST /api/v1/auth/register/` — account creation | FR-001 | ADS-FR-001-01 |
| Registration email validation | FR-002 | ADS-FR-002-01 |
| Registration password validation | FR-003, SEC-003 | ADS-FR-003-01, ADS-SEC-003-01 |
| Registration timezone validation | FR-004 | ADS-FR-004-01 |
| `GET /api/v1/auth/csrf/` | SEC-005 | ADS-SEC-005-02, ADS-SEC-005-03, ADS-SEC-005-05, ADS-SEC-005-07, ADS-SEC-005-08 |
| `POST /api/v1/auth/login/` request contract | FR-005, SEC-005 | ADS-FR-005-01, ADS-SEC-005-02, ADS-SEC-005-03, ADS-SEC-005-06 |
| Login access-token response | FR-005 | ADS-FR-005-02 |
| Access-token lifetime | FR-005 | ADS-FR-005-06 |
| Login refresh-token cookie | FR-005, SEC-005 | ADS-FR-005-03, ADS-SEC-005-04 |
| Frontend access-token storage and bearer transport | FR-005 | ADS-FR-005-04 |
| Generic invalid-credentials response | FR-005 | ADS-FR-005-05 |
| `POST /api/v1/auth/logout/` request contract | FR-006, SEC-005 | ADS-FR-006-01, ADS-SEC-005-02, ADS-SEC-005-03, ADS-SEC-005-06 |
| Logout refresh-token invalidation | FR-006 | ADS-FR-006-02 |
| Logout refresh-cookie clearing | FR-006, SEC-005 | ADS-FR-006-03, ADS-SEC-005-04 |
| Idempotent logout response | FR-006 | ADS-FR-006-04 |
| Immediate local session-state clearing | FR-006 | ADS-FR-006-05 |
| Persistent logout-intent marker and restoration suppression | FR-006 | ADS-FR-006-06 |
| Logout-intent marker removal after successful login | FR-006 | ADS-FR-006-07 |
| Logout navigation outcome | FR-006 | ADS-FR-006-08 |
| `POST /api/v1/auth/refresh/` request contract | FR-007, SEC-005 | ADS-FR-007-01, ADS-SEC-005-02, ADS-SEC-005-03, ADS-SEC-005-06 |
| Refresh-token rotation and previous-token invalidation | FR-007 | ADS-FR-007-02 |
| Refresh-session maximum lifetime | FR-007 | ADS-FR-007-07 |
| Replacement refresh-token cookie | FR-007, SEC-005 | ADS-FR-007-03, ADS-SEC-005-04 |
| Refreshed access-token response | FR-007 | ADS-FR-007-04 |
| Invalid refresh-token response and stale-cookie clearing | FR-007, SEC-005 | ADS-FR-007-05, ADS-SEC-005-04 |
| Session restoration after page reload | FR-007 | ADS-FR-007-06 |
| Active-session access-token recovery | FR-008 | ADS-FR-008-01 |
| Failed active-session refresh outcome | FR-008 | ADS-FR-008-02 |
| Failed initialization refresh outcome | FR-008 | ADS-FR-008-03 |
| Single-flight refresh coordination | FR-008 | ADS-FR-008-04 |
| `GET` and `PATCH /api/v1/account/` | FR-009 | ADS-FR-009-01 |
| Draft examination creation | FR-010 | ADS-FR-010-01 |
| Planned examination creation | FR-011 | ADS-FR-011-01 |
| Examination status values | FR-012 | ADS-FR-012-01 |
| Optional examination metadata | FR-013 | ADS-FR-013-01 |
| Status-dependent examination validation | FR-014 | ADS-FR-014-01 |
| Future completed-date rejection | FR-014 | ADS-FR-014-02 |
| Category and status reference validation | FR-015 | ADS-FR-015-01 |
| Draft-to-planned update | FR-016 | ADS-FR-016-01 |
| Reminder rejection for drafts | FR-017 | ADS-FR-017-01 |
| Recurrence rejection for drafts | FR-018 | ADS-FR-018-01 |
| Draft exclusion from upcoming, overdue, and calendar data | FR-019 | ADS-FR-019-01 |
| `GET /api/v1/examinations/` | FR-020 | ADS-FR-020-01 |
| `GET /api/v1/examinations/{id}/` | FR-021 | ADS-FR-021-01 |
| `PATCH /api/v1/examinations/{id}/` | FR-022 | ADS-FR-022-01 |
| `DELETE /api/v1/examinations/{id}/` and cascade | FR-023 | ADS-FR-023-01 |
| Category assignment | FR-025 | ADS-FR-025-01 |
| `GET /api/v1/categories/` and fixed category set | FR-026 | ADS-FR-026-01 |
| Null category representation | FR-027 | ADS-FR-027-01 |
| Examination title search | FR-028 | ADS-FR-028-01 |
| Examination status and category filters | FR-029 | ADS-FR-029-01 |
| Scheduled-date ordering and null placement | FR-030 | ADS-FR-030-01 |
| `time_state=past` | FR-031 | ADS-FR-031-01 |
| `time_state=upcoming` | FR-032 | ADS-FR-032-01 |
| Derived overdue state and boundary | FR-033 | ADS-FR-033-01, ADS-FR-033-02 |
| Overdue status restriction | FR-034 | ADS-FR-034-01 |
| Reminder create, update, and disable operations | FR-035 | ADS-FR-035-01 |
| Reminder due-date calculation | FR-036 | ADS-FR-036-01 |
| Due-reminder query | FR-037 | ADS-FR-037-01 |
| Automatic reminder deactivation | FR-038 | ADS-FR-038-01 |
| Recurrence create and update operations | FR-039 | ADS-FR-039-01 |
| Recurrence persistence across status changes | FR-039 | ADS-FR-039-02 |
| Recurrence next-due-date calculation | FR-040 | ADS-FR-040-01 |
| Null next due date without a scheduled date | FR-040 | ADS-FR-040-02 |
| `POST /api/v1/examinations/{id}/next-occurrence/` | FR-041 | ADS-FR-041-01 |
| Allowed next-occurrence source statuses | FR-041 | ADS-FR-041-02 |
| Calendar date-range API | FR-042 | ADS-FR-042-01 |
| Calendar state value supplied to the frontend | FR-043 | ADS-FR-043-01 |
| `GET /api/v1/dashboard/` examination sections | FR-044 | ADS-FR-044-01 |
| Dashboard `recently_completed` eligibility window | FR-044 | ADS-FR-044-02 |
| Dashboard `recently_completed` ordering | FR-044 | ADS-FR-044-03 |
| Dashboard `recently_completed` limit and pagination behavior | FR-044 | ADS-FR-044-04 |
| Dashboard status counts | FR-045 | ADS-FR-045-01 |
| Dashboard `category_counts` and `uncategorized_count` | FR-046 | ADS-FR-046-01 |
| Dashboard overdue count | FR-047 | ADS-FR-047-01 |
| Examination field boundary | PRV-001 | ADS-PRV-001-01 |
| Examination create-data boundary | PRV-002 | ADS-PRV-002-01 |

## 4. Requirements Without a Direct API Operation

The following requirement groups are verified outside a direct API contract operation and are therefore not represented as standalone endpoint rows:

- user-interface layout, form behavior, accessibility, and delete confirmation;
- the public non-clinical-purpose statement;
- environment-variable configuration, production debug configuration, CORS deployment behavior, HTTPS deployment, and repository documentation;
- secret scanning and other repository-level controls.

Where these concerns depend on API behavior, the relevant API operation is already mapped in the table above.