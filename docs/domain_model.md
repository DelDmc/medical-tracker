# Medical Tracker Application — Domain Model

## 1. Purpose

This document defines the approved domain model for the Medical Tracker Application MVP.

The requirements specification is authoritative. 
This document translates the accepted requirements and application design decisions into domain entities, relationships, stored fields, derived values, and invariants.

## 2. Scope

The MVP domain model contains:

- `User`;
- `ExaminationCategory`;
- `ExaminationRecord`;
- `Reminder`;
- `RecurrenceRule`.

Calendar entries, dashboard sections, upcoming examinations, past examinations, overdue examinations, due reminders, and recurrence next-due dates are derived views or values. They are not separate core entities.

## 3. Entities

### 3.1 User

Represents an authenticated application account.

Domain responsibilities:

- authenticates through an email address and password;
- owns examination records;
- provides the ownership and security boundary for examination, reminder, and recurrence data;
- stores one supported IANA timezone identifier;
- uses the configured timezone for date and time presentation and time-state calculations.

Relevant attributes:

| Field | Domain type | Required | Rule |
|---|---|---:|---|
| `id` | Identifier | Yes | Internal account identifier. |
| `email` | Email address | Yes | Normalized and unique using case-insensitive comparison. |
| `password` | Password credential | Yes | Stored only through Django's password-hashing framework. |
| `timezone` | IANA timezone identifier | Yes | Must belong to the backend-supported timezone set. |

### 3.2 ExaminationCategory

Represents a fixed, system-defined category used to classify an examination.

Fields:

| Field | Domain type | Required | Rule |
|---|---|---:|---|
| `id` | Identifier | Yes | Internal category identifier. |
| `name` | Text | Yes | Unique human-readable category name. |
| `slug` | Slug | Yes | Stable unique identifier used by seed data and internal references. |

System-defined values:

- General medical appointment;
- Dental appointment;
- Specialist consultation;
- Laboratory test;
- Vaccination;
- Preventive examination;
- Follow-up;
- Other.

Rules:

- categories are inserted through an idempotent data migration;
- duplicate names and slugs are prohibited;
- category resources are read-only for MVP users;
- an examination may reference at most one category;
- category assignment is optional;
- a null category is displayed and counted as **Uncategorized**;
- **Uncategorized** is a presentation fallback, not a stored category row.

### 3.3 ExaminationRecord

Represents a user-owned health-related examination, appointment, checkup, or visit record.

Fields:

| Field | Domain type | Required | Rule |
|---|---|---:|---|
| `id` | Identifier | Yes | Internal examination identifier. |
| `user` | User reference | Yes | Assigned by the backend from the authenticated user and not writable by clients. |
| `category` | ExaminationCategory reference | No | Null means uncategorized. |
| `title` | Text | Yes | Required for every examination status. |
| `medical_specialty` | Text | No | Optional organizational metadata. |
| `scheduled_date` | Date | Conditional | Required for `planned`, `cancelled`, and `missed`; optional for `draft` and `completed`. |
| `scheduled_time` | Time | No | Optional and stored separately from `scheduled_date`. |
| `completed_date` | Date | Conditional | Required for `completed`; optional for other statuses. |
| `status` | Enumeration | Yes | `draft`, `planned`, `completed`, `cancelled`, or `missed`. |
| `location` | Text | No | Optional appointment location. |
| `notes` | Long text | No | Optional general organizational notes. |
| `source_occurrence` | ExaminationRecord reference | No | Identifies the recurring source occurrence when this record was generated as the next occurrence. |
| `created_at` | Timezone-aware datetime | Yes | System generated. |
| `updated_at` | Timezone-aware datetime | Yes | System generated. |

Rules:

- a draft requires only `title`; all other examination fields may be omitted;
- a draft may preserve any valid optional examination information supplied by the user;
- a planned examination requires `title` and `scheduled_date`;
- a cancelled or missed examination requires `title` and `scheduled_date`;
- a completed examination requires `title` and `completed_date`;
- `category` and `scheduled_time` remain optional for a planned examination;
- every create or update operation validates the complete resulting record against its status-dependent rules;
- a supplied category must reference an existing system-defined category;
- ownership cannot be selected or changed by the client.

### 3.4 Reminder

Represents the single in-application reminder that may be associated with an examination.

Fields:

| Field | Domain type | Required | Rule |
|---|---|---:|---|
| `id` | Identifier | Yes | Internal reminder identifier. |
| `examination` | ExaminationRecord reference | Yes | One-to-one relationship; ownership is inherited from the examination. |
| `offset_days` | Positive integer | Yes | Whole-number number of days before the scheduled date. |
| `due_date` | Date | Yes | Calculated as `scheduled_date - offset_days`. |
| `is_active` | Boolean | Yes | Determines whether the reminder may appear as due. |
| `created_at` | Timezone-aware datetime | Yes | System generated. |
| `updated_at` | Timezone-aware datetime | Yes | System generated. |

Rules:

- an examination may have at most one reminder;
- reminder configuration is allowed only for a `planned` examination;
- `offset_days` must be greater than zero and must be a whole number;
- `due_date` is recalculated when `scheduled_date` or `offset_days` changes;
- a reminder is deactivated when its examination becomes `completed`, `cancelled`, or `missed`;
- reminder changes are limited to the examination owner.

### 3.5 RecurrenceRule

Represents the optional recurrence configuration attached to a planned examination.

Fields:

| Field | Domain type | Required | Rule |
|---|---|---:|---|
| `id` | Identifier | Yes | Internal recurrence-rule identifier. |
| `examination` | ExaminationRecord reference | Yes | One-to-one relationship; ownership is inherited from the examination. |
| `interval` | Enumeration | Yes | `monthly`, `six_months`, or `yearly`. |
| `created_at` | Timezone-aware datetime | Yes | System generated. |
| `updated_at` | Timezone-aware datetime | Yes | System generated. |

Rules:

- an examination may have at most one recurrence rule;
- recurrence configuration is allowed only for a `planned` examination;
- unsupported recurrence intervals are rejected;
- the next due date is calculated from the source examination's `scheduled_date` and the recurrence interval;
- future occurrences are created one at a time only after an explicit user request;
- a repeated request must not create another occurrence for the same source occurrence and due date.

## 4. Relationships

```text
User 1 ─────── * ExaminationRecord

ExaminationCategory 1 ─────── * ExaminationRecord
                               category may be null

ExaminationRecord 1 ─────── 0..1 Reminder

ExaminationRecord 1 ─────── 0..1 RecurrenceRule

ExaminationRecord 1 ─────── 0..* generated ExaminationRecord
                               through source_occurrence
```

Ownership of `Reminder` and `RecurrenceRule` is derived through their associated `ExaminationRecord`.

Deleting an examination cascades to its associated reminder and recurrence rule.

## 5. Examination Status

Accepted status values:

- `draft` — an incomplete examination record saved for later;
- `planned` — an examination with a scheduled calendar date that has not been completed, cancelled, or missed;
- `completed` — an examination that occurred and has a completion date;
- `cancelled` — an examination that was cancelled and retains its scheduled date;
- `missed` — an examination that was not attended or completed and retains its scheduled date.

`overdue` is not a persisted examination status. It is a derived time state that applies only to planned examinations.

## 6. Derived Examination Collections and States

All date and time boundaries are evaluated using the authenticated user's configured timezone.

### 6.1 Past Examinations

An examination belongs to the past collection when either condition is true:

```text
status = completed
AND completed_date <= user's current local date
```

```text
status IN (cancelled, missed)
AND scheduled_date <= user's current local date
```

The past collection excludes planned records, draft records, and records whose relevant date is in the future.

### 6.2 Overdue

A planned examination is overdue when:

```text
status = planned
AND (
    scheduled_date < user's current local date
    OR (
        scheduled_date = user's current local date
        AND scheduled_time is not null
        AND scheduled_time < user's current local time
    )
)
```

A planned examination scheduled for the current date without a scheduled time is not overdue.

### 6.3 Upcoming

A planned examination is upcoming when it is not overdue. This includes:

- a future scheduled date;
- the current local date without a scheduled time;
- the current local date with a scheduled time that has not passed.

### 6.4 Calendar Placement

Monthly calendar placement uses:

- `scheduled_date` for `planned`, `cancelled`, and `missed` records;
- `completed_date` for `completed` records.

Draft records are excluded from calendar results. A record lacking the date required for its calendar status is also excluded.

### 6.5 Due Reminder

A reminder is due when:

```text
is_active = true
AND due_date <= user's current local date
```

### 6.6 Recurrence Next Due Date

The recurrence next due date is calculated from the source examination's `scheduled_date`:

- `monthly` adds one calendar month;
- `six_months` adds six calendar months;
- `yearly` adds one calendar year.

When the target month does not contain the source day, the target month's last valid day is used. A yearly recurrence from February 29 therefore resolves to the last valid day of February in a non-leap year.

## 7. Why Overdue Is Derived

The database stores the examination's lifecycle status and scheduled calendar values. The current date and time change without modifying the examination record.

Example stored values:

```text
status = planned
scheduled_date = 2026-07-26
scheduled_time = 09:00
```

Before 09:00 in the user's timezone, the examination is upcoming. After 09:00, it is overdue. The stored facts remain unchanged.

The application therefore calculates overdue during queries or presentation. This prevents stale persisted state and allows rescheduling or timezone-aware boundary evaluation to be reflected immediately.

## 8. Core Invariants

- every examination belongs to exactly one user;
- examination ownership is assigned by the backend and is not writable by clients;
- users cannot retrieve, update, delete, or attach dependent records to another user's examination;
- object lookup for a missing examination and another user's examination returns the same not-found response;
- every examination has a title;
- every planned, cancelled, and missed examination has a scheduled date;
- every completed examination has a completion date;
- a draft may contain only a title or may include valid optional examination information;
- an examination has zero or one system-defined category;
- category absence is represented by null and presented as **Uncategorized**;
- only planned examinations can be upcoming or overdue;
- drafts are excluded from upcoming, overdue, and calendar results;
- an examination has zero or one reminder;
- an examination has zero or one recurrence rule;
- reminders and recurrence rules can be configured only for planned examinations;
- terminal examination statuses deactivate the associated reminder;
- deleting an examination permanently deletes its reminder and recurrence rule;
- next-occurrence creation produces at most one generated examination for a source occurrence and due date.

## 9. Status Changes

The following behavior is defined:

- a draft may change to `planned` through the normal examination update operation when the resulting record contains `scheduled_date`;
- changing any record to `planned`, `cancelled`, or `missed` requires `scheduled_date`;
- changing any record to `completed` requires `completed_date`;
- changing an examination to `completed`, `cancelled`, or `missed` deactivates its reminder in the same transaction;
- every update validates the complete resulting record rather than only the submitted fields.

A complete matrix of all permitted forward, reverse, and correction transitions is not defined by the current requirements or accepted design decisions. No additional transition restriction should be introduced without a corresponding approved decision.

## 10. Date, Time, and Timezone Rules

- `scheduled_date`, `completed_date`, and reminder `due_date` are calendar-date values;
- `scheduled_time` is an optional time value stored separately from `scheduled_date`;
- date-only values are displayed as stored and are not shifted through UTC conversion;
- timestamps representing real instants, including audit timestamps, are timezone-aware and use Django timezone support;
- the user's IANA timezone determines the current local date and time used for upcoming, overdue, past, and due-reminder calculations;
- timezone-aware timestamps are converted to the user's configured timezone for presentation;
- boundary behavior must be tested with a controlled current time.

## 11. Deletion

- users may delete only examinations they own;
- deletion is permanent in the MVP;
- the user interface requires explicit confirmation before sending the delete request;
- deleting an examination cascades to its associated reminder and recurrence rule;
- the deleted examination and its dependent records cannot be retrieved afterward.