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

## 3. Cross-Document Inconsistencies

#### RF-01 — Response indistinguishability is recorded at two different hierarchy levels
**Documents:** `requirements_specification.md:214`, `design_specification.md (113-118)`, `traceability_matrix.md:47`, `test_specification.md:149`
**Disposition:** In progress
**Finding:** The same security principle — that a failure response must not disclose whether something exists — is a requirement for examination lookups (SEC-006) but only a design decision for login (`ADS-FR-005-05`). Two levels of the hierarchy express one principle, so a future non-disclosure decision has no consistent parent. The agreed fix is to broaden SEC-006 to cover both scopes and re-home `ADS-FR-005-05` as `ADS-SEC-006-02`, which also requires updating the matrix row and splitting the indistinguishability assertion out of `TC-FR-005-04` into a new `TC-SEC-006-02`.

#### RF-04 — The `time_state` field domain has no value for a past record
**Documents:** `api_contract.md:473`, `api_contract.md:511`
**Disposition:** Needs decision
**Finding:** The `time_state` response field is documented as `upcoming`, `overdue`, or `null`, while the list endpoint accepts `time_state=past` as a filter value. A past record is therefore selected by a value that the field itself can never hold. Either the field domain gains `past`, or the contract must state explicitly that filter values and field values are separate vocabularies.

## 4. Security and Design Gaps

#### RF-12 — The refresh-token invalidation mechanism is never specified
**Documents:** `design_specification.md (140-145)`, `design_specification.md (212-215)`, `design_specification.md (239-244)`, `design_specification.md (257-262)`
**Disposition:** Needs decision
**Finding:** Four accepted decisions require server-side refresh-token state: logout invalidates a token, refresh rotates and invalidates the previous token, invalid tokens are rejected, and a session carries an absolute seven-day lifetime measured from login. No decision defines where that state is held, how a token is marked invalid, how the original session start is recorded across rotations, or what happens when an already-rotated token is replayed. Reuse detection and token-family revocation are therefore undefined.

#### RF-13 — Password policy is underspecified in both directions
**Documents:** `design_specification.md:870`, `requirements_specification.md (24-25)`
**Disposition:** Needs decision
**Finding:** `ADS-SEC-003-01` states that Django password validators "will run where configured" without deciding which validators are configured, so the effective policy is whatever the settings happen to contain. No maximum password length is defined either, which allows an arbitrarily long input to reach the password hasher.

#### RF-14 — Password change is referenced but exists nowhere else
**Documents:** `design_specification.md:870`
**Disposition:** Needs decision
**Finding:** `ADS-SEC-003-01` requires that "all account creation and password changes" use Django's password API. No requirement, endpoint, user flow, or explicit exclusion covers password change or password reset, so the decision constrains a capability the product does not define.

#### RF-15 — No security-header decisions exist
**Documents:** `design_specification.md (995-1056)`
**Disposition:** Deferred
**Finding:** The technical and operational decisions cover HTTPS, debug mode, environment configuration, and repository documentation, but no decision addresses HSTS, `X-Content-Type-Options`, frame options, or `Referrer-Policy`. Trigger: revisit before the first production deployment.

#### RF-16 — Response and query sizes are unbounded
**Documents:** `api_contract.md:29`, `api_contract.md:936`
**Disposition:** Deferred
**Finding:** MVP list endpoints return complete JSON arrays with pagination excluded from the contract, and the calendar endpoint places no maximum span on its date range. Both response sizes grow with stored data and with a caller-chosen range. Trigger: revisit when pagination is implemented, or as soon as any account is expected to hold a large number of records.

#### RF-17 — Logout does not end access-token validity
**Documents:** `design_specification.md (140-145)`, `design_specification.md (122-127)`, `user_flows.md (85-94)`
**Disposition:** Needs decision
**Finding:** Logout invalidates the refresh token and clears client state, but a bearer access token already issued remains valid until its own expiry, up to ten minutes after logout. This is a normal consequence of stateless access tokens, but it is documented nowhere, so a reader cannot tell whether it is intended.

#### RF-18 — JWT algorithm and claim set are unspecified
**Documents:** `design_specification.md (86-127)`, `design_specification.md:879`
**Disposition:** Needs decision
**Finding:** The design accepts an access token in `access_token` with a ten-minute expiry and reads JWT signing material from environment variables, but no decision states the signing algorithm or the claim set. Algorithm confusion and unexpected claim contents are both avoidable by deciding this before implementation.

#### RF-19 — `offset_days` has no upper bound
**Documents:** `api_contract.md:724`, `design_specification.md (569-574)`, `requirements_specification.md (126-127)`
**Disposition:** Deferred
**Finding:** A reminder offset must be a positive whole number, with no maximum. A very large offset produces a `due_date` far in the past, which is immediately due and stays due. Trigger: revisit when the due-reminder view is implemented.

## 5. Repository Artifacts Outside `docs/`

#### RF-20 — Required repository documentation does not exist
**Documents:** `README.md`, `requirements_specification.md (248-249)`, `design_specification.md (1051-1056)`
**Disposition:** Deferred
**Finding:** TECH-007 requires documented local setup, test execution, migration, build, and deployment procedures, and `ADS-TECH-007-01` requires those instructions to be maintained in the repository and tied to its actual structure. `README.md` is empty. `.gitignore` is also empty, although `ADS-SEC-004-01` depends on excluding local `.env` files from version control. Trigger: `.gitignore` before the first backend commit; `README.md` before Phase 2 completes.

#### RF-22 — Historical log entries plan filenames and a structure the project did not adopt
**Documents:** `DEVELOPMENT_LOG.md (135-143)`, `DEVELOPMENT_LOG.md (202-210)`
**Disposition:** Needs decision
**Finding:** The 18.07.2026 and 19.07.2026 entries plan `domain-model.md`, `api-contract.md`, `user-flows.md`, and a `docs/decisions/` directory of numbered decision records. The repository uses underscored filenames and records all decisions in a single `design_specification.md`. The current status and phase table have since been corrected, but these entries still describe a structure that does not exist. Decide whether historical daily entries may be corrected in place or must remain exactly as written, in which case a superseding note is added instead.

#### RF-23 — Historical log entries use field names the domain model does not have
**Documents:** `DEVELOPMENT_LOG.md (128-129)`, `DEVELOPMENT_LOG.md (195-196)`
**Disposition:** Needs decision
**Finding:** Two open business rules in the 18.07.2026 and 19.07.2026 entries are written in terms of `scheduled_at` and `completed_at`. The accepted model uses `scheduled_date`, a separate optional `scheduled_time`, and `completed_date`, and both questions have since been answered by accepted requirements and decisions. Resolution depends on the same decision as RF-22.

## 6. Summary

- Findings open: **13**
- Fix now: **0**
- Needs decision: **8** — RF-04, RF-12, RF-13, RF-14, RF-17, RF-18, RF-22, RF-23
- In progress: **1** — RF-01
- Deferred: **4** — RF-15, RF-16, RF-19, RF-20
- Accepted: **0**
