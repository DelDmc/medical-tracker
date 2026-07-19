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

- **Current phase:** [Phase name]
- **Current milestone:** [Milestone or feature]
- **Current branch:** `[branch-name]`
- **Next major deliverable:** [Deliverable]
- **Last updated:** YYYY-MM-DD

---

## Daily Entries

<!--
Copy the template below and place the new entry directly under this comment.
Use an exact date and a short description of the day's main focus.
-->
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
| 1. Product Definition | Not started | — | — | MVP, user stories, acceptance criteria, privacy boundaries |
| 2. Architecture and Repository Setup | Not started | — | — | Repository structure, projects, configuration, tooling |
| 3. Authentication | Not started | — | — | Registration, login, refresh, protected routes and endpoints |
| 4. Examination Records | Not started | — | — | Data model, CRUD API, frontend records, authorization tests |
| 5. Planning and Recurrence | Not started | — | — | Recurrence rules, due dates, overdue calculations |
| 6. Calendar and Dashboard | Not started | — | — | Calendar views, dashboard sections, meaningful charts |
| 7. Testing and Documentation | Not started | — | — | Coverage, API documentation, architecture and security records |
| 8. Deployment | Not started | — | — | Production configuration, deployment, migrations, verification |

Allowed statuses: `Not started`, `In progress`, `Blocked`, `Completed`, `Deferred`.