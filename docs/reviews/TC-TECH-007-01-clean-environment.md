# TC-TECH-007-01 — Clean-Environment Documentation Review

**Standing:** This is a non-normative verification record. It is evidence that test case `TC-TECH-007-01` (`docs/test_specification.md`) was executed; it is not part of the source-of-truth hierarchy in `product_definition.md` §2, defines no behavior, and must never be cited as authority. When it disagrees with `README.md` or the specification, the review is repeated.

| | |
|---|---|
| **Test case** | `TC-TECH-007-01` — Documented procedures succeed in a clean environment |
| **Requirement** | `TECH-007` (decision `ADS-TECH-007-01`) |
| **Layer** | Documented review |
| **Date** | 2026-09-25 |
| **Reviewed document** | `README.md` — Local Setup, Running the Tests, Database Migrations, Production Builds, Deployment |
| **Branch reviewed** | `feature/s18-docs-contract` |

## 1. Environment

- Linux (kernel 6.8), Python 3.12.3 with `venv`, Node.js 22.23.3 with npm 10.9.9, Git — the README's stated prerequisites and nothing more.
- Each pass started from a fresh `git clone` into an empty directory: no virtualenv, no `node_modules/`, no `backend/.env`, no `frontend/.env.local`, no database.
- Network access to PyPI and the npm registry; no access to Render or Vercel.
- The machine's default `node` is v19, so a Node 22 binary was put first on `PATH` before starting. That meets the documented prerequisite; it is not a corrective step.

## 2. Method

The README was followed top to bottom, copying each command as written and running it from the directory the README names. Nothing else was run in the clean clone. Every point where the text had to be interpreted, completed or worked around counted as a corrective step. The documentation was fixed after each pass that needed one, the fix was committed, and the review was repeated from a new clone.

The running application was checked with a browser (headless Firefox): register an account, log in, create a planned examination, then confirm it appears on the dashboard.

## 3. Steps followed

| # | README section | Commands | Result (pass 2) |
|---|---|---|---|
| 1 | Local Setup → Backend | `python3 -m venv .venv`, activate, `pip install -r requirements.txt -r requirements-dev.txt`, `cp .env.example .env`, the `python -c` secret fill-in, `python manage.py migrate`, `python manage.py runserver 8000` | Both placeholders replaced; every migration applied, including `examinations.0002_seed_categories`; `GET /api/v1/health/` → `200 {"status":"ok"}` |
| 2 | Local Setup → Frontend | `npm ci`, `cp .env.example .env.local`, `npm run dev` | Served at `http://localhost:5173`; register → log in → create examination (8 categories offered) → dashboard shows it |
| 3 | Running the Tests → Backend | `pytest`, `pytest -k tc_tech_004_01`, `ruff check . && ruff format --check .` | 213 passed; 1 selected and passed; lint and format clean |
| 4 | Running the Tests → Frontend | `npm run test`, `npx vitest run -t 'TC-PRV-003-01'`, `npm run lint` | 46 passed; 1 selected and passed; lint clean |
| 5 | Running the Tests → Repository secret scan | `bash scripts/secret-scan.sh` | No secrets in the tree or the history |
| 6 | Running the Tests → API contract | `python manage.py spectacular --file openapi.yaml` | Regenerated file identical to the committed one (`git status` clean) |
| 7 | Database Migrations | `python manage.py migrate`, `python manage.py makemigrations`, `python manage.py makemigrations --check --dry-run` | Nothing to apply; no changes detected |
| 8 | Production Builds → Frontend | `npm ci`, `VITE_API_BASE_URL=https://<backend-host> npm run build` (with a test host), `npm run preview` | `dist/` built; the given origin is compiled into the bundle in place of the `.env.local` value; the preview serves `/` and the deep link `/examinations/12` |

## 4. Deployment section

Deployment runs on the owner's Render and Vercel accounts and was **not executed** in this review; the plan re-runs this check over the Deployment section after the owner's deployment in Task 19.2. What could be verified without the platforms was:

- **Paths.** Every file and directory the section names exists: `backend/`, `frontend/`, `backend/requirements.txt`, `backend/config/wsgi.py`, `frontend/package.json`, `frontend/vercel.json`, and the `examinations.0002_seed_categories` migration.
- **Start command.** `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT` was run with `PORT` and every required production variable set. It started under `config.settings.production`. Plain HTTP to `/api/v1/health/` got a `301` to `https://`. The same request carrying `X-Forwarded-Proto: https` got `200 {"status":"ok"}`.
- **Pre-deploy command.** `python manage.py migrate --noinput && python manage.py createcachetable` was run under the production settings. The database was switched to SQLite for this check, because no PostgreSQL server was available. All migrations applied, the eight categories were seeded, and the `django_cache` table was created.
- **Frontend settings.** The Vercel settings match the Production Builds section, which was executed in step 8. `frontend/vercel.json` holds exactly one rewrite, which sends unmatched paths to `/index.html`. It has no `/api` rewrite.

## 5. Corrective steps by pass

| Pass | README reviewed | Corrective steps | Documentation change |
|---|---|---|---|
| 1 | First draft | **0** needed to reach a running backend, a running frontend and green suites. **1** documentation defect: Production Builds → Backend gave the `gunicorn` command without saying it runs on the platform. A reader following the README in order would run it locally, where it fails because `PORT` and the production variables are unset. | The section now says Render runs these commands, with `PORT` and the production variables it sets, and that they are not part of local setup. |
| 2 | Revised draft, as committed | **0** | None |

## 6. Verdict

**Pass** for the local setup, environment variables, dependency installation, migration, test and production build procedures. On the second pass, a fresh clone reached a running backend, a running frontend, a completed main flow and green suites using only the README, with no undocumented corrective step.

The Deployment section is consistent with the repository as far as it can be checked without the platforms. It will be confirmed when the owner deploys in Task 19.2.
