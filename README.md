# Medical Tracker Application

A portfolio project for organizing personal medical appointments and examination history — one place to record completed examinations, prepare draft records, plan upcoming examinations, and configure basic reminders and recurrence. It is an organizational tool only: it does not provide medical advice, diagnoses, treatment recommendations, or emergency assistance.

Stack: Django REST Framework backend (JSON API under `/api/v1/`) + React frontend (mobile-first, responsive).

## Project Status

**Implementation in progress** on the `project/mvp` branch, slice by slice, following [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md). `backend/` holds the Django REST Framework project and `frontend/` the React application; both have runnable test suites (see [Running the Tests](#running-the-tests)).

The `docs/` suite below is a complete, decision-level specification: functional requirements, accepted design decisions, domain model, API contract, and user flows for the application described above. It is the plan the implementation follows.

Progress is tracked day-by-day in [`DEVELOPMENT_LOG.md`](DEVELOPMENT_LOG.md).

## Branching

`main` holds the documentation snapshot and receives implementation code only once, when the MVP is complete.

Each project gets one finite project branch cut from `main` — for this MVP, `project/mvp`. Work for each implementation slice happens on a `feature/<slice-id>-<slug>` branch cut from the project branch and is squash-merged back into it when that slice's Definition of Done passes. At project completion the project branch merges into `main` once and is then deleted; a later project cuts a fresh project branch from `main`.

## Documentation

Source-of-truth hierarchy (highest precedence first) — when two documents disagree, the higher one wins:

| # | Document | Purpose |
|---|---|---|
| 1 | [`docs/requirements_specification.md`](docs/requirements_specification.md) | Authoritative, testable requirements (`FR-`, `UX-`, `SEC-`, `PRV-`, `TECH-` identifiers) |
| 2 | [`docs/product_definition.md`](docs/product_definition.md) | Product-level summary, target user, MVP scope and explicit exclusions |
| 3 | [`docs/design_specification.md`](docs/design_specification.md) | Accepted implementation decisions (`ADS-*` identifiers), one or more per requirement |
| 4 | [`docs/domain_model.md`](docs/domain_model.md), [`docs/api_contract.md`](docs/api_contract.md), [`docs/user_flows.md`](docs/user_flows.md) | Detailed design artifacts derived from the above: entities and invariants, the JSON API contract, and step-by-step user flows |
| 5 | [`docs/test_specification.md`](docs/test_specification.md) | Given/When/Then test cases (`TC-<REQ-ID>-NN`), one or more per requirement |

Supporting documents:

- [`docs/traceability_matrix.md`](docs/traceability_matrix.md) — administrative mapping from requirement IDs to design-decision IDs to API operations; defines no behavior itself.
- [`docs/review_findings.md`](docs/review_findings.md) — non-normative tracking log for open specification inconsistencies and design gaps found during review.
- [`docs/technology_decisions.md`](docs/technology_decisions.md) — non-normative record of technology selections and repository-workflow decisions; defines no behavior.
- [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md) — non-normative implementation task sequence; outranked by every document in the hierarchy above.

## Diagrams

PlantUML diagrams (domain class diagram, authentication and key sequence flows) live under [`docs/diagrams/`](docs/diagrams/).

## Local Setup

### Prerequisites

- **Python 3.12** or newer, with the `venv` module.
- **Node.js 22** (at least 22.12) and **npm 10** — the version is pinned in [`frontend/.nvmrc`](frontend/.nvmrc); with nvm, `nvm install && nvm use` inside `frontend/` selects it.
- **Git**.

The backend uses SQLite locally, so no database server is needed.

### Backend

From the repository root:

```bash
cd backend
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver 8000
```

The API is then served under `http://localhost:8000/api/v1/`; `http://localhost:8000/api/v1/health/` answers `{"status": "ok"}`.

`manage.py` reads `backend/.env` (never committed) for local development. Every variable is documented in [`backend/.env.example`](backend/.env.example):

| Variable | Local development | Production |
|---|---|---|
| `DJANGO_SETTINGS_MODULE` | `config.settings.development` (the `manage.py` default) | `config.settings.production` |
| `DJANGO_SECRET_KEY` | Optional — without it a random value is generated per process, so sessions end when the server restarts | Required |
| `JWT_SIGNING_KEY` | Optional — same behavior as above | Required |
| `DJANGO_ALLOWED_HOSTS` | Optional — defaults to `localhost,127.0.0.1,[::1]` | Required |
| `FRONTEND_ORIGINS` | Optional — defaults to `http://localhost:5173` | Required; explicit `scheme://host[:port]` origins, no wildcards |
| `DATABASE_URL` | Optional — unset means `backend/db.sqlite3` | Required; `postgres://…` URL |
| `DJANGO_DEBUG` | Optional — defaults to `true` | Ignored; production always runs with debug off |
| `DJANGO_SECURE_SSL_REDIRECT` | Not used | Optional — defaults to `true` |

To give the two signing secrets stable local values (so sessions survive a server restart), replace the placeholders in `backend/.env` with generated values, for example the output of:

```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

### Frontend

In a second terminal, from the repository root:

```bash
cd frontend
npm ci
cp .env.example .env.local
npm run dev
```

The application is then served at `http://localhost:5173`. `VITE_API_BASE_URL` in `frontend/.env.local` points it at the backend (`http://localhost:8000` by default; see [`frontend/.env.example`](frontend/.env.example)). Use `localhost`, not `127.0.0.1`, for both halves: the authentication cookies are `SameSite=Lax` locally and are only sent between same-site origins.

## Running the Tests

Every automated test carries the identifier of the test case it implements from [`docs/test_specification.md`](docs/test_specification.md) — `test_tc_fr_001_01_…` in Python, `it('TC-FR-020-01 — …')` in TypeScript — so a single case can be selected by its identifier.

### Backend

```bash
cd backend
. .venv/bin/activate
pytest                      # the whole suite
pytest -k tc_tech_004_01    # one test case
ruff check . && ruff format --check .
```

### Frontend

```bash
cd frontend
npm run test                          # the whole suite
npx vitest run -t 'TC-PRV-003-01'     # one test case
npm run lint
```

### Repository secret scan

`scripts/secret-scan.sh` scans the tracked files and the full Git history with `detect-secrets` (installed into the backend virtualenv by `requirements-dev.txt`) and fails on anything not recorded in [`.secrets.baseline`](.secrets.baseline) as an audited false positive. The backend suite runs it as `TC-SEC-004-01`; to run it on its own, from the repository root:

```bash
. backend/.venv/bin/activate
bash scripts/secret-scan.sh
```

## Build and Deployment

Not yet documented: database migration, production build, and deployment procedures are added as the corresponding implementation slices land.
