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
python -c "import pathlib, secrets; env = pathlib.Path('.env'); env.write_text(env.read_text().replace('<generate-a-long-random-value>', secrets.token_urlsafe(50)).replace('<generate-a-different-long-random-value>', secrets.token_urlsafe(50)))"
python manage.py migrate
python manage.py runserver 8000
```

The `python -c` line replaces the two signing-secret placeholders in `backend/.env` with generated random values, so sessions survive a server restart. `migrate` creates `backend/db.sqlite3` and seeds the eight examination categories (see [Database Migrations](#database-migrations)).

The API is then served under `http://localhost:8000/api/v1/`; `http://localhost:8000/api/v1/health/` answers `{"status": "ok"}`.

`manage.py` reads `backend/.env` (never committed) for local development. Every variable is documented in [`backend/.env.example`](backend/.env.example):

| Variable | Local development | Production |
|---|---|---|
| `DJANGO_SETTINGS_MODULE` | `config.settings.development` (the `manage.py` default) | `config.settings.production` |
| `DJANGO_SECRET_KEY` | Optional — when blank, a random value is generated per process, so sessions end whenever the server restarts | Required |
| `JWT_SIGNING_KEY` | Optional — same behavior as above | Required; distinct from `DJANGO_SECRET_KEY` |
| `DJANGO_ALLOWED_HOSTS` | Optional — defaults to `localhost,127.0.0.1,[::1]` | Required |
| `FRONTEND_ORIGINS` | Optional — defaults to `http://localhost:5173` | Required; explicit `scheme://host[:port]` origins, no wildcards |
| `DATABASE_URL` | Optional — unset means `backend/db.sqlite3` | Required; `postgres://…` URL |
| `DJANGO_DEBUG` | Optional — defaults to `true` | Ignored; production always runs with debug off |
| `DJANGO_SECURE_SSL_REDIRECT` | Not used | Optional — defaults to `true` |

A new random value for either secret, for example to rotate one, is the output of:

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

The deployment tests in `tests/test_deployment.py` are skipped here; they run only against a deployed environment (see [Verify the deployment](#5-verify-the-deployment)).

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

### API contract

[`backend/openapi.yaml`](backend/openapi.yaml) is the OpenAPI contract generated from the implementation. The backend suite fails when it is stale; after changing an endpoint, regenerate and commit it:

```bash
cd backend
. .venv/bin/activate
python manage.py spectacular --file openapi.yaml
```

A running development server also serves it at `/api/v1/schema/` to authenticated requests.

## Database Migrations

Migrations live in `backend/accounts/migrations/` and `backend/examinations/migrations/`. `examinations/migrations/0002_seed_categories.py` is a data migration that creates the eight fixed examination categories, so a migrated database is ready to use with no fixture loading.

Apply every pending migration — after the first setup and after pulling changes:

```bash
cd backend
. .venv/bin/activate
python manage.py migrate
```

After changing a model, generate the migration, commit it with the change, and confirm nothing is left ungenerated:

```bash
python manage.py makemigrations
python manage.py makemigrations --check --dry-run
```

In production the same `migrate` command runs automatically each time the web service starts (see [Deployment](#deployment)), followed by `python manage.py createcachetable`, which creates the `django_cache` table the production settings use to share rate-limit counters between worker processes.

## Production Builds

### Backend

The backend has no build output: the API serves JSON only, so there are no static files to collect. A production install is the runtime dependencies alone, and the process is served by Gunicorn through `config/wsgi.py`, which selects `config.settings.production` by default. These are the build and serve commands Render runs in [Deployment](#deployment) step 2, where the platform sets `PORT` and the production environment variables and the start command applies migrations before Gunicorn starts; they are not part of local setup:

```bash
cd backend
pip install -r requirements.txt
gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
```

Production settings refuse to start unless `DJANGO_SECRET_KEY`, `JWT_SIGNING_KEY`, `DJANGO_ALLOWED_HOSTS`, `DATABASE_URL` and `FRONTEND_ORIGINS` are all set, and they reject a wildcard origin. Debug mode is always off, authentication cookies are `Secure`, `SameSite=None` and `Partitioned` — the frontend and backend are different sites, and browsers that block third-party cookies accept only partitioned ones — and plain-HTTP requests are redirected to HTTPS based on the platform's `X-Forwarded-Proto` header.

### Frontend

`VITE_API_BASE_URL` is compiled into the bundle, so set it to the backend origin the build will talk to:

```bash
cd frontend
npm ci
VITE_API_BASE_URL=https://<backend-host> npm run build
```

`npm run build` type-checks the project and writes a static site to `frontend/dist/`. `npm run preview` serves that build locally at `http://localhost:4173` for a last look. The site is a single-page application: any path that is not a file must be answered with `index.html`, which [`frontend/vercel.json`](frontend/vercel.json) configures on Vercel.

## Deployment

The backend runs as a web service on [Render](https://render.com), its PostgreSQL database on [Neon](https://neon.tech), and the frontend is a static site on [Vercel](https://vercel.com) (decision D12 in [`docs/technology_decisions.md`](docs/technology_decisions.md)). Render and Vercel terminate HTTPS, and the backend reaches Neon over TLS. The two halves stay on **separate origins**: the browser calls the Render origin directly, the production cookies are `SameSite=None; Secure` for exactly that reason, and the frontend must never proxy `/api/` through its own origin.

All three run on free plans. A free Render web service spins down after 15 minutes without traffic, and the next request waits about a minute while it starts again; a Neon free database does not expire. Moving the web service to a paid instance type removes the spin-down and needs no other change.

Deploy from the branch that holds the release: `project/mvp` until the MVP is merged, `main` afterwards. Each platform deploys again automatically on every push to that branch.

### 1. Create the database

In the Neon console create a project with the default Postgres version, in the region closest to the Render region you will pick in step 2 — **AWS Europe Central 1 (Frankfurt)** pairs with Render's **Frankfurt**. On the project dashboard choose **Connect**, switch **Connection pooling** off, and copy the connection string (`postgresql://…?sslmode=require&channel_binding=require`). Use the direct connection, not the pooled one: Django keeps its own persistent connections, and the pooler's transaction mode does not keep the session state Django relies on.

### 2. Create the backend web service

Choose **New → Web Service**, connect the repository (authorize Render's GitHub app for this repository only), and set:

| Setting | Value |
|---|---|
| Language | Python 3 |
| Branch | The release branch (see above) |
| Region | The region matching the database's (Frankfurt for Neon's Europe Central 1) |
| Root Directory | `backend` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `python manage.py migrate --noinput && python manage.py createcachetable && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT` |
| Instance Type | Free |
| Health Check Path (under **Advanced**) | `/api/v1/health/` |

Environment variables — secrets live only here, never in the repository:

| Variable | Value |
|---|---|
| `PYTHON_VERSION` | `3.12.3` |
| `DJANGO_SETTINGS_MODULE` | `config.settings.production` — required: `manage.py` in the start command would otherwise load the development settings |
| `DJANGO_SECRET_KEY` | Click **Generate** |
| `JWT_SIGNING_KEY` | Click **Generate** — a different value |
| `DJANGO_ALLOWED_HOSTS` | The service's host name, e.g. `medical-tracker-api.onrender.com` — shown under the service name once it exists |
| `DATABASE_URL` | The Neon connection string from step 1 |
| `FRONTEND_ORIGINS` | The Vercel production origin, e.g. `https://medical-tracker.vercel.app` — use the project name you will give Vercel in step 3; correct it in step 4 if Vercel assigns a different domain |

Free instances cannot run a pre-deploy command, so the start command applies pending migrations and creates the cache table before Gunicorn starts; both are no-ops when there is nothing to do. On a paid instance type they may move to a **Pre-Deploy Command** instead.

Create the service. Render asks for a card before it creates any service, even a free one; it places a temporary $1 authorization to verify it, and a free instance is not billed unless the workspace exceeds its monthly included bandwidth or build minutes. When the deploy finishes, `https://<service-host>/api/v1/health/` answers `{"status": "ok"}`. The first deploy's log shows the migrations, including `examinations.0002_seed_categories`.

### 3. Create the frontend project

In the Vercel dashboard choose **Add New → Project**, import the repository, and set:

| Setting | Value |
|---|---|
| Project Name | The name used for `FRONTEND_ORIGINS` in step 2 |
| Root Directory | `frontend` |
| Framework Preset | Vite |
| Install Command | `npm ci` |
| Build Command | `npm run build` |
| Output Directory | `dist` |
| Environment variable `VITE_API_BASE_URL` | `https://<service-host>` — the Render origin from step 2, no trailing slash, no `/api/v1` |

Create the project. Vercel builds the repository's default branch on import, and its **Root Directory** picker lists only that branch's directories. While the release branch is not the default one — `main` has no `frontend/` until the MVP is merged — leave Root Directory at `./` and create the project anyway; that first build fails. Then set **Settings → Build and Deployment → Root Directory** to `frontend`, set the branch under **Settings → Environments → Production → Branch Tracking** to the release branch, and deploy it with **Deployments → ⋯ → Create Deployment**, entering the release branch and choosing **Deploy to Production**. Later pushes to that branch deploy automatically. Vercel takes the Node.js version from `engines` in `frontend/package.json`. `frontend/vercel.json` only sends unknown paths to `index.html` so that deep links such as `/examinations/12` load; it contains no `/api` rewrite, and none may be added. Because `VITE_API_BASE_URL` is compiled in, changing it takes a redeploy.

### 4. Allow the frontend origin

Copy the production domain Vercel shows for the project (under **Settings → Environments → Production → Domains**); when the project name is already taken on `vercel.app`, Vercel adds a suffix, such as `medical-tracker-opal.vercel.app`. If it differs from the `FRONTEND_ORIGINS` value set in step 2, update that variable on Render with **Save, rebuild, and deploy**. The value is the exact origin — `https://`, the host, a port only if one is used, no trailing slash and no wildcard. List several origins comma-separated only when each is meant to reach the API, such as a custom domain; Vercel preview deployments are rejected unless their origins are listed.

### 5. Verify the deployment

1. Open `https://<service-host>/api/v1/health/` and confirm `{"status": "ok"}`; open `http://<service-host>/api/v1/health/` and confirm it redirects to HTTPS.
2. From the Vercel origin, register an account, log in, create an examination — the category list shows the eight seeded categories — and confirm it appears on the dashboard.
3. Reload a deep link such as `/examinations` and confirm the page loads rather than a 404.
4. Run the deployment tests from a local checkout, with the backend virtualenv from [Local Setup](#backend) active. They make HTTPS requests to both origins, and each run registers two throwaway accounts under `example.com` with random passwords:

   ```bash
   cd backend
   . .venv/bin/activate
   DEPLOYMENT_BASE_URL=https://<service-host> DEPLOYMENT_FRONTEND_ORIGIN=https://<vercel-domain> pytest -m deployment -v
   ```

   All eight must pass: the CORS and CSRF cases `TC-SEC-005-01/02/04/05/06/07` and the HTTPS cases `TC-TECH-006-01/02`.
