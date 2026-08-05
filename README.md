# Medical Tracker Application

A portfolio project for organizing personal medical appointments and examination history — one place to record completed examinations, prepare draft records, plan upcoming examinations, and configure basic reminders and recurrence. It is an organizational tool only: it does not provide medical advice, diagnoses, treatment recommendations, or emergency assistance.

Planned stack: Django REST Framework backend (JSON API under `/api/v1/`) + React frontend (mobile-first, responsive).

## Project Status

**Documentation-only, pre-implementation.** `backend/` and `frontend/` are empty placeholder directories — no Django project, no React project, no dependency manifests exist yet. There are no build, lint, or test commands to run.

The `docs/` suite below is a complete, decision-level specification: functional requirements, accepted design decisions, domain model, API contract, and user flows for the application described above. It is the plan to implement against.

Progress is tracked day-by-day in [`DEVELOPMENT_LOG.md`](DEVELOPMENT_LOG.md).

## Branching

`main` holds the documentation snapshot and, once implementation begins, only the completed MVP. All implementation work happens on other branches.

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

## Diagrams

PlantUML diagrams (domain class diagram, authentication and key sequence flows) live under [`docs/diagrams/`](docs/diagrams/).

## Setup, Build, and Deployment

Not yet documented — there is no implementation to run. This section will be filled in once `backend/` and `frontend/` contain real projects.
