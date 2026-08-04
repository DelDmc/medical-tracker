# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Status

This repository is currently **documentation-only**. `backend/` and `frontend/` exist as empty directories — no Django project, no React project, and no dependency manifests have been created yet. There are no build, lint, or test commands to run because there is no code to build, lint, or test. Do not invent commands or scaffolding that isn't backed by a file in the repo.

Before writing any implementation code, read the relevant documents in `docs/` — they are a complete, decision-level specification (functional requirements, accepted design decisions, domain model, API contract, and user flows) for a Django REST Framework + React application that has not been built yet. Treat them as the plan to implement against, not background reading to skim.

## Document Source-of-Truth Hierarchy

When documents disagree, this precedence applies (highest first):

1. `docs/requirements_specification.md` — authoritative, testable requirements (`FR-`, `UX-`, `SEC-`, `PRV-`, `TECH-` identifiers).
2. `docs/product_definition.md` — product-level summary and MVP scope/exclusions.
3. `docs/design_specification.md` — accepted implementation decisions (`ADS-*` identifiers, one decision per requirement, always phrased "It is decided ...").
4. `docs/domain_model.md`, `docs/api_contract.md`, `docs/user_flows.md` — detailed design artifacts derived from the above.
5. `docs/test_specification.md` — Given/When/Then test cases (`TC-<REQ-ID>-NN`), one or more per requirement.

`docs/traceability_matrix.md` is an administrative mapping from requirement IDs to design-decision IDs to API operations — it doesn't define behavior itself. When implementing a feature, find its requirement ID, read its `ADS-*` decision(s) for the exact contract, and cross-check `api_contract.md` / `domain_model.md` for the concrete shape.

Every `ADS-*` decision maps to exactly one requirement; a requirement may have several decisions but a decision never spans multiple requirements. If a change appears to require altering a requirement, that must happen in `requirements_specification.md` first — don't let implementation drift silently redefine behavior described there.

## Architecture (as specified, to be implemented)

**Backend:** Django + Django REST Framework, JSON API namespaced under `/api/v1/`. Authenticated-by-default permissions; auth endpoints (`register`, `csrf`, `login`, `refresh`, `logout`) and `health` are the explicit exceptions.

**Frontend:** React, mobile-first responsive, consumes the backend only through the documented API contract.

**Auth model** (see `api_contract.md` §5 and design decisions `ADS-FR-005-*` through `ADS-FR-008-*`, `ADS-SEC-005-*`):
- Short-lived JWT `access_token` (10 min) returned in the JSON response body and held only in frontend memory (never `localStorage`); sent via `Authorization: Bearer <token>`.
- Longer-lived `refresh_token` set as an `HttpOnly`, host-only cookie scoped to `/api/v1/auth/`, rotated on every use, with an absolute 7-day session lifetime from login that rotation does not extend.
- CSRF protection on `login`, `refresh`, and `logout` via `GET /api/v1/auth/csrf/` bootstrap + `X-CSRFToken` header; the CSRF token itself is also memory-only on the frontend, never read from the cookie directly.
- Frontend does at most one refresh-and-replay on a 401, coordinates concurrent 401s into a single in-flight refresh, and distinguishes a failed *initialization* refresh (silent redirect to login) from a failed *active-session* refresh (redirect + session-expired message).
- Logout clears local state before the network request, writes a `medical_tracker.logout_intent` localStorage marker to suppress refresh-on-init, and removes that marker on next successful login.

**Domain model** (`docs/domain_model.md`): `User` (1) → `ExaminationRecord` (*); `ExaminationCategory` (fixed, seeded, read-only, nullable FK on examination); `ExaminationRecord` → `Reminder` (0..1) and → `RecurrenceRule` (0..1), both cascade-deleted with the examination and inherit its ownership. `ExaminationRecord.source_occurrence` self-references the examination a recurring occurrence was generated from; deleting that source examination sets `source_occurrence` to null on the generated occurrence rather than deleting it or blocking the delete.

Core rules that recur throughout the spec and are easy to violate accidentally:
- **`overdue` is never stored** — it's derived at query/presentation time from `status`, `scheduled_date`, `scheduled_time`, and the user's timezone-derived current local time. Don't add an `overdue` column or cache it.
- Status-dependent required fields: `title` always; `scheduled_date` for `planned`/`cancelled`/`missed`; `completed_date` (not in the future, per user's local date) for `completed`. Every create/update validates the *complete resulting record*, not just the submitted diff.
- Drafts are excluded from upcoming/overdue/calendar results regardless of what optional fields they happen to have filled in.
- Reminders/recurrence: creation, updates, and reactivation are permitted only while the examination is `planned` — rejected for `draft` **and** for `completed`/`cancelled`/`missed`, not just drafts; both persist across status changes; a `planned → non-planned` transition deactivates (not deletes) the reminder; moving back to `planned` never auto-reactivates it; disabling an existing reminder is allowed regardless of status.
- Recurrence next-due-date uses calendar-month arithmetic with last-valid-day clamping (e.g., yearly from Feb 29 lands on Feb 28 in non-leap years); "create next occurrence" is idempotent per (source, calculated due date) — a repeat returns `200` with the existing record instead of creating a duplicate (`201` only on first creation).
- All owner-scoped lookups (examination/reminder/recurrence) must return an identical 404 for "doesn't exist" and "belongs to another user" — never leak existence via status-code difference.
- Date-only fields (`scheduled_date`, `completed_date`, reminder `due_date`) are stored/displayed as-is, never shifted through UTC conversion; only true instants (`created_at`, `updated_at`, JWT expiry) are timezone-aware and converted for display.

## Working in `docs/`

- `docs/design_specification.md` decisions are all `Accepted`; a new decision should also be Accepted unless you have a concrete reason to mark it `Proposed` pending review — check Section 10's traceability summary counts and update them if you add/remove decisions.
- Follow the existing per-decision structure exactly: unique `ADS-<REQ>-NN` id, status, single requirement reference, "It is decided ..." decision text, rationale, verification impact.
- `docs/test_specification.md` holds one Given/When/Then test case per scenario, each with a unique `TC-<REQ-ID>-NN` id and exactly one requirement reference — mirrors the `ADS-<REQ-ID>-NN` pattern. When you write the actual test in code later, put its `TC-*` id in the test name or docstring so the link back to this spec is traceable; don't invent a new id scheme per test file. Update Section 11's traceability summary counts whenever you add or remove a test case.
- `DEVELOPMENT_LOG.md` has its own usage rules at the top (one entry per dev day, newest first, only record actually-completed work, never record secrets/tokens/private medical data). Follow them when asked to update the log — don't mark something complete unless its acceptance criteria in the requirements are actually satisfied.
