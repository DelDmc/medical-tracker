# Medical Tracker Application — Daily Development Log

This file records daily project progress, technical decisions, verification work, blockers, and the next planned tasks.

## Usage Rules

1. Create one entry for every development day.
2. Keep the newest entry at the top of the **Daily Entries** section.
3. Record only work that was actually completed.
4. Do not mark a feature as complete unless its acceptance criteria are satisfied.
5. Record the tests or commands used to verify completed work.
6. Move unfinished work into **Tomorrow's Plan** or the project backlog.
7. Link relevant commits, pull requests, issues, or documentation when available.
8. Never include passwords, tokens, secret keys, private medical data, or environment-variable values.

---

## Current Project Status

- **Current phase:** Documentation hardening complete; preparing for the implementation phase
- **Current milestone:** Independent documentation review (owner), then implementation kickoff
- **Current branch:** `main`
- **Next major deliverable:** Decide the implementation branching workflow, then begin backend/frontend implementation on non-`main` branches
- **Last updated:** 2026-08-05

---

## Daily Entries

<!--
Copy the template below and place the new entry directly under this comment.
Use an exact date and a short description of the day's main focus.
-->
## 05.08.2026 — Resolve all active review findings; prepare `main` for implementation handoff

### Daily Objective

Resolve the full backlog of open findings in `docs/review_findings.md`, harden the documentation suite to internal consistency, and prepare `main` as a complete, pushable documentation snapshot ahead of the implementation phase — including populating `README.md`, updating `CLAUDE.md` with the branching policy, and adding PlantUML diagrams.

### Completed Today

- [+] Fixed a contradictory `time_state` value for examination 184 (RF-03).
- [+] Resolved RF-02: accepted registration's account-existence disclosure as an intentional MVP exclusion.
- [+] Added SEC-007 (rate limiting on unauthenticated registration/login/refresh) across requirements, design, traceability, and tests; resolved RF-11.
- [+] Resolved the five "Fix now" findings — RF-05, RF-06, RF-07, RF-09, RF-10 — covering pagination-language cleanup, documenting token lifetimes, broadening FR-006/FR-037 verification methods, a section cross-reference fix, and calendar date-range parameter validation.
- [+] Resolved RF-04: clarified that the `time_state` filter and the `time_state` response field are intentionally separate vocabularies.
- [+] Resolved RF-12: specified the refresh-token revocation mechanism (`ADS-FR-007-08` session-start/expiry encoding, `ADS-FR-007-09` `RevokedRefreshToken` denylist) — a minimal design scoped to this project's actual needs rather than a full token-family/reuse-detection model.
- [+] Resolved RF-13: enumerated Django's default password validators and added a 128-character maximum to the password policy.
- [+] Resolved RF-14: added authenticated password change (`FR-048`, `ADS-FR-048-01`, new endpoint, flow, and tests) and formally excluded unauthenticated password reset from the MVP.
- [+] Resolved RF-17: documented that logout does not revoke an already-issued access token, as an accepted, bounded consequence of the stateless JWT design.
- [+] Resolved RF-18: pinned the JWT signing algorithm (HS256) and named the access/refresh token claim sets, closing the algorithm-confusion gap.
- [+] Resolved RF-22 and RF-23: added a superseding note to this entry (below) rather than editing the frozen 18.07.2026/19.07.2026 entries.
- [+] Resolved RF-01: broadened SEC-006 into the single shared non-disclosure parent for both examination-lookup and login responses; re-homed `ADS-FR-005-05` as `ADS-SEC-006-02`.
- [+] Partially addressed RF-20: populated `.gitignore` (env files, Python/Django and Node/React artifacts, editor/OS files); narrowed the finding to its remaining `README.md` gap.
- [+] Populated `README.md` (project status, source-of-truth hierarchy, branching policy, diagrams pointer) and updated `CLAUDE.md` with a Branching section and a `docs/diagrams/` note.
- [+] Added `docs/diagrams/` — PlantUML source (domain class diagram, examination status state diagram, login/refresh/logout/password-change sequence diagrams) plus an index README.

### Files Created or Modified

| File or directory | Change | Reason |
|---|---|---|
| `docs/review_findings.md` | Created, then 14 findings resolved and removed (RF-01, RF-02, RF-03, RF-04, RF-05, RF-06, RF-07, RF-09, RF-10, RF-11, RF-12, RF-13, RF-14, RF-17, RF-18, RF-22, RF-23) | Track and close active specification inconsistencies |
| `docs/requirements_specification.md` | SEC-006 broadened; FR-003, FR-006, FR-037 reworded; FR-048 added | Bring requirements in line with resolved findings |
| `docs/design_specification.md` | Decisions added, re-homed, or reworded (`ADS-SEC-006-02`, `ADS-FR-007-08/09/10`, `ADS-FR-005-07`, `ADS-FR-006-09`, `ADS-FR-048-01`, `ADS-FR-003-01`, `ADS-SEC-003-01`, `ADS-FR-030-01`, `ADS-FR-031-01`, `ADS-SEC-007-01`); Section 10 counts updated | Implement the agreed fixes and design decisions |
| `docs/api_contract.md` | `time_state` vocabulary note, token lifetimes, password validation rules, new `POST /api/v1/account/password/` endpoint | Keep the contract consistent with the above |
| `docs/test_specification.md` | New and reworded test cases across FR-003, FR-005, FR-006, FR-007, FR-037, FR-042, FR-048, SEC-006; Section 11 counts updated | Verification coverage for every resolved finding |
| `docs/traceability_matrix.md` | Rows added or updated for every new or re-homed decision | Keep the matrix an accurate mapping |
| `docs/user_flows.md` | Absolute session lifetime note, access-token-survives-logout note, new Change Account Password flow | Reflect accepted decisions in the user-facing flows |
| `docs/product_definition.md` | Password reset exclusion added, password change feature added, `ADS-SEC-006-02` cross-reference fixed | Keep MVP scope statements accurate |
| `.gitignore` | Populated | RF-20 (partial) |
| `README.md` | Populated | Was empty |
| `CLAUDE.md` | Added Branching section and `docs/diagrams/` note | Reflect the new branch policy and new diagrams |
| `docs/diagrams/*.puml`, `docs/diagrams/README.md` | Created (6 diagrams + index) | New illustrative diagram set |
| `DEVELOPMENT_LOG.md` | This entry rewritten to reflect the full day; superseding note for RF-22/RF-23 | Keep the log an accurate daily record |

### Technical Decisions

| Decision | Reason | Alternatives considered |
|---|---|---|
| Minimal refresh-token revocation: `session_start`/fixed-`exp` claim plus a `RevokedRefreshToken(jti, expires_at)` denylist (RF-12) | Satisfies every already-accepted decision without building capability (reuse detection, token-family revocation) nothing requires yet | Full token-family table with reuse detection; a stateless per-user session-epoch claim (rejected — breaks legitimate multi-device use) |
| Cut password reset, add password change (RF-14) | Reset depends on email, which is already excluded from MVP; change is cheap and closes a real permanent-lockout gap | Excluding both; building reset without email |
| Access token survives logout, documented as an accepted risk rather than closed with a denylist (RF-17) | A per-request denylist check would defeat the reason for using short-lived stateless JWTs, for a window already capped at 10 minutes | Access-token blacklist checked on every protected request |
| Pin HS256 and name the full claim set, including `token_type` (RF-18) | Closes the standard algorithm-confusion vector and prevents access/refresh token cross-submission, at effectively no extra cost | Asymmetric (RS256/ES256) keypair — rejected as over-engineered for a single-backend MVP |
| Broaden SEC-006 as the single non-disclosure parent; re-home `ADS-FR-005-05` as `ADS-SEC-006-02` (RF-01) | Gives every future non-disclosure decision one consistent requirement parent | Leaving the decision under FR-005 with duplicated requirement text |
| Historical `DEVELOPMENT_LOG.md` entries (18.07/19.07) left verbatim; superseding note added instead (RF-22, RF-23) | Preserves the journal-of-record convention implied by the log's own structure | Correcting the stale filenames/field names in place |
| PlantUML diagrams committed as source only (`.puml`), no rendered images | No PlantUML renderer available locally (Java and Graphviz are present; PlantUML itself is not) | Fetching the official PlantUML jar to also render SVG/PNG |

### Tests and Verification

| Test, command, or manual check | Result | Notes |
|---|---|---|
| Re-read every document location a finding referenced, before editing | Passed | Confirmed each finding was still accurate (none had been silently resolved) before applying its fix |
| `grep -rn "RF-<NN>"` across `docs/` after every finding deletion | Passed | Confirmed no dangling references to a resolved finding id remained |
| `git diff` review before every commit | Passed | Confirmed each change matched what was reported before committing |
| Manual `@startuml`/`@enduml`, `alt`/`else`/`end`, `note`/`end note`, brace-balance check across all 6 `.puml` files | Passed | No PlantUML renderer available locally to fully validate; structural balance confirmed by inspection |
| `git check-ignore -v` against `.env`, `backend/staticfiles/`, `frontend/node_modules/` | Passed | Confirmed `.gitignore` excludes the intended patterns without affecting already-tracked files |

### Problems and Blockers

None outstanding. Yesterday's blockers (response-indistinguishability hierarchy, missing SEC-007) were resolved today via RF-01 and the SEC-007 addition.

### What I Learned

- Re-verifying a finding's referenced locations against current file state, rather than trusting the finding text, mattered: several findings had drifted line numbers, and confirming RF-02/RF-03's earlier fixes hadn't already overlapped RF-01's scope avoided duplicate work.
- Renaming or re-homing an identifier (`ADS-FR-005-05` → `ADS-SEC-006-02`) has a wider blast radius than it looks — it touched five files, and a repo-wide grep for the old identifier after the change was the only reliable way to catch every reference, including one buried in `product_definition.md`'s exclusions prose.
- Proportionality is a real design lever: several findings (RF-12, RF-13, RF-14, RF-17, RF-18) had a "build more security/capability" option and a "build only what's decided" option, and matching the choice to this project's actual scope (a personal, multi-device portfolio MVP, not an enterprise system) consistently pointed at the smaller design.
- A compound finding (RF-14's password change + reset, RF-20's `.gitignore` + `README.md`) is often two decisions wearing one id — splitting them let one half resolve now without forcing a premature decision on the half that isn't due yet.

### Tomorrow's Plan

1. **Owner reviews the full documentation suite independently** — `docs/requirements_specification.md` through `docs/test_specification.md`, plus the new `docs/diagrams/`.
2. **Begin the implementation phase** — branching strategy and workflow to be discussed and decided together before backend/frontend work starts.

### Carry-Over or Backlog Items

- RF-15 (security headers) — deferred, revisit before first production deployment.
- RF-16 (unbounded response/query sizes) — deferred, revisit with pagination or once an account holds many records.
- RF-19 (`offset_days` upper bound) — deferred, revisit when the due-reminder view is implemented.
- RF-20 (`README.md` setup/build/deployment instructions) — deferred, revisit before Phase 2 completes.
- Decide the implementation branching workflow before the first backend/frontend commit.

### Note: Superseding Earlier Planned Structure (RF-22, RF-23)

The 18.07.2026 and 19.07.2026 entries' "Tomorrow's Plan" sections describe creating `domain-model.md`, `api-contract.md`, `user-flows.md`, and a `docs/decisions/` directory of numbered decision records, and pose open business-rule questions using `scheduled_at`/`completed_at`. Those entries are left unchanged below, as an accurate record of what was planned and asked at the time. For a current reader: the adopted filenames use underscores (`domain_model.md`, `api_contract.md`, `user_flows.md`), all decisions are recorded in a single `design_specification.md` rather than a `docs/decisions/` directory, and the accepted domain model uses `scheduled_date`, a separate optional `scheduled_time`, and `completed_date` rather than `scheduled_at`/`completed_at`. Both open business-rule questions from those entries have since been answered by the accepted requirements and design decisions.

### Development Record

- **Time spent:** Not tracked
- **Branch:** `main`
- **Commits:** `a780070`..`67808a1` (15 commits), plus the commit that adds this entry
- **Pull request:** `Not created`
- **Related issue:** `None`

---

## 19.07.2026 — [Main focus]

### Daily Objective

Complete first steps in developing the Medical Tracker applictaion

### Completed Today

- [+] Completed requirements document 

### Files Created or Modified

| File or directory | Change | Reason |
|---|---|---|



### Tomorrow's Plan

1. **Review MVP scope**
   - Definition of done: [Observable completion condition]
2. **Review Important business rules to resolve**
   - Take a decision on:
    1. Whether scheduled_at is mandatory for all records.
    2. Whether a completed examination can have both scheduled_at and completed_at.
    3. How an examination becomes overdue.
    4. Whether users can create custom categories.
    5. Whether reminders are calculated dynamically or stored as records.
    6. Whether recurrence creates future records immediately or only calculates the next due date.

4. **Create**
docs/
├── domain-model.md
├── api-contract.md
├── user-flows.md
└── decisions/
    ├── 001-auth-token-storage.md
    ├── 002-category-ownership.md
    └── 003-recurrence-strategy.md

### Carry-Over or Backlog Items

- [Unfinished task moved from today]
- [New issue or improvement that is outside tomorrow's scope]

### Development Record

- **Time spent:** 3 hours
- **Branch:** `main`
- **Commits:** 
- **Pull request:** `Not created`
- **Related issue:** `None`

---

## 18.07.2026 — [Main focus]

### Daily Objective

Complete first steps in developing the Medical Tracker applictaion

### Completed Today

- [+] Created Git monorepo
- [+] Created and reviewed proudct_definition file
- [+] Created and reviewed requirements_specification file
- [+] Created and started the daily development log file

### Files Created or Modified

| File or directory | Change | Reason |
|---|---|---|
| `medical-tracker/backend` | created | basic structure |
| `medical-tracker/frontend` | created | basic structure |
| `medical-tracker/docs` | created | basic structure |
| `medical-tracker/docs/product_definition.md` | created and filled up | basic structure |
| `medical-tracker/docs/requirements_specification.md` | created and filled up | basic structure |
| `medical-tracker/.editorconfig` | created | basic structure |
| `medical-tracker/.gitignore` | created | basic structure |
| `medical-tracker/README.md` | created | basic structure |


### Tomorrow's Plan

1. **Complete requirements review**
   - Definition of done: all the requiremnts match MVP plan
2. **Review MVP scope**
   - Definition of done: [Observable completion condition]
3. **Review Important business rules to resolve**
   - Take a decision on:
    1. Whether scheduled_at is mandatory for all records.
    2. Whether a completed examination can have both scheduled_at and completed_at.
    3. How an examination becomes overdue.
    4. Whether users can create custom categories.
    5. Whether reminders are calculated dynamically or stored as records.
    6. Whether recurrence creates future records immediately or only calculates the next due date.

4. **Create**
docs/
├── domain-model.md
├── api-contract.md
├── user-flows.md
└── decisions/
    ├── 001-auth-token-storage.md
    ├── 002-category-ownership.md
    └── 003-recurrence-strategy.md

### Carry-Over or Backlog Items

- [Unfinished task moved from today]
- [New issue or improvement that is outside tomorrow's scope]

### Development Record

- **Time spent:** 7 hours
- **Branch:** `main`
- **Commits:** 9be2719
- **Pull request:** `Not created`
- **Related issue:** `None`

---

## YYYY-MM-DD — [Main focus]

### Daily Objective

[State the specific result intended for today.]

### Completed Today

- [ ] [Completed task or deliverable]
- [ ] [Completed task or deliverable]
- [ ] [Completed task or deliverable]

### Files Created or Modified

| File or directory | Change | Reason |
|---|---|---|
| `[path]` | [What changed] | [Why it was necessary] |

### Technical Decisions

| Decision | Reason | Alternatives considered |
|---|---|---|
| [Decision made] | [Reasoning] | [Rejected or deferred alternatives] |

### Tests and Verification

| Test, command, or manual check | Result | Notes |
|---|---|---|
| `[command or test name]` | Passed / Failed / Not run | [Relevant result or evidence] |

### Problems and Blockers

| Problem | Impact | Current understanding | Next action |
|---|---|---|---|
| [Problem] | [What it prevents] | [Known cause or uncertainty] | [Planned action] |

Use `None` when there were no blockers.

### What I Learned

- [Framework, architecture, testing, security, or domain knowledge learned today]
- [Code or design area that requires further study]

### Tomorrow's Plan

1. **[Task]**
   - Definition of done: [Observable completion condition]
2. **[Task]**
   - Definition of done: [Observable completion condition]
3. **[Task]**
   - Definition of done: [Observable completion condition]

### Carry-Over or Backlog Items

- [Unfinished task moved from today]
- [New issue or improvement that is outside tomorrow's scope]

### Development Record

- **Time spent:** [Hours or minutes]
- **Branch:** `[branch-name]`
- **Commits:** [Commit hashes or links]
- **Pull request:** [Link or `Not created`]
- **Related issue:** [Link or `None`]

---

## Weekly Review Template

Complete this section at the end of each development week.

### Week: YYYY-MM-DD to YYYY-MM-DD

#### Planned Outcomes

- [Planned outcome]
- [Planned outcome]

#### Completed Outcomes

- [Completed outcome]
- [Completed outcome]

#### Incomplete Outcomes

| Item | Reason | Revised plan |
|---|---|---|
| [Item] | [Reason] | [New target or next action] |

#### Quality and Verification

- **Tests added:** [Summary]
- **Tests passing:** [Count or status]
- **Known failing tests:** [Summary or `None`]
- **Security checks completed:** [Summary]
- **Documentation updated:** [Summary]

#### Main Technical Decisions

- [Decision and its impact]
- [Decision and its impact]

#### Main Risks or Blockers

- [Risk or blocker]
- [Risk or blocker]

#### Next Week's Priority

1. [Highest-priority result]
2. [Second-priority result]
3. [Third-priority result]

---

## Phase Progress

Update this table when a phase changes status.

| Phase | Status | Started | Completed | Notes |
|---|---|---|---|---|
| 1. Product Definition | In progress | 2026-07-18 | — | Core product definition, requirements, and specification suite exist; active review findings are being resolved before implementation |
| 2. Architecture and Repository Setup | In progress | 2026-07-18 | — | Monorepo skeleton exists; backend and frontend implementation directories are still empty |
| 3. Authentication | Not started | — | — | Behavior is documented; implementation has not started |
| 4. Examination Records | Not started | — | — | Behavior is documented; implementation has not started |
| 5. Planning and Recurrence | Not started | — | — | Behavior is documented; implementation has not started |
| 6. Calendar and Dashboard | Not started | — | — | Behavior is documented; implementation has not started |
| 7. Testing and Documentation | In progress | 2026-08-04 | — | Test specification exists and review findings are tracked; `README.md` and implementation test suites remain pending |
| 8. Deployment | Not started | — | — | Production deployment, migrations, and deployment verification have not started |

Allowed statuses: `Not started`, `In progress`, `Blocked`, `Completed`, `Deferred`.