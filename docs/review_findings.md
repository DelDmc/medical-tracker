# Medical Tracker Application — Review Findings

## 1. Purpose and Standing

This document records inconsistencies, unsourced statements, and unresolved design gaps found while reviewing the specification suite.

**This document is non-normative.** It is not part of the source-of-truth hierarchy defined in `product_definition.md` §2. It defines no behavior, and it must never be cited as authority for an implementation choice. Every finding below points at the documents that are authoritative; the fix always happens there, not here.

The document exists so that a known problem is not lost between review sessions. It is expected to shrink.

## 2. Conventions

Each finding has a stable identifier in the form `RF-NN` and records:

- the documents and locations involved;
- a disposition;
- the finding itself, stated so that it can be confirmed or refuted from the referenced documents.

Allowed dispositions:

- **Fix now** — the correct outcome is already known and only needs applying;
- **Needs decision** — a choice must be made before anything can be written;
- **In progress** — a fix is actively being applied;
- **Deferred** — deliberately postponed, with the trigger recorded;
- **Accepted** — the behavior is intentional. An accepted finding is moved to `product_definition.md` §8 as an explicit exclusion and then removed from this document.

Maintenance rules:

1. A resolved finding is **deleted** from this document, not marked complete. This document's value depends on being short.
2. Identifiers are not reused after deletion.
3. A finding must reference a location that can be checked, not a recollection.
4. When a finding is deleted, the commit message states which `RF-NN` was resolved and where the fix landed.

## 3. Security and Design Gaps

#### RF-15 — No security-header decisions exist
**Documents:** `design_specification.md (995-1056)`
**Disposition:** Deferred
**Finding:** The technical and operational decisions cover HTTPS, debug mode, environment configuration, and repository documentation, but no decision addresses HSTS, `X-Content-Type-Options`, frame options, or `Referrer-Policy`. Trigger: revisit before the first production deployment.

#### RF-16 — Response and query sizes are unbounded
**Documents:** `api_contract.md:29`, `api_contract.md:936`
**Disposition:** Deferred
**Finding:** MVP list endpoints return complete JSON arrays with pagination excluded from the contract, and the calendar endpoint places no maximum span on its date range. Both response sizes grow with stored data and with a caller-chosen range. Trigger: revisit when pagination is implemented, or as soon as any account is expected to hold a large number of records.

#### RF-19 — `offset_days` has no upper bound
**Documents:** `api_contract.md:724`, `design_specification.md (569-574)`, `requirements_specification.md (126-127)`
**Disposition:** Deferred
**Finding:** A reminder offset must be a positive whole number, with no maximum. A very large offset produces a `due_date` far in the past, which is immediately due and stays due. Trigger: revisit when the due-reminder view is implemented.

## 4. Repository Artifacts Outside `docs/`

#### RF-20 — Required repository documentation does not exist
**Documents:** `README.md`, `requirements_specification.md (248-249)`, `design_specification.md (1051-1056)`
**Disposition:** Deferred
**Finding:** TECH-007 requires documented local setup, test execution, migration, build, and deployment procedures, and `ADS-TECH-007-01` requires those instructions to be maintained in the repository and tied to its actual structure. `README.md` is empty. Trigger: before Phase 2 completes.

## 5. Summary

- Findings open: **4**
- Fix now: **0**
- Needs decision: **0**
- In progress: **0**
- Deferred: **4** — RF-15, RF-16, RF-19, RF-20
- Accepted: **0**
