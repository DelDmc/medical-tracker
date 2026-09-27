# Medical Tracker Application — Technology Decisions

## 1. Purpose and Standing

This document records the technology selections and repository-workflow decisions taken for implementing the Medical Tracker Application MVP.

**This document is non-normative.** It is not part of the source-of-truth hierarchy defined in `product_definition.md` §2. It defines no behavior, and it must never be cited as authority for an implementation choice that the specification governs. `requirements_specification.md` §8 keeps technology selections out of the requirements, and `ADS-*` decisions are requirement-linked, so the selections below have no place in either; they are recorded here so that they are not lost.

When anything below appears to conflict with `requirements_specification.md`, `product_definition.md`, `design_specification.md`, `domain_model.md`, `api_contract.md`, `user_flows.md`, or `test_specification.md`, those documents win and this one is corrected.

The implementation task sequence lives in `IMPLEMENTATION_PLAN.md` at the repository root, which is likewise non-normative.

## 2. Decisions

Decision identifiers match `IMPLEMENTATION_PLAN.md` §2. Identifiers are stable and never reused.

| # | Decision | Rationale |
|---|---|---|
| D1 | **Branching.** `main` receives implementation only at MVP completion. One project branch (`project/mvp`) is cut from `main` and collects the work; one `feature/<slice-id>-<slug>` branch per slice is cut from the project branch and squash-merged back when the slice's Definition of Done passes; the project branch merges into `main` once and is then deleted. | Keeps `main` a stable documentation snapshot until the MVP is whole, while each slice still lands as one reviewable unit. A project branch is per-project and finite, not a permanent `develop`. |
| D2 | **Database.** SQLite for local development, PostgreSQL in production. | Zero-setup local development; a managed, durable production database. Null ordering and other engine differences are handled explicitly in code rather than left to engine defaults. |
| D3 | **JWT.** Hand-rolled on `PyJWT`, not `djangorestframework-simplejwt`. | `simplejwt` recomputes `exp` relative to rotation time, which `ADS-FR-007-08` forbids. A small token module makes the fixed `session_start + 7 days` expiry the only expressible form. |
| D4 | **Backend tests.** `pytest` + `pytest-django`, with `freezegun` for frozen-clock cases. | Plain functions carry `TC-*` identifiers naturally; `freezegun` controls every clock read that flows through `config.clock`. |
| D5 | **Settings.** A typed environment reader (`config/settings/env.py`) with separate `development` and `production` modules over a shared `base`; production raises at import time when a mandatory value is absent. | Implements `ADS-TECH-003-01` and `ADS-TECH-005-01` with no fallback from production to development defaults. |
| D6 | **Current time.** One injectable clock service (`config/clock.py`) is the only source of "now"; the user's local date and time are resolved from it through the account timezone. | Every frozen-clock `TC-*` case controls one function, and no code path can compute "today" in UTC or server-local time by accident. |
| D7 | **Frontend.** TypeScript + Vite + React Router + TanStack Query + CSS Modules + Vitest + React Testing Library + MSW. | A typed single-page application with a fast build, declarative data fetching, scoped styles, and API mocking at the network boundary so tests exercise the real client code. |
| D8 | **Node.** Node 22 LTS, pinned in `frontend/.nvmrc` (`package.json` requires `>=22.12`). Originally Node 20 LTS; **changed by the owner on 2026-09-25** because Node 20 left upstream support on 2026-04-30. | Vite and Vitest refuse Node 19, and hosting platforms drop end-of-life runtimes. |
| D9 | **This document.** Technology decisions are recorded here, outside the source-of-truth hierarchy, by the task that introduces each technology. | Keeps technology selections out of the requirement-linked documents. |
| D10 | **Deployment is in scope** for the MVP (Slice 19). | Closes `TECH-006` and the deployment-layer `SEC-005` cases. |
| D11 | **Accepted-status gating.** Work skips any requirement, decision, or test case not marked `Accepted`; an item that moves to `Draft` blocks its task and is escalated. | Implementation never runs ahead of an unapproved specification change. |
| D12 | **Deployment platform.** Backend on a free Render web service, PostgreSQL on Neon's free plan, frontend static site on Vercel. Frontend and backend stay on separate origins — the frontend never proxies `/api/` through its own origin. Originally a paid Render web service and paid Render PostgreSQL; **changed by the owner on 2026-09-27** to avoid a recurring cost. | Render terminates HTTPS and sets `X-Forwarded-Proto`, the single proxy header `ADS-TECH-006-01` lets the backend trust. Separate origins are what the production `SameSite=None` cookies (`ADS-SEC-005-04`, `ADS-SEC-005-08`) are designed for. A Neon free database does not expire, where Render's free database is deleted 30 days after creation plus a 14-day grace period. A free Render web service spins down after 15 idle minutes and takes about a minute to start again; the deployment tests' 120-second client timeout absorbs that. Free instances cannot run a pre-deploy command, so the start command applies migrations. Moving the web service to a paid instance type removes the spin-down and needs no other change. |

## 3. Assumptions

Assumption identifiers match `IMPLEMENTATION_PLAN.md` §2.1 and are never reused.

| # | Assumption | Consequence if wrong |
|---|---|---|
| A2 | `curl`, `wget` and `docker` are denied to the coding agent, and no PostgreSQL client is installed locally. Steps that reach a deployment over the network are owner-run. | Only who runs the Slice 19 commands changes. |
| A3 | Manual review artifacts live in `docs/reviews/<TC-ID>-<slug>.md`, each opening with a non-normative standing line. **Confirmed by the owner on 2026-09-25.** | Fallback: record the review inside the day's `DEVELOPMENT_LOG.md` entry. |
| A4 | Python packaging uses `backend/requirements.txt` and `backend/requirements-dev.txt` for dependencies and `backend/pyproject.toml` for tool configuration. | Only the install commands change. |
| A5 | Secret scanning uses `detect-secrets`. | Only the `TC-SEC-004-01` command changes. |
| A6 | `PUT /api/v1/examinations/{id}/` is not implemented; `api_contract.md` §12 documents `PATCH` only. | A contract change would be needed first. |
| A7 | The registration and account timezone lists come from the browser (`Intl.supportedValuesOf('timeZone')`, with a static fallback); the backend stays authoritative. | A served list would need a new endpoint in `api_contract.md` first. |

## 4. Implementation Record

What the decisions above look like in the repository. Updated by the task that introduces each item.

### 4.1 Backend (D2, D3, D4, D5, D6, A4)

- **Framework and packages** — pinned in `backend/requirements.txt`: Django 5.2 (LTS), Django REST Framework, `django-cors-headers`, PyJWT, `psycopg` 3, `drf-spectacular` (OpenAPI generation), `tzdata` (a consistent IANA database on every host) and `gunicorn` (the production WSGI server). Development and test tools are pinned in `backend/requirements-dev.txt`; tool configuration lives in `backend/pyproject.toml`.
- **Settings layout (D5)** — `config/settings/env.py` holds the typed reader (`str`, `bool`, `int`, `list`, `database_url`) and origin validation; `base.py` holds shared settings; `development.py` and `production.py` each import `base` and nothing else. `production.py` reads every mandatory value without a default. `manage.py` loads an optional `backend/.env` for local convenience; the WSGI/ASGI entry points and the test suite never read it.
- **Environment variables** — documented, with placeholders only, in `backend/.env.example`.

### 4.2 Frontend (D7, D8, A7)

- **Packages** — pinned exactly in `frontend/package.json` (lockfile `frontend/package-lock.json`): React 19, React Router 7, TanStack Query 5, Vite 8, TypeScript 5.9, Vitest 4 with jsdom, React Testing Library, `@testing-library/jest-dom`, `@testing-library/user-event`, MSW 2, and ESLint with `typescript-eslint` and `eslint-plugin-react-hooks`.
- **Node (D8)** — `frontend/.nvmrc` pins major 22 and `package.json` requires `>=22.12` (Vite 8's floor on that line). The pinned package versions were chosen while D8 still named Node 20 and run on both; newer majors (React Router 8, Vitest 5, jsdom 30) are now open to a later upgrade.
- **Styling** — `src/styles/global.css` holds design tokens and shared primitives (buttons, form fields, alerts); component-specific layout uses CSS Modules.
- **Test environment** — Vitest runs with `TZ=Pacific/Honolulu`, so any date-only value that is accidentally routed through a UTC conversion renders on the previous day and fails the suite.
