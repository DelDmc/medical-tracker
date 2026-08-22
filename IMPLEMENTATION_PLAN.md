# Medical Tracker Application — Implementation Plan

## 1. Purpose and Standing

**This document is non-normative.** It is not part of the source-of-truth hierarchy defined in `product_definition.md` §2 and repeated in `CLAUDE.md`. It defines no behavior. It must never be cited as authority for an implementation choice.

It sequences work that is already specified elsewhere. Every behavioral statement an implementer needs comes from the authoritative documents, in this precedence order:

1. `docs/requirements_specification.md` — the requirements (`FR-`, `UX-`, `SEC-`, `PRV-`, `TECH-`).
2. `docs/product_definition.md` — product scope, §8 exclusions, §11 Definition of Done.
3. `docs/design_specification.md` — accepted decisions (`ADS-*`), one requirement each.
4. `docs/domain_model.md`, `docs/api_contract.md`, `docs/user_flows.md` — derived design artifacts.
5. `docs/test_specification.md` — `TC-*` cases, one requirement each.

`docs/traceability_matrix.md` is administrative. `docs/review_findings.md` is non-normative and must never be cited as authority. Neither this plan nor either of those documents can settle a behavioral question.

**Why this file sits at the repository root and not in `docs/`.** `docs/` holds the specification of the *product* — what the application must do, decided and change-controlled. This plan is about how this *repository* gets built, which is what the root-level files already cover: `README.md` (what the project is and how to run it), `CLAUDE.md` (how an agent works here), `DEVELOPMENT_LOG.md` (what was done, day by day). This plan is the forward-looking counterpart to that log. Placement is also the durable signal: everything in `docs/` except `review_findings.md` is normative, so a plan filed there invites exactly the misreading §1 opens by forbidding — and a reader who skims the disclaimer still sees the directory. `review_findings.md` is not a counter-example; it is non-normative *about the specification itself*, and its findings are fixed inside `docs/`. This plan is downstream of all of it and describes work instead.

**Which branch it lives on.** The project branch, `project/mvp` — not `main`. `main` is the documentation snapshot and receives implementation work only at MVP completion (D1); this plan is implementation-phase working material that will be corrected as slices land. Keeping it on the project branch means those corrections do not require commits to `main` during implementation. It reaches `main` with everything else at the final merge, by which point it is spent — `DEVELOPMENT_LOG.md` is the record that outlives it.

**`docs/reviews/` stays in `docs/`.** The eight manual review artifacts (assumption A3) are verification evidence for named `TC-*` cases, permanent, and written for a human auditor checking requirement coverage — that belongs beside `test_specification.md`, not beside this plan.

### 1.1 How to use this plan

An implementer reads §1–§4 of this plan once (standing rules, decisions, invariants, and where shared machinery lives), then picks **one task** from §5, reads only the documents that task's **Read before starting** names, and executes it. Nothing else in §5 needs reading to execute a task. A task is self-contained on that basis; if it is not, that is a defect in this plan — record it and ask, do not improvise.

Three rules override anything written here:

- **The spec is the contract.** No task may redefine documented behavior. If implementing a task appears to require changing a requirement, stop. The change happens in `requirements_specification.md` first, by the owner. Escalate; do not proceed under a reinterpretation.
- **New contradictions become findings, not decisions.** A contradiction discovered between authoritative documents is written up as a proposed finding for `docs/review_findings.md` using the next free identifier. `RF-01`…`RF-23` are spent and identifiers are never reused; `RF-24`…`RF-27` were raised and resolved while this plan was written (§9.2), so the next new one is **`RF-28`**. Follow `review_findings.md` §2 for the record's shape. Resolving a finding that requires a spec change is the owner's call.
- **Never mark work complete** unless the requirement's acceptance criteria in `requirements_specification.md` are actually satisfied and its `TC-*` cases pass. This applies to `DEVELOPMENT_LOG.md` entries (see its own usage rules, rule 4) and to the Phase Progress table.

---

## 2. Decisions Taken and Assumptions

Every item below was open when this plan was written. `requirements_specification.md` §8 keeps technology selections out of itself, and `ADS-*` decisions are requirement-linked, so none of these belong in `design_specification.md` either.

| # | Decision | Standing |
|---|---|---|
| D1 | **Branching:** nothing touches `main` until MVP completion. One project branch, `project/mvp`, cut from `main`; one `feature/<slice-id>-<slug>` branch per slice cut from `project/mvp` and squash-merged back when that slice's Definition of Done passes; `project/mvp` merges into `main` once, at MVP completion, and is deleted afterwards. A project branch is per-project and finite — not a permanent GitFlow `develop`. | *Confirmed by owner* |
| D2 | **Database:** SQLite for local development, PostgreSQL in production. | *Confirmed by owner* |
| D3 | **JWT:** hand-rolled on `PyJWT`. Not `djangorestframework-simplejwt` — its rotation recomputes `exp` relative to rotation time, which `ADS-FR-007-08` forbids. | *Confirmed by owner* |
| D4 | **Backend tests:** `pytest` + `pytest-django`, with `freezegun` for the frozen-clock cases. | *Confirmed by owner* |
| D5 | **Settings:** typed environment loader with separate development/production modules and fail-fast production validation, per `ADS-TECH-003-01`. | *Confirmed by owner* |
| D6 | **Current local time:** one injectable clock service, so every frozen-clock `TC-*` case can control it. | *Confirmed by owner* |
| D7 | **Frontend:** TypeScript + Vite + React Router + TanStack Query + CSS Modules + Vitest + React Testing Library + MSW. | *Confirmed by owner* |
| D8 | **Node:** upgrade to 20 LTS. The installed v19.9.0 is refused by Vite 5+ and Vitest 1+ (`^18 \|\| >=20`). | *Confirmed by owner* |
| D9 | **Technology decisions are recorded in a new non-normative `docs/technology_decisions.md`,** sitting outside the source-of-truth hierarchy exactly as `review_findings.md` does. The task that introduces a technology writes its entry. | *Confirmed by owner* |
| D10 | **Deployment is in scope now** — Slice 19 closes `TECH-006` and the deployment-layer `SEC-005` cases. | *Confirmed by owner* |
| D11 | **Accepted-status gating applies.** A task skips any requirement, decision, or test case not marked `Accepted`. All 73 requirements, 120 decisions and 274 test cases are `Accepted` today, so nothing is skipped; an item that later moves to `Draft` blocks its task and is escalated. | *Confirmed by owner* |
| D12 | **Deployment platform:** backend web service plus managed PostgreSQL on **Render**; frontend static site on **Vercel**. Frontend and backend stay on separate origins — the frontend must not proxy `/api/` through its own origin, which would contradict the production `SameSite=None` cookies `ADS-SEC-005-04` and `ADS-SEC-005-08` require. Render terminates HTTPS and sets `X-Forwarded-Proto`, the single reverse-proxy header `ADS-TECH-006-01` permits the backend to trust. Use a paid Render instance type and a paid PostgreSQL plan: free web services sleep and free databases expire, which makes `TC-TECH-006-01/02` and the six deployment-layer `TC-SEC-005-*` cases cold-start flaky. | *Confirmed by owner* |

### 2.1 Assumptions (owner did not specify; labelled, not hidden)

`A1` is absent by design: the deployment platform was settled by the owner and is now **D12** above. Assumption identifiers follow the same rule as `RF-NN` — spent, never reused, never renumbered — so the list starts at `A2`.

| # | Assumption | Why, and what changes if wrong |
|---|---|---|
| A2 | **`curl`, `wget` and `docker` are denied** by `.claude/settings.local.json`, and no PostgreSQL client is installed. Deployment verification (Slice 19) and any Postgres-specific check must be run by the owner, or the permission allowlist extended first. | Slice 19 tasks say explicitly which steps are owner-run. |
| A3 | **Manual review artifacts live in `docs/reviews/<TC-ID>-<slug>.md`,** each opening with a non-normative standing line. This adds a subdirectory under `docs/`; confirm with the owner before Slice 7's Task 7.7 (the first one). Fallback if refused: record the review inside the day's `DEVELOPMENT_LOG.md` entry. | Affects 8 test cases (7 `Documented review` + 1 `Data-model review`); nothing else. |
| A4 | **Python packaging:** `backend/requirements.txt` + `backend/requirements-dev.txt` for dependencies, `backend/pyproject.toml` for tool config (pytest, ruff). Pip-installable with no extra tooling. | Only the install/verify commands change. |
| A5 | **Secret scanning uses `detect-secrets`** (pip-installable). `gitleaks` would need a binary download, and `curl`/`wget` are denied. | Only `TC-SEC-004-01`'s command changes. |
| A7 | **The registration timezone list comes from the browser** (`Intl.supportedValuesOf('timeZone')`, with a small static fallback). `ADS-UX-004-01` says the control is "populated from supported values supplied by the application", and `api_contract.md` defines no timezone endpoint — adding one would be a contract change. The backend stays authoritative: an identifier the browser offers but Python's `zoneinfo` rejects surfaces as a `timezone` field error, which is `TC-UX-004-02`. | If the owner wants a served list, `api_contract.md` needs a new endpoint first. |
| A6 | **`PUT` on `/api/v1/examinations/{id}/` is not implemented.** `ADS-FR-022-01` makes it conditional on being "retained in the documented API contract"; `api_contract.md` §12 documents `PATCH` only. | If the owner wants `PUT`, it needs a contract change first. |

---

## 3. Invariants Every Task Must Respect

These cut across slices. Violating one is a defect even when the task's own `TC-*` cases pass. They are reproduced here verbatim from the sources named; when in doubt, read the source.

### 3.1 Domain invariants

- **`overdue` is never stored.** It is derived at query/presentation time from `status`, `scheduled_date`, `scheduled_time`, and the user's timezone-derived current local time. One shared query/service implementation, reused by the list `time_state` filter, the calendar `state`, and the dashboard `overdue`/`overdue_count`. Sources: `ADS-FR-033-01`, `ADS-FR-033-02`, `ADS-FR-047-01`, `domain_model.md` §5–§7.
- **Status-dependent required fields:** `title` always; `scheduled_date` for `planned`/`cancelled`/`missed`; `completed_date` (not later than the user's current local date) for `completed`. **Every create and update validates the complete resulting record, not the submitted diff.** Sources: `ADS-FR-014-01`, `ADS-FR-014-02`, `api_contract.md` §8.2, `domain_model.md` §3.3.
- **Drafts are excluded from upcoming, overdue, and calendar results** regardless of which optional fields they contain. Source: `ADS-FR-019-01`.
- **Reminders/recurrence:** creation, offset updates, and reactivation are permitted **only while the examination is `planned`** — rejected for `draft` *and* for `completed`/`cancelled`/`missed`. Disabling an existing reminder is allowed in any status. A `planned → non-planned` transition **deactivates** (never deletes) the reminder, in the same transaction. Moving back to `planned` never auto-reactivates. A recurrence rule always stays attached across status changes. Sources: `ADS-FR-035-02`, `ADS-FR-038-01`, `ADS-FR-039-01`, `ADS-FR-039-02`.
- **Recurrence next-due-date uses calendar-month arithmetic with last-valid-day clamping** (yearly from Feb 29 → Feb 28 in a non-leap year). "Create next occurrence" is **idempotent per (source examination, calculated due date)**: `201` on first creation, `200` with the existing record on repeat. Sources: `ADS-FR-040-01`, `ADS-FR-041-01`, `ADS-FR-041-03`.
- **All owner-scoped lookups (examination, reminder, recurrence) return an identical 404** for "does not exist" and "belongs to another user". Login returns an identical `401` for unknown email and wrong password. Sources: `ADS-SEC-006-01`, `ADS-SEC-006-02`, `api_contract.md` §3.3.
- **Date-only fields (`scheduled_date`, `completed_date`, reminder `due_date`) are stored and displayed as-is and are never shifted through UTC.** Only true instants (`created_at`, `updated_at`, token expiry) are timezone-aware and converted for display. Sources: `ADS-TECH-002-01`, `ADS-UX-007-01`, `domain_model.md` §10.
- **Ownership is assigned by the backend and is never writable by a client;** `user_id`, `source_occurrence`, `time_state`, `created_at`, `updated_at` are not accepted on write. Sources: `ADS-SEC-002-01`, `api_contract.md` §8.1 and §10.

### 3.2 Auth model — one coherent design, not loose details

Read `api_contract.md` §5 together with `ADS-FR-005-*`, `ADS-FR-006-*`, `ADS-FR-007-*`, `ADS-FR-008-*`, `ADS-SEC-005-*`, `ADS-SEC-007-01`. The pieces interlock:

- **Access token:** JWT, HS256 only, 10-minute lifetime, claims `sub` / `token_type: "access"` / `iat` / `exp`. Returned in the JSON body field `access_token`. Held **only in frontend memory** — never `localStorage` or `sessionStorage`. Sent as `Authorization: Bearer <access_token>`. A token whose header `alg` is not exactly `HS256`, or whose `token_type` is not `access`, is rejected as a bearer credential.
- **Refresh token:** JWT, HS256 only, claims `sub` / `token_type: "refresh"` / `jti` / `session_start` / `iat` / `exp`. Delivered **only** in an `HttpOnly`, host-only `refresh_token` cookie scoped to path `/api/v1/auth/`; never in a JSON body. Rotated on every use. `session_start` is set once at login and copied unchanged into every rotated token; `exp` is computed as `session_start + 7 days` at login **and at every rotation** — never relative to rotation time. That is the whole of the absolute-session-lifetime mechanism.
- **Revocation:** a `RevokedRefreshToken(jti, expires_at)` table. Logout inserts the token it invalidates; every successful rotation inserts the token it supersedes. A refresh whose `jti` is in the table is rejected. Rows past `expires_at` carry no meaning and may be purged.
- **CSRF:** `GET /api/v1/auth/csrf/` bootstraps; `login`, `refresh` and `logout` require a matching `X-CSRFToken` header. The CSRF cookie is `HttpOnly` in both environments, path `/api/v1/`. The frontend holds `csrf_token` in memory and **never reads the cookie directly**.
- **Frontend refresh behavior:** at most **one** refresh-and-replay per 401; concurrent 401s **single-flight** onto one in-progress refresh; a failed *initialization* refresh redirects silently, a failed *active-session* refresh redirects **with** a session-expired message carried through navigation state.
- **Logout:** clears local state **first**, writes `medical_tracker.logout_intent = "true"` to `localStorage`, then sends the request; navigates to login whether the request succeeds, fails, or the backend is unreachable. The marker suppresses initialization refresh and is removed on the next successful login. An access token issued before logout stays valid until its own expiry — accepted and bounded (`ADS-FR-006-09`), not a defect.
- **Throttling:** per client IP — `register` 10/min, `login` 10/min, `refresh` 30/min. Over the limit returns `429` with a `Retry-After` header giving seconds until the window resets.

### 3.3 Test traceability

- Every automated test carries its `TC-<REQ-ID>-NN` id. **One test case ↔ exactly one automated test.** No parallel id scheme per test file.
  - **Python:** function named `test_tc_fr_001_01_<slug>`, docstring first line `TC-FR-001-01 — <test case title>`. Select with `pytest -k tc_fr_001_01`.
  - **TypeScript:** `it('TC-FR-020-01 — <title>', ...)`. Select with `npx vitest run -t 'TC-FR-020-01'`.
  - **Manual (`Documented review`, `Data-model review`):** satisfied by the recorded artifact at `docs/reviews/<TC-ID>-<slug>.md` (assumption A3), not by code.
- A test case's id is stable. If a scenario no longer applies, it is marked **Superseded** in `test_specification.md` by the owner — never renumbered or reused.

---

## 4. Slice Map and Dependency Order

A slice delivers **one user-visible capability end to end** — migration → model → serializer/validation → view/permission → URL → backend tests → frontend API client → state → UI → frontend tests. A slice is **not done** until both its backend and frontend halves and all their tests are done, `main` is untouched, and the full suite is green.

| # | Slice | Depends on | Closes | Advances (partial) | TCs |
|---|---|---|---|---|---|
| 0 | Walking skeleton | — | TECH-003, TECH-004, TECH-005, SEC-004 | TECH-001, SEC-001, SEC-005, PRV-003 | 10 |
| 1 | Registration end to end | 0 | FR-001, FR-002, FR-003, FR-004, SEC-003, UX-002, UX-003, UX-004 | SEC-001, SEC-007 | 21 |
| 2 | Login, CSRF bootstrap, authenticated API client | 1 | FR-005, PRV-003 | SEC-001, SEC-005, SEC-006, SEC-007 | 20 |
| 3 | Refresh, rotation, absolute lifetime, session restore | 2 | FR-007, FR-008, SEC-007 | SEC-001 | 17 |
| 4 | Logout | 3 | FR-006 | SEC-005 | 15 |
| 5 | Account timezone + shared presentation utility | 2 | FR-009, UX-007 | SEC-001 | 5 |
| 6 | Password change | 2 | FR-048 | — | 3 |
| 7 | Categories + examination model, create, list | 2, 5 | FR-010, FR-011, FR-012, FR-014, FR-015, FR-020, FR-025, FR-026, FR-027, UX-005, UX-006, PRV-001, PRV-002, TECH-002 | SEC-001, SEC-002 | 32 |
| 8 | Examination detail, edit, delete | 7 | FR-013, FR-016, FR-021, FR-022, FR-024, SEC-006 | FR-023, SEC-001, SEC-002 | 15 |
| 9 | List search, filters, ordering | 8 | FR-028, FR-029, FR-030 | — | 7 |
| 10 | Derived time states (past/upcoming/overdue) | 8 | FR-031, FR-032, FR-033, FR-034 | FR-019 | 19 |
| 11 | Reminders: configuration and due-date calculation | 8, 10 | FR-017, FR-035, FR-036 | SEC-001, SEC-002 | 28 |
| 12 | Reminder lifecycle and due-reminders view | 11 | FR-037, FR-038 | — | 7 |
| 13 | Recurrence rules | 8, 11 | FR-018, FR-039, FR-040, SEC-002 | SEC-001 | 20 |
| 14 | Next occurrence | 13 | FR-023, FR-041 | — | 8 |
| 15 | Monthly calendar | 10, 14 | FR-019, FR-042, FR-043 | SEC-001 | 16 |
| 16 | Dashboard | 10, 15 | FR-044, FR-045, FR-046, FR-047, SEC-001 | — | 15 |
| 17 | Cross-cutting UX review | 16 | UX-001, UX-008 | — | 6 |
| 18 | Repository documentation + OpenAPI contract | 17 | TECH-001, TECH-007 | — | 2 |
| 19 | Deployment | 18 | SEC-005, TECH-006 | — | 8 |

**Total: 20 slices, 274 test cases.**

### 4.1 Deviations from the proposed sequence, and why

- **Categories are folded into Slice 7 rather than standing alone.** A category-seed-plus-read-only-endpoint slice delivers nothing a user can do — there is no form to pick a category in yet. Merged into examination creation, where the selector and the `Uncategorized` label are genuinely user-visible.
- **The shared derived-overdue module is introduced in Slice 7, not Slice 10.** `api_contract.md` §8.1 makes `time_state` a field of every examination representation, and `ADS-FR-014-02` needs the user's current local date to reject a future `completed_date`. Both land in Slice 7, so that is the first slice that genuinely needs the module. Slice 10 adds the **queryset filters** to the same module against the same rule — it does not write a second implementation. This is the single most important reuse point in the plan.
- **Reminder status restrictions ship with reminder creation (Slice 11), not later.** Splitting `FR-035`'s twelve status-matrix cases into a later slice would ship a `project/mvp` state where a draft can carry an active reminder — a spec violation, however briefly.
- **`FR-019` closes in Slice 15, not Slice 10.** `TC-FR-019-03` asserts calendar exclusion, and the calendar endpoint does not exist until Slice 15.
- **`FR-023` closes in Slice 14, not Slice 8.** `TC-FR-023-03` needs a generated occurrence, which requires the next-occurrence endpoint.
- **`TECH-005` closes in Slice 0.** Its only case, `TC-TECH-005-01`, is a configuration test on the production settings module — no deployment needed.
- **`SEC-001` closes in Slice 16.** Its eleven cases enumerate endpoints across nine slices; the dashboard case is the last.
- **Slices 7 and 11 are the two largest** (32 and 28 cases). Each is decomposed so that a natural stopping point with a green suite exists mid-slice: after Task 7.4 (backend complete) and after Task 11.3 (backend complete). Expect two sessions for each.

### 4.2 Shared machinery — built once, in the first slice that needs it

| Machinery | Introduced | Reused by |
|---|---|---|
| Typed env settings loader, dev/prod modules | 0.3 | every backend task |
| Injectable clock service | 0.4 | 7.3, 10.1, 11.3, 12.1, 15.1, 16.1 |
| pytest harness, fixtures, factories | 0.4 | every backend test task |
| OpenAPI schema generation | 0.6 | extended by every endpoint task; asserted in 18.2 |
| Frontend app shell, router, protected-route wrapper | 0.7 | every frontend task |
| Shared accessible field-error component | 1.4 | 5.2, 6.2, 7.6, 8.3 |
| API client (bearer + credentials + `X-CSRFToken`) | 2.4 | every frontend data task |
| Refresh single-flight + one-replay interceptor | 3.3 | every frontend data task |
| Shared timezone-aware presentation utility | 5.3 | 7.6, 8.3, 11.5, 12.2, 15.3, 16.3 |
| Owner-scoped queryset mixin + uniform 404 `get_object` | 7.2, 8.1 | 8, 9, 10, 11, 12, 13, 14, 15, 16 |
| Derived time-state module (predicate + filters) | 7.3, extended 10.1 | 10, 15, 16 |
| `require_planned(examination)` business-rule validator | 11.2 | 11, 12, 13 |
| Calendar-month arithmetic with last-valid-day clamping | 13.2 | 14 |

---

## 5. Slices and Tasks

Standing conventions for every task below, so they are not repeated in each one:

- Work happens on `feature/<slice-id>-<slug>` branched from `project/mvp`. `main` is never touched.
- One commit per task, message `<type>(s<NN>): <summary>` (e.g. `feat(s01): registration serializer and endpoint`).
- Backend commands run from `backend/` inside its virtualenv; frontend commands from `frontend/`.
- **On finishing any task:** the full suite must be green (`pytest` and `npm run test`), not only the new tests.
- **On finishing any slice:** squash-merge into `project/mvp`, add the day's `DEVELOPMENT_LOG.md` entry per that file's usage rules, and update the Phase Progress table only if the phase's state actually changed (see §10.3).

---

### Slice 0 — Walking skeleton

**Capability delivered:** a person opens the frontend, sees the non-clinical purpose page, and the backend answers `GET /api/v1/health/`.

**Definition of Done:** backend and frontend both start from documented commands; `pytest` and `npm run test` both pass; `TC-TECH-003-01/02/03`, `TC-TECH-004-01`, `TC-TECH-005-01`, `TC-SEC-004-01`, `TC-SEC-001-11`, `TC-SEC-005-03`, `TC-PRV-003-01`, `TC-PRV-003-02` pass.

#### Task 0.1 — Establish the branching workflow and the technology-decisions record
**Slice:** 0 — Walking skeleton
**Depends on:** none
**Requirements:** none directly (enables every later task)   **Design decisions:** none
**Read before starting:**
- `CLAUDE.md` §"Branching" (records the workflow as undecided — you are replacing that sentence)
- `README.md` §"Branching" (same statement, second location)
- `DEVELOPMENT_LOG.md` §"Current Project Status" and its "Carry-Over or Backlog Items" (both name this as the blocking open item)
- `docs/review_findings.md` §1–§2 (the standing statement and record shape you are mirroring in the new document)
**Do:**
1. Cut the project branch from `main`: `git switch -c project/mvp main`. This is the only branch cut from `main`; every later branch is cut from this one.
2. Create `docs/technology_decisions.md`. Open it with a §1 that states plainly that it is **non-normative**, is not part of the source-of-truth hierarchy in `product_definition.md` §2, defines no behavior, and must never be cited as authority — mirroring `review_findings.md` §1. Then record decisions D1–D12 from §2 of this plan, one row each, with a one-line rationale.
3. Update `CLAUDE.md` §"Branching" to state the confirmed workflow: a project branch (`project/mvp`) is cut from `main` and collects the work; one `feature/<slice-id>-<slug>` branch per slice is cut from it and squash-merged back; `main` receives implementation only at MVP completion, when the project branch merges once and is then deleted. Describe the shape generally — one project branch per project — not just this instance, since the convention outlives this MVP.
4. Update `README.md` §"Branching" to match, and add pointers to `docs/technology_decisions.md` and to `IMPLEMENTATION_PLAN.md` under "Supporting documents", each labelled non-normative.
5. Add a line to `CLAUDE.md` naming `IMPLEMENTATION_PLAN.md` as the implementation task sequence, explicitly non-normative and outranked by every document in the source-of-truth hierarchy. `CLAUDE.md` is the first thing an agent reads in this repository, so this pointer is what makes the plan discoverable now that it does not sit in `docs/`.
6. Update `DEVELOPMENT_LOG.md` §"Current Project Status": current branch `project/mvp`, next deliverable "Slice 0 — walking skeleton".
**Test cases to implement:** none.
**Acceptance criteria:** `git branch` lists `project/mvp`; `docs/technology_decisions.md` exists and its §1 declares non-normative standing; `CLAUDE.md` and `README.md` both point at `IMPLEMENTATION_PLAN.md` and both label it non-normative; no file in `CLAUDE.md`, `README.md` or `DEVELOPMENT_LOG.md` still describes the branching workflow as undecided.
**Verify with:** `git branch --list 'project/mvp'` and `grep -rn "not yet decided\|has not been decided" CLAUDE.md README.md DEVELOPMENT_LOG.md` (expect no branching-related hit).
**Out of scope for this task:** any `backend/` or `frontend/` file; any edit to `requirements_specification.md`, `design_specification.md`, `domain_model.md`, `api_contract.md`, `user_flows.md`, `test_specification.md` or `traceability_matrix.md`.
**On finishing:** commit on `project/mvp` directly (this task establishes the branch itself). No `DEVELOPMENT_LOG.md` daily entry yet if no other work happened today.

#### Task 0.2 — Upgrade Node to 20 LTS
**Slice:** 0 — Walking skeleton
**Depends on:** 0.1
**Requirements:** none directly (prerequisite for every frontend task)   **Design decisions:** none
**Read before starting:** nothing in `docs/` — this is a toolchain prerequisite, not a specified behavior.
**Do:**
1. The installed Node is v19.9.0. Vite 5+ and Vitest 1+ require `^18.0.0 || >=20.0.0` and will refuse to install or run. **This step is owner-run** — ask the owner to install Node 20 LTS (for example `nvm install 20 && nvm use 20`) and report `node -v` and `npm -v`.
2. Record the pinned Node major version in `frontend/.nvmrc` (created in Task 0.7) and in `docs/technology_decisions.md` under D8.
**Test cases to implement:** none.
**Acceptance criteria:** `node -v` reports `v20.x`; `npm -v` reports the bundled 10.x.
**Verify with:** `node -v && npm -v`
**Out of scope for this task:** installing any npm package — that is Task 0.7.
**On finishing:** no commit unless `docs/technology_decisions.md` changed.

#### Task 0.3 — Create the backend project, typed settings, and the health endpoint
**Slice:** 0 — Walking skeleton
**Depends on:** 0.1
**Requirements:** TECH-003, TECH-004, TECH-005, SEC-004, SEC-005 (config-level), SEC-001 (health exemption)   **Design decisions:** ADS-TECH-003-01, ADS-TECH-004-01, ADS-TECH-005-01, ADS-SEC-004-01, ADS-SEC-005-01, ADS-SEC-005-03, ADS-SEC-005-08, ADS-SEC-001-01, ADS-TECH-001-01
**Read before starting:**
- `docs/design_specification.md` `ADS-TECH-003-01` (typed env loader, dev/prod defaults, fail-fast production validation), `ADS-TECH-004-01` (exact health response and what it must not expose), `ADS-TECH-005-01` (`DEBUG = False` unconditionally in production; startup fails on missing mandatory config), `ADS-SEC-004-01` (which values come from environment variables; `.env` excluded from VCS, only `.env.example` committed)
- `docs/design_specification.md` `ADS-SEC-005-01` and `ADS-SEC-005-03` (CORS allowlist and CSRF trusted origins both built from explicit env-supplied origins; no wildcard in production), `ADS-SEC-005-08` (CSRF cookie path `/api/v1/`, prod `Secure`+`SameSite=None`, local `SameSite=Lax` without `Secure`), `ADS-SEC-005-07` (CSRF cookie `HttpOnly` in both environments)
- `docs/api_contract.md` §2 (base path, JSON conventions) and §4 (health-check request/response)
- `docs/design_specification.md` `ADS-SEC-001-01` (authenticated-by-default permission; health is one of the explicit exemptions)
**Do:**
1. Create the Django project under `backend/` with the project package `config` and `manage.py` at `backend/manage.py`.
2. Create `backend/requirements.txt` (`Django`, `djangorestframework`, `django-cors-headers`, `PyJWT`, `psycopg[binary]`, `drf-spectacular`) and `backend/requirements-dev.txt` (`pytest`, `pytest-django`, `freezegun`, `detect-secrets`, `ruff`). Pin exact versions.
3. Build the settings layer as `config/settings/base.py`, `development.py`, `production.py`, plus `config/settings/env.py` holding a typed reader with explicit `str`/`bool`/`int`/`list` parsers. Required production values raise at import time when absent — no defaulting, no fallback to development settings.
4. Set in `base.py`: `USE_TZ = True`; DRF `DEFAULT_PERMISSION_CLASSES = ['rest_framework.permissions.IsAuthenticated']`; `CSRF_COOKIE_HTTPONLY = True`; `CSRF_COOKIE_PATH = '/api/v1/'`. In `development.py`: SQLite, `CSRF_COOKIE_SAMESITE = 'Lax'`, `CSRF_COOKIE_SECURE = False`. In `production.py`: `DEBUG = False` as a literal, PostgreSQL from env, `CSRF_COOKIE_SAMESITE = 'None'`, `CSRF_COOKIE_SECURE = True`.
5. Build `CORS_ALLOWED_ORIGINS` and `CSRF_TRUSTED_ORIGINS` from one env variable of explicit scheme+host+port origins. Production must reject a wildcard entry at settings load.
6. Add the `/api/v1/` URL namespace and a `health` app (or a `config` view) serving `GET /api/v1/health/` — unauthenticated, `200 OK`, body exactly `{"status": "ok"}`, exposing no configuration or secret value.
7. Commit `backend/.env.example` with every required variable name and placeholder values only. Confirm `.gitignore` already excludes `.env` and `.env.*` except `.env.example`.
**Test cases to implement:** none in this task (see 0.4).
**Acceptance criteria:** `python manage.py check` passes under development settings; `GET /api/v1/health/` returns `200` with exactly `{"status": "ok"}`; importing `config.settings.production` with a mandatory variable unset raises; `backend/.env.example` contains no real value.
**Verify with:**
```
cd backend && python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
python manage.py check
python manage.py migrate
python manage.py runserver   # then GET /api/v1/health/ from the browser or a test client
```
**Out of scope for this task:** any domain model; any auth endpoint; the OpenAPI schema route (Task 0.6); tests (Task 0.4).
**On finishing:** commit; add a `docs/technology_decisions.md` entry for the settings layout (D5) and packaging (A4).

#### Task 0.4 — Backend test harness, clock service, and configuration tests
**Slice:** 0 — Walking skeleton
**Depends on:** 0.3
**Requirements:** TECH-003, TECH-004, TECH-005, SEC-001, SEC-005 (config-level)   **Design decisions:** ADS-TECH-003-01, ADS-TECH-004-01, ADS-TECH-005-01, ADS-SEC-001-01, ADS-SEC-005-01
**Read before starting:**
- `docs/test_specification.md` §3.3 (the layer vocabulary) and §3.4 (how a test links back to its `TC-*` id)
- `docs/test_specification.md` `TC-TECH-003-01`, `TC-TECH-003-02`, `TC-TECH-003-03`, `TC-TECH-004-01`, `TC-TECH-005-01`, `TC-SEC-001-11`, `TC-SEC-005-03` (the seven scenarios, verbatim)
- `docs/domain_model.md` §10 (why boundary behavior must be tested with a controlled current time — the reason the clock service exists)
**Do:**
1. Configure pytest in `backend/pyproject.toml`: `DJANGO_SETTINGS_MODULE = "config.settings.development"`, testpaths, and a `python_functions` pattern that accepts `test_tc_*`.
2. Create `config/clock.py` exposing `now()` returning an aware UTC datetime, as the single source of "now" for the backend. Nothing else may call `django.utils.timezone.now()` directly from this point on. The user-timezone wrapper is added in Task 7.3.
3. Create `backend/tests/conftest.py` with an `api_client` fixture and a `settings_env` helper that loads a named settings module against a supplied environment dict.
4. Implement the seven test cases named above, each carrying its `TC-*` id in the function name and docstring per §3.3 of this plan.
**Test cases to implement:**
- `TC-TECH-003-01` (Configuration test) — development env values produce development settings
- `TC-TECH-003-02` (Configuration test) — production env values produce production settings
- `TC-TECH-003-03` (Configuration test) — a missing mandatory production value fails startup
- `TC-TECH-004-01` (API integration test) — `GET /api/v1/health/` returns `200` and `{"status": "ok"}`
- `TC-TECH-005-01` (Configuration test) — production `DEBUG` is `False` with no explicit override
- `TC-SEC-001-11` (API integration test) — health check is not rejected for missing bearer authentication
- `TC-SEC-005-03` (Configuration test) — the production CORS allowlist contains explicit origins only, with no wildcard entry
**Acceptance criteria:** all seven pass; every test name and docstring carries its `TC-*` id; `grep -rn "timezone.now()" backend/config backend/apps` returns only `config/clock.py`.
**Verify with:** `cd backend && pytest -q` and `pytest -k "tc_tech_003 or tc_tech_004 or tc_tech_005 or tc_sec_001_11 or tc_sec_005_03" -v`
**Out of scope for this task:** the user-local-time wrapper (Task 7.3); any frontend test setup (Task 0.7).
**On finishing:** commit.

#### Task 0.5 — Repository secret scanning
**Slice:** 0 — Walking skeleton
**Depends on:** 0.3
**Requirements:** SEC-004   **Design decisions:** ADS-SEC-004-01
**Read before starting:**
- `docs/design_specification.md` `ADS-SEC-004-01` (what must come from environment variables; only placeholder example files may be committed)
- `docs/test_specification.md` `TC-SEC-004-01` (scope: committed history *and* current tree)
- `.gitignore` (confirm the env-file exclusions it already carries)
**Do:**
1. Add `detect-secrets` to `backend/requirements-dev.txt` (assumption A5 — swap tools only with the owner's agreement).
2. Generate `.secrets.baseline` at the repository root from the current tree and audit it to empty.
3. Add a repository-root script `scripts/secret-scan.sh` running the scan over the tree and over `git log -p`, exiting non-zero on any finding.
4. Implement `TC-SEC-004-01` as a test that invokes the script and asserts a zero exit status.
**Test cases to implement:** `TC-SEC-004-01` (Repository secret scan) — no committed file contains a configured secret.
**Acceptance criteria:** the script exits `0` on the current tree and history; a deliberately planted fake secret makes it exit non-zero (verify, then remove the plant without committing it).
**Verify with:** `bash scripts/secret-scan.sh` and `cd backend && pytest -k tc_sec_004_01 -v`
**Out of scope for this task:** CI wiring — no CI system is in this MVP's scope (`product_definition.md` §12 lists it as a future feature).
**On finishing:** commit. Re-run this scan before every slice merge — it is a standing gate, not a one-time check.

#### Task 0.6 — OpenAPI schema generation
**Slice:** 0 — Walking skeleton
**Depends on:** 0.3
**Requirements:** TECH-001 (partial — closes in 18.2)   **Design decisions:** ADS-TECH-001-01
**Read before starting:**
- `docs/design_specification.md` `ADS-TECH-001-01` ("documented in an OpenAPI contract maintained with the implementation" — this is the mechanism)
- `docs/api_contract.md` §2 (the conventions the generated schema must reflect: base path, `snake_case`, JSON)
**Do:**
1. Wire `drf-spectacular` into DRF settings and expose the schema at `/api/v1/schema/`.
2. Add an `npm`-independent make-style command or `manage.py spectacular --file openapi.yaml` invocation, and commit the generated `backend/openapi.yaml`.
3. Add a test asserting the schema generates without warnings that indicate an undocumented endpoint.
**Test cases to implement:** none — `TC-TECH-001-01` is the Contract test and executes in Task 18.2, once every documented endpoint exists.
**Acceptance criteria:** `manage.py spectacular` produces a schema containing the `/api/v1/health/` path with no generation errors.
**Verify with:** `cd backend && python manage.py spectacular --file openapi.yaml && pytest -q`
**Out of scope for this task:** asserting the schema matches `api_contract.md` endpoint by endpoint — that is `TC-TECH-001-01` in Task 18.2. **Every later endpoint task must regenerate `openapi.yaml`.**
**On finishing:** commit.

#### Task 0.7 — Create the frontend app shell and test stack
**Slice:** 0 — Walking skeleton
**Depends on:** 0.2
**Requirements:** UX-001 (advances only; closes in Slice 17), PRV-003 (partial)   **Design decisions:** ADS-UX-001-01, ADS-UX-008-01
**Read before starting:**
- `docs/design_specification.md` `ADS-UX-001-01` (mobile-first base styles, explicit tablet/desktop enhancements, no horizontal page scrolling) and `ADS-UX-008-01` (semantic interactive elements, visible keyboard focus, labelled controls, focus-managed dialogs, practical touch targets)
- `docs/user_flows.md` §24 (the shared UX behavior every page inherits)
**Do:**
1. Scaffold Vite + React + TypeScript in `frontend/`. Commit `frontend/.nvmrc` pinning Node 20.
2. Install and configure React Router, TanStack Query, Vitest, React Testing Library, `@testing-library/jest-dom`, and MSW. Add scripts `dev`, `build`, `preview`, `test`, `lint`.
3. Create the mobile-first layout shell: a base stylesheet with phone-width defaults and explicit tablet/desktop breakpoints, a semantic `<header>`/`<nav>`/`<main>` structure, and a visible focus style applied globally.
4. Add routes for `/` and the informational page (Task 0.8 fills the page's content).
5. Configure `VITE_API_BASE_URL` through `frontend/.env.example`; never hard-code the backend origin.
**Test cases to implement:** none in this task (see 0.8).
**Acceptance criteria:** `npm run dev` serves the shell; `npm run build` succeeds; `npm run test` runs with zero tests and exits `0`; no page scrolls horizontally at a 320px viewport.
**Verify with:** `cd frontend && npm ci && npm run build && npm run test`
**Out of scope for this task:** any API call, auth state, or protected route — those arrive in Slices 1–3.
**On finishing:** commit; record D7/D8 in `docs/technology_decisions.md`.

#### Task 0.8 — Non-clinical purpose page
**Slice:** 0 — Walking skeleton
**Depends on:** 0.7
**Requirements:** PRV-003 (partial — `TC-PRV-003-03` closes in Task 2.6)   **Design decisions:** ADS-PRV-003-01
**Read before starting:**
- `docs/design_specification.md` `ADS-PRV-003-01` (a dedicated informational page reachable from **both** unauthenticated and authenticated navigation)
- `docs/user_flows.md` §23 (the four statements the page must carry)
- `docs/requirements_specification.md` `PRV-003` (the exact limitations to state)
- `docs/test_specification.md` `TC-PRV-003-01`, `TC-PRV-003-02`
**Do:**
1. Build the informational page stating that the application is an organizational tool and does not provide medical advice, diagnosis, treatment, or emergency assistance.
2. Link it from the unauthenticated navigation. The authenticated navigation link is added in Task 2.6, when authenticated navigation exists.
3. Implement the two component/integration tests.
**Test cases to implement:**
- `TC-PRV-003-01` (Frontend component test) — the page states the organizational-tool purpose and all four exclusions
- `TC-PRV-003-02` (Frontend integration test) — reachable from unauthenticated navigation
**Acceptance criteria:** both tests pass; the page is reachable by keyboard alone from the unauthenticated navigation.
**Verify with:** `cd frontend && npx vitest run -t 'TC-PRV-003'`
**Out of scope for this task:** `TC-PRV-003-03` (authenticated navigation) — Task 2.6.
**On finishing:** commit.

#### Task 0.9 — Initial README setup and test sections
**Slice:** 0 — Walking skeleton
**Depends on:** 0.4, 0.7
**Requirements:** TECH-007 (partial — closes in Task 18.1)   **Design decisions:** ADS-TECH-007-01
**Read before starting:**
- `docs/design_specification.md` `ADS-TECH-007-01` (commands must be copyable and tied to the actual repository structure)
- `docs/review_findings.md` `RF-20` (its recorded trigger is "before Phase 2 completes" — Slice 0 completes Phase 2, so this is that moment)
- `README.md` §"Setup, Build, and Deployment" (currently a placeholder)
**Do:**
1. Replace the placeholder section with real, copyable local-setup and test-execution instructions for both `backend/` and `frontend/`, including the environment variables each needs and a pointer to `.env.example`.
2. Update `README.md` §"Project Status" — it currently states there is no implementation and no test commands. That is no longer true.
3. Do **not** delete `RF-20` from `docs/review_findings.md` yet — migration, build, and deployment procedures are still missing. Narrow nothing on the owner's behalf; note in the commit message that `RF-20` remains open pending Task 18.1.
**Test cases to implement:** none — `TC-TECH-007-01` is a `Documented review` executed in Task 18.1 against the complete instructions.
**Acceptance criteria:** a reader following only the README, from a clean clone, reaches a running backend, a running frontend, and green test suites.
**Verify with:** follow your own instructions in a fresh shell with no prior state, using no step you did not write down.
**Out of scope for this task:** migration, build, and deployment sections — Task 18.1.
**On finishing:** commit. **Slice 0 complete:** squash-merge into `project/mvp`, write the `DEVELOPMENT_LOG.md` entry, and set Phase 2 to `Completed` in the Phase Progress table.

---

### Slice 1 — Registration end to end

**Capability delivered:** a visitor creates an account with email, password and timezone, and sees a field-level error for every rejected value.

**Definition of Done:** backend and frontend halves both done; the 21 test cases listed below pass; the full suite is green.

#### Task 1.1 — User model with email login and account timezone
**Slice:** 1 — Registration end to end
**Depends on:** 0.4
**Requirements:** FR-001, FR-004, SEC-003   **Design decisions:** ADS-FR-001-01, ADS-FR-004-01, ADS-SEC-003-01
**Read before starting:**
- `docs/domain_model.md` §3.1 (the four `User` attributes and their rules — `email` normalized and unique case-insensitively, `timezone` from the backend-supported set, password only through Django's hashing framework)
- `docs/design_specification.md` `ADS-FR-004-01` (IANA identifiers obtained through Python's timezone database; stored exactly as the canonical supported value), `ADS-SEC-003-01` (`set_password` / approved manager methods only; never assign a raw password)
- `docs/api_contract.md` §5.2 and §6.1 (the account representation: `id`, `email`, `timezone` — nothing else)
**Do:**
1. Create the `accounts` app. Define a custom user model with `email` as `USERNAME_FIELD`, no `username` field, and a `timezone` character field.
2. Give it a manager whose `create_user` normalizes the email, calls `set_password`, and rejects a blank email.
3. Enforce case-insensitive email uniqueness at the database level.
4. Add `accounts/timezones.py` exposing the supported set from `zoneinfo.available_timezones()`, with one function that validates an identifier and returns the canonical value.
5. Set `AUTH_USER_MODEL` in `config/settings/base.py`; add `AUTH_PASSWORD_VALIDATORS` with exactly `MinimumLengthValidator` (min 8), `CommonPasswordValidator`, `NumericPasswordValidator`, `UserAttributeSimilarityValidator` compared against `email`.
6. Generate and apply the migration.
**Test cases to implement:** none in this task (see 1.3).
**Acceptance criteria:** `manage.py migrate` applies cleanly; creating a user through the manager stores a hashed password; registering `person@example.com` then `Person@Example.com` violates the uniqueness constraint at the database level.
**Verify with:** `cd backend && python manage.py makemigrations --check --dry-run && python manage.py migrate && pytest -q`
**Out of scope for this task:** the registration serializer and endpoint (Task 1.2); the timezone update endpoint (Slice 5); password change (Slice 6).
**On finishing:** commit.

#### Task 1.2 — Registration endpoint, serializer, and throttle
**Slice:** 1 — Registration end to end
**Depends on:** 1.1
**Requirements:** FR-001, FR-002, FR-003, FR-004, SEC-003, SEC-007 (register limit), SEC-001 (register exemption)   **Design decisions:** ADS-FR-001-01, ADS-FR-002-01, ADS-FR-003-01, ADS-FR-004-01, ADS-SEC-003-01, ADS-SEC-007-01, ADS-SEC-001-01
**Read before starting:**
- `docs/api_contract.md` §5.2 (exact request fields, the full validation list, and the `201` response shape — `id`, `email`, `timezone`, no password, **no token**) and §3.4 (the field-error response shape) and §3.5 (the `429` shape and `Retry-After`)
- `docs/design_specification.md` `ADS-FR-002-01` (DRF email validation, normalization before comparison, case-insensitive uniqueness), `ADS-FR-003-01` (required, write-only, min 8 / max 128, account created through Django's password-setting API), `ADS-SEC-003-01` (the four validators), `ADS-SEC-007-01` (10/min per client IP on register; `429` with `Retry-After`)
- `docs/design_specification.md` `ADS-SEC-001-01` (registration is an explicit exemption from bearer authentication; it needs neither browser credentials nor CSRF — see `api_contract.md` §5.1's matrix row)
**Do:**
1. Add a registration serializer: `email` required and format-validated, normalized, case-insensitively unique; `password` required, write-only, `min_length=8`, `max_length=128`, run through `django.contrib.auth.password_validation.validate_password` with the user instance so `UserAttributeSimilarityValidator` sees the email; `timezone` required and validated against `accounts/timezones.py`.
2. Create the account through the manager (`set_password`), never by assigning the field.
3. Add `POST /api/v1/auth/register/` with `AllowAny`, no CSRF requirement, returning `201` with `{"id", "email", "timezone"}`.
4. Add a scoped DRF throttle class limited to `10/min` keyed on client IP, applied to this view.
5. Regenerate `backend/openapi.yaml`.
**Test cases to implement:** none in this task (see 1.3).
**Acceptance criteria:** a valid request returns `201` with exactly `id`, `email`, `timezone`; each invalid field returns `400` with that field's name as the error key; the 11th request within a minute from one IP returns `429` with `Retry-After`.
**Verify with:** `cd backend && pytest -q && python manage.py spectacular --file openapi.yaml`
**Out of scope for this task:** login (Slice 2); hiding account existence at registration — `product_definition.md` §8 records that disclosure as an intentional MVP exclusion.
**On finishing:** commit.

#### Task 1.3 — Backend registration tests
**Slice:** 1 — Registration end to end
**Depends on:** 1.2
**Requirements:** FR-001, FR-002, FR-003, FR-004, SEC-003, SEC-001, SEC-007 (register limit)   **Design decisions:** as Task 1.2
**Read before starting:**
- `docs/test_specification.md` `TC-FR-001-01`, `TC-FR-002-01/02/03`, `TC-FR-003-01/02/03`, `TC-FR-004-01`, `TC-SEC-003-01/02/03/04`, `TC-SEC-001-07`, `TC-SEC-007-03` — read each Given/When/Then verbatim; the exact literals (`short12`, a 129-character value, `Person@Example.com`, `password123`) are part of the case
**Do:** implement one automated test per case, each carrying its `TC-*` id in the function name and docstring. `TC-SEC-007-03` needs the throttle cache cleared between tests, or it leaks a `429` into the twelve cases beside it — make the reset a fixture on this module, not a one-off inside the throttle test (risk register R7).
**Test cases to implement:**
- `TC-FR-001-01` (API integration test) — valid registration creates an account that can subsequently log in
- `TC-FR-002-01` (API validation test) — missing email
- `TC-FR-002-02` (API validation test) — malformed email
- `TC-FR-002-03` (API validation test) — already-registered email, different case
- `TC-FR-003-01` (API validation test) — missing password
- `TC-FR-003-02` (API validation test) — seven-character password
- `TC-FR-003-03` (API validation test) — 129-character password
- `TC-FR-004-01` (API validation test) — unsupported timezone
- `TC-SEC-003-01` (Backend model test) — stored password differs from plaintext and verifies with Django's checker
- `TC-SEC-003-02` (API validation test) — common password rejected
- `TC-SEC-003-03` (API validation test) — entirely numeric password rejected
- `TC-SEC-003-04` (API validation test) — password resembling the email rejected
- `TC-SEC-001-07` (API integration test) — registration is not rejected for missing bearer authentication
- `TC-SEC-007-03` (API integration test) — the 11th registration within a minute from one client IP returns `429` with `Retry-After`
**Acceptance criteria:** all 14 pass; every rejection case also asserts that **no account was created**, as each Then clause requires; `TC-SEC-007-03` passes in any order and across two consecutive full runs.
**Verify with:** `cd backend && pytest -k "tc_fr_001 or tc_fr_002 or tc_fr_003 or tc_fr_004 or tc_sec_003 or tc_sec_001_07 or tc_sec_007_03" -v`
**Out of scope for this task:** the login and refresh throttle cases — `TC-SEC-007-01/02` (login) belong to Task 2.4 and `TC-SEC-007-04` (refresh) to Task 3.2.
**On finishing:** commit.

#### Task 1.4 — Shared field-error component and registration form
**Slice:** 1 — Registration end to end
**Depends on:** 0.8, 1.2
**Requirements:** UX-002, UX-003, UX-004   **Design decisions:** ADS-UX-002-01, ADS-UX-003-01, ADS-UX-004-01, ADS-UX-008-01
**Read before starting:**
- `docs/design_specification.md` `ADS-UX-002-01` (errors from **client validation or the API** associated with the control through shared form-error state, displayed immediately adjacent, exposed through accessible descriptive attributes), `ADS-UX-003-01` (client-side required + min-8 check *and* backend errors through the same component), `ADS-UX-004-01` (a required selection control populated from supported values supplied by the application)
- `docs/user_flows.md` §2 "Registration flow" and its "Failure behavior" list
- `docs/api_contract.md` §3.4 (the field-error payload shape the client must map onto fields)
**Do:**
1. Build a reusable accessible field-error component: renders the message adjacent to its control, wires `aria-describedby` and `aria-invalid`. **Every later form reuses this** — do not write a second one.
2. Build the registration page with email, password and timezone controls.
3. Client-side validation before submit: email required, password required and at least 8 characters, timezone required.
4. Map a `400` response body (`{"field": ["message"]}`) onto the same shared form-error state, so API errors and client errors render identically.
5. Populate the timezone control from `Intl.supportedValuesOf('timeZone')` with a small static fallback list. There is **no** timezone endpoint in `api_contract.md`; adding one would require a contract change. The backend remains authoritative — an identifier the browser offers but the backend rejects surfaces as a `timezone` field error, which is exactly `TC-UX-004-02`. (Assumption A7.)
6. On success, present the registration result and route the user to login (`user_flows.md` §2 step 7).
**Test cases to implement:** none in this task (see 1.5).
**Acceptance criteria:** every control has a programmatically associated label and error; the form is completable with keyboard alone; a `400` from the API renders adjacent to the correct field.
**Verify with:** `cd frontend && npm run test && npm run build`
**Out of scope for this task:** login (Slice 2); any authenticated route.
**On finishing:** commit; record the timezone-list source (A7) in `docs/technology_decisions.md`.

#### Task 1.5 — Frontend registration tests
**Slice:** 1 — Registration end to end
**Depends on:** 1.4
**Requirements:** UX-002, UX-003, UX-004   **Design decisions:** as Task 1.4
**Read before starting:** `docs/test_specification.md` `TC-UX-002-01/02/03`, `TC-UX-003-01/02`, `TC-UX-004-01/02` — note which cases are client-side (`-01`, `-02` of UX-002/003; `-01` of UX-004) and which require a mocked API rejection (`TC-UX-002-03`, `TC-UX-004-02`).
**Do:** implement one Vitest/RTL test per case, using MSW to supply the API rejections. Each `it()` title begins with its `TC-*` id.
**Test cases to implement:**
- `TC-UX-002-01` (Frontend integration test) — empty email
- `TC-UX-002-02` (Frontend integration test) — `not-an-email`
- `TC-UX-002-03` (Frontend integration test) — API-rejected duplicate email
- `TC-UX-003-01` (Frontend integration test) — empty password
- `TC-UX-003-02` (Frontend integration test) — seven-character password
- `TC-UX-004-01` (Frontend integration test) — no timezone selected
- `TC-UX-004-02` (Frontend integration test) — API-rejected unsupported timezone
**Acceptance criteria:** all 7 pass; each asserts the error is *adjacent to and associated with* its field, not merely present on the page.
**Verify with:** `cd frontend && npx vitest run -t 'TC-UX-00'`
**Out of scope for this task:** any login or session assertion.
**On finishing:** commit. **Slice 1 complete:** squash-merge, `DEVELOPMENT_LOG.md` entry, set Phase 3 to `In progress`.

---

### Slice 2 — Login, CSRF bootstrap, authenticated API client

**Capability delivered:** a registered user logs in and reaches an authenticated area; protected endpoints reject unauthenticated callers by default.

**Definition of Done:** both halves done; the 20 cases below pass; the full suite is green.

#### Task 2.1 — JWT token service and the revocation table
**Slice:** 2 — Login, CSRF bootstrap, authenticated API client
**Depends on:** 1.1
**Requirements:** FR-005, FR-007 (token shape only)   **Design decisions:** ADS-FR-005-06, ADS-FR-005-07, ADS-FR-007-08, ADS-FR-007-09, ADS-FR-007-10, ADS-SEC-004-01
**Read before starting:**
- `docs/design_specification.md` `ADS-FR-005-07` (access token: HS256 only, `sub`/`token_type: "access"`/`iat`/`exp`; reject any other `alg`; reject a non-`access` `token_type` as a bearer credential), `ADS-FR-005-06` (ten-minute lifetime)
- `docs/design_specification.md` `ADS-FR-007-10` (refresh token: HS256 only, `sub`/`token_type: "refresh"`/`jti`/`session_start`/`iat`/`exp`), `ADS-FR-007-08` (**`session_start` set once at login and copied unchanged into every rotated token; `exp` computed as `session_start + 7 days` identically at login and at every rotation, never relative to rotation time**), `ADS-FR-007-07` (the seven-day absolute lifetime this encodes), `ADS-FR-007-09` (`RevokedRefreshToken` keyed by `jti`, `expires_at` copied from the token's own `exp`)
- `docs/design_specification.md` `ADS-SEC-004-01` (the signing secret comes from an environment variable)
- §3.2 of this plan (how these pieces interlock)
**Do:**
1. Create `accounts/tokens.py` with `issue_access_token(user)`, `issue_refresh_token(user, session_start=None)`, `decode_access_token(raw)`, `decode_refresh_token(raw)`. Pass `algorithms=["HS256"]` explicitly to every `jwt.decode` call and additionally assert the decoded header's `alg == "HS256"`. Assert the expected `token_type` in each decoder.
2. `issue_refresh_token` takes `session_start` as an argument: at login it is `clock.now()`, at rotation it is the incoming token's own `session_start`. In both paths `exp = session_start + timedelta(days=7)`. There is no other expression for `exp`.
3. Every timestamp comes from `config.clock.now()`, never from `timezone.now()` directly.
4. Add the `RevokedRefreshToken` model (`jti` unique, `expires_at`) and its migration, with a helper `revoke(token_payload)` and `is_revoked(jti)`.
5. Add a DRF authentication class that reads `Authorization: Bearer <token>`, decodes it as an access token, and returns the user.
**Test cases to implement:** none in this task (`TC-FR-005-05/07` land in Task 2.4, `TC-FR-007-10/11` in Task 3.2).
**Acceptance criteria:** an issued access token decodes to exactly the four documented claims with `exp - iat == 600`; a refresh token issued with a supplied `session_start` from six days ago carries `exp = session_start + 7 days`, not `now + 7 days`; a token with `alg` rewritten to `none` or `HS512` fails to decode.
**Verify with:** `cd backend && pytest -q`
**Out of scope for this task:** any endpoint; rotation logic (Slice 3); logout revocation (Slice 4).
**On finishing:** commit. This module is the single most error-prone piece in the plan — see the risk register, §9.3 R2.

#### Task 2.2 — CSRF bootstrap endpoint and cookie configuration
**Slice:** 2 — Login, CSRF bootstrap, authenticated API client
**Depends on:** 0.3
**Requirements:** SEC-005, SEC-001 (csrf exemption)   **Design decisions:** ADS-SEC-005-05, ADS-SEC-005-07, ADS-SEC-005-08, ADS-SEC-001-01
**Read before starting:**
- `docs/api_contract.md` §5.3 (the endpoint, its `200` body `{"csrf_token": ...}`, and the CSRF cookie attribute table for both environments) and §5.1 (its authentication-matrix row: no bearer, browser credentials yes, no `X-CSRFToken`)
- `docs/design_specification.md` `ADS-SEC-005-05`, `ADS-SEC-005-07` (`HttpOnly` in **both** environments), `ADS-SEC-005-08` (path `/api/v1/`; prod `Secure`+`SameSite=None`; local `SameSite=Lax` without `Secure`)
**Do:**
1. Add `GET /api/v1/auth/csrf/` with `AllowAny` and no bearer authentication, decorated so it sets or renews the CSRF cookie, returning `{"csrf_token": <token>}` matching that cookie.
2. Confirm the cookie settings from Task 0.3 produce the documented attributes in each environment. Because the cookie is `HttpOnly`, the token reaches the client only through this response body — that is the design, not a workaround.
3. Regenerate `backend/openapi.yaml`.
**Test cases to implement:** none in this task (see 2.4).
**Acceptance criteria:** the response sets a CSRF cookie with `HttpOnly`, path `/api/v1/`, and the environment-appropriate `Secure`/`SameSite`; the returned `csrf_token` validates against that cookie on a subsequent protected POST.
**Verify with:** `cd backend && pytest -q`
**Out of scope for this task:** applying CSRF protection to login/refresh/logout — each of those endpoints enforces it in its own task.
**On finishing:** commit.

#### Task 2.3 — Login endpoint
**Slice:** 2 — Login, CSRF bootstrap, authenticated API client
**Depends on:** 2.1, 2.2
**Requirements:** FR-005, SEC-005, SEC-006, SEC-007, SEC-001   **Design decisions:** ADS-FR-005-01, ADS-FR-005-02, ADS-FR-005-03, ADS-SEC-005-04, ADS-SEC-006-02, ADS-SEC-007-01, ADS-SEC-001-01
**Read before starting:**
- `docs/api_contract.md` §5.4 (request requirements including `X-CSRFToken`, the `200` body containing **only** `access_token`, the `401` body `{"detail": "Invalid credentials."}`, and the `403` CSRF failure) and §5.7 (the refresh-cookie attribute table for both environments and its clearing rules)
- `docs/design_specification.md` `ADS-FR-005-02` (access token in JSON), `ADS-FR-005-03` (refresh token **only** in the cookie, never in JSON), `ADS-SEC-005-04` (`HttpOnly`, host-only, path `/api/v1/auth/`, expiry aligned with the token), `ADS-SEC-006-02` (one generic error regardless of whether the email exists), `ADS-SEC-007-01` (10/min per IP)
**Do:**
1. Add `POST /api/v1/auth/login/` with `AllowAny`, no bearer authentication, and explicit CSRF protection (the view must enforce CSRF even though it does not use session authentication).
2. Authenticate `email` + `password`. On failure return `401` with exactly `{"detail": "Invalid credentials."}` — the same object for an unknown email and for a wrong password. Do not branch the message, the status, or the response shape.
3. On success: issue an access token and a refresh token with `session_start = clock.now()`; return `{"access_token": ...}`; set the `refresh_token` cookie **host-only** (do not set a `Domain` attribute), `HttpOnly`, path `/api/v1/auth/`, expiry aligned with the token's `exp`, and the environment-specific `Secure`/`SameSite`.
4. Apply the 10/min per-IP throttle.
5. Regenerate `backend/openapi.yaml`.
**Test cases to implement:** none in this task (see 2.4).
**Acceptance criteria:** the `200` body contains `access_token` and no refresh token in any field; the `refresh_token` cookie carries every documented attribute; both failure modes are byte-identical; a missing `X-CSRFToken` yields `403` and issues no credentials.
**Verify with:** `cd backend && pytest -q && python manage.py spectacular --file openapi.yaml`
**Out of scope for this task:** refresh (Slice 3); logout (Slice 4).
**On finishing:** commit.

#### Task 2.4 — Backend login and CSRF tests
**Slice:** 2 — Login, CSRF bootstrap, authenticated API client
**Depends on:** 2.3
**Requirements:** FR-005, SEC-001, SEC-005, SEC-006, SEC-007   **Design decisions:** as Tasks 2.1–2.3
**Read before starting:** `docs/test_specification.md` — `TC-FR-005-01/02/03/04/05/07`, `TC-SEC-001-08/09`, `TC-SEC-005-08/09/10/12/13/14/15`, `TC-SEC-006-02`, `TC-SEC-007-01/02`. `TC-FR-005-05` and `TC-FR-005-07` need a mocked clock and a hand-forged token respectively; read their When clauses closely.
**Do:** implement one automated test per case. Use `freezegun` (or the clock service's own override hook) for `TC-FR-005-05`. For the throttle cases, reset the throttle cache between tests so they do not leak state — see risk register R7.
**Test cases to implement:**
- `TC-FR-005-01` (API integration test) — valid credentials return `access_token`
- `TC-FR-005-02` (API integration test) — refresh token only in the cookie
- `TC-FR-005-03` (API integration test) — unknown email returns the generic `401`
- `TC-FR-005-04` (API integration test) — incorrect password returns the generic `401`
- `TC-FR-005-05` (API integration test) — `exp` is T+10min; accepted at T+9m59s, rejected at T+10m1s
- `TC-FR-005-07` (API integration test) — HS256 and claim set; `alg`-substituted copy rejected; refresh token rejected as a bearer credential
- `TC-SEC-001-08` (API integration test) — CSRF bootstrap needs no bearer token
- `TC-SEC-001-09` (API integration test) — login needs no bearer token
- `TC-SEC-005-08` (API integration test) — refresh cookie production attributes
- `TC-SEC-005-09` (API integration test) — refresh cookie local-development attributes
- `TC-SEC-005-10` (API integration test) — bootstrap sets the cookie and returns a matching token
- `TC-SEC-005-12` (API integration test) — CSRF cookie `HttpOnly` in production
- `TC-SEC-005-13` (API integration test) — CSRF cookie `HttpOnly` in local development
- `TC-SEC-005-14` (Configuration test) — CSRF cookie production path/`Secure`/`SameSite`
- `TC-SEC-005-15` (Configuration test) — CSRF cookie local-development path/`Secure`/`SameSite`
- `TC-SEC-006-02` (API integration test) — unknown email and wrong password are identical
- `TC-SEC-007-01` (API integration test) — over the login limit returns `429` with `Retry-After`
- `TC-SEC-007-02` (API integration test) — the limit resets after the window
**Acceptance criteria:** all 18 pass; `TC-SEC-006-02` compares the two responses structurally, not just by status code; the throttle tests pass when run in any order and when the whole suite runs twice.
**Verify with:** `cd backend && pytest -k "tc_fr_005 or tc_sec_001_08 or tc_sec_001_09 or tc_sec_005 or tc_sec_006_02 or tc_sec_007" -v`
**Out of scope for this task:** `TC-FR-005-06` (frontend memory-only storage) — Task 2.6.
**On finishing:** commit.

#### Task 2.5 — Frontend API client, auth state, and login page
**Slice:** 2 — Login, CSRF bootstrap, authenticated API client
**Depends on:** 1.4, 2.3
**Requirements:** FR-005, SEC-005   **Design decisions:** ADS-FR-005-04, ADS-SEC-005-02, ADS-SEC-005-06
**Read before starting:**
- `docs/design_specification.md` `ADS-FR-005-04` (access token **only in application memory**; sent as `Authorization: Bearer`), `ADS-SEC-005-06` (`csrf_token` **only in application memory**, sent as `X-CSRFToken` on login/refresh/logout, **never read from the cookie**), `ADS-SEC-005-02` (browser credentials enabled for requests touching auth/CSRF cookies)
- `docs/user_flows.md` §2 "Login flow" steps 2–10 — including step 9 (remove `medical_tracker.logout_intent` on successful login) and step 10 (the dashboard opens)
- `docs/api_contract.md` §5.1 (which operations need credentials and which need `X-CSRFToken`)
**Do:**
1. Build `src/api/client.ts`: a single fetch wrapper that attaches `Authorization: Bearer` from in-memory state, sets `credentials: 'include'` for auth requests, and attaches `X-CSRFToken` from in-memory state on login, refresh and logout. **The refresh interceptor is Slice 3 — leave a documented seam, not a placeholder implementation.**
2. Build the auth context holding `accessToken` and the authenticated user **in memory only**. Nothing writes the token to `localStorage` or `sessionStorage`, ever.
3. Add a CSRF bootstrap call performed when no in-memory `csrf_token` exists, per `user_flows.md` §2 step 2.
4. Build the login page reusing the shared field-error component from Task 1.4.
5. On successful login: store the token in memory, remove `medical_tracker.logout_intent` from `localStorage`, navigate to the authenticated area.
6. Add a protected-route wrapper that redirects to login when no in-memory token exists. (Its initialization-refresh behavior arrives in Slice 3.)
**Test cases to implement:** none in this task (see 2.6).
**Acceptance criteria:** after login, `localStorage` and `sessionStorage` contain no token; protected requests carry the bearer header; login, and only login, carries `X-CSRFToken` at this stage.
**Verify with:** `cd frontend && npm run test && npm run build`
**Out of scope for this task:** refresh, replay, single-flight (Slice 3); logout (Slice 4).
**On finishing:** commit.

#### Task 2.6 — Frontend login tests and authenticated navigation
**Slice:** 2 — Login, CSRF bootstrap, authenticated API client
**Depends on:** 2.5
**Requirements:** FR-005, PRV-003   **Design decisions:** ADS-FR-005-04, ADS-PRV-003-01
**Read before starting:** `docs/test_specification.md` `TC-FR-005-06`, `TC-PRV-003-03`; `docs/design_specification.md` `ADS-PRV-003-01` (the informational page must be reachable from authenticated navigation too).
**Do:**
1. Add the informational-page link to the authenticated navigation built in Task 2.5.
2. Implement both tests.
**Test cases to implement:**
- `TC-FR-005-06` (Frontend integration test) — the access token lives only in memory, is absent from `localStorage` and `sessionStorage`, and subsequent protected requests carry it as a bearer token
- `TC-PRV-003-03` (Frontend integration test) — the informational page is reachable from authenticated navigation
**Acceptance criteria:** both pass; `TC-FR-005-06` asserts all three of its Then clauses, not only the storage absence.
**Verify with:** `cd frontend && npx vitest run -t 'TC-FR-005-06' && npx vitest run -t 'TC-PRV-003-03'`
**Out of scope for this task:** session restore on reload (Slice 3).
**On finishing:** commit. **Slice 2 complete:** squash-merge, `DEVELOPMENT_LOG.md` entry. `PRV-003` closes here; `SEC-007` now closes in Slice 3, once the refresh limit has its own case.

---

### Slice 3 — Refresh, rotation, absolute session lifetime, session restore

**Capability delivered:** a session survives a page reload and an expired access token; when it cannot be renewed, the user is told.

**Definition of Done:** both halves done; the 17 cases below pass; the full suite is green.

#### Task 3.1 — Refresh endpoint with rotation and absolute lifetime
**Slice:** 3 — Refresh, rotation, absolute session lifetime, session restore
**Depends on:** 2.3
**Requirements:** FR-007, SEC-005, SEC-007 (refresh limit), SEC-001   **Design decisions:** ADS-FR-007-01, ADS-FR-007-02, ADS-FR-007-03, ADS-FR-007-04, ADS-FR-007-05, ADS-FR-007-07, ADS-FR-007-08, ADS-FR-007-09, ADS-FR-007-10, ADS-SEC-005-04, ADS-SEC-007-01
**Read before starting:**
- `docs/api_contract.md` §5.5 (request requirements — credentials, `X-CSRFToken`, token read **only** from the cookie, **no JSON body**; the `200` body; the `401` body `{"detail": "Refresh token is invalid or expired."}` and the stale-cookie clearing) and §5.7 (cookie attributes and the absolute-lifetime statement)
- `docs/design_specification.md` `ADS-FR-007-02` (rotate and invalidate the submitted token), `ADS-FR-007-05` (expired/revoked/malformed/missing/invalid all rejected without new credentials, stale cookie cleared), `ADS-FR-007-07` + `ADS-FR-007-08` (**rotation copies `session_start` unchanged and recomputes `exp` as `session_start + 7 days` — it must not extend the session**), `ADS-FR-007-09` (insert the superseded token's `jti` into `RevokedRefreshToken`)
- §3.2 of this plan
**Do:**
1. Add `POST /api/v1/auth/refresh/` with `AllowAny`, no bearer authentication, explicit CSRF protection, reading the raw token only from `request.COOKIES['refresh_token']`.
2. Decode as a refresh token (HS256 pinned, `token_type == "refresh"`). Reject when: absent, malformed, expired, `jti` present in `RevokedRefreshToken`, or `alg`/`token_type` wrong. Every rejection returns the same `401` body and clears the `refresh_token` cookie using the same name/path/host-only scope/`Secure`/`SameSite` as creation.
3. On success, inside one transaction: insert the submitted token's `jti` into `RevokedRefreshToken` with `expires_at` copied from its `exp`; issue a replacement refresh token passing the **incoming token's `session_start`**; issue a new access token; set the replacement cookie; return `{"access_token": ...}`.
4. Apply the 30/min per-IP throttle.
5. Regenerate `backend/openapi.yaml`.
**Test cases to implement:** none in this task (see 3.2).
**Acceptance criteria:** a token rotated on day 6 carries `exp` equal to the original `session_start + 7 days`, not day 13; the previously submitted token is rejected on resubmission; every invalid-token path clears the cookie.
**Verify with:** `cd backend && pytest -q && python manage.py spectacular --file openapi.yaml`
**Out of scope for this task:** logout (Slice 4); purging expired `RevokedRefreshToken` rows — `ADS-FR-007-09` permits it but requires nothing.
**On finishing:** commit.

#### Task 3.2 — Backend refresh tests
**Slice:** 3 — Refresh, rotation, absolute session lifetime, session restore
**Depends on:** 3.1
**Requirements:** FR-007, SEC-001, SEC-007 (refresh limit)   **Design decisions:** as Task 3.1
**Read before starting:** `docs/test_specification.md` `TC-FR-007-01/02/03/04/05/06/07/08/10/11`, `TC-SEC-001-10`, `TC-SEC-007-04`. `TC-FR-007-10` is the absolute-lifetime case — read its Given clause (several successful rotations before T+7d) exactly; a test that only rotates once does not verify what it claims.
**Do:** implement one automated test per case; use `freezegun` for `TC-FR-007-10`. `TC-SEC-007-04` needs the throttle cache cleared between tests — a module fixture, not a one-off (risk register R7); note its limit is 30/min, not the 10/min of register and login.
**Test cases to implement:**
- `TC-FR-007-01` (API integration test) — valid refresh returns a new access token
- `TC-FR-007-02` (API integration test) — rotation invalidates the previous token
- `TC-FR-007-03` (API integration test) — replacement cookie is set with the accepted attributes
- `TC-FR-007-04` (API integration test) — new token returned in `access_token`
- `TC-FR-007-05` (API integration test) — expired token rejected, no credentials, cookie cleared
- `TC-FR-007-06` (API integration test) — revoked token rejected, no credentials, cookie cleared
- `TC-FR-007-07` (API integration test) — malformed token rejected, no credentials, cookie cleared
- `TC-FR-007-08` (API integration test) — missing token rejected, no credentials
- `TC-FR-007-10` (API integration test) — rejected at T+7d+1s despite intervening rotations
- `TC-FR-007-11` (API integration test) — HS256 and claim set; `alg`-substituted copy rejected; access token rejected as a refresh token
- `TC-SEC-001-10` (API integration test) — refresh needs no bearer token
- `TC-SEC-007-04` (API integration test) — the 31st refresh within a minute from one client IP returns `429` with `Retry-After`
**Acceptance criteria:** all 12 pass; `TC-FR-007-10` performs at least two successful rotations before the final rejection; `TC-SEC-007-04` passes in any order and across two consecutive full runs.
**Verify with:** `cd backend && pytest -k "tc_fr_007 or tc_sec_001_10 or tc_sec_007_04" -v`
**Out of scope for this task:** `TC-FR-007-09` (page-reload restore) — Task 3.4.
**On finishing:** commit.

#### Task 3.3 — Frontend refresh interceptor with single-flight and one replay
**Slice:** 3 — Refresh, rotation, absolute session lifetime, session restore
**Depends on:** 2.5, 3.1
**Requirements:** FR-007, FR-008   **Design decisions:** ADS-FR-007-06, ADS-FR-008-01, ADS-FR-008-02, ADS-FR-008-03, ADS-FR-008-04, ADS-FR-006-06
**Read before starting:**
- `docs/design_specification.md` `ADS-FR-008-01` (**at most one** refresh after an auth failure; on success replace the token and replay the original request **once**), `ADS-FR-008-04` (at most one refresh in flight per application instance; others await the same result and start no second refresh), `ADS-FR-008-02` (failed *active-session* refresh: clear state, redirect to login, show a session-expired message carried through navigation state), `ADS-FR-008-03` (failed *initialization* refresh: open login, no retry loop, **no** session-expired message), `ADS-FR-007-06` (initialization may call refresh once, only when no in-memory token exists **and** `medical_tracker.logout_intent` is absent), `ADS-FR-006-06` (what that marker means)
- `docs/user_flows.md` §3 — both sub-flows and the "Absolute session lifetime" paragraph, which states that an elapsed absolute lifetime behaves exactly like any other invalid refresh token
**Do:**
1. Fill the seam left in `src/api/client.ts`: on a `401` from a protected request, call refresh at most once, then replay the original request at most once with the new token. Never loop.
2. Implement single-flight: hold the in-flight refresh promise in module state; concurrent `401`s await that same promise. Clear it when it settles.
3. Distinguish the two failure contexts explicitly. An *initialization* refresh (started by the protected-route wrapper on mount) that fails → navigate to login silently. An *active-session* refresh (started by a `401` on a user-initiated request) that fails → clear auth state, navigate to login, carry a session-expired message in navigation state and render it on the login page.
4. Initialization refresh runs only when there is no in-memory access token **and** `medical_tracker.logout_intent` is absent from `localStorage`. Bootstrap the CSRF token first (`user_flows.md` §3 step 4).
**Test cases to implement:** none in this task (see 3.4).
**Acceptance criteria:** three concurrent failing requests produce exactly one refresh request; a failed init refresh renders no session-expired message; a failed active-session refresh does.
**Verify with:** `cd frontend && npm run test && npm run build`
**Out of scope for this task:** writing the logout-intent marker — that is Slice 4. This task only **reads** it.
**On finishing:** commit. See risk register R2.

#### Task 3.4 — Frontend refresh and session tests
**Slice:** 3 — Refresh, rotation, absolute session lifetime, session restore
**Depends on:** 3.3
**Requirements:** FR-007, FR-008   **Design decisions:** as Task 3.3
**Read before starting:** `docs/test_specification.md` `TC-FR-007-09`, `TC-FR-008-01/02/03/04`.
**Do:** implement one Vitest/RTL test per case, using MSW request counting to assert *how many* refresh requests were sent — the count is the point of `TC-FR-007-09`, `TC-FR-008-01` and `TC-FR-008-04`.
**Test cases to implement:**
- `TC-FR-007-09` (Frontend integration test) — page reload sends exactly one refresh and restores the session
- `TC-FR-008-01` (Frontend integration test) — exactly one refresh and exactly one replay
- `TC-FR-008-02` (Frontend integration test) — failed active-session refresh redirects with a session-expired message
- `TC-FR-008-03` (Frontend integration test) — failed initialization refresh opens login with no retry loop and no message
- `TC-FR-008-04` (Frontend integration test) — concurrent failures share one refresh
**Acceptance criteria:** all 5 pass; each asserts an exact request count, not merely "at least one".
**Verify with:** `cd frontend && npx vitest run -t 'TC-FR-008' && npx vitest run -t 'TC-FR-007-09'`
**Out of scope for this task:** logout behaviors.
**On finishing:** commit. **Slice 3 complete:** squash-merge, `DEVELOPMENT_LOG.md` entry. `FR-007`, `FR-008` and `SEC-007` close here — `SEC-007`'s third endpoint limit lands in Task 3.2.

---

### Slice 4 — Logout

**Capability delivered:** a user logs out; the session ends locally and on the server, and stays ended across a reload even if the backend was unreachable.

**Definition of Done:** both halves done; the 15 cases below pass; the full suite is green.

#### Task 4.1 — Logout endpoint
**Slice:** 4 — Logout
**Depends on:** 3.1
**Requirements:** FR-006, SEC-005   **Design decisions:** ADS-FR-006-01, ADS-FR-006-02, ADS-FR-006-03, ADS-FR-006-04, ADS-FR-006-09, ADS-SEC-005-04, ADS-SEC-001-01
**Read before starting:**
- `docs/api_contract.md` §5.6 (credentials + `X-CSRFToken`, token read from the cookie when present, no JSON body, **`204 No Content` with an empty body for valid, expired, revoked, already-invalid and missing tokens alike**, and the `403` CSRF failure)
- `docs/design_specification.md` `ADS-FR-006-02` (invalidate a valid token), `ADS-FR-006-04` (one deterministic response that discloses nothing about token state), `ADS-FR-006-03` (clear the cookie with matching identity and attributes), `ADS-FR-006-09` (logout does **not** revoke an already-issued access token — this is accepted, not a defect to fix)
- `docs/design_specification.md` `ADS-SEC-001-01` (logout uses refresh-cookie validation and CSRF instead of the default bearer permission)
**Do:**
1. Add `POST /api/v1/auth/logout/` with `AllowAny`, no bearer authentication, explicit CSRF protection.
2. If the cookie holds a decodable, unexpired, unrevoked refresh token, insert its `jti` into `RevokedRefreshToken` with `expires_at` from its `exp`. Otherwise do nothing.
3. Always clear the `refresh_token` cookie with the same name, path, host-only scope and applicable `Secure`/`SameSite` used at creation.
4. Always return `204` with an empty body. Do not branch the response on token state.
5. Regenerate `backend/openapi.yaml`.
**Test cases to implement:** none in this task (see 4.2).
**Acceptance criteria:** all five token states return an identical `204` with an empty body; a refresh token used for logout is subsequently rejected by the refresh endpoint; the cookie is cleared in every case.
**Verify with:** `cd backend && pytest -q && python manage.py spectacular --file openapi.yaml`
**Out of scope for this task:** revoking access tokens — explicitly excluded by `ADS-FR-006-09`.
**On finishing:** commit.

#### Task 4.2 — Backend logout tests
**Slice:** 4 — Logout
**Depends on:** 4.1
**Requirements:** FR-006   **Design decisions:** as Task 4.1
**Read before starting:** `docs/test_specification.md` `TC-FR-006-01` … `TC-FR-006-07`, `TC-FR-006-14`.
**Do:** implement one automated test per case; `TC-FR-006-14` needs a mocked clock to stay inside the ten-minute access-token window.
**Test cases to implement:**
- `TC-FR-006-01` (API integration test) — logout invalidates the refresh token
- `TC-FR-006-02` (API integration test) — logout clears the refresh cookie with its accepted attributes
- `TC-FR-006-03` (API integration test) — valid token → empty `204`
- `TC-FR-006-04` (API integration test) — missing token → empty `204`
- `TC-FR-006-05` (API integration test) — expired token → empty `204`
- `TC-FR-006-06` (API integration test) — revoked token → empty `204`
- `TC-FR-006-07` (API integration test) — already-invalid token → empty `204`
- `TC-FR-006-14` (API integration test) — a pre-logout access token still authenticates until its own expiry
**Acceptance criteria:** all 8 pass; the five idempotence cases assert an **empty** body, not just the status.
**Verify with:** `cd backend && pytest -k "tc_fr_006_0 or tc_fr_006_14" -v`
**Out of scope for this task:** frontend logout behavior — Task 4.4.
**On finishing:** commit.

#### Task 4.3 — Frontend logout flow
**Slice:** 4 — Logout
**Depends on:** 3.3, 4.1
**Requirements:** FR-006, SEC-005   **Design decisions:** ADS-FR-006-05, ADS-FR-006-06, ADS-FR-006-07, ADS-FR-006-08, ADS-SEC-005-06
**Read before starting:**
- `docs/user_flows.md` §4 — the step order matters: write the marker (step 2), clear in-memory state (step 3, **the CSRF token deliberately survives for the request itself**), then send the request (step 4)
- `docs/design_specification.md` `ADS-FR-006-05` (clear state **before** sending), `ADS-FR-006-06` (marker value `true` under `medical_tracker.logout_intent`; suppresses initialization refresh while present), `ADS-FR-006-07` (a later successful login removes it), `ADS-FR-006-08` (navigate to login after success, failure, **or** an unreachable backend)
**Do:**
1. Add the logout action: write `medical_tracker.logout_intent = "true"` to `localStorage`; clear the in-memory access token and authenticated-user state; keep the in-memory CSRF token; send the credentialed `POST /api/v1/auth/logout/` with `X-CSRFToken` and no body.
2. Navigate to the login page in the success, error and network-failure paths alike — wrap the request so no rejection can skip the navigation.
3. Confirm Task 2.5's login handler already removes the marker (`ADS-FR-006-07`); if not, add it there.
**Test cases to implement:** none in this task (see 4.4).
**Acceptance criteria:** state is cleared before the request is dispatched, observably; the marker exists after logout and is gone after the next successful login; navigation happens in all three outcomes.
**Verify with:** `cd frontend && npm run test && npm run build`
**Out of scope for this task:** any change to the refresh interceptor.
**On finishing:** commit.

#### Task 4.4 — Frontend logout tests
**Slice:** 4 — Logout
**Depends on:** 4.3
**Requirements:** FR-006, SEC-005   **Design decisions:** as Task 4.3
**Read before starting:** `docs/test_specification.md` `TC-FR-006-08` … `TC-FR-006-13`, `TC-SEC-005-11`. `TC-SEC-005-11` spans login, refresh **and** logout — it can only be written now that all three exist.
**Do:** implement one Vitest/RTL test per case.
**Test cases to implement:**
- `TC-FR-006-08` (Frontend integration test) — local state cleared before the request is dispatched
- `TC-FR-006-09` (Frontend integration test) — marker written; initialization attempts no refresh while it is present
- `TC-FR-006-10` (Frontend integration test) — a later successful login removes the marker
- `TC-FR-006-11` (Frontend integration test) — navigates to login after success
- `TC-FR-006-12` (Frontend integration test) — navigates to login after an error response
- `TC-FR-006-13` (Frontend integration test) — navigates to login when the backend is unreachable
- `TC-SEC-005-11` (Frontend integration test) — login, refresh and logout each carry `X-CSRFToken`; the code never reads the CSRF cookie directly
**Acceptance criteria:** all 7 pass; `TC-FR-006-08` asserts the ordering (state cleared *before* dispatch), not merely that both happened.
**Verify with:** `cd frontend && npx vitest run -t 'TC-FR-006' && npx vitest run -t 'TC-SEC-005-11'`
**Out of scope for this task:** backend logout assertions.
**On finishing:** commit. **Slice 4 complete:** squash-merge, `DEVELOPMENT_LOG.md` entry. `FR-006` closes here.

---

### Slice 5 — Account timezone and shared timezone-aware presentation

**Capability delivered:** an authenticated user views and changes their account timezone, and every timestamp in the interface follows it while date-only values do not shift.

**Definition of Done:** both halves done; the 5 cases below pass; the full suite is green.

#### Task 5.1 — Account retrieve and timezone update endpoints
**Slice:** 5 — Account timezone and shared timezone-aware presentation
**Depends on:** 2.3
**Requirements:** FR-009, SEC-001   **Design decisions:** ADS-FR-009-01, ADS-SEC-001-01, ADS-FR-004-01
**Read before starting:**
- `docs/api_contract.md` §6.1 and §6.2 (the account representation; **only `timezone` is writable**; the value must be a supported IANA identifier)
- `docs/design_specification.md` `ADS-FR-009-01` (`PATCH /api/v1/account/`; the user may modify only their own account), `ADS-FR-004-01` (the same supported-timezone source used at registration)
- `docs/product_definition.md` §10.2 (changing the timezone must not alter the stored instant of an existing timezone-aware datetime)
**Do:**
1. Add `GET /api/v1/account/` and `PATCH /api/v1/account/`, both authenticated, both operating on `request.user` only — no id in the path, no way to address another account.
2. The serializer exposes `id`, `email`, `timezone` and makes only `timezone` writable, validated through `accounts/timezones.py`.
3. Regenerate `backend/openapi.yaml`.
**Test cases to implement:** none in this task (see 5.4).
**Acceptance criteria:** `PATCH` with an unsupported value returns `400` with a `timezone` field error and leaves the stored value untouched; `email` and `id` are not writable.
**Verify with:** `cd backend && pytest -q && python manage.py spectacular --file openapi.yaml`
**Out of scope for this task:** password change (Slice 6); using the timezone for any query (Slice 7 onward).
**On finishing:** commit.

#### Task 5.2 — Account settings page
**Slice:** 5 — Account timezone and shared timezone-aware presentation
**Depends on:** 2.5, 5.1
**Requirements:** FR-009   **Design decisions:** ADS-FR-009-01, ADS-UX-004-01
**Read before starting:** `docs/user_flows.md` §5 (the ten-step flow and its failure behavior).
**Do:**
1. Build the account settings page: fetch `GET /api/v1/account/`, show the current timezone, offer the same timezone control used at registration, submit `PATCH /api/v1/account/`.
2. On success, update the timezone held in client auth state so presentation follows immediately (`user_flows.md` §5 steps 7–10).
3. Reuse the shared field-error component for the rejection path.
**Test cases to implement:** none in this task (see 5.4).
**Acceptance criteria:** the page shows the stored timezone on load; a successful update is reflected in client state without a reload; a rejected value shows an error adjacent to the control and leaves the displayed value unchanged.
**Verify with:** `cd frontend && npm run test && npm run build`
**Out of scope for this task:** the formatting utility (Task 5.3).
**On finishing:** commit.

#### Task 5.3 — Shared timezone-aware presentation utility
**Slice:** 5 — Account timezone and shared timezone-aware presentation
**Depends on:** 5.2
**Requirements:** UX-007   **Design decisions:** ADS-UX-007-01, ADS-TECH-002-01
**Read before starting:**
- `docs/design_specification.md` `ADS-UX-007-01` (account timezone held in application state and passed to a **shared** formatting utility; **timezone-aware timestamps are converted; date-only values are displayed as stored and are not shifted through UTC**)
- `docs/domain_model.md` §10 (which fields are which — `scheduled_date`, `completed_date` and reminder `due_date` are calendar dates; `created_at`/`updated_at` are instants)
- §3.1 of this plan, final bullet
**Do:**
1. Create `src/format/datetime.ts` with two distinct exported functions: `formatInstant(iso, timeZone)` — parses an ISO instant and converts it to the account timezone; and `formatCalendarDate(isoDate)` — renders a `YYYY-MM-DD` string **without ever constructing a `Date` from it in a way that applies an offset**. Do not merge them into one polymorphic helper: the whole point is that these two paths never meet.
2. Add `formatCalendarTime(isoTime)` for the optional `scheduled_time` local-time value, likewise unconverted.
3. **Every later component formats dates and times through this module only.**
**Test cases to implement:** none in this task (see 5.4).
**Acceptance criteria:** `formatCalendarDate('2026-08-15')` returns `2026-08-15`'s rendering under any account timezone, including ones west of UTC; `formatInstant` converts correctly for `Europe/Warsaw`.
**Verify with:** `cd frontend && npm run test`
**Out of scope for this task:** applying it to examination views — those slices consume it.
**On finishing:** commit. See risk register R4.

#### Task 5.4 — Account and presentation tests
**Slice:** 5 — Account timezone and shared timezone-aware presentation
**Depends on:** 5.1, 5.3
**Requirements:** FR-009, UX-007, SEC-001   **Design decisions:** as Tasks 5.1–5.3
**Read before starting:** `docs/test_specification.md` `TC-FR-009-01`, `TC-FR-009-02`, `TC-UX-007-01`, `TC-UX-007-02`, `TC-SEC-001-06`.
**Do:** implement one automated test per case — three backend, two frontend.
**Test cases to implement:**
- `TC-FR-009-01` (API integration test) — update persists and a later `GET` confirms it
- `TC-FR-009-02` (API validation test) — unsupported value rejected; stored timezone unchanged
- `TC-SEC-001-06` (API integration test) — unauthenticated `GET /api/v1/account/` returns `401`
- `TC-UX-007-01` (Frontend integration test) — a fixed UTC timestamp renders in `Europe/Warsaw`
- `TC-UX-007-02` (Frontend integration test) — `2026-08-15` renders as `2026-08-15` under a non-UTC account timezone
**Acceptance criteria:** all 5 pass; `TC-UX-007-02` uses a timezone whose offset would visibly shift the date if the value were routed through UTC.
**Verify with:** `cd backend && pytest -k "tc_fr_009 or tc_sec_001_06" -v` and `cd frontend && npx vitest run -t 'TC-UX-007'`
**Out of scope for this task:** any examination data.
**On finishing:** commit. **Slice 5 complete:** squash-merge, `DEVELOPMENT_LOG.md` entry. `FR-009` and `UX-007` close here.

---

### Slice 6 — Password change

**Capability delivered:** an authenticated user changes their password and can then log in only with the new one.

**Definition of Done:** both halves done; the 3 cases below pass; the full suite is green.

#### Task 6.1 — Password change endpoint
**Slice:** 6 — Password change
**Depends on:** 5.1
**Requirements:** FR-048   **Design decisions:** ADS-FR-048-01, ADS-FR-003-01, ADS-SEC-003-01
**Read before starting:**
- `docs/design_specification.md` `ADS-FR-048-01` (`POST /api/v1/account/password/`, **standard bearer permission with no CSRF requirement**, `current_password` + `new_password`, verify the current password against the stored hash, validate the new one against the registration policy, `200 OK` with an empty body, and **no modification to the stored password if either check fails**)
- `docs/api_contract.md` §6.3 (validation list and the two `400` failure paths)
- `docs/user_flows.md` §25
**Do:**
1. Add the endpoint with the default authenticated permission. It is a domain-API operation, not an auth-cookie operation — do **not** add CSRF protection to it.
2. Verify `current_password` with `user.check_password`; validate `new_password` with the same validator stack registration uses (including `UserAttributeSimilarityValidator` against the email) plus the 8–128 length bounds.
3. On success call `set_password` and save; return `200` with an empty body.
4. Regenerate `backend/openapi.yaml`.
**Test cases to implement:** none in this task (see 6.3).
**Acceptance criteria:** a wrong current password returns `400` with a field-level error and leaves the hash byte-identical; a policy-failing new password does the same; success makes the old password stop working and the new one start.
**Verify with:** `cd backend && pytest -q && python manage.py spectacular --file openapi.yaml`
**Out of scope for this task:** unauthenticated password reset — excluded by `product_definition.md` §8 and by `ADS-FR-048-01`.
**On finishing:** commit.

#### Task 6.2 — Password change form
**Slice:** 6 — Password change
**Depends on:** 5.2, 6.1
**Requirements:** FR-048   **Design decisions:** ADS-FR-048-01
**Read before starting:** `docs/user_flows.md` §25 including its failure behavior (errors adjacent to the offending field; the stored password remains unchanged).
**Do:**
1. Add a change-password form to the account settings page with `current_password` and `new_password` controls, reusing the shared field-error component.
2. On success show a confirmation and clear both password values from client state (`user_flows.md` §25 step 6).
**Test cases to implement:** none in this task (see 6.3).
**Acceptance criteria:** neither password value remains in component state or in any store after a successful submit; both failure paths render adjacent to the correct field.
**Verify with:** `cd frontend && npm run test && npm run build`
**Out of scope for this task:** logging the user out after a password change — nothing in the spec requires it; do not add it.
**On finishing:** commit.

#### Task 6.3 — Password change tests
**Slice:** 6 — Password change
**Depends on:** 6.1
**Requirements:** FR-048   **Design decisions:** ADS-FR-048-01
**Read before starting:** `docs/test_specification.md` `TC-FR-048-01/02/03`.
**Do:** implement one automated test per case.
**Test cases to implement:**
- `TC-FR-048-01` (API integration test) — success returns an empty `200`; a later login works only with the new password
- `TC-FR-048-02` (API validation test) — incorrect current password rejected; stored password unchanged
- `TC-FR-048-03` (API validation test) — policy-failing new password rejected; stored password unchanged
**Acceptance criteria:** all 3 pass; both rejection cases assert the stored hash is unchanged, not merely that the response was `400`.
**Verify with:** `cd backend && pytest -k tc_fr_048 -v`
**Out of scope for this task:** frontend assertions — none are specified for this requirement.
**On finishing:** commit. **Slice 6 complete:** squash-merge, `DEVELOPMENT_LOG.md` entry. `FR-048` closes here, satisfying `product_definition.md` §11's password-change bullet (added when `RF-26` was resolved).

---

### Slice 7 — Categories, examination model, creation and list

**Capability delivered:** an authenticated user saves a draft or a planned examination, optionally categorised, and sees it in their examination list.

**This is the largest slice (32 cases).** Tasks 7.1–7.5 are the backend half and end with a green suite — that is the natural stopping point if the work spans two sessions. Tasks 7.6–7.9 are the frontend half plus the data-model review.

**Definition of Done:** both halves done; the 32 cases below pass; the full suite is green.

#### Task 7.1 — Category model, seed migration, and read-only endpoint
**Slice:** 7 — Categories, examination model, creation and list
**Depends on:** 2.3
**Requirements:** FR-026, FR-025 (partial), SEC-001   **Design decisions:** ADS-FR-026-01, ADS-FR-025-01, ADS-SEC-001-01
**Read before starting:**
- `docs/domain_model.md` §3.2 (fields `id`/`name`/`slug`; the eight system-defined values; **idempotent data migration**, unique names and slugs, read-only for MVP users, `Uncategorized` is not a stored row)
- `docs/design_specification.md` `ADS-FR-026-01` (idempotent data migration with stable unique slugs; duplicates prevented by database constraints)
- `docs/api_contract.md` §7 (the read-only collection, the exact eight names, and the response object shape)
**Do:**
1. Create the `examinations` app. Define `ExaminationCategory` with unique `name` and unique `slug`; generate the schema migration.
2. Add a **data migration** inserting the eight categories with stable slugs, written so that re-running it creates no duplicates (`update_or_create` keyed on `slug`, or `get_or_create` — not bare `create`). Give it a no-op reverse.
3. Add `GET /api/v1/categories/`, authenticated, read-only. Provide no create, update or delete route.
4. Regenerate `backend/openapi.yaml`.
**Test cases to implement:** none in this task (see 7.5).
**Acceptance criteria:** after `migrate`, exactly eight categories exist with the documented names; running the data migration twice still yields eight; no write route exists on the categories resource.
**Verify with:** `cd backend && python manage.py migrate && python manage.py shell -c "from examinations.models import ExaminationCategory as C; print(C.objects.count())"`
**Out of scope for this task:** user-defined categories — excluded by `product_definition.md` §8.
**On finishing:** commit.

#### Task 7.2 — Examination model, migration, and the owner-scoped queryset mixin
**Slice:** 7 — Categories, examination model, creation and list
**Depends on:** 7.1
**Requirements:** FR-012, FR-013, TECH-002, PRV-001, SEC-002   **Design decisions:** ADS-FR-012-01, ADS-FR-013-01, ADS-FR-025-01, ADS-FR-023-02, ADS-TECH-002-01, ADS-PRV-001-01, ADS-SEC-002-01
**Read before starting:**
- `docs/domain_model.md` §3.3 — **the complete field table is the whitelist**; every field, its domain type, and its required/conditional status. Also §4 (relationships, including `source_occurrence` and its set-null-on-delete rule) and §8 (core invariants)
- `docs/design_specification.md` `ADS-TECH-002-01` (date field, separate nullable time field, timezone-aware datetimes for instants), `ADS-PRV-001-01` (**adding any stored examination field requires an approved requirements and design change before the migration is created** — this task adds none beyond the domain model), `ADS-FR-023-02` (deleting a source sets `source_occurrence` to null; it does not cascade or block), `ADS-SEC-002-01` (querysets always filtered by `request.user`; ownership assigned server-side)
- `docs/api_contract.md` §8.1 (the representation and the writable column of its field table)
**Do:**
1. Define `ExaminationRecord` with exactly the fields in `domain_model.md` §3.3 — no more. `user` FK cascade; `category` FK nullable with `on_delete=PROTECT` (categories are seed data and are never deleted); `title`; `medical_specialty`; `scheduled_date` (`DateField`, nullable); `scheduled_time` (`TimeField`, nullable); `completed_date` (`DateField`, nullable); `status` with the five choices; `location`; `notes`; `source_occurrence` self-FK, nullable, **`on_delete=SET_NULL`**; `created_at`/`updated_at` timezone-aware.
2. Define `Reminder` and `RecurrenceRule` **models and migrations now** — one-to-one to `ExaminationRecord`, `on_delete=CASCADE`, fields per `domain_model.md` §3.4 and §3.5. Their endpoints and rules arrive in Slices 11–13; defining them here keeps `TC-FR-023-02`'s cascade assertable in Slice 8 and avoids a second migration pass over the same table.
3. Add `examinations/querysets.py` with an owner-scoped mixin providing `get_queryset()` filtered by `self.request.user`. **Every examination, reminder and recurrence view uses it.**
4. Generate and apply migrations.
**Test cases to implement:** none in this task (see 7.5).
**Acceptance criteria:** `makemigrations --check` is clean; the model's field set equals `domain_model.md` §3.3's table exactly; deleting a referenced source examination nulls the referring record rather than deleting it.
**Verify with:** `cd backend && python manage.py makemigrations --check --dry-run && python manage.py migrate && pytest -q`
**Out of scope for this task:** reminder/recurrence serializers, views or business rules (Slices 11–13); any serializer at all.
**On finishing:** commit.

#### Task 7.3 — User-local time, the derived time-state module, and status-dependent validation
**Slice:** 7 — Categories, examination model, creation and list
**Depends on:** 7.2
**Requirements:** FR-014, FR-033 (the rule; its filters arrive in Slice 10)   **Design decisions:** ADS-FR-014-01, ADS-FR-014-02, ADS-FR-033-01, ADS-FR-033-02
**Read before starting:**
- `docs/design_specification.md` `ADS-FR-014-01` (title always; `scheduled_date` for planned/cancelled/missed; `completed_date` for completed; enforced for **both create and update**), `ADS-FR-014-02` (`completed_date` not later than the authenticated user's current local date, on create **and** update)
- `docs/design_specification.md` `ADS-FR-033-01` and `ADS-FR-033-02` (the derived overdue rule and its exact date/time boundary — a current-date record **without** a scheduled time is not overdue)
- `docs/domain_model.md` §6.2, §6.3 and §7 (the rule in pseudocode, and why it is derived rather than stored)
- `docs/api_contract.md` §8.1 (`time_state` is a read-only response field whose domain is `upcoming`, `overdue`, or `null`) and §8.2 (every create or update validates the complete resulting record)
- §3.1 of this plan, first two bullets
**Do:**
1. Extend `config/clock.py` (or add `accounts/localtime.py`) with `user_local_now(user)` and `user_local_date(user)`, resolving `clock.now()` into the user's stored IANA timezone. **Nothing computes a user's local date any other way.**
2. Create `examinations/time_state.py` — the single source of truth for the derived state. Expose `time_state_for(record, local_now)` returning `'upcoming'`, `'overdue'`, or `None`, implementing `ADS-FR-033-02` exactly: `None` unless `status == 'planned'`; `'overdue'` when `scheduled_date < local_date`, or when `scheduled_date == local_date` **and** `scheduled_time is not None` **and** `scheduled_time < local_time`; otherwise `'upcoming'`. Slice 10 adds queryset filters to this same module against this same rule — it does not write a second implementation.
3. Create `examinations/validators.py` with `validate_resulting_record(data, user)` applying the status-dependent rules to the **complete resulting record**. For a `PATCH`, the caller merges the instance with the submitted diff *before* calling this — the validator never sees a partial record.
4. Field-error keys must match `api_contract.md` §3.4: `title`, `scheduled_date`, `completed_date`, `status`, `category_id`.
**Test cases to implement:** none in this task (see 7.5).
**Acceptance criteria:** `time_state_for` returns `None` for every non-planned status regardless of dates; a completed record dated one day after the user's local date fails validation; `grep -rn "date.today()\|datetime.now()" backend/examinations` returns nothing.
**Verify with:** `cd backend && pytest -q`
**Out of scope for this task:** `time_state` **filters** on the list endpoint (Slice 10); the calendar `state` value (Slice 15); `overdue_count` (Slice 16). All three consume this module.
**On finishing:** commit. See risk register R1 and R5.

#### Task 7.4 — Examination create and list endpoints
**Slice:** 7 — Categories, examination model, creation and list
**Depends on:** 7.3
**Requirements:** FR-010, FR-011, FR-012, FR-013, FR-014, FR-015, FR-025, PRV-002, SEC-001, SEC-002   **Design decisions:** ADS-FR-010-01, ADS-FR-011-01, ADS-FR-012-01, ADS-FR-013-01, ADS-FR-014-01, ADS-FR-014-02, ADS-FR-015-01, ADS-FR-025-01, ADS-PRV-002-01, ADS-SEC-002-01, ADS-SEC-001-01
**Read before starting:**
- `docs/api_contract.md` §8.1 (the full representation, and which fields are writable — `category_id` is write-only, `category` is read-only), §8.2 (status-dependent validation), §10 (the four documented create request shapes and the line **"The request must not accept `user_id`, `source_occurrence`, `time_state`, `created_at`, or `updated_at`"**), §9.1 (the list returns a JSON array; no pagination)
- `docs/design_specification.md` `ADS-FR-010-01` (draft requires only `title` and preserves every valid optional value supplied), `ADS-FR-011-01` (planned needs `title` + `scheduled_date`; category and time stay optional), `ADS-FR-015-01` (category resolved only against existing rows; status validated by the enumeration)
- `docs/user_flows.md` §7 and §8
**Do:**
1. Build the examination serializer: writable `category_id`, `title`, `medical_specialty`, `scheduled_date`, `scheduled_time`, `completed_date`, `status`, `location`, `notes`; read-only `id`, `user_id`, `category`, `source_occurrence`, `time_state`, `created_at`, `updated_at`. Reject the five non-writable request fields rather than silently ignoring them.
2. Compute `time_state` through `examinations/time_state.py` — never inline.
3. Route validation through `validators.validate_resulting_record`, merging instance + diff for updates from the outset so the Slice 8 `PATCH` inherits correct behavior.
4. Add `POST /api/v1/examinations/` and `GET /api/v1/examinations/`, both authenticated, both on the owner-scoped queryset, assigning `user` from `request.user` on create.
5. Regenerate `backend/openapi.yaml`.
**Test cases to implement:** none in this task (see 7.5).
**Acceptance criteria:** a draft with only a title returns `201`; a planned record without `scheduled_date` returns `400` with a `scheduled_date` error; submitting `user_id` does not change ownership; the list returns only the caller's records as a bare JSON array.
**Verify with:** `cd backend && pytest -q && python manage.py spectacular --file openapi.yaml`
**Out of scope for this task:** detail/update/delete (Slice 8); search, filters, ordering (Slice 9); `time_state` **filters** (Slice 10).
**On finishing:** commit.

#### Task 7.5 — Backend examination and category tests
**Slice:** 7 — Categories, examination model, creation and list
**Depends on:** 7.4
**Requirements:** FR-010, FR-011, FR-012, FR-014, FR-015, FR-025, FR-026, PRV-002, TECH-002   **Design decisions:** as Tasks 7.1–7.4
**Read before starting:** `docs/test_specification.md` `TC-FR-010-01`, `TC-FR-011-01`, `TC-FR-012-01…06`, `TC-FR-014-01…07`, `TC-FR-015-01/02`, `TC-FR-025-01`, `TC-FR-026-01`, `TC-PRV-002-01`, `TC-TECH-002-01/02/03`. `TC-FR-014-06` and `TC-FR-014-07` freeze the user's local date at `2026-08-04` — use the clock service from Task 7.3, not a naive patch of `date.today`.
**Do:** implement one automated test per case.
**Test cases to implement:**
- `TC-FR-010-01` (API integration test) — draft preserves title and supplied optional values
- `TC-FR-011-01` (API integration test) — minimal planned creation
- `TC-FR-012-01…05` (API validation tests) — each of the five statuses accepted
- `TC-FR-012-06` (API validation test) — `archived` rejected with a `status` error
- `TC-FR-014-01` (API validation test) — missing title
- `TC-FR-014-02/03/04` (API validation tests) — planned/cancelled/missed without `scheduled_date`
- `TC-FR-014-05` (API validation test) — completed without `completed_date`
- `TC-FR-014-06` (API validation test) — `completed_date` equal to the frozen local date is accepted
- `TC-FR-014-07` (API validation test) — `completed_date` one day later is rejected
- `TC-FR-015-01` (API validation test) — `category_id: 9999` rejected with a `category_id` error
- `TC-FR-015-02` (API validation test) — unsupported status with a valid category rejected with a `status` error
- `TC-FR-025-01` (API integration test) — assigned category returned as the `category` object
- `TC-FR-026-01` (API integration test) — exactly the eight required categories, each once
- `TC-PRV-002-01` (API integration test) — creation succeeds with only appointment/examination metadata
- `TC-TECH-002-01` (Backend model test) — date-only round-trip with no time or timezone component
- `TC-TECH-002-02` (Backend model test) — date and optional time stored separately
- `TC-TECH-002-03` (Backend model test) — `created_at` is a timezone-aware instant, unaffected by the account timezone
**Acceptance criteria:** all 23 pass; the `TC-TECH-002-*` cases assert the Python **types** retrieved from the database, not just string equality.
**Verify with:** `cd backend && pytest -k "tc_fr_010 or tc_fr_011 or tc_fr_012 or tc_fr_014 or tc_fr_015 or tc_fr_025 or tc_fr_026 or tc_prv_002 or tc_tech_002" -v`
**Out of scope for this task:** `TC-FR-013-*` (needs `PATCH`/detail — Slice 8).
**On finishing:** commit. **Backend half of Slice 7 is complete here — a safe stopping point with a green suite.**

#### Task 7.6 — Examination form (draft and planned modes)
**Slice:** 7 — Categories, examination model, creation and list
**Depends on:** 5.3, 7.4
**Requirements:** UX-005, UX-006, FR-025, FR-027   **Design decisions:** ADS-UX-005-01, ADS-UX-006-01, ADS-FR-027-01, ADS-UX-008-01
**Read before starting:**
- `docs/design_specification.md` `ADS-UX-005-01` (an explicit draft save action; in draft mode **only title is required**; entered optional values are submitted unchanged), `ADS-UX-006-01` (planned mode marks title and scheduled date required; category and scheduled time stay optional; submission is blocked only for missing required planned fields or backend rejection), `ADS-FR-027-01` (the API represents no category as `null`; shared frontend presentation displays `Uncategorized`)
- `docs/user_flows.md` §7 and §8
**Do:**
1. Build the examination form with all documented fields, fetching categories from `GET /api/v1/categories/`.
2. Implement the two required-field modes exactly as the decisions state. Do not add a required marker the spec does not call for.
3. Build a small shared `CategoryLabel` component rendering `Uncategorized` when the category value is `null`. Every list, detail, calendar and dashboard view reuses it.
4. Format all dates and times through `src/format/datetime.ts` from Task 5.3.
5. Reuse the shared field-error component for backend `400` responses.
**Test cases to implement:** none in this task (see 7.8).
**Acceptance criteria:** a title-only draft submits successfully; a planned record with title and date submits without category or time; the form is completable by keyboard alone.
**Verify with:** `cd frontend && npm run test && npm run build`
**Out of scope for this task:** editing an existing record (Slice 8).
**On finishing:** commit.

#### Task 7.7 — Examination list page with four states
**Slice:** 7 — Categories, examination model, creation and list
**Depends on:** 7.6
**Requirements:** FR-020, FR-027   **Design decisions:** ADS-FR-020-01, ADS-FR-027-01
**Read before starting:**
- `docs/design_specification.md` `ADS-FR-020-01` (**four mutually exclusive states**: loading, empty, populated, error)
- `docs/user_flows.md` §10 "Main flow" steps 4–7 (including: each record shows its stored lifecycle status, a null category shows as `Uncategorized`, and planned records show their derived upcoming/overdue state)
**Do:**
1. Build the list page consuming `GET /api/v1/examinations/` through TanStack Query.
2. Render exactly one of the four states at a time — a loading skeleton beside stale data would violate "mutually exclusive".
3. Show each record's status, its `time_state` when non-null, and its category through `CategoryLabel`.
**Test cases to implement:** none in this task (see 7.8).
**Acceptance criteria:** each state renders alone; the error state appears on a failed request rather than an empty list.
**Verify with:** `cd frontend && npm run test && npm run build`
**Out of scope for this task:** search/filter/order controls (Slice 9); detail navigation (Slice 8).
**On finishing:** commit.

#### Task 7.8 — Frontend examination tests
**Slice:** 7 — Categories, examination model, creation and list
**Depends on:** 7.7
**Requirements:** FR-020, FR-027, UX-005, UX-006   **Design decisions:** as Tasks 7.6–7.7
**Read before starting:** `docs/test_specification.md` `TC-FR-020-01…04`, `TC-FR-027-01`, `TC-UX-005-01/02`, `TC-UX-006-01`.
**Do:** implement one Vitest/RTL test per case, using MSW for each list response condition.
**Test cases to implement:**
- `TC-FR-020-01` (Frontend integration test) — loading state and no other
- `TC-FR-020-02` (Frontend integration test) — empty state and no other
- `TC-FR-020-03` (Frontend integration test) — populated state listing the returned records
- `TC-FR-020-04` (Frontend integration test) — error state and no other
- `TC-FR-027-01` (Frontend component test) — a record with `category: null` displays `Uncategorized`
- `TC-UX-005-01` (Frontend integration test) — a title-only draft saves
- `TC-UX-005-02` (Frontend integration test) — a draft with optional values saves with them
- `TC-UX-006-01` (Frontend integration test) — planned saves with only title and scheduled date
**Acceptance criteria:** all 8 pass; each `TC-FR-020-*` asserts the **absence** of the other three states, as its Then clause requires.
**Verify with:** `cd frontend && npx vitest run -t 'TC-FR-020' && npx vitest run -t 'TC-FR-027-01' && npx vitest run -t 'TC-UX-005' && npx vitest run -t 'TC-UX-006-01'`
**Out of scope for this task:** delete confirmation (Slice 8).
**On finishing:** commit.

#### Task 7.9 — Examination field-boundary data-model review
**Slice:** 7 — Categories, examination model, creation and list
**Depends on:** 7.5
**Requirements:** PRV-001   **Design decisions:** ADS-PRV-001-01
**Read before starting:**
- `docs/test_specification.md` `TC-PRV-001-01` (the comparison to perform: the model *and* its create/update serializers against the approved domain model)
- `docs/domain_model.md` §3.3 (the approved field table — the whitelist)
- `docs/design_specification.md` `ADS-PRV-001-01`
- `docs/review_findings.md` §1 (the non-normative standing line your artifact must open with)
**Do:**
1. Confirm assumption A3 with the owner before creating `docs/reviews/` — one line is enough.
2. Produce `docs/reviews/TC-PRV-001-01-examination-field-boundary.md`: a non-normative standing line, the date, the two field lists side by side (model fields; writable serializer fields) against `domain_model.md` §3.3, and an explicit verdict.
3. If any field is present in the code but absent from the domain model, **stop** — that is a spec change and belongs to the owner. Record it as a proposed finding, do not remove the field on your own authority.
**Test cases to implement:** `TC-PRV-001-01` (Data-model review) — satisfied by the recorded artifact, not by code.
**Acceptance criteria:** the artifact exists, names every field on both sides, and states a verdict; the two lists match.
**Verify with:** read the artifact against `docs/domain_model.md` §3.3 with both open.
**Out of scope for this task:** changing the model or the domain model.
**On finishing:** commit. **Slice 7 complete:** squash-merge, `DEVELOPMENT_LOG.md` entry, set Phase 4 to `In progress`.

---

### Slice 8 — Examination detail, edit, and delete

**Capability delivered:** a user opens one of their examinations, edits it, promotes a draft to planned, and deletes it after confirming — and cannot reach anyone else's.

**Definition of Done:** both halves done; the 15 cases below pass; the full suite is green.

#### Task 8.1 — Detail, update, and delete endpoints with uniform not-found
**Slice:** 8 — Examination detail, edit, and delete
**Depends on:** 7.4
**Requirements:** FR-013, FR-016, FR-021, FR-022, FR-023, SEC-001, SEC-002, SEC-006   **Design decisions:** ADS-FR-013-01, ADS-FR-016-01, ADS-FR-021-01, ADS-FR-022-01, ADS-FR-023-01, ADS-FR-023-02, ADS-SEC-002-01, ADS-SEC-006-01
**Read before starting:**
- `docs/api_contract.md` §11 (retrieve: `200`/`401`/`404`), §12 (`PATCH` is partial but **validation applies to the complete resulting record**; the documented status-change side effects), §13 (delete is permanent; reminder and recurrence cascade; a generated occurrence survives with `source_occurrence` set to `null`), §3.3 (the single not-found body)
- `docs/design_specification.md` `ADS-SEC-006-01` (**lookup happens only inside the authenticated user's filtered queryset**, so "missing" and "another user's" are indistinguishable by construction — do not implement this as a permission check after a global lookup), `ADS-FR-022-01` (`PATCH` is the primary edit operation; `PUT` only if retained in the contract — it is not; see assumption A6), `ADS-FR-016-01` (draft→planned through the normal update endpoint)
- §3.1 of this plan, bullets 2 and 6
**Do:**
1. Add `GET`, `PATCH` and `DELETE` on `/api/v1/examinations/{id}/`, all authenticated, all resolving the object **only** from the owner-scoped queryset built in Task 7.2. A miss raises `404` with the body from §3.3 — one code path, no branch on the reason.
2. `PATCH` merges instance + diff and validates the complete resulting record through `validators.validate_resulting_record`.
3. `DELETE` returns `204`. Cascade to reminder and recurrence comes from the model `on_delete` set in Task 7.2; `source_occurrence` set-null likewise.
4. Do not add `PUT`.
5. Regenerate `backend/openapi.yaml`.
**Test cases to implement:** none in this task (see 8.2).
**Acceptance criteria:** a `PATCH` clearing `scheduled_date` on a planned record is rejected because the *resulting* record is invalid; another user's id and a nonexistent id produce byte-identical `404` responses; deleting removes the reminder and recurrence rows.
**Verify with:** `cd backend && pytest -q && python manage.py spectacular --file openapi.yaml`
**Out of scope for this task:** reminder deactivation on status change (Slice 12) — reminders have no endpoints yet.
**On finishing:** commit. See risk register R5.

#### Task 8.2 — Backend detail, update, delete, and ownership tests
**Slice:** 8 — Examination detail, edit, and delete
**Depends on:** 8.1
**Requirements:** FR-013, FR-016, FR-021, FR-022, FR-023, SEC-001, SEC-002, SEC-006   **Design decisions:** as Task 8.1
**Read before starting:** `docs/test_specification.md` `TC-FR-013-01/02`, `TC-FR-016-01/02`, `TC-FR-021-01`, `TC-FR-022-01`, `TC-FR-023-01/02`, `TC-SEC-001-01`, `TC-SEC-002-01/02/03`, `TC-SEC-006-01`.
**Do:** implement one automated test per case. `TC-SEC-006-01` must compare the two `404` bodies structurally.
**Test cases to implement:**
- `TC-FR-013-01` (API integration test) — optional metadata saved and retrieved
- `TC-FR-013-02` (API integration test) — optional metadata cleared to `null` and persisted
- `TC-FR-016-01` (API integration test) — draft becomes planned when a scheduled date is added
- `TC-FR-016-02` (API validation test) — draft→planned without a scheduled date rejected; record stays a draft
- `TC-FR-021-01` (API integration test) — retrieving an owned record returns its stored fields
- `TC-FR-022-01` (API integration test) — updating `location` persists
- `TC-FR-023-01` (API integration test) — delete returns `204`; a later `GET` returns `404`
- `TC-FR-023-02` (API integration test) — delete cascades to reminder and recurrence
- `TC-SEC-001-01` (API integration test) — unauthenticated `GET /api/v1/examinations/` returns `401`
- `TC-SEC-002-01` (API authorization test) — cross-user retrieve returns `404`
- `TC-SEC-002-02` (API authorization test) — cross-user update returns `404`; record unchanged
- `TC-SEC-002-03` (API authorization test) — cross-user delete returns `404`; record still exists
- `TC-SEC-006-01` (API integration test) — missing id and another user's id return identical `404` status and body structure
**Acceptance criteria:** all 13 pass; `TC-SEC-002-02/03` assert the target record's state afterwards, not only the status code.
**Verify with:** `cd backend && pytest -k "tc_fr_013 or tc_fr_016 or tc_fr_021 or tc_fr_022 or tc_fr_023_01 or tc_fr_023_02 or tc_sec_001_01 or tc_sec_002_0 or tc_sec_006_01" -v`
**Out of scope for this task:** `TC-FR-023-03` (source-occurrence null-out) — needs a generated occurrence; Task 14.3.
**On finishing:** commit.

#### Task 8.3 — Examination detail, edit, and delete confirmation UI
**Slice:** 8 — Examination detail, edit, and delete
**Depends on:** 7.7, 8.1
**Requirements:** FR-021, FR-022, FR-024   **Design decisions:** ADS-FR-024-01, ADS-UX-008-01, ADS-UX-007-01
**Read before starting:**
- `docs/design_specification.md` `ADS-FR-024-01` (a **modal** confirmation dialog; the destructive action executes neither on opening nor on cancellation, only on explicit confirmation), `ADS-UX-008-01` (focus-managed modal dialogs)
- `docs/user_flows.md` §12, §13, §15
**Do:**
1. Build the detail view, formatting all values through `src/format/datetime.ts` and `CategoryLabel`.
2. Reuse the Task 7.6 form for editing, submitting `PATCH`.
3. Build the delete confirmation modal: focus moves into the dialog on open and returns to the trigger on close; `Escape` cancels; cancel sends no request; confirm sends exactly one `DELETE`.
4. Invalidate the examination list query after a successful edit or delete.
**Test cases to implement:** none in this task (see 8.4).
**Acceptance criteria:** the dialog traps focus and is operable by keyboard alone; cancelling sends zero requests.
**Verify with:** `cd frontend && npm run test && npm run build`
**Out of scope for this task:** reminder or recurrence controls (Slices 11–13).
**On finishing:** commit.

#### Task 8.4 — Delete confirmation tests
**Slice:** 8 — Examination detail, edit, and delete
**Depends on:** 8.3
**Requirements:** FR-024   **Design decisions:** ADS-FR-024-01
**Read before starting:** `docs/test_specification.md` `TC-FR-024-01/02` — both assert **request counts**.
**Do:** implement both tests with MSW request counting.
**Test cases to implement:**
- `TC-FR-024-01` (Frontend integration test) — cancelling closes the dialog and sends no `DELETE`
- `TC-FR-024-02` (Frontend integration test) — confirming sends exactly one `DELETE`
**Acceptance criteria:** both pass and assert exact counts (`0` and `1`).
**Verify with:** `cd frontend && npx vitest run -t 'TC-FR-024'`
**Out of scope for this task:** backend delete behavior.
**On finishing:** commit. **Slice 8 complete:** squash-merge, `DEVELOPMENT_LOG.md` entry. `SEC-006` closes here.

---

### Slice 9 — List search, filters, and ordering

**Capability delivered:** a user searches their examinations by title, filters by status and category, and orders by scheduled date.

**Definition of Done:** both halves done; the 7 cases below pass; the full suite is green.

#### Task 9.1 — Search, filter, and ordering query parameters
**Slice:** 9 — List search, filters, and ordering
**Depends on:** 8.1
**Requirements:** FR-028, FR-029, FR-030   **Design decisions:** ADS-FR-028-01, ADS-FR-029-01, ADS-FR-030-01
**Read before starting:**
- `docs/api_contract.md` §9.1 (the supported-parameter table, AND semantics for `status`+`category`, **`400` for invalid filter or ordering values**, and: both ordering directions place `scheduled_date = null` **after** all dated records, with identifier as the stable secondary ordering)
- `docs/design_specification.md` `ADS-FR-028-01` (case-insensitive containment on `title`), `ADS-FR-029-01` (validate supplied values; AND semantics), `ADS-FR-030-01` (**explicit** null placement — not left to database default ordering — plus a stable secondary ordering by identifier)
- `docs/user_flows.md` §10 "Search, filter, and ordering flows"
**Do:**
1. Add `search`, `status`, `category`, `ordering` to the list endpoint, all applied to the owner-scoped queryset.
2. Validate each: an unsupported `status`, a nonexistent `category`, or an `ordering` value other than `scheduled_date`/`-scheduled_date` returns `400`.
3. Implement null placement **explicitly** — annotate a null-flag and sort on it first, then on `scheduled_date`, then on `id`. Do not rely on the backend database's default null handling: SQLite and PostgreSQL disagree, and development and production use different databases (D2). This is the concrete form of risk R6.
4. Regenerate `backend/openapi.yaml`.
**Test cases to implement:** none in this task (see 9.2).
**Acceptance criteria:** undated records come last in **both** directions; two records sharing a date come back in the same order on every request; `?status=archived` returns `400`.
**Verify with:** `cd backend && pytest -q && python manage.py spectacular --file openapi.yaml`
**Out of scope for this task:** `time_state` filters (Slice 10); pagination — excluded by `product_definition.md` §8 and `api_contract.md` §2.
**On finishing:** commit.

#### Task 9.2 — Backend search, filter, and ordering tests
**Slice:** 9 — List search, filters, and ordering
**Depends on:** 9.1
**Requirements:** FR-028, FR-029, FR-030   **Design decisions:** as Task 9.1
**Read before starting:** `docs/test_specification.md` `TC-FR-028-01`, `TC-FR-029-01/02/03`, `TC-FR-030-01/02/03`.
**Do:** implement one automated test per case. `TC-FR-030-03` requires repeating the request and asserting a stable relative order.
**Test cases to implement:**
- `TC-FR-028-01` (API integration test) — `?search=dental` returns only the matching title
- `TC-FR-029-01` (API integration test) — status filter
- `TC-FR-029-02` (API integration test) — category filter
- `TC-FR-029-03` (API integration test) — combined filters use AND semantics
- `TC-FR-030-01` (API integration test) — ascending order, undated last
- `TC-FR-030-02` (API integration test) — descending order, undated last
- `TC-FR-030-03` (API integration test) — same-date records tie-break by identifier, repeatably
**Acceptance criteria:** all 7 pass; `TC-FR-030-03` issues the request more than once.
**Verify with:** `cd backend && pytest -k "tc_fr_028 or tc_fr_029 or tc_fr_030" -v`
**Out of scope for this task:** frontend controls (Task 9.3).
**On finishing:** commit.

#### Task 9.3 — List search, filter, and ordering controls
**Slice:** 9 — List search, filters, and ordering
**Depends on:** 7.7, 9.1
**Requirements:** FR-028, FR-029, FR-030   **Design decisions:** ADS-FR-028-01, ADS-FR-029-01, ADS-FR-030-01, ADS-UX-008-01
**Read before starting:** `docs/user_flows.md` §10 "Search, filter, and ordering flows"; `docs/design_specification.md` `ADS-UX-008-01` (labelled controls, keyboard operability).
**Do:**
1. Add a title search input, status and category selects, and an ordering control to the list page; drive them through the query parameters from Task 9.1.
2. Keep the four page states from Task 7.7 correct while filters change — a filtered request that returns nothing shows the empty state, not the error state.
3. Every control has a visible, programmatically associated label.
**Test cases to implement:** none — the specification defines no frontend test case for these three requirements. The controls are still required for the slice to deliver a usable capability.
**Acceptance criteria:** each control changes the request; all are operable by keyboard alone.
**Verify with:** `cd frontend && npm run test && npm run build`
**Out of scope for this task:** past/upcoming/overdue views (Slice 10).
**On finishing:** commit. **Slice 9 complete:** squash-merge, `DEVELOPMENT_LOG.md` entry. `FR-028`, `FR-029`, `FR-030` close here.

---

### Slice 10 — Derived time states: past, upcoming, overdue

**Capability delivered:** a user reviews past, upcoming and overdue examinations, and the same record moves between them as time passes without anyone editing it.

**Definition of Done:** both halves done; the 19 cases below pass; the full suite is green.

#### Task 10.1 — Time-state queryset filters on the shared module
**Slice:** 10 — Derived time states: past, upcoming, overdue
**Depends on:** 7.3, 9.1
**Requirements:** FR-019 (partial), FR-031, FR-032, FR-033, FR-034   **Design decisions:** ADS-FR-019-01, ADS-FR-031-01, ADS-FR-032-01, ADS-FR-033-01, ADS-FR-033-02, ADS-FR-034-01
**Read before starting:**
- `docs/domain_model.md` §6.1, §6.2, §6.3 — the three collection definitions in pseudocode; these are the specification, read them character by character
- `docs/api_contract.md` §9.2, §9.3, §9.4, and the note in §9.1 explaining that the `time_state` **filter** vocabulary (`past`/`upcoming`/`overdue`) is deliberately separate from the `time_state` **response field** vocabulary (`upcoming`/`overdue`/`null`) — every record returned by `time_state=past` carries `time_state: null`
- `docs/design_specification.md` `ADS-FR-019-01` (**exclude drafts before applying date conditions**), `ADS-FR-031-01` (completed by `completed_date`, cancelled/missed by `scheduled_date`, both `<=` the local date), `ADS-FR-032-01`, `ADS-FR-034-01` (the overdue query **starts** from `status = planned`)
- §3.1 of this plan, bullets 1 and 3
**Do:**
1. Add `past_queryset`, `upcoming_queryset` and `overdue_queryset` to `examinations/time_state.py` — the module Task 7.3 created. They must express the same rule as `time_state_for`; do not restate the boundary logic anywhere else.
2. Every one of them takes the user's local date/time from `user_local_now(user)`.
3. Wire `?time_state=past|upcoming|overdue` into the list endpoint; an unsupported value returns `400`.
4. Regenerate `backend/openapi.yaml`.
**Test cases to implement:** none in this task (see 10.2).
**Acceptance criteria:** a draft with a past `scheduled_date` appears in no collection; a current-date planned record **without** `scheduled_time` is upcoming and not overdue; `overdue_queryset` returns nothing for any non-planned status regardless of dates; the three functions and `time_state_for` never disagree for the same record and clock.
**Verify with:** `cd backend && pytest -q && python manage.py spectacular --file openapi.yaml`
**Out of scope for this task:** the calendar `state` value (Slice 15) and `overdue_count` (Slice 16) — both consume these functions rather than reimplementing them.
**On finishing:** commit. See risk register R1.

#### Task 10.2 — Backend time-state tests
**Slice:** 10 — Derived time states: past, upcoming, overdue
**Depends on:** 10.1
**Requirements:** FR-019, FR-031, FR-032, FR-033, FR-034   **Design decisions:** as Task 10.1
**Read before starting:** `docs/test_specification.md` `TC-FR-019-01/02`, `TC-FR-031-01…06`, `TC-FR-032-01…05`, `TC-FR-033-01…05`, `TC-FR-034-01`. Every one of these freezes the user's local date or time — several to a specific hour (`2026-08-04T09:00`, `2026-08-04T11:00`, `2026-08-04T08:59`, `2026-08-04T09:01`). Use a **non-UTC** account timezone in at least one case so a UTC-versus-local error cannot pass unnoticed.
**Do:** implement one automated test per case through the clock service.
**Test cases to implement:**
- `TC-FR-019-01/02` (API integration tests) — dated drafts excluded from upcoming and from overdue
- `TC-FR-031-01…03` (API integration tests) — completed by completion date; cancelled and missed by scheduled date
- `TC-FR-031-04/05/06` (API integration tests) — planned, draft, and future-completed excluded from past
- `TC-FR-032-01…03` (API integration tests) — future date; current date without time; current date with an unpassed time
- `TC-FR-032-04/05` (API integration tests) — overdue and completed excluded from upcoming
- `TC-FR-033-01/02` (API integration tests) — past date is overdue; current date with a passed time is overdue
- `TC-FR-033-03/04` (API integration tests) — unpassed time and no time are not overdue
- `TC-FR-033-05` (API integration test) — the same unchanged record flips state across its boundary at `08:59` and `09:01`
- `TC-FR-034-01` (API integration test) — among past-dated records in all five statuses, only the planned one is overdue
**Acceptance criteria:** all 19 pass; `TC-FR-033-05` modifies no record between the two evaluations.
**Verify with:** `cd backend && pytest -k "tc_fr_019_01 or tc_fr_019_02 or tc_fr_031 or tc_fr_032 or tc_fr_033 or tc_fr_034" -v`
**Out of scope for this task:** `TC-FR-019-03` (calendar exclusion) — Task 15.2.
**On finishing:** commit.

#### Task 10.3 — Past, upcoming, and overdue views
**Slice:** 10 — Derived time states: past, upcoming, overdue
**Depends on:** 9.3, 10.1
**Requirements:** FR-031, FR-032, FR-033   **Design decisions:** ADS-FR-031-01, ADS-FR-032-01, ADS-FR-033-01
**Read before starting:** `docs/user_flows.md` §11 (all three flows plus "Derived-state refresh behavior").
**Do:**
1. Add past, upcoming and overdue views driven by `?time_state=`, reusing the list page's four states and record presentation.
2. Show the derived `time_state` on planned records; render nothing for records whose `time_state` is `null`.
3. Do not cache a derived state across a mount — the value comes from the server on each fetch, per `user_flows.md` §11.
**Test cases to implement:** none — the specification defines no frontend test case for these three requirements.
**Acceptance criteria:** each view issues the corresponding `time_state` request; all three reuse the same record component.
**Verify with:** `cd frontend && npm run test && npm run build`
**Out of scope for this task:** dashboard sections (Slice 16).
**On finishing:** commit. **Slice 10 complete:** squash-merge, `DEVELOPMENT_LOG.md` entry. `FR-031`, `FR-032`, `FR-033`, `FR-034` close here.

---

### Slice 11 — Reminders: configuration and due-date calculation

**Capability delivered:** a user sets a reminder a whole number of days before a planned examination, changes or disables it, and sees the computed due date — and the backend refuses every configuration the rules forbid.

**This is the second-largest slice (28 cases).** Tasks 11.1–11.3 are the backend half and end with a green suite — the natural stopping point if the work spans two sessions.

**Definition of Done:** both halves done; the 28 cases below pass; the full suite is green.

#### Task 11.1 — Reminder serializer, due-date calculation, and endpoints
**Slice:** 11 — Reminders: configuration and due-date calculation
**Depends on:** 8.1
**Requirements:** FR-035, FR-036, SEC-001, SEC-002   **Design decisions:** ADS-FR-035-01, ADS-FR-036-01, ADS-SEC-002-01, ADS-SEC-001-01
**Read before starting:**
- `docs/api_contract.md` §14 (the representation and its rule list), §14.1 (retrieve; **`404` when the examination is unavailable *or* has no reminder**), §14.2 (create, `201`, and: a second reminder cannot be created while one exists), §14.3 (update offset / disable / re-enable, `200`)
- `docs/design_specification.md` `ADS-FR-035-01` (at most one reminder; fields `examination`, positive integer `offset_days`, `due_date`, `is_active`, audit timestamps; operations limited to the examination owner), `ADS-FR-036-01` (**`due_date = scheduled_date - offset_days`** by calendar-date arithmetic, stored nullable, **recalculated whenever the scheduled date or the offset changes**, and **null when `scheduled_date` is absent**)
- `docs/domain_model.md` §3.4 (the same rules, as invariants)
**Do:**
1. Add the reminder serializer: writable `offset_days` (integer, strictly greater than zero, rejecting decimals and non-numerics) and `is_active`; read-only `id`, `examination`, `due_date`, `created_at`, `updated_at`.
2. Put the due-date calculation in one function used on reminder save **and** on examination save, so an examination's `scheduled_date` change recalculates it. Set it to `null` when `scheduled_date` is absent.
3. Add `GET`, `POST`, `PATCH` on `/api/v1/examinations/{id}/reminder/`, all authenticated, all resolving the examination from the owner-scoped queryset so an unavailable examination and a missing reminder both yield the same `404`.
4. Creating a second reminder for an examination that already has one is rejected.
5. Regenerate `backend/openapi.yaml`.
**Test cases to implement:** none in this task (see 11.3).
**Acceptance criteria:** `scheduled_date 2026-08-15` with `offset_days 7` gives `due_date 2026-08-08`; changing either value recalculates it; removing `scheduled_date` nulls it.
**Verify with:** `cd backend && pytest -q && python manage.py spectacular --file openapi.yaml`
**Out of scope for this task:** the status restriction (Task 11.2 — but **do not ship this task to `project/mvp` without it**); auto-deactivation (Slice 12); the due-reminders list (Slice 12).
**On finishing:** commit on the slice branch only.

#### Task 11.2 — The planned-only business rule
**Slice:** 11 — Reminders: configuration and due-date calculation
**Depends on:** 11.1
**Requirements:** FR-017, FR-035   **Design decisions:** ADS-FR-017-01, ADS-FR-035-02
**Read before starting:**
- `docs/design_specification.md` `ADS-FR-035-02` — the governing decision. Creation, offset updates and **reactivation** (`is_active: true`) are rejected whenever the examination's status is not `planned`, covering `completed`, `cancelled` and `missed` **in addition to** the `draft` case in `ADS-FR-017-01`. **Disabling an existing reminder remains allowed regardless of examination status.**
- `docs/api_contract.md` §14 (the same four rules restated)
- `docs/domain_model.md` §3.4 rules and §8 invariants
- §3.1 of this plan, bullet 4
**Do:**
1. Add `require_planned(examination)` to `examinations/validators.py`, raising a business-rule validation error (`400`, `non_field_errors` per `api_contract.md` §3.4) when the status is anything but `planned`.
2. Apply it to reminder creation, to any request changing `offset_days`, and to any request setting `is_active` to `true`. Do **not** apply it to a request setting `is_active` to `false`.
3. This same helper is reused by recurrence in Slice 13 — write it once, in the shared module.
**Test cases to implement:** none in this task (see 11.3).
**Acceptance criteria:** for each of `draft`, `completed`, `cancelled`, `missed`: create rejected, offset update rejected, reactivation rejected, disable **accepted**. For `planned`: all four accepted.
**Verify with:** `cd backend && pytest -q`
**Out of scope for this task:** recurrence (Slice 13).
**On finishing:** commit.

#### Task 11.3 — Backend reminder tests
**Slice:** 11 — Reminders: configuration and due-date calculation
**Depends on:** 11.2
**Requirements:** FR-017, FR-035, FR-036, SEC-001, SEC-002   **Design decisions:** as Tasks 11.1–11.2
**Read before starting:** `docs/test_specification.md` `TC-FR-017-01/02/03`, `TC-FR-035-01…19`, `TC-FR-036-01…04`, `TC-SEC-001-02`, `TC-SEC-002-04`. `TC-FR-035-08…19` form a 4-status × 3-operation matrix — parametrize it, but every one of the twelve must still carry its own `TC-*` id (one test case ↔ one automated test).
**Do:** implement one automated test per case.
**Test cases to implement:**
- `TC-FR-017-01/02/03` (API validation tests) — draft: create, offset update, reactivation all rejected
- `TC-FR-035-01/02/03` (API integration tests) — create on planned; update offset; disable while planned
- `TC-FR-035-04` (API integration test) — **disable succeeds while the examination is completed**
- `TC-FR-035-05/06/07` (API validation tests) — offset `0`, `-3`, `2.5` rejected
- `TC-FR-035-08/09/10` (API validation tests) — draft: create / offset update / reactivation rejected
- `TC-FR-035-11/12/13` (API validation tests) — completed: same three rejected
- `TC-FR-035-14/15/16` (API validation tests) — cancelled: same three rejected
- `TC-FR-035-17/18/19` (API validation tests) — missed: same three rejected
- `TC-FR-036-01` (API integration test) — `2026-08-15` minus 7 days is `2026-08-08`
- `TC-FR-036-02` (API integration test) — recalculated when the scheduled date changes
- `TC-FR-036-03` (API integration test) — recalculated when the offset changes
- `TC-FR-036-04` (API integration test) — `null` when the examination has no scheduled date
- `TC-SEC-001-02` (API integration test) — unauthenticated reminder request returns `401`
- `TC-SEC-002-04` (API authorization test) — cannot attach a reminder to another user's examination, with no disclosure
**Acceptance criteria:** all 28 pass; each rejection case also asserts the unchanged state its Then clause names (no reminder created, offset unchanged, still inactive).
**Verify with:** `cd backend && pytest -k "tc_fr_017 or tc_fr_035 or tc_fr_036 or tc_sec_001_02 or tc_sec_002_04" -v`
**Out of scope for this task:** `TC-FR-037-*` and `TC-FR-038-*` — Slice 12.
**On finishing:** commit. **Backend half of Slice 11 is complete here — a safe stopping point with a green suite.**

#### Task 11.4 — Reminder settings UI
**Slice:** 11 — Reminders: configuration and due-date calculation
**Depends on:** 8.3, 11.2
**Requirements:** FR-035, FR-036   **Design decisions:** ADS-FR-035-01, ADS-FR-035-02, ADS-FR-036-01
**Read before starting:** `docs/user_flows.md` §16 (enable/update, disable, and the failure behavior list).
**Do:**
1. Add reminder controls to the examination detail view: an `offset_days` number input, an enable/disable control, and the read-only computed `due_date` rendered through `formatCalendarDate`.
2. Show the controls for configuration only when the examination is `planned`; keep the disable control available in any status, matching the backend rule rather than second-guessing it.
3. Surface backend business-rule errors (`non_field_errors`) through the shared field-error component.
**Test cases to implement:** none — the specification defines no frontend test case for `FR-035` or `FR-036`.
**Acceptance criteria:** a positive offset on a planned examination creates the reminder and shows the returned `due_date`; a rejected configuration shows the backend's message.
**Verify with:** `cd frontend && npm run test && npm run build`
**Out of scope for this task:** the due-reminders area (Slice 12).
**On finishing:** commit. **Slice 11 complete:** squash-merge, `DEVELOPMENT_LOG.md` entry, set Phase 5 to `In progress`. `FR-017`, `FR-035`, `FR-036` close here.

---

### Slice 12 — Reminder lifecycle and the due-reminders view

**Capability delivered:** completing, cancelling, missing or un-planning an examination turns its reminder off; the user sees the reminders that have come due.

**Definition of Done:** both halves done; the 7 cases below pass; the full suite is green.

#### Task 12.1 — Automatic reminder deactivation on status change
**Slice:** 12 — Reminder lifecycle and the due-reminders view
**Depends on:** 8.1, 11.2
**Requirements:** FR-038   **Design decisions:** ADS-FR-038-01
**Read before starting:**
- `docs/design_specification.md` `ADS-FR-038-01` (changing from `planned` to `draft`/`completed`/`cancelled`/`missed` sets the reminder's `is_active` to `false` **within the same database transaction**; changing **to** `planned` does **not** reactivate)
- `docs/api_contract.md` §12 "Status-change side effects"
- `docs/domain_model.md` §9
- §3.1 of this plan, bullet 4
**Do:**
1. In the examination update path, detect a transition **from** `planned` to any other status and set the attached reminder inactive inside the same `transaction.atomic()` block as the examination save. A partial failure must leave neither change applied.
2. Add no reactivation logic on a transition **to** `planned`. This is a deliberate absence.
3. Deactivation is unconditional on the reminder's current state — deactivating an already-inactive reminder is a no-op, not an error.
**Test cases to implement:** none in this task (see 12.3).
**Acceptance criteria:** all four target statuses deactivate; returning to `planned` leaves `is_active` false; the recurrence rule (once Slice 13 exists) is untouched by any of this.
**Verify with:** `cd backend && pytest -q`
**Out of scope for this task:** the recurrence rule's own persistence across status changes (Slice 13).
**On finishing:** commit.

#### Task 12.2 — Due-reminders endpoint
**Slice:** 12 — Reminder lifecycle and the due-reminders view
**Depends on:** 11.1
**Requirements:** FR-037   **Design decisions:** ADS-FR-037-01
**Read before starting:**
- `docs/api_contract.md` §14.4 (`GET /api/v1/reminders/?state=due`; the exact condition `is_active = true AND due_date <= user's current local date`; a JSON array response)
- `docs/domain_model.md` §6.6
- `docs/design_specification.md` `ADS-FR-037-01` (filtering happens on the backend so every client shares one definition of "currently due")
- `docs/review_findings.md` `RF-19` — **its recorded trigger is "revisit when the due-reminder view is implemented", which is now.** Read the finding, then follow step 3 below.
**Do:**
1. Add `GET /api/v1/reminders/?state=due`, authenticated, restricted to reminders whose examination belongs to `request.user`, applying the documented condition with `user_local_date(user)`.
2. Regenerate `backend/openapi.yaml`.
3. **`RF-19` is now triggered.** `offset_days` has no upper bound, so a very large offset produces a `due_date` far in the past that is immediately and permanently due. Do **not** invent a bound — that is a spec change, and `api_contract.md` §14, `ADS-FR-035-01` and `FR-035` all define the field as "a positive whole number" with no maximum. Report to the owner that the trigger has fired, with a one-paragraph description of the observed behavior, and continue with the unbounded field as specified.
**Test cases to implement:** none in this task (see 12.3).
**Acceptance criteria:** the response contains only active reminders due on or before the user's local date; another user's due reminders never appear.
**Verify with:** `cd backend && pytest -q && python manage.py spectacular --file openapi.yaml`
**Out of scope for this task:** deciding `RF-19`.
**On finishing:** commit; record the `RF-19` escalation in the day's `DEVELOPMENT_LOG.md` entry under Problems and Blockers.

#### Task 12.3 — Backend reminder lifecycle and due-query tests
**Slice:** 12 — Reminder lifecycle and the due-reminders view
**Depends on:** 12.1, 12.2
**Requirements:** FR-037, FR-038   **Design decisions:** as Tasks 12.1–12.2
**Read before starting:** `docs/test_specification.md` `TC-FR-037-02`, `TC-FR-038-01…05`.
**Do:** implement one automated test per case.
**Test cases to implement:**
- `TC-FR-037-02` (API integration test) — the due filter returns only the due, active reminder among a due-active, a future-active and a due-inactive fixture
- `TC-FR-038-01` (API integration test) — planned → draft deactivates
- `TC-FR-038-02` (API integration test) — planned → completed deactivates
- `TC-FR-038-03` (API integration test) — planned → cancelled deactivates
- `TC-FR-038-04` (API integration test) — planned → missed deactivates
- `TC-FR-038-05` (API integration test) — returning to planned does **not** reactivate
**Acceptance criteria:** all 6 pass; the four deactivation cases assert the change happened as part of the same update, not through a later request.
**Verify with:** `cd backend && pytest -k "tc_fr_037_02 or tc_fr_038" -v`
**Out of scope for this task:** `TC-FR-037-01` (frontend) — Task 12.4.
**On finishing:** commit.

#### Task 12.4 — Due-reminders area and its test
**Slice:** 12 — Reminder lifecycle and the due-reminders view
**Depends on:** 11.4, 12.2
**Requirements:** FR-037   **Design decisions:** ADS-FR-037-01
**Read before starting:** `docs/user_flows.md` §17; `docs/test_specification.md` `TC-FR-037-01` (the fixture is three reminders — due-active, future-active, due-inactive — and only the first may render).
**Do:**
1. Build the due-reminders area consuming `GET /api/v1/reminders/?state=due`, rendering each reminder's examination title and `due_date` through `formatCalendarDate`.
2. Render only what the endpoint returns — do not re-filter client-side; the backend is the single definition of "due".
3. Implement the test.
**Test cases to implement:** `TC-FR-037-01` (Frontend integration test) — only the due active reminder is displayed.
**Acceptance criteria:** the test passes and asserts the **absence** of the other two fixtures.
**Verify with:** `cd frontend && npx vitest run -t 'TC-FR-037-01'`
**Out of scope for this task:** dashboard placement (Slice 16).
**On finishing:** commit. **Slice 12 complete:** squash-merge, `DEVELOPMENT_LOG.md` entry. `FR-037` and `FR-038` close here.

---

### Slice 13 — Recurrence rules

**Capability delivered:** a user sets a monthly, six-month or yearly recurrence on a planned examination and sees the calculated next due date, including at month ends and across leap years.

**Definition of Done:** both halves done; the 20 cases below pass; the full suite is green.

#### Task 13.1 — Recurrence serializer, endpoints, and the planned-only rule
**Slice:** 13 — Recurrence rules
**Depends on:** 8.1, 11.2
**Requirements:** FR-018, FR-039, SEC-001, SEC-002   **Design decisions:** ADS-FR-018-01, ADS-FR-039-01, ADS-FR-039-02, ADS-SEC-002-01, ADS-SEC-001-01
**Read before starting:**
- `docs/api_contract.md` §15 (the representation; an existing rule **remains attached** when the status changes; creation and update allowed **only** while planned), §15.1 (retrieve; `404` when the examination is unavailable or has no rule), §15.2 (create, `201`, the three accepted intervals, and: the source must be planned **and** have a `scheduled_date`), §15.3 (update, `200`)
- `docs/design_specification.md` `ADS-FR-039-01` (at most one rule; the interval constrained to the three values; **every other interval and every non-planned source rejected**), `ADS-FR-039-02` (a status change never deletes or modifies the rule), `ADS-FR-018-01`
- `docs/domain_model.md` §3.5
- §3.1 of this plan, bullet 4
**Do:**
1. Add the recurrence serializer: writable `interval` constrained to `monthly`/`six_months`/`yearly`; read-only `id`, `examination`, `next_due_date`, `created_at`, `updated_at`.
2. Add `GET`, `POST`, `PATCH` on `/api/v1/examinations/{id}/recurrence/`, all authenticated, all resolving the examination from the owner-scoped queryset.
3. Apply `require_planned` from Task 11.2 to create **and** update. Retrieval stays allowed in any status — a retained rule must remain readable.
4. Add nothing to the examination update path: an existing rule is untouched by a status change because no code touches it.
5. Regenerate `backend/openapi.yaml`.
**Test cases to implement:** none in this task (see 13.3).
**Acceptance criteria:** `weekly` is rejected with an `interval` error; create is rejected for each of the four non-planned statuses; a rule survives a status change with its interval unchanged and stays retrievable.
**Verify with:** `cd backend && pytest -q && python manage.py spectacular --file openapi.yaml`
**Out of scope for this task:** next-occurrence creation (Slice 14); advanced recurrence patterns — excluded by `product_definition.md` §8.
**On finishing:** commit.

#### Task 13.2 — Calendar-month arithmetic with last-valid-day clamping
**Slice:** 13 — Recurrence rules
**Depends on:** 13.1
**Requirements:** FR-040   **Design decisions:** ADS-FR-040-01, ADS-FR-040-02
**Read before starting:**
- `docs/design_specification.md` `ADS-FR-040-01` (add one month / six months / one year in **calendar** arithmetic; **when the target month lacks the source day, use the target month's last valid day**; leap-day yearly recurrence therefore lands on the last valid February day in a non-leap year), `ADS-FR-040-02` (`next_due_date` is `null` when the source has no `scheduled_date`)
- `docs/domain_model.md` §6.7
- `docs/api_contract.md` §15 (`next_due_date` is read-only)
**Do:**
1. Add `examinations/recurrence_math.py` with `next_due_date(scheduled_date, interval) -> date | None`. Implement month addition by advancing year/month arithmetically and clamping the day to the target month's length. **Do not add a fixed number of days**, and do not reach for a date library's "add months" that rolls over into the following month — `2026-01-31` plus one month is `2026-02-28`, not `2026-03-03`.
2. Return `None` when `scheduled_date` is `None`.
3. Expose it as the serializer's `next_due_date`. Slice 14 calls the same function — there is exactly one implementation.
**Test cases to implement:** none in this task (see 13.3).
**Acceptance criteria:** `2026-03-15` monthly → `2026-04-15`; six-month → `2026-09-15`; yearly → `2027-03-15`; `2026-01-31` monthly → `2026-02-28`; `2028-02-29` yearly → `2029-02-28`; no scheduled date → `null`.
**Verify with:** `cd backend && pytest -q`
**Out of scope for this task:** occurrence creation (Slice 14).
**On finishing:** commit. See risk register R3.

#### Task 13.3 — Backend recurrence tests
**Slice:** 13 — Recurrence rules
**Depends on:** 13.2
**Requirements:** FR-018, FR-039, FR-040, SEC-001, SEC-002   **Design decisions:** as Tasks 13.1–13.2
**Read before starting:** `docs/test_specification.md` `TC-FR-018-01/02`, `TC-FR-039-01…10`, `TC-FR-040-01…06`, `TC-SEC-001-03`, `TC-SEC-002-05`. The dates in `TC-FR-040-04` and `TC-FR-040-05` are the specification, not examples — use them exactly.
**Do:** implement one automated test per case.
**Test cases to implement:**
- `TC-FR-018-01/02` (API validation tests) — draft: create and update rejected; the existing interval is unchanged
- `TC-FR-039-01/02/03` (API validation tests) — `monthly`, `six_months`, `yearly` accepted on a planned source
- `TC-FR-039-04` (API validation test) — `weekly` rejected with an `interval` error
- `TC-FR-039-05/06/07/08` (API validation tests) — creation rejected for draft, completed, cancelled, missed sources
- `TC-FR-039-09` (API integration test) — the rule survives a status change to completed, unchanged
- `TC-FR-039-10` (API validation test) — update rejected once no longer planned; interval remains `monthly`
- `TC-FR-040-01/02/03` (API integration tests) — the three intervals from `2026-03-15`
- `TC-FR-040-04` (API integration test) — `2026-01-31` monthly → `2026-02-28`
- `TC-FR-040-05` (API integration test) — `2028-02-29` yearly → `2029-02-28`
- `TC-FR-040-06` (API integration test) — `null` when the source has no scheduled date
- `TC-SEC-001-03` (API integration test) — unauthenticated recurrence request returns `401`
- `TC-SEC-002-05` (API authorization test) — cannot attach a rule to another user's examination
**Acceptance criteria:** all 20 pass.
**Verify with:** `cd backend && pytest -k "tc_fr_018 or tc_fr_039 or tc_fr_040 or tc_sec_001_03 or tc_sec_002_05" -v`
**Out of scope for this task:** `TC-FR-041-*` — Slice 14.
**On finishing:** commit.

#### Task 13.4 — Recurrence settings UI
**Slice:** 13 — Recurrence rules
**Depends on:** 11.4, 13.2
**Requirements:** FR-039, FR-040   **Design decisions:** ADS-FR-039-01, ADS-FR-040-01, ADS-FR-040-02
**Read before starting:** `docs/user_flows.md` §18 (the flow and its failure behavior, including: an existing rule stays **retrievable** but not modifiable while the examination is non-planned).
**Do:**
1. Add recurrence controls to the examination detail view: an interval select limited to the three values, and the read-only `next_due_date` rendered through `formatCalendarDate`.
2. Show the rule in any status; allow editing it only while the examination is planned.
3. Render `next_due_date: null` as an explicit "not available" state rather than a blank.
**Test cases to implement:** none — the specification defines no frontend test case for `FR-039` or `FR-040`.
**Acceptance criteria:** the select offers exactly three options; a retained rule on a completed examination is visible and not editable.
**Verify with:** `cd frontend && npm run test && npm run build`
**Out of scope for this task:** the next-occurrence action (Slice 14).
**On finishing:** commit. **Slice 13 complete:** squash-merge, `DEVELOPMENT_LOG.md` entry. `FR-018`, `FR-039`, `FR-040`, `SEC-002` close here.

---

### Slice 14 — Next occurrence

**Capability delivered:** a user creates the next occurrence of a recurring examination, once — and a second click returns the same record rather than a duplicate.

**Definition of Done:** both halves done; the 8 cases below pass; the full suite is green.

#### Task 14.1 — Idempotent next-occurrence endpoint
**Slice:** 14 — Next occurrence
**Depends on:** 13.2
**Requirements:** FR-041, FR-023   **Design decisions:** ADS-FR-041-01, ADS-FR-041-02, ADS-FR-041-03, ADS-FR-041-04, ADS-FR-023-02
**Read before starting:**
- `docs/api_contract.md` §16 — the preconditions (owned, status in planned/completed/cancelled/missed, has `scheduled_date`, has a recurrence rule; a `draft` source is `400`), the **field-value table for the generated examination** (which fields are copied, which are set, which are left `null`), the statement that no reminder and no recurrence rule is created for it, and the `201`-then-`200` repeated-request contract
- `docs/design_specification.md` `ADS-FR-041-01` (runs in a transaction; records the source occurrence so a repeat cannot duplicate), `ADS-FR-041-03` (**a repeat resolving to an existing occurrence for the same source and calculated due date returns `200 OK` with that existing record; only the first creation returns `201 Created`**), `ADS-FR-041-04` (the exact copied/empty field set and why), `ADS-FR-041-02` (accepted source statuses)
- `docs/user_flows.md` §19
- §3.1 of this plan, bullet 5
**Do:**
1. Add `POST /api/v1/examinations/{id}/next-occurrence/`, authenticated, resolving the source from the owner-scoped queryset.
2. Validate the preconditions; reject a `draft` source with `400`.
3. Compute the due date through `recurrence_math.next_due_date` from Task 13.2 — do not reimplement it.
4. Inside `transaction.atomic()`, look for an existing examination with `source_occurrence = source` **and** `scheduled_date = calculated due date`. If one exists, return it with `200`. Otherwise create one and return `201`. **The idempotency key is the pair, not the source alone** — a source whose date later changes can legitimately produce a second, different occurrence.
5. Set the generated record's fields exactly as the §16 table specifies: copy `title`, `category`, `medical_specialty`, `scheduled_time`, `location`; set `status = planned`, `scheduled_date =` the calculated date, `source_occurrence =` the source; leave `notes` and `completed_date` empty; create no reminder and no recurrence rule.
6. Regenerate `backend/openapi.yaml`.
**Test cases to implement:** none in this task (see 14.3).
**Acceptance criteria:** the first call returns `201`, the second `200` with the same `id`, and exactly one record exists; a draft source returns `400` and creates nothing.
**Verify with:** `cd backend && pytest -q && python manage.py spectacular --file openapi.yaml`
**Out of scope for this task:** generating more than one occurrence — `product_definition.md` §8 excludes unlimited generation, and §10.8 requires one at a time on explicit request.
**On finishing:** commit. See risk register R3.

#### Task 14.2 — Next-occurrence action in the UI
**Slice:** 14 — Next occurrence
**Depends on:** 13.4, 14.1
**Requirements:** FR-041   **Design decisions:** ADS-FR-041-01, ADS-FR-041-03
**Read before starting:** `docs/user_flows.md` §19 (including step 10 — a repeat receives the existing occurrence) and its failure behavior.
**Do:**
1. Add a "create next occurrence" action to the examination detail view, shown when the examination has a recurrence rule, a `scheduled_date`, and a non-draft status.
2. Treat `200` and `201` as the same success path from the user's point of view; do not present a repeat as an error.
3. Invalidate the examination list query afterwards so the new occurrence appears.
**Test cases to implement:** none — the specification defines no frontend test case for `FR-041`.
**Acceptance criteria:** the action is absent for a draft source; a double click produces one record and no error.
**Verify with:** `cd frontend && npm run test && npm run build`
**Out of scope for this task:** calendar or dashboard placement of the new record (Slices 15–16).
**On finishing:** commit.

#### Task 14.3 — Backend next-occurrence tests
**Slice:** 14 — Next occurrence
**Depends on:** 14.1
**Requirements:** FR-041, FR-023   **Design decisions:** as Task 14.1
**Read before starting:** `docs/test_specification.md` `TC-FR-041-01…07`, `TC-FR-023-03`.
**Do:** implement one automated test per case.
**Test cases to implement:**
- `TC-FR-041-01` (API integration test) — `201`, exactly one new planned record at the calculated date
- `TC-FR-041-02/03/04` (API integration tests) — accepted from completed, cancelled, missed sources
- `TC-FR-041-05` (API validation test) — draft source returns `400`; nothing created
- `TC-FR-041-06` (API integration test) — a repeat returns `200` with the same record; no second row
- `TC-FR-041-07` (API integration test) — every copied field, the planned status, the calculated date, the recorded source, empty `notes`/`completed_date`, and **no** reminder or recurrence rule
- `TC-FR-023-03` (API integration test) — deleting the source leaves the generated occurrence retrievable with `source_occurrence: null`
**Acceptance criteria:** all 8 pass; `TC-FR-041-06` asserts the database row count, not only the response.
**Verify with:** `cd backend && pytest -k "tc_fr_041 or tc_fr_023_03" -v`
**Out of scope for this task:** frontend assertions.
**On finishing:** commit. **Slice 14 complete:** squash-merge, `DEVELOPMENT_LOG.md` entry. `FR-023` and `FR-041` close here.

---

### Slice 15 — Monthly calendar

**Capability delivered:** a user browses a month and sees each examination on the date its status defines, with a distinguishable indicator per state.

**Definition of Done:** both halves done; the 16 cases below pass; the full suite is green.

#### Task 15.1 — Calendar endpoint with range validation and derived state
**Slice:** 15 — Monthly calendar
**Depends on:** 10.1
**Requirements:** FR-019, FR-042, FR-043, SEC-001   **Design decisions:** ADS-FR-042-01, ADS-FR-042-02, ADS-FR-043-01, ADS-FR-019-01, ADS-SEC-001-01
**Read before starting:**
- `docs/api_contract.md` §17 — the entry representation (`calendar_date`, `state`, and the nested examination subset), the placement rules, and: **`state` is one of `planned`/`completed`/`cancelled`/`missed`/`overdue`, and a planned record satisfying the overdue rule uses `overdue`**
- `docs/design_specification.md` `ADS-FR-042-01` (planned/cancelled/missed on `scheduled_date`, completed on `completed_date`; drafts and records lacking their required display date excluded), `ADS-FR-042-02` (**both** parameters required, `YYYY-MM-DD`, rejected when either is missing or malformed or when `start_date` is later than `end_date`), `ADS-FR-019-01`
- `docs/domain_model.md` §6.5
- `docs/review_findings.md` `RF-16` — read it; step 4 below applies
**Do:**
1. Add `GET /api/v1/calendar/`, authenticated, on the owner-scoped queryset.
2. Validate `start_date` and `end_date`: both required, both `YYYY-MM-DD`, `start_date <= end_date`. Any violation is a `400`.
3. Build entries by status-specific display date, excluding drafts and any record missing the date its status requires. Derive `state` from `examinations/time_state.py` — a planned record that the overdue rule matches gets `overdue`, everything else gets its stored status. Do not write a second overdue rule here.
4. **`RF-16` is partly triggered:** the calendar range has no maximum span, so a caller-chosen range grows the response without bound. Do not impose a cap — `ADS-FR-042-02` defines exactly three validations and adding a fourth is a spec change. Report to the owner that the calendar half of `RF-16`'s trigger has been reached, and continue as specified.
5. Regenerate `backend/openapi.yaml`.
**Test cases to implement:** none in this task (see 15.2).
**Acceptance criteria:** a completed record with no `completed_date` is absent; a draft inside the range is absent; a past-dated planned record has `state: "overdue"`; each of the three invalid range conditions returns `400`.
**Verify with:** `cd backend && pytest -q && python manage.py spectacular --file openapi.yaml`
**Out of scope for this task:** deciding `RF-16`.
**On finishing:** commit; record the `RF-16` escalation in the day's `DEVELOPMENT_LOG.md` entry.

#### Task 15.2 — Backend calendar tests
**Slice:** 15 — Monthly calendar
**Depends on:** 15.1
**Requirements:** FR-019, FR-042, SEC-001   **Design decisions:** as Task 15.1
**Read before starting:** `docs/test_specification.md` `TC-FR-042-05/06/07/08/09`, `TC-FR-019-03`, `TC-SEC-001-04`.
**Do:** implement one automated test per case.
**Test cases to implement:**
- `TC-FR-019-03` (API integration test) — a dated draft inside the range is absent
- `TC-FR-042-05` (API integration test) — a draft record is excluded
- `TC-FR-042-06` (API integration test) — a completed record without `completed_date` is excluded
- `TC-FR-042-07` (API integration test) — only one of the two range parameters supplied is rejected
- `TC-FR-042-08` (API integration test) — a malformed date is rejected
- `TC-FR-042-09` (API integration test) — `start_date` later than `end_date` is rejected
- `TC-SEC-001-04` (API integration test) — unauthenticated calendar request returns `401`
**Acceptance criteria:** all 7 pass; the three rejection cases assert that **no calendar data** is returned, as their Then clauses require.
**Verify with:** `cd backend && pytest -k "tc_fr_019_03 or tc_fr_042_0 or tc_sec_001_04" -v`
**Out of scope for this task:** the four placement cases and the five indicator cases — those are frontend; Task 15.4.
**On finishing:** commit.

#### Task 15.3 — Monthly calendar view with state indicators
**Slice:** 15 — Monthly calendar
**Depends on:** 10.3, 15.1
**Requirements:** FR-042, FR-043   **Design decisions:** ADS-FR-042-01, ADS-FR-043-01, ADS-UX-008-01
**Read before starting:**
- `docs/design_specification.md` `ADS-FR-043-01` (each of the five states maps to a **distinct combination of label, icon or shape, and styling**; **colour is not the sole differentiator**)
- `docs/user_flows.md` §20 steps 7–8
- `docs/product_definition.md` §6.5
**Do:**
1. Build the monthly calendar, requesting the selected month's inclusive range from `GET /api/v1/calendar/`.
2. Place each entry on its `calendar_date`, formatted through `formatCalendarDate` — never through a `Date` that could shift it.
3. Give each of the five states a semantic text label **and** a non-colour indicator (icon or shape). A reviewer must be able to tell them apart in greyscale.
4. Add month navigation; every control is keyboard-operable.
**Test cases to implement:** none in this task (see 15.4).
**Acceptance criteria:** the five states are distinguishable with colour removed; entries land on the documented date for their status.
**Verify with:** `cd frontend && npm run test && npm run build`
**Out of scope for this task:** dashboard (Slice 16).
**On finishing:** commit.

#### Task 15.4 — Frontend calendar tests
**Slice:** 15 — Monthly calendar
**Depends on:** 15.3
**Requirements:** FR-042, FR-043   **Design decisions:** as Task 15.3
**Read before starting:** `docs/test_specification.md` `TC-FR-042-01/02/03/04`, `TC-FR-043-01…05`. Each `TC-FR-043-*` requires a **semantic label and a non-colour indicator distinguishing it from every other state** — assert both, and assert distinctness against the other four.
**Do:** implement one Vitest/RTL test per case.
**Test cases to implement:**
- `TC-FR-042-01/02/03` (Frontend integration tests) — planned, cancelled, missed on `scheduled_date`
- `TC-FR-042-04` (Frontend integration test) — completed on `completed_date`
- `TC-FR-043-01…05` (Frontend component tests) — planned, completed, cancelled, missed, overdue each render a distinct label and non-colour indicator
**Acceptance criteria:** all 9 pass; the five indicator tests fail if two states are given the same indicator.
**Verify with:** `cd frontend && npx vitest run -t 'TC-FR-042-0' && npx vitest run -t 'TC-FR-043'`
**Out of scope for this task:** the documented responsive review — Slice 17.
**On finishing:** commit. **Slice 15 complete:** squash-merge, `DEVELOPMENT_LOG.md` entry, set Phase 6 to `In progress`. `FR-019`, `FR-042`, `FR-043` close here.

---

### Slice 16 — Dashboard

**Capability delivered:** a user opens the dashboard and sees upcoming, overdue and recently completed examinations alongside status, category, uncategorized and overdue counts.

**Definition of Done:** both halves done; the 15 cases below pass; the full suite is green.

#### Task 16.1 — Dashboard endpoint
**Slice:** 16 — Dashboard
**Depends on:** 10.1, 15.1
**Requirements:** FR-044, FR-045, FR-046, FR-047, SEC-001   **Design decisions:** ADS-FR-044-01, ADS-FR-044-02, ADS-FR-044-03, ADS-FR-044-04, ADS-FR-045-01, ADS-FR-046-01, ADS-FR-047-01, ADS-SEC-001-01
**Read before starting:**
- `docs/api_contract.md` §18 — the complete response shape and its rule list, in particular: `upcoming` and `overdue` use **the same shared calculation** as the corresponding `time_state` filters; `recently_completed` is `completed_date >= local date - 29 days` and `<= local date`; ordered by `completed_date` descending then `id` descending; **filtered and ordered before** the five-record limit; not paginated; `status_counts` always carries all five keys including zeros; `category_counts` carries every system category including zeros; `uncategorized_count` counts null categories; `overdue_count` equals the shared overdue query's row count
- `docs/design_specification.md` `ADS-FR-044-02` (the inclusive 30-date window), `ADS-FR-044-03` (ordering), `ADS-FR-044-04` (the limit applied last), `ADS-FR-047-01` (**the same shared overdue query, not duplicated logic**)
- `docs/domain_model.md` §6.4 (including why the upper bound is retained defensively)
**Do:**
1. Add `GET /api/v1/dashboard/`, authenticated, owner-scoped.
2. Build `upcoming` and `overdue` by calling `upcoming_queryset` and `overdue_queryset` from `examinations/time_state.py`. Build `overdue_count` from the **same** call. There must be no second overdue expression anywhere in the codebase.
3. Build `recently_completed`: filter, then order by `-completed_date, -id`, then slice to five. Keep the upper-bound condition even though validation already rejects future completion dates — `domain_model.md` §6.4 calls for it explicitly.
4. Build `status_counts` zero-filled across all five statuses, `category_counts` zero-filled across all eight categories, and `uncategorized_count`.
5. Regenerate `backend/openapi.yaml`.
**Test cases to implement:** none in this task (see 16.2).
**Acceptance criteria:** with six eligible completions, exactly the five most recent are returned; a status and a category with no records still appear with `0`; `overdue_count` equals `len(dashboard['overdue'])` for the same clock.
**Verify with:** `cd backend && pytest -q && python manage.py spectacular --file openapi.yaml`
**Out of scope for this task:** pagination of any collection — excluded by `api_contract.md` §18 and `product_definition.md` §8.
**On finishing:** commit. See risk register R1.

#### Task 16.2 — Backend dashboard tests
**Slice:** 16 — Dashboard
**Depends on:** 16.1
**Requirements:** FR-044, FR-045, FR-046, FR-047, SEC-001   **Design decisions:** as Task 16.1
**Read before starting:** `docs/test_specification.md` `TC-FR-044-01…09`, `TC-FR-045-01`, `TC-FR-046-01/02`, `TC-FR-047-01`, `TC-SEC-001-05`. The boundary dates in `TC-FR-044-04` (`2026-07-06`, included) and `TC-FR-044-06` (`2026-07-05`, excluded) are the specification — an off-by-one here is exactly what they exist to catch.
**Do:** implement one automated test per case, freezing the user's local date at `2026-08-04` where the case specifies it.
**Test cases to implement:**
- `TC-FR-044-01` (API integration test) — dashboard `upcoming` matches the separate upcoming query
- `TC-FR-044-02` (API integration test) — dashboard `overdue` matches the separate overdue query
- `TC-FR-044-03` (API integration test) — an eligible record appears in `recently_completed`
- `TC-FR-044-04` (API integration test) — 29 days earlier is included
- `TC-FR-044-05` (API integration test) — today is included
- `TC-FR-044-06` (API integration test) — 30 days earlier is excluded
- `TC-FR-044-07` (API integration test) — ordered by completion date descending
- `TC-FR-044-08` (API integration test) — same-date ties by `id` descending
- `TC-FR-044-09` (API integration test) — limited to five, no pagination metadata
- `TC-FR-045-01` (API integration test) — all five status keys, correct and zero-filled
- `TC-FR-046-01` (API integration test) — every category present, zero-filled
- `TC-FR-046-02` (API integration test) — `uncategorized_count` is `2`
- `TC-FR-047-01` (API integration test) — `overdue_count` equals the overdue query's row count
- `TC-SEC-001-05` (API integration test) — unauthenticated dashboard request returns `401`
**Acceptance criteria:** all 14 pass; `TC-FR-044-01/02` and `TC-FR-047-01` compare against a live second request rather than a hard-coded expectation.
**Verify with:** `cd backend && pytest -k "tc_fr_044 or tc_fr_045 or tc_fr_046 or tc_fr_047 or tc_sec_001_05" -v`
**Out of scope for this task:** `TC-FR-044-10` (frontend section rendering) — Task 16.3.
**On finishing:** commit.

#### Task 16.3 — Dashboard page and its test
**Slice:** 16 — Dashboard
**Depends on:** 15.3, 16.1
**Requirements:** FR-044, FR-045, FR-046, FR-047   **Design decisions:** ADS-FR-044-01, ADS-FR-045-01, ADS-FR-046-01, ADS-FR-047-01
**Read before starting:**
- `docs/design_specification.md` `ADS-FR-044-01` (one section per collection, **each with its own loading-independent empty presentation**)
- `docs/user_flows.md` §21
- `docs/test_specification.md` `TC-FR-044-10` (an empty `overdue` beside populated `upcoming` and `recently_completed`; only the overdue section shows its empty presentation)
**Do:**
1. Build the dashboard from a single `GET /api/v1/dashboard/` request.
2. Render three record sections, each with its own empty presentation, plus the status counts, category counts, uncategorized count and overdue count.
3. Reuse the record component, `CategoryLabel` and `src/format/datetime.ts`. Add the due-reminders area from Task 12.4 if the design places it here.
4. Implement `TC-FR-044-10`.
**Test cases to implement:** `TC-FR-044-10` (Frontend integration test) — one empty section renders its empty presentation while the other two render records.
**Acceptance criteria:** the test passes; zero-valued counts render as `0` rather than being omitted.
**Verify with:** `cd frontend && npx vitest run -t 'TC-FR-044-10'`
**Out of scope for this task:** the responsive and input-method reviews — Slice 17.
**On finishing:** commit. **Slice 16 complete:** squash-merge, `DEVELOPMENT_LOG.md` entry, set Phase 4, 5 and 6 to `Completed`. `FR-044`, `FR-045`, `FR-046`, `FR-047` and `SEC-001` close here.

---

### Slice 17 — Cross-cutting UX review

**Capability delivered:** every primary page works at phone, tablet and desktop widths, and every primary action works by touch, mouse and keyboard.

These six cases are `Documented review` — manual, recorded reviews, not automated tests. They cannot be executed earlier because they exercise all six primary pages, and the calendar and dashboard only exist from Slice 16.

**Definition of Done:** both review artifacts exist with a stated verdict, every defect they record is either fixed or escalated, and the full suite is still green.

#### Task 17.1 — Responsive review at the approved viewport widths
**Slice:** 17 — Cross-cutting UX review
**Depends on:** 16.3
**Requirements:** UX-001   **Design decisions:** ADS-UX-001-01, ADS-UX-001-02
**Read before starting:**
- `docs/requirements_specification.md` `UX-001` (the six pages named: registration, login, examination list, examination form, calendar, dashboard)
- `docs/design_specification.md` `ADS-UX-001-01` (mobile-first base styles with explicit tablet and desktop enhancements; **no horizontal page scrolling** at the approved widths; the review records any overflow or unusable control)
- `docs/design_specification.md` `ADS-UX-001-02` — **the approved widths: 320 CSS pixels phone, 768 tablet, 1280 desktop.** 320 is the narrowest *supported* viewport, deliberately not a representative one; each review artifact records the width it used
- `docs/user_flows.md` §24
- `docs/test_specification.md` `TC-UX-001-01/02/03`
**Do:**
1. Set the browser viewport to each approved width in turn: **320 CSS pixels (phone), 768 (tablet), 1280 (desktop)** — `ADS-UX-001-02`. These three are exactly what `UX-001`, `ADS-UX-001-01` and `TC-UX-001-01/02/03` mean by "approved"; do not substitute others. Expect 320 to be the width that finds defects — it is chosen as the strict floor, so a page that overflows only there is a real failure, not a false positive.
2. Review all six pages at each width. Record for each page/width: horizontal scrolling present or absent, and any control that is unusable.
3. Fix the layout defects you find. A defect that would require changing documented behavior is escalated, not fixed.
4. Write `docs/reviews/TC-UX-001-01-phone.md`, `-02-tablet.md`, `-03-desktop.md` — each with the non-normative standing line, the date, the width used, a per-page table, and a verdict.
**Test cases to implement:**
- `TC-UX-001-01` (Documented review) — phone width
- `TC-UX-001-02` (Documented review) — tablet width
- `TC-UX-001-03` (Documented review) — desktop width
**Acceptance criteria:** three artifacts exist, each covering all six pages at its width with an explicit verdict; no page requires horizontal scrolling at any of the three.
**Verify with:** `npm run dev` in `frontend/`, then set the viewport to 320, 768 and 1280 CSS pixels in turn and walk all six pages at each. Re-run `npm run test` after any fix.
**Out of scope for this task:** input-method review (Task 17.2).
**On finishing:** commit.

#### Task 17.2 — Input-method and accessibility review
**Slice:** 17 — Cross-cutting UX review
**Depends on:** 17.1
**Requirements:** UX-008   **Design decisions:** ADS-UX-008-01
**Read before starting:**
- `docs/requirements_specification.md` `UX-008` (primary navigation, forms, dialogs and examination actions)
- `docs/design_specification.md` `ADS-UX-008-01` (semantic interactive elements, visible keyboard focus, correctly labelled controls, focus-managed modal dialogs, practical touch targets; **no primary action may depend exclusively on hover, pointer gestures, or colour**)
- `docs/user_flows.md` §24
- `docs/test_specification.md` `TC-UX-008-01/02/03` — note that `-03` additionally requires **visible keyboard focus at each step**
**Do:**
1. Enumerate the primary actions: navigate, register, log in, log out, create a draft, create a planned examination, edit, delete (including the confirmation dialog), configure and disable a reminder, configure recurrence, create a next occurrence, change month in the calendar, change the account timezone, change the password.
2. Complete each with touch, then mouse, then keyboard alone. For keyboard, confirm focus is visible at every step and that the delete dialog traps and restores focus.
3. Fix what fails. Escalate anything whose fix would change documented behavior.
4. Write `docs/reviews/TC-UX-008-01-touch.md`, `-02-mouse.md`, `-03-keyboard.md` with the standing line, the date, a per-action table, and a verdict.
**Test cases to implement:**
- `TC-UX-008-01` (Documented review) — touch
- `TC-UX-008-02` (Documented review) — mouse
- `TC-UX-008-03` (Documented review) — keyboard only, with visible focus at each step
**Acceptance criteria:** three artifacts exist covering every enumerated action; every primary action completes with all three input methods; no primary action depends solely on hover, gesture or colour.
**Verify with:** manual walkthrough per the artifacts; `cd frontend && npm run test && npm run build` after any fix.
**Out of scope for this task:** a formal WCAG conformance claim — nothing in the requirements asks for one.
**On finishing:** commit. **Slice 17 complete:** squash-merge, `DEVELOPMENT_LOG.md` entry. `UX-001` and `UX-008` close here.

---

### Slice 18 — Repository documentation and the OpenAPI contract

**Capability delivered:** another developer can clone the repository and, from the written instructions alone, set it up, migrate it, test it, build it and deploy it — and the API matches its published contract.

**Definition of Done:** the README review passes in a clean environment; the contract test passes; `RF-20` is proposed for deletion; the full suite is green.

#### Task 18.1 — Complete the repository operating documentation
**Slice:** 18 — Repository documentation and the OpenAPI contract
**Depends on:** 17.2
**Requirements:** TECH-007   **Design decisions:** ADS-TECH-007-01
**Read before starting:**
- `docs/design_specification.md` `ADS-TECH-007-01` (local setup, environment variables, dependency installation, database migrations, backend and frontend tests, production builds, and deployment; **commands copyable and tied to the actual repository structure**)
- `docs/test_specification.md` `TC-TECH-007-01` (a clean environment, instructions followed **in order**, with **no undocumented corrective step**)
- `docs/review_findings.md` `RF-20` and its maintenance rules §2 (a resolved finding is **deleted**, not marked complete; the commit message states which `RF-NN` was resolved and where the fix landed)
- `README.md` as it stands after Task 0.9
**Do:**
1. Complete the README: environment variables for both halves, dependency installation, database migration, running each half, backend and frontend test commands, production build commands, and the deployment procedure. Slice 19 fills in the platform-specific deployment detail — sequence this task's deployment section after 19.2 if the platform is not yet chosen, and say so in the commit message rather than writing a placeholder.
2. Perform the clean-environment review: fresh clone into an empty directory, follow only what is written, and record every step where you had to improvise. Fix the documentation, then repeat until no improvisation is needed.
3. Write `docs/reviews/TC-TECH-007-01-clean-environment.md` with the standing line, the date, the steps followed, the corrective steps needed on each pass, and the final verdict.
4. `RF-20` is now resolvable. Delete it from `docs/review_findings.md` per that document's maintenance rule 1, update its §5 summary counts, and state in the commit message that `RF-20` was resolved and where.
**Test cases to implement:** `TC-TECH-007-01` (Documented review) — satisfied by the recorded artifact.
**Acceptance criteria:** a fresh clone reaches a running backend, a running frontend and green suites using only the README; the review artifact records a pass with zero undocumented corrective steps; `review_findings.md` §5 shows three open findings.
**Verify with:** `git clone <repo> /tmp/clean-check && cd /tmp/clean-check` then follow the README verbatim.
**Out of scope for this task:** `RF-15`, `RF-16` and `RF-19` — those need spec changes and stay open.
**On finishing:** commit.

#### Task 18.2 — OpenAPI contract test
**Slice:** 18 — Repository documentation and the OpenAPI contract
**Depends on:** 18.1
**Requirements:** TECH-001   **Design decisions:** ADS-TECH-001-01
**Read before starting:**
- `docs/design_specification.md` `ADS-TECH-001-01` (routes namespaced under `/api/v1/`, JSON in and out, documented in an OpenAPI contract **maintained with the implementation**; the React application consumes the API only through that contract)
- `docs/api_contract.md` in full — this is the checklist the test verifies against, endpoint by endpoint
- `docs/test_specification.md` `TC-TECH-001-01` (each documented MVP endpoint exercised **directly over HTTP**, without browser-specific behavior)
**Do:**
1. Regenerate `backend/openapi.yaml` and confirm every endpoint in `api_contract.md` §4–§18 is present with its documented method, status codes and payload shape: health, register, csrf, login, refresh, logout, account get/patch, account password, categories, examinations list/create/detail/patch/delete, reminder get/post/patch, reminders due list, recurrence get/post/patch, next-occurrence, calendar, dashboard.
2. Implement `TC-TECH-001-01` as a single Contract test that walks the documented MVP endpoints with a plain HTTP client — no browser, no cookie jar behavior beyond what the contract itself specifies — and asserts the documented JSON structures.
3. Where the generated schema and `api_contract.md` disagree, **`api_contract.md` wins** and the implementation or the schema annotation changes. If the contract itself is internally inconsistent, that is a finding for the owner, not a change you make.
**Test cases to implement:** `TC-TECH-001-01` (Contract test) — every documented MVP endpoint accepts and returns the documented JSON structures without browser-specific behavior.
**Acceptance criteria:** the test passes; `backend/openapi.yaml` is committed and current; no documented endpoint is missing from it.
**Verify with:** `cd backend && python manage.py spectacular --file openapi.yaml && git diff --exit-code openapi.yaml && pytest -k tc_tech_001_01 -v`
**Out of scope for this task:** deployment verification (Slice 19).
**On finishing:** commit. **Slice 18 complete:** squash-merge, `DEVELOPMENT_LOG.md` entry, set Phase 7 to `Completed`. `TECH-001` and `TECH-007` close here.

---

### Slice 19 — Deployment

**Capability delivered:** the application is reachable over HTTPS at public URLs, the backend accepts browser requests only from the configured frontend origin, and the main integration flow is verified against the deployment.

**Platform: Render** (backend web service plus managed PostgreSQL) **and Vercel** (frontend static site) — D12. Several steps here are owner-run: `curl`, `wget` and `docker` are denied by `.claude/settings.local.json` (assumption A2), so anything that reaches the deployment over the network is the owner's to run; confirm who runs the deploy commands at kickoff.

**Definition of Done:** both halves deployed; the 8 cases below pass against the deployment; the full suite is green.

#### Task 19.1 — Production settings hardening and the security-header escalation
**Slice:** 19 — Deployment
**Depends on:** 18.2
**Requirements:** TECH-005, TECH-006, SEC-005   **Design decisions:** ADS-TECH-005-01, ADS-TECH-006-01, ADS-SEC-005-01, ADS-SEC-005-02, ADS-SEC-005-03, ADS-SEC-005-04, ADS-SEC-005-08
**Read before starting:**
- `docs/design_specification.md` `ADS-TECH-006-01` (HTTPS public URLs; **the backend trusts only the configured reverse-proxy HTTPS header**; production marks authentication cookies secure and redirects plain HTTP where the platform supports it), `ADS-TECH-005-01` (fail-fast on missing mandatory production configuration)
- `docs/design_specification.md` `ADS-SEC-005-01/02/03` (explicit CORS allowlist and CSRF trusted origins from environment variables, each with scheme, host and port; **no wildcard in production**; preflight permits `Authorization`, `Content-Type`, `X-CSRFToken`)
- `docs/api_contract.md` §5.3 and §5.7 (the production cookie attribute tables both halves must produce)
- `docs/review_findings.md` `RF-15` — **its recorded trigger is "revisit before the first production deployment", which is now**
**Do:**
1. Confirm the production settings module: `DEBUG = False`, `SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")` — Render's header, and nothing else, per `ADS-TECH-006-01`, `SESSION_COOKIE_SECURE`/`CSRF_COOKIE_SECURE` true, `SECURE_SSL_REDIRECT` where the platform supports it, CORS and CSRF origins from environment variables with a wildcard rejected at load.
2. Verify the refresh and CSRF cookies carry their documented production attributes when the app runs under production settings.
3. **`RF-15` is now triggered.** No accepted decision covers HSTS, `X-Content-Type-Options`, frame options or `Referrer-Policy`. Do **not** add them on your own authority — `ADS-TECH-006-01` is the only transport-security decision and adding headers beyond it is a design change. Report to the owner that the trigger has fired, propose that a new `ADS-TECH-006-NN` decision be written, and continue with the deployment as currently specified. Record the escalation in the day's log entry.
**Test cases to implement:** none in this task — `TC-SEC-005-03` and `TC-TECH-005-01` already passed in Slice 0; re-run them here as a regression check.
**Acceptance criteria:** production settings load with real values and fail without them; the wildcard rejection fires; `RF-15` is escalated in writing, not silently fixed or silently skipped.
**Verify with:** `cd backend && pytest -k "tc_tech_005_01 or tc_sec_005_03" -v`
**Out of scope for this task:** deciding `RF-15`.
**On finishing:** commit.

#### Task 19.2 — Deploy the backend and frontend
**Slice:** 19 — Deployment
**Depends on:** 19.1
**Requirements:** TECH-006, SEC-005   **Design decisions:** ADS-TECH-006-01, ADS-SEC-005-01, ADS-SEC-005-03
**Read before starting:**
- `docs/design_specification.md` `ADS-TECH-006-01`
- `README.md` (the deployment procedure you are about to execute and correct)
- `docs/product_definition.md` §11, second-to-last bullet (deployed **and** the main integration flow verified)
**Do:**
1. Confirm with the owner who runs the deploy commands (assumption A2). The hosts are settled by D12: Render for the backend and its managed PostgreSQL, Vercel for the frontend.
2. Provision Render PostgreSQL on a paid plan and run the backend on a paid instance type (D12 — a free instance sleeps and a free database expires, which makes the deployment cases below flaky). Set every required environment variable as a Render environment variable, and the frontend's as Vercel environment variables. Never commit a real value; `.env.example` stays placeholder-only per `ADS-SEC-004-01`.
3. Deploy the backend, run migrations (including the category seed data migration from Task 7.1) against the production database, and confirm `GET /api/v1/health/` over HTTPS.
4. Build and deploy the frontend to Vercel with `VITE_API_BASE_URL` pointed at the deployed Render backend origin. **Do not add a Vercel rewrite that proxies `/api/` through the frontend origin.** That would make the two same-origin and contradict the production `SameSite=None` cookies `ADS-SEC-005-04` and `ADS-SEC-005-08` require — separate origins are the design, not an accident of hosting.
5. Set the backend's CORS and CSRF origin variables to the deployed Vercel production origin, with scheme, host and port. Add a preview-deployment origin only if previews are meant to reach the API, and never a wildcard — `ADS-SEC-005-01` and `ADS-SEC-005-03` forbid one in production.
6. Update the README's deployment section with what you actually did, and re-run the Task 18.1 clean-environment check over that section.
**Test cases to implement:** none in this task (see 19.3 and 19.4).
**Acceptance criteria:** both URLs are HTTPS and reachable; the eight seeded categories exist in production; a real registration → login → create examination → dashboard flow completes against the deployment.
**Verify with:** owner-run: request the public Render health URL over HTTPS, then walk the flow in a browser from the Vercel origin.
**Out of scope for this task:** the deployment test cases themselves (19.3, 19.4).
**On finishing:** commit.

#### Task 19.3 — CORS and CSRF deployment integration tests
**Slice:** 19 — Deployment
**Depends on:** 19.2
**Requirements:** SEC-005   **Design decisions:** ADS-SEC-005-01, ADS-SEC-005-02, ADS-SEC-005-03
**Read before starting:** `docs/test_specification.md` `TC-SEC-005-01/02/04/05/06/07`; `docs/design_specification.md` `ADS-SEC-005-02` (the three headers preflight must permit and the credentialed-request rule).
**Do:** implement these six as a deployment-targeted test module that runs against a configured base URL rather than the local test client, skipping cleanly when that URL is unset so `pytest` stays green in local development.
**Test cases to implement:**
- `TC-SEC-005-01` (Deployment integration test) — a configured origin's credentialed cross-origin request is accepted
- `TC-SEC-005-02` (Deployment integration test) — an unconfigured origin is rejected
- `TC-SEC-005-04` (Deployment integration test) — preflight permits `Authorization`, `Content-Type`, `X-CSRFToken`
- `TC-SEC-005-05` (Deployment integration test) — a credentialed request from an unconfigured origin is rejected and **sets no cookies**
- `TC-SEC-005-06` (Deployment integration test) — a CSRF token from a configured origin passes validation
- `TC-SEC-005-07` (Deployment integration test) — a CSRF-protected request from an unconfigured origin is rejected
**Acceptance criteria:** all 6 pass against the deployment; all 6 skip (not fail) when the deployment URL is unset.
**Verify with:** `cd backend && DEPLOYMENT_BASE_URL=https://<service>.onrender.com DEPLOYMENT_FRONTEND_ORIGIN=https://<project>.vercel.app pytest -k tc_sec_005 -v` — **owner-run**: these reach the deployment over the network, which assumption A2 denies the agent.
**Out of scope for this task:** the HTTPS smoke tests (19.4).
**On finishing:** commit.

#### Task 19.4 — HTTPS deployment smoke tests
**Slice:** 19 — Deployment
**Depends on:** 19.2
**Requirements:** TECH-006   **Design decisions:** ADS-TECH-006-01
**Read before starting:** `docs/test_specification.md` `TC-TECH-006-01/02` — `-02` additionally asserts that authentication cookies are marked `Secure` and that the primary flows require no plain HTTP request.
**Do:** implement both against the deployed URLs, with the same skip-when-unset behavior as Task 19.3. Do not set a short client timeout: if a free Render instance is ever used despite D12, its first request cold-starts and a tight timeout turns that into a spurious failure.
**Test cases to implement:**
- `TC-TECH-006-01` (Deployment smoke test) — public frontend and API URLs are served over HTTPS
- `TC-TECH-006-02` (Deployment smoke test) — the primary flows require no plain HTTP, and authentication cookies are `Secure`
**Acceptance criteria:** both pass against the deployment; `-02` exercises the primary flows end to end rather than checking a single URL.
**Verify with:** `cd backend && DEPLOYMENT_BASE_URL=https://<service>.onrender.com pytest -k tc_tech_006 -v` — **owner-run**, per assumption A2.
**Out of scope for this task:** anything in `product_definition.md` §12 (future features).
**On finishing:** commit. **Slice 19 complete:** squash-merge into `project/mvp`, `DEVELOPMENT_LOG.md` entry, set Phase 8 to `Completed`. `SEC-005` and `TECH-006` close here.

**MVP complete.** All 73 requirements are closed and all 274 test cases pass. Merge `project/mvp` into `main` — the first implementation code `main` receives, per D1 and `CLAUDE.md`'s Branching section — then delete the project branch. A later project cuts a fresh one from `main`.

---

## 6. Requirement Coverage

All **73** requirement identifiers, each mapped to the task that closes it. "Closed by" is the last task carrying one of the requirement's test cases. The right-hand column lists **only test-bearing tasks** — implementation tasks that advance a requirement name it in their own **Requirements:** line.

| Requirement | Closed by | Tasks that touch it |
|---|---|---|
| **FR-001** | Slice 1 Registration (Task 1.3) | 1.3 |
| **FR-002** | Slice 1 Registration (Task 1.3) | 1.3 |
| **FR-003** | Slice 1 Registration (Task 1.3) | 1.3 |
| **FR-004** | Slice 1 Registration (Task 1.3) | 1.3 |
| **FR-005** | Slice 2 Login (Task 2.6) | 2.4, 2.6 |
| **FR-006** | Slice 4 Logout (Task 4.4) | 4.2, 4.4 |
| **FR-007** | Slice 3 Refresh (Task 3.4) | 3.2, 3.4 |
| **FR-008** | Slice 3 Refresh (Task 3.4) | 3.4 |
| **FR-009** | Slice 5 Account timezone (Task 5.4) | 5.4 |
| **FR-010** | Slice 7 Examinations core (Task 7.5) | 7.5 |
| **FR-011** | Slice 7 Examinations core (Task 7.5) | 7.5 |
| **FR-012** | Slice 7 Examinations core (Task 7.5) | 7.5 |
| **FR-013** | Slice 8 Detail/edit/delete (Task 8.2) | 8.2 |
| **FR-014** | Slice 7 Examinations core (Task 7.5) | 7.5 |
| **FR-015** | Slice 7 Examinations core (Task 7.5) | 7.5 |
| **FR-016** | Slice 8 Detail/edit/delete (Task 8.2) | 8.2 |
| **FR-017** | Slice 11 Reminders (Task 11.3) | 11.3 |
| **FR-018** | Slice 13 Recurrence (Task 13.3) | 13.3 |
| **FR-019** | Slice 15 Calendar (Task 15.2) | 10.2, 15.2 |
| **FR-020** | Slice 7 Examinations core (Task 7.8) | 7.8 |
| **FR-021** | Slice 8 Detail/edit/delete (Task 8.2) | 8.2 |
| **FR-022** | Slice 8 Detail/edit/delete (Task 8.2) | 8.2 |
| **FR-023** | Slice 14 Next occurrence (Task 14.3) | 8.2, 14.3 |
| **FR-024** | Slice 8 Detail/edit/delete (Task 8.4) | 8.4 |
| **FR-025** | Slice 7 Examinations core (Task 7.5) | 7.5 |
| **FR-026** | Slice 7 Examinations core (Task 7.5) | 7.5 |
| **FR-027** | Slice 7 Examinations core (Task 7.8) | 7.8 |
| **FR-028** | Slice 9 Search/filter/order (Task 9.2) | 9.2 |
| **FR-029** | Slice 9 Search/filter/order (Task 9.2) | 9.2 |
| **FR-030** | Slice 9 Search/filter/order (Task 9.2) | 9.2 |
| **FR-031** | Slice 10 Time states (Task 10.2) | 10.2 |
| **FR-032** | Slice 10 Time states (Task 10.2) | 10.2 |
| **FR-033** | Slice 10 Time states (Task 10.2) | 10.2 |
| **FR-034** | Slice 10 Time states (Task 10.2) | 10.2 |
| **FR-035** | Slice 11 Reminders (Task 11.3) | 11.3 |
| **FR-036** | Slice 11 Reminders (Task 11.3) | 11.3 |
| **FR-037** | Slice 12 Reminder lifecycle (Task 12.4) | 12.3, 12.4 |
| **FR-038** | Slice 12 Reminder lifecycle (Task 12.3) | 12.3 |
| **FR-039** | Slice 13 Recurrence (Task 13.3) | 13.3 |
| **FR-040** | Slice 13 Recurrence (Task 13.3) | 13.3 |
| **FR-041** | Slice 14 Next occurrence (Task 14.3) | 14.3 |
| **FR-042** | Slice 15 Calendar (Task 15.4) | 15.2, 15.4 |
| **FR-043** | Slice 15 Calendar (Task 15.4) | 15.4 |
| **FR-044** | Slice 16 Dashboard (Task 16.3) | 16.2, 16.3 |
| **FR-045** | Slice 16 Dashboard (Task 16.2) | 16.2 |
| **FR-046** | Slice 16 Dashboard (Task 16.2) | 16.2 |
| **FR-047** | Slice 16 Dashboard (Task 16.2) | 16.2 |
| **FR-048** | Slice 6 Password change (Task 6.3) | 6.3 |
| **UX-001** | Slice 17 UX review (Task 17.1) — Approved widths are **320 / 768 / 1280 CSS pixels** (`ADS-UX-001-02`). | 17.1 |
| **UX-002** | Slice 1 Registration (Task 1.5) | 1.5 |
| **UX-003** | Slice 1 Registration (Task 1.5) | 1.5 |
| **UX-004** | Slice 1 Registration (Task 1.5) | 1.5 |
| **UX-005** | Slice 7 Examinations core (Task 7.8) | 7.8 |
| **UX-006** | Slice 7 Examinations core (Task 7.8) | 7.8 |
| **UX-007** | Slice 5 Account timezone (Task 5.4) | 5.4 |
| **UX-008** | Slice 17 UX review (Task 17.2) — Review artifact location depends on assumption **A3**. | 17.2 |
| **SEC-001** | Slice 16 Dashboard (Task 16.2) | 0.4, 1.3, 2.4, 3.2, 5.4, 8.2, 11.3, 13.3, 15.2, 16.2 |
| **SEC-002** | Slice 13 Recurrence (Task 13.3) | 8.2, 11.3, 13.3 |
| **SEC-003** | Slice 1 Registration (Task 1.3) | 1.3 |
| **SEC-004** | Slice 0 Skeleton (Task 0.5) — Scanner choice is assumption **A5**. | 0.5 |
| **SEC-005** | Slice 19 Deployment (Task 19.3) — Render + Vercel, separate origins (**D12**). | 0.4, 2.4, 4.4, 19.3 |
| **SEC-006** | Slice 8 Detail/edit/delete (Task 8.2) | 2.4, 8.2 |
| **SEC-007** | Slice 3 Refresh (Task 3.2) — All three endpoint limits now covered: register 1.3, login 2.4, refresh 3.2. | 1.3, 2.4, 3.2 |
| **PRV-001** | Slice 7 Examinations core (Task 7.9) — Review artifact location depends on assumption **A3**. | 7.9 |
| **PRV-002** | Slice 7 Examinations core (Task 7.5) | 7.5 |
| **PRV-003** | Slice 2 Login (Task 2.6) | 0.8, 2.6 |
| **TECH-001** | Slice 18 Docs/contract (Task 18.2) | 18.2 |
| **TECH-002** | Slice 7 Examinations core (Task 7.5) | 7.5 |
| **TECH-003** | Slice 0 Skeleton (Task 0.4) | 0.4 |
| **TECH-004** | Slice 0 Skeleton (Task 0.4) | 0.4 |
| **TECH-005** | Slice 0 Skeleton (Task 0.4) | 0.4 |
| **TECH-006** | Slice 19 Deployment (Task 19.4) — Render + Vercel, HTTPS terminated by the platform (**D12**). | 19.4 |
| **TECH-007** | Slice 18 Docs/contract (Task 18.1) — Review artifact location depends on assumption **A3**. | 18.1 |

**Total requirements: 73.** Every requirement id is assigned; none is unassigned.

Requirement counts by category: **48 `FR-`, 8 `UX-`, 7 `SEC-`, 3 `PRV-`, 7 `TECH-` = 73**, matching `requirements_specification.md` and `design_specification.md` §10.

---

## 7. Test-Case Coverage

All **274** `TC-*` identifiers, grouped by requirement, with layer and assigning task. Layer abbreviations: `API-I` API integration, `API-V` API validation, `API-A` API authorization, `BE-M` backend model, `FE-I` frontend integration, `FE-C` frontend component, `CFG` configuration, `DEP-I` deployment integration, `DEP-S` deployment smoke, `SCAN` repository secret scan, `REV-DM` data-model review, `REV-DOC` documented review, `CONTRACT` contract test.

The eight manual cases (`REV-DOC` ×7, `REV-DM` ×1) are assigned to tasks that produce a recorded artifact — Tasks 7.9, 17.1, 17.2, 18.1 — not dropped.

| Requirement | Test cases | Layer | Task |
|---|---|---|---|
| **FR-001** (1) | `TC-FR-001-`01 | API-I | 1.3 |
| **FR-002** (3) | `TC-FR-002-`01–03 | API-V | 1.3 |
| **FR-003** (3) | `TC-FR-003-`01–03 | API-V | 1.3 |
| **FR-004** (1) | `TC-FR-004-`01 | API-V | 1.3 |
| **FR-005** (7) | `TC-FR-005-`01–05,07 | API-I | 2.4 |
|  | `TC-FR-005-`06 | FE-I | 2.6 |
| **FR-006** (14) | `TC-FR-006-`01–07,14 | API-I | 4.2 |
|  | `TC-FR-006-`08–13 | FE-I | 4.4 |
| **FR-007** (11) | `TC-FR-007-`01–08,10–11 | API-I | 3.2 |
|  | `TC-FR-007-`09 | FE-I | 3.4 |
| **FR-008** (4) | `TC-FR-008-`01–04 | FE-I | 3.4 |
| **FR-009** (2) | `TC-FR-009-`01 | API-I | 5.4 |
|  | `TC-FR-009-`02 | API-V | 5.4 |
| **FR-010** (1) | `TC-FR-010-`01 | API-I | 7.5 |
| **FR-011** (1) | `TC-FR-011-`01 | API-I | 7.5 |
| **FR-012** (6) | `TC-FR-012-`01–06 | API-V | 7.5 |
| **FR-013** (2) | `TC-FR-013-`01–02 | API-I | 8.2 |
| **FR-014** (7) | `TC-FR-014-`01–07 | API-V | 7.5 |
| **FR-015** (2) | `TC-FR-015-`01–02 | API-V | 7.5 |
| **FR-016** (2) | `TC-FR-016-`01 | API-I | 8.2 |
|  | `TC-FR-016-`02 | API-V | 8.2 |
| **FR-017** (3) | `TC-FR-017-`01–03 | API-V | 11.3 |
| **FR-018** (2) | `TC-FR-018-`01–02 | API-V | 13.3 |
| **FR-019** (3) | `TC-FR-019-`01–02 | API-I | 10.2 |
|  | `TC-FR-019-`03 | API-I | 15.2 |
| **FR-020** (4) | `TC-FR-020-`01–04 | FE-I | 7.8 |
| **FR-021** (1) | `TC-FR-021-`01 | API-I | 8.2 |
| **FR-022** (1) | `TC-FR-022-`01 | API-I | 8.2 |
| **FR-023** (3) | `TC-FR-023-`01–02 | API-I | 8.2 |
|  | `TC-FR-023-`03 | API-I | 14.3 |
| **FR-024** (2) | `TC-FR-024-`01–02 | FE-I | 8.4 |
| **FR-025** (1) | `TC-FR-025-`01 | API-I | 7.5 |
| **FR-026** (1) | `TC-FR-026-`01 | API-I | 7.5 |
| **FR-027** (1) | `TC-FR-027-`01 | FE-C | 7.8 |
| **FR-028** (1) | `TC-FR-028-`01 | API-I | 9.2 |
| **FR-029** (3) | `TC-FR-029-`01–03 | API-I | 9.2 |
| **FR-030** (3) | `TC-FR-030-`01–03 | API-I | 9.2 |
| **FR-031** (6) | `TC-FR-031-`01–06 | API-I | 10.2 |
| **FR-032** (5) | `TC-FR-032-`01–05 | API-I | 10.2 |
| **FR-033** (5) | `TC-FR-033-`01–05 | API-I | 10.2 |
| **FR-034** (1) | `TC-FR-034-`01 | API-I | 10.2 |
| **FR-035** (19) | `TC-FR-035-`01–04 | API-I | 11.3 |
|  | `TC-FR-035-`05–19 | API-V | 11.3 |
| **FR-036** (4) | `TC-FR-036-`01–04 | API-I | 11.3 |
| **FR-037** (2) | `TC-FR-037-`02 | API-I | 12.3 |
|  | `TC-FR-037-`01 | FE-I | 12.4 |
| **FR-038** (5) | `TC-FR-038-`01–05 | API-I | 12.3 |
| **FR-039** (10) | `TC-FR-039-`01–08,10 | API-V | 13.3 |
|  | `TC-FR-039-`09 | API-I | 13.3 |
| **FR-040** (6) | `TC-FR-040-`01–06 | API-I | 13.3 |
| **FR-041** (7) | `TC-FR-041-`01–04,06–07 | API-I | 14.3 |
|  | `TC-FR-041-`05 | API-V | 14.3 |
| **FR-042** (9) | `TC-FR-042-`05–09 | API-I | 15.2 |
|  | `TC-FR-042-`01–04 | FE-I | 15.4 |
| **FR-043** (5) | `TC-FR-043-`01–05 | FE-C | 15.4 |
| **FR-044** (10) | `TC-FR-044-`01–09 | API-I | 16.2 |
|  | `TC-FR-044-`10 | FE-I | 16.3 |
| **FR-045** (1) | `TC-FR-045-`01 | API-I | 16.2 |
| **FR-046** (2) | `TC-FR-046-`01–02 | API-I | 16.2 |
| **FR-047** (1) | `TC-FR-047-`01 | API-I | 16.2 |
| **FR-048** (3) | `TC-FR-048-`01 | API-I | 6.3 |
|  | `TC-FR-048-`02–03 | API-V | 6.3 |
| **UX-001** (3) | `TC-UX-001-`01–03 | REV-DOC | 17.1 |
| **UX-002** (3) | `TC-UX-002-`01–03 | FE-I | 1.5 |
| **UX-003** (2) | `TC-UX-003-`01–02 | FE-I | 1.5 |
| **UX-004** (2) | `TC-UX-004-`01–02 | FE-I | 1.5 |
| **UX-005** (2) | `TC-UX-005-`01–02 | FE-I | 7.8 |
| **UX-006** (1) | `TC-UX-006-`01 | FE-I | 7.8 |
| **UX-007** (2) | `TC-UX-007-`01–02 | FE-I | 5.4 |
| **UX-008** (3) | `TC-UX-008-`01–03 | REV-DOC | 17.2 |
| **SEC-001** (11) | `TC-SEC-001-`11 | API-I | 0.4 |
|  | `TC-SEC-001-`07 | API-I | 1.3 |
|  | `TC-SEC-001-`08–09 | API-I | 2.4 |
|  | `TC-SEC-001-`10 | API-I | 3.2 |
|  | `TC-SEC-001-`06 | API-I | 5.4 |
|  | `TC-SEC-001-`01 | API-I | 8.2 |
|  | `TC-SEC-001-`02 | API-I | 11.3 |
|  | `TC-SEC-001-`03 | API-I | 13.3 |
|  | `TC-SEC-001-`04 | API-I | 15.2 |
|  | `TC-SEC-001-`05 | API-I | 16.2 |
| **SEC-002** (5) | `TC-SEC-002-`01–03 | API-A | 8.2 |
|  | `TC-SEC-002-`04 | API-A | 11.3 |
|  | `TC-SEC-002-`05 | API-A | 13.3 |
| **SEC-003** (4) | `TC-SEC-003-`01 | BE-M | 1.3 |
|  | `TC-SEC-003-`02–04 | API-V | 1.3 |
| **SEC-004** (1) | `TC-SEC-004-`01 | SCAN | 0.5 |
| **SEC-005** (15) | `TC-SEC-005-`03 | CFG | 0.4 |
|  | `TC-SEC-005-`08–10,12–13 | API-I | 2.4 |
|  | `TC-SEC-005-`14–15 | CFG | 2.4 |
|  | `TC-SEC-005-`11 | FE-I | 4.4 |
|  | `TC-SEC-005-`01–02,04–07 | DEP-I | 19.3 |
| **SEC-006** (2) | `TC-SEC-006-`02 | API-I | 2.4 |
|  | `TC-SEC-006-`01 | API-I | 8.2 |
| **SEC-007** (4) | `TC-SEC-007-`03 | API-I | 1.3 |
|  | `TC-SEC-007-`01–02 | API-I | 2.4 |
|  | `TC-SEC-007-`04 | API-I | 3.2 |
| **PRV-001** (1) | `TC-PRV-001-`01 | REV-DM | 7.9 |
| **PRV-002** (1) | `TC-PRV-002-`01 | API-I | 7.5 |
| **PRV-003** (3) | `TC-PRV-003-`01 | FE-C | 0.8 |
|  | `TC-PRV-003-`02 | FE-I | 0.8 |
|  | `TC-PRV-003-`03 | FE-I | 2.6 |
| **TECH-001** (1) | `TC-TECH-001-`01 | CONTRACT | 18.2 |
| **TECH-002** (3) | `TC-TECH-002-`01–03 | BE-M | 7.5 |
| **TECH-003** (3) | `TC-TECH-003-`01–03 | CFG | 0.4 |
| **TECH-004** (1) | `TC-TECH-004-`01 | API-I | 0.4 |
| **TECH-005** (1) | `TC-TECH-005-`01 | CFG | 0.4 |
| **TECH-006** (2) | `TC-TECH-006-`01–02 | DEP-S | 19.4 |
| **TECH-007** (1) | `TC-TECH-007-`01 | REV-DOC | 18.1 |

**Total test cases assigned: 274.** No test case is unassigned; none appears twice.

### 7.1 Layer totals

| Layer | Count |
|---|---:|
| API integration test | 135 |
| API validation test | 59 |
| Frontend integration test | 39 |
| Frontend component test | 7 |
| Documented review | 7 |
| Configuration test | 7 |
| Deployment integration test | 6 |
| API authorization test | 5 |
| Backend model test | 4 |
| Deployment smoke test | 2 |
| Repository secret scan | 1 |
| Data-model review | 1 |
| Contract test | 1 |
| **Total** | **274** |

### 7.2 Reconciliation with the source documents

Counted directly from the documents, this plan's totals agree with them:

| Claim | `test_specification.md` §11 / `design_specification.md` §10 | Counted here | Agree |
|---|---:|---:|:--:|
| Requirement references represented | 73 | 73 | yes |
| Test cases recorded | 274 | 274 | yes |
| Design decisions recorded | 120 | 120 | yes |
| Requirements with at least one `ADS-*` | 73 | 73 | yes |
| Decisions linked to more than one requirement | 0 | 0 | yes |
| Test cases linked to more than one requirement | 0 | 0 | yes |

No discrepancy in the counts. The discrepancies this plan did find were content-level, not count-level; all four were settled by the owner and are recorded with their outcomes in §9.2.

---

## 8. Definition-of-Done Mapping

Every bullet of `product_definition.md` §11, mapped to the slice that satisfies it.

| # | Definition-of-Done bullet | Satisfied by |
|---:|---|---|
| 1 | users can register, log in, refresh a session, and log out | Slices 1, 2, 3, 4 |
| 2 | authenticated users can view and update their account timezone | Slice 5 |
| 3 | authenticated users can change their password | Slice 6 |
| 4 | authenticated users can create, view, edit, and permanently delete examination records | Slices 7, 8 |
| 5 | users can save drafts and planned records with the required and optional fields | Slice 7 (backend and form), Slice 8 (`FR-013` clearing optional values) |
| 6 | users can manage the five supported examination statuses | Slice 7 (all five accepted), Slice 8 (transitions through update) |
| 7 | users can search, filter, and order their examination records | Slice 9 |
| 8 | users can view past, upcoming, and overdue examination collections | Slice 10 |
| 9 | users can configure one in-application reminder and one recurrence rule for a planned examination | Slices 11, 13 |
| 10 | users can create one next recurring occurrence when requested | Slice 14 |
| 11 | users can view applicable examinations in a monthly calendar | Slice 15 |
| 12 | users can review upcoming, overdue, recently completed, status-count, category-count, `uncategorized_count`, and `overdue_count` dashboard information | Slice 16 |
| 13 | users cannot access examinations, reminders, or recurrence rules owned by another account | Slice 8 (examinations), Slice 11 (reminders), Slice 13 (recurrence — closes `SEC-002`) |
| 14 | the main user flows work on phone, tablet, and desktop screen sizes and with touch, mouse, and keyboard input | Slice 17 |
| 15 | critical backend and frontend behavior is covered by automated tests linked to requirements | every slice; final gate Slice 18 (`TC-TECH-001-01`) |
| 16 | the frontend and backend are deployed and their main integration flow is verified | Slice 19 |
| 17 | local setup, testing, database migration, build, and deployment instructions are documented | Slice 0 (setup and test), Slice 18 (complete, reviewed) |
| 18 | the application clearly states its privacy boundary and non-clinical purpose | Slice 0 (page, unauthenticated reach), Slice 2 (authenticated reach — closes `PRV-003`) |

Bullet 3 is new: §11 previously omitted authenticated password change, so the MVP could have been declared complete by that checklist without `FR-048` existing. `RF-26` resolved it and Slice 6 satisfies it.

---

## 9. Open Findings and Risk Register

### 9.1 The four open deferred findings

Each is placed at the slice its own recorded trigger names. **The plan schedules and flags; it does not decide.** Fixing any of these requires a spec change by the owner.

| Finding | Recorded trigger | Lands in | What the implementer does |
|---|---|---|---|
| `RF-15` — no security-header decisions | "revisit before the first production deployment" | Task 19.1 | Report that the trigger has fired; propose a new `ADS-TECH-006-NN`; **do not add HSTS, `X-Content-Type-Options`, frame options or `Referrer-Policy` on their own authority** — `ADS-TECH-006-01` is the only accepted transport-security decision. |
| `RF-16` — unbounded responses and query ranges | "revisit when pagination is implemented, or as soon as any account is expected to hold a large number of records" | Task 15.1 (calendar range half) | Report that the calendar half of the trigger is reached. **Impose no cap** — `ADS-FR-042-02` defines exactly three validations. The pagination half stays untriggered: pagination is excluded by `product_definition.md` §8. |
| `RF-19` — `offset_days` has no upper bound | "revisit when the due-reminder view is implemented" | Task 12.2 | Report that the trigger has fired, with the observed behavior (a large offset yields a permanently-due reminder). **Invent no bound.** |
| `RF-20` — required repository documentation does not exist | "before Phase 2 completes" | Task 0.9 (partial), Task 18.1 (closes) | Slice 0 writes setup and test instructions; Slice 18 completes migration, build and deployment, then deletes `RF-20` per `review_findings.md` maintenance rule 1 and states the resolution in the commit message. |

### 9.2 Contradictions found while writing this plan — resolved

Four contradictions between authoritative documents surfaced during the read-through. All four were put to the owner and settled on 22.08.2026, and each fix landed in the authoritative document that owned the defect. None was ever added to `review_findings.md`: that document's maintenance rule 1 deletes a finding once resolved, so a finding raised and fixed in one session never enters it. Rule 2 still applies — `RF-24`…`RF-27` are consumed and are never reused. The next free identifier is **`RF-28`**.

| Finding | Outcome | Where the fix landed |
|---|---|---|
| `RF-24` — the contract said registration returns an access token, while `api_contract.md` §5.2, `ADS-FR-001-01` and `TC-FR-001-01` all said it does not | **Fixed.** The word "register" was the error, as proposed. | `api_contract.md` §5.7's closing paragraph — now "the login and refresh response bodies". |
| `RF-25` — `SEC-007`'s verification says "for each endpoint" but both `TC-SEC-007-*` cases tested login only | **Fixed by adding the two missing test cases,** not by narrowing the requirement. The owner chose to leave `SEC-007` and `ADS-SEC-007-01` — whose verification impact also says "each endpoint" — as written. | `test_specification.md` — new `TC-SEC-007-03` (register limit) and `TC-SEC-007-04` (refresh limit); §11 count 272 → 274. Assigned to Tasks 1.3 and 3.2, so `SEC-007` now closes in Slice 3 rather than Slice 2. |
| `RF-26` — `product_definition.md` §11's Definition of Done omitted authenticated password change | **Fixed.** | `product_definition.md` §11 — new bullet 3; §8 of this plan maps it to Slice 6. |
| `RF-27` — `TC-FR-044-03`'s title named the past collection while its scenario concerns only `recently_completed` | **Fixed.** Title corrected; the identifier and the Given/When/Then are untouched. | `test_specification.md` `TC-FR-044-03` — now "An eligible record appears in the dashboard's recently-completed collection". |

### 9.3 Risk register

The places most likely to be implemented wrongly, each with its mitigation baked into a task.

| # | Risk | Why it bites | Mitigation, and where |
|---|---|---|---|
| **R1** | **Derived-overdue timezone boundaries.** The same record is upcoming at 08:59 and overdue at 09:01 in the user's zone, and a current-date record *without* a time is never overdue. | Easy to compute "now" in UTC or server-local, or to treat a missing `scheduled_time` as midnight — either passes a UTC-timezone test and fails a real user. | **One** module (`examinations/time_state.py`) holds the rule, introduced in Task 7.3 and extended — never duplicated — in Task 10.1; consumed by Tasks 15.1 and 16.1. `user_local_now(user)` is the only source of the user's clock. Task 10.2 requires a non-UTC account timezone in at least one case, and `TC-FR-033-05` flips the state without touching the record. |
| **R2** | **Refresh rotation with a fixed absolute expiry.** `exp` must be `session_start + 7 days` at *every* rotation, not `now + 7 days`. | The natural implementation, and every JWT library's default, extends the session on rotation — producing a session that never ends. A single-rotation test cannot see this. | `issue_refresh_token` takes `session_start` as a parameter (Task 2.1) so the extending form is not expressible; rotation passes the incoming token's own claim (Task 3.1). `TC-FR-007-10` is required to perform at least two successful rotations before its final rejection (Task 3.2). This is also why `simplejwt` was rejected (D3). |
| **R3** | **Next-occurrence idempotency and calendar-month clamping.** `201` first, `200` on repeat, keyed on **(source, calculated due date)**; `2026-01-31 + 1 month = 2026-02-28`. | Keying on the source alone breaks a legitimate second occurrence after a date change; keying on nothing creates duplicates on a double click. Naive month addition rolls `Jan 31` into `Mar 3`. | The lookup is explicitly the pair, inside `transaction.atomic()` (Task 14.1). Arithmetic lives in one function with clamping (Task 13.2). `TC-FR-041-06` asserts the row count, not just the response; `TC-FR-040-04` and `-05` pin the clamping dates. |
| **R4** | **Date-only values shifted through UTC.** `scheduled_date`, `completed_date` and reminder `due_date` must render exactly as stored. | Constructing a JavaScript `Date` from `"2026-08-15"` and formatting it locally shifts the date by a day for any viewer west of UTC. The bug is invisible in a UTC test environment. | Two deliberately separate functions — `formatInstant` and `formatCalendarDate` — with an instruction not to merge them (Task 5.3). `TC-UX-007-02` must use a timezone whose offset would visibly shift the date. Backend side: `ADS-TECH-002-01` field types, verified by `TC-TECH-002-01/02/03` on retrieved Python types. |
| **R5** | **`PATCH` validating the diff instead of the resulting record.** | DRF's partial update naturally validates only submitted fields, so `PATCH {"scheduled_date": null}` on a planned record silently produces an invalid record. | `validate_resulting_record(data, user)` is written to receive a merged record and never a partial one (Task 7.3); the merge happens in the serializer from Task 7.4 onward, so Slice 8's `PATCH` inherits it. Task 8.1's acceptance criteria name this exact case. |
| **R6** | **Null ordering differs between SQLite and PostgreSQL.** Development and production use different databases (D2). | `ORDER BY scheduled_date` places nulls first on PostgreSQL and last on SQLite by default. A test green locally fails in production, or vice versa. | Task 9.1 requires an **explicit** null-flag annotation sorted first, then the date, then `id` — never the database default. `TC-FR-030-01/02` assert placement in both directions. |
| **R7** | **Throttle tests leaking state.** Per-IP counters persist across tests in the same process, and after `RF-25` the four throttle cases sit in three different modules. | `TC-SEC-007-01/02/03/04` pass alone and fail in a full run, or poison unrelated auth tests with a `429`. `-03` and `-04` are the sharper risk: they live beside twelve registration cases and eleven refresh cases respectively, all of which hit the same throttled endpoint. | Tasks 1.3, 2.4 and 3.2 each require clearing the throttle cache between tests — as a module fixture, not a one-off inside the throttle test — and require the cases to pass in any order and across two consecutive full runs. |
| **R8** | **CSRF enforcement on views that do not use session authentication.** `login`, `refresh` and `logout` need CSRF; DRF only applies it automatically under `SessionAuthentication`. | Omitting explicit enforcement leaves three state-changing endpoints unprotected while every happy-path test still passes. | Tasks 2.3, 3.1 and 4.1 each state "explicit CSRF protection" as a step. `TC-SEC-005-11` asserts the header on all three from the client side; the `403` path is documented in `api_contract.md` §3.2. |

---

## 10. Working Agreements

### 10.1 Branching and commits

- `main` receives implementation code exactly once, at MVP completion (D1, `CLAUDE.md` Branching). Nothing else touches it.
- **`project/mvp` is the project branch** — cut from `main`, it collects the whole MVP, merges to `main` once when the MVP is done, and is then deleted. It is finite and named for its project, not a permanent `develop`: a repository that ships one MVP has no use for an integration branch that outlives it, and a later project cuts its own `project/<name>` from `main`.
- **One project branch at a time, for this MVP.** The 20 slices are strictly dependency-ordered and share machinery — the owner-scoped queryset mixin from Slice 7, the derived time-state module from Slices 7 and 10, the API client from Slices 2 and 3. Concurrent project branches would keep those apart until the final merge, and Slice 11 cannot be built against a mixin it cannot see. Parallelism belongs at the feature-branch level, where branches are short-lived and rebase cheaply onto `project/mvp`.
- One `feature/<slice-id>-<slug>` branch per slice, cut from `project/mvp` and squash-merged back when that slice's Definition of Done passes.
- One commit per task; message `<type>(s<NN>): <summary>`.
- A slice does not merge with a red suite, and does not merge with only one of its halves done.
- Re-run `bash scripts/secret-scan.sh` before every slice merge.

### 10.2 `DEVELOPMENT_LOG.md`

Follow that file's own usage rules, at its top. In particular: one entry per development day, newest first; record only work actually completed; **do not mark a feature complete unless its acceptance criteria are satisfied**; record the commands used to verify; never record secrets, tokens or private medical data. Record every escalation (§10.4) under Problems and Blockers.

### 10.3 Phase Progress table

Update `DEVELOPMENT_LOG.md`'s Phase Progress table only when a phase's state actually changes. Slice-to-phase mapping:

| Phase | Slices | Set `In progress` at | Set `Completed` at |
|---|---|---|---|
| 2. Architecture and Repository Setup | 0 | already `In progress` | end of Slice 0 |
| 3. Authentication | 1–6 | end of Slice 1 | end of Slice 6 |
| 4. Examination Records | 7–10 | end of Slice 7 | end of Slice 16 |
| 5. Planning and Recurrence | 11–14 | end of Slice 11 | end of Slice 16 |
| 6. Calendar and Dashboard | 15–16 | end of Slice 15 | end of Slice 16 |
| 7. Testing and Documentation | 17–18 | already `In progress` | end of Slice 18 |
| 8. Deployment | 19 | start of Slice 19 | end of Slice 19 |

Phase 1 (Product Definition) is the owner's to close — it turns on their independent documentation review, not on implementation.

### 10.4 What to escalate rather than decide

Stop and ask the owner when any of these occurs. Record the escalation in the day's log entry.

1. **A task appears to require changing a requirement.** The change happens in `requirements_specification.md` first, by the owner.
2. **Two authoritative documents contradict each other.** Write it up as a proposed finding starting at `RF-28` in `review_findings.md`'s record shape. Do not resolve it on your own authority.
3. **A deferred finding's trigger fires** (`RF-15` at Task 19.1, `RF-16` at Task 15.1, `RF-19` at Task 12.2). Report; do not fix.
4. **A requirement, decision or test case is not `Accepted`** (D11). The task is blocked.
5. **A value the specification calls "approved" is not documented anywhere.** The one known instance is closed: `ADS-UX-001-02` now names the `UX-001` viewport widths as 320 / 768 / 1280 CSS pixels. Escalate any further instance rather than choosing a value.
6. **Who runs the deploy commands** (assumption A2), at Slice 19 kickoff. The platform itself is settled — Render + Vercel, D12.
7. **A new field, endpoint, status or query parameter looks necessary.** `ADS-PRV-001-01` requires an approved requirements and design change *before* a migration adds a stored examination field; `api_contract.md` §19 records the contract as having no open points.
8. **Adding `docs/reviews/`** (assumption A3), before Task 7.9.

### 10.5 What never needs asking

- Implementing exactly what an `Accepted` `ADS-*` decision states.
- Refactoring within a task's own scope, provided no documented behavior changes and the suite stays green.
- Choosing test fixture data, helper names and file layout, provided the `TC-*` linking convention in §3.3 holds.
