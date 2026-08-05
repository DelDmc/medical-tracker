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

- **Current phase:** Specification review and pre-implementation documentation hardening
- **Current milestone:** Resolve active review findings and finalize rate-limiting requirements
- **Current branch:** `main`
- **Next major deliverable:** Standardize the response-indistinguishability requirement, then add SEC-007 rate limiting across requirements, design, API contract, user flows, traceability, and tests
- **Last updated:** 2026-08-05

---

## Daily Entries

<!--
Copy the template below and place the new entry directly under this comment.
Use an exact date and a short description of the day's main focus.
-->
## 05.08.2026 — Specification consistency review and findings tracking

### Daily Objective

Record the current documentation-review state, preserve active specification findings, and prepare the project to continue the SEC-006 and SEC-007 security-documentation updates.

### Completed Today

- [+] Created `docs/review_findings.md` as a non-normative tracking document for active specification inconsistencies, unsourced statements, and design gaps.
- [+] Re-verified the documentation suite and confirmed that `docs/test_specification.md` is present and accepted.
- [+] Seeded the findings document with active review findings, including response indistinguishability, rate limiting, token-state, password-policy, API-contract, and repository-documentation concerns.
- [+] Updated this development log's current status and phase table to reflect the documentation-first project state.

### Files Created or Modified

| File or directory | Change | Reason |
|---|---|---|
| `docs/review_findings.md` | Created | Preserve active audit findings outside the normative source-of-truth hierarchy |
| `DEVELOPMENT_LOG.md` | Updated current status, added this entry, and refreshed phase progress | Make the log reflect the current project state rather than the initial placeholder state |

### Technical Decisions

| Decision | Reason | Alternatives considered |
|---|---|---|
| Keep `docs/review_findings.md` non-normative and outside the source-of-truth hierarchy | Findings should guide cleanup work without defining behavior or overriding accepted specifications | Tracking findings only in conversation history, which is easy to lose |
| Delete resolved findings from `docs/review_findings.md` instead of marking them complete | The document should remain a short list of active problems | Maintaining a long completed-findings archive in the repository |

### Tests and Verification

| Test, command, or manual check | Result | Notes |
|---|---|---|
| `ls -la /home/del12dmc/projects/medical-tracker/ /home/del12dmc/projects/medical-tracker/docs/` | Passed | Confirmed the current documentation files, empty implementation directories, empty `README.md`, and presence of `docs/test_specification.md` |
| `git -C /home/del12dmc/projects/medical-tracker --no-pager status --short` | Passed | Confirmed the working tree was clean before this documentation update |

### Problems and Blockers

| Problem | Impact | Current understanding | Next action |
|---|---|---|---|
| Response indistinguishability is represented at inconsistent hierarchy levels | Blocks a clean SEC-007 throttling design because generic authentication and rate-limit responses need a consistent security parent | SEC-006 should likely be broadened and `ADS-FR-005-05` re-homed under SEC-006 | Review and apply the SEC-006 standardization across requirements, design, traceability, and tests |
| No rate-limiting requirement or contract exists yet | Leaves unauthenticated registration and login endpoints without a documented abuse control | SEC-007 is being drafted step by step with review before each change | Resume the approved step-by-step SEC-007 documentation update after RF-01 is resolved |

### What I Learned

- The test specification is part of the accepted documentation suite and must be included in every requirements or design change that affects verification.
- Response indistinguishability should be standardized before adding throttling so that login, examination lookup, and future rate-limit responses follow one security model.

### Tomorrow's Plan

1. **Standardize response indistinguishability**
   - Definition of done: SEC-006, its design decisions, the matrix, and related test cases consistently cover login and examination lookup non-disclosure.
2. **Continue SEC-007 rate limiting**
   - Definition of done: registration and login throttling requirements, decisions, contract updates, flows, matrix rows, and test cases are reviewed and applied step by step.
3. **Triage highest-impact review findings**
   - Definition of done: RF-02 and RF-12 have accepted dispositions or follow-up tasks.

### Carry-Over or Backlog Items

- Resolve RF-01 before finalizing SEC-007 response semantics.
- Decide whether registration's duplicate-email error is an accepted account-existence disclosure or should change.
- Define refresh-token server-side state, reuse behavior, and seven-day session tracking before authentication implementation.

### Development Record

- **Time spent:** Not tracked
- **Branch:** `main`
- **Commits:** Recorded in the commit that adds this entry
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