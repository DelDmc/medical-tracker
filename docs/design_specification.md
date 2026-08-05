# Medical Tracker Application — Application Design Specification

## 1. Purpose

This document records proposed and accepted implementation design decisions for the Medical Tracker Application MVP.

`requirements_specification.md` remains the source of truth for required behavior and verification. This document references requirement identifiers for traceability but does not reproduce requirement statements or verification criteria. A design decision must not change, weaken, combine, or replace a requirement.

## 2. Document Status

**Status:** Accepted

Every design decision recorded in this document is accepted. Each decision also carries its own status, and that per-decision status is authoritative.

No design decision in this document is accepted merely because it is recorded here. A decision marked **Proposed** must be reviewed and accepted before the affected implementation begins. Section 10 records the current accepted and proposed decision counts.

## 3. Traceability Rules

The following traceability rules apply throughout this document:

1. Each design decision references exactly one requirement.
2. One requirement may have more than one separate design decision when its implementation requires several decisions.
3. A design decision must not reference or combine multiple requirements.
4. Every decision statement begins with the words **“It is decided …”**.
5. Requirement statements and verification criteria are not reproduced in this document; they remain only in `requirements_specification.md`.
6. When a requirement changes, the design decisions referencing that requirement are reviewed for direct impact. Secondary impacts on other requirements must be handled through separate design decisions under those requirements.

Each design decision contains:

- a unique `ADS` identifier;
- status;
- exactly one requirement identifier;
- decision;
- rationale;
- verification impact.

## 4. Functional Design Decisions

### 4.1 Account and Session Management

#### ADS-FR-001-01 — Registration endpoint and account fields
**Status:** Accepted  
**Requirement reference:** FR-001  
**Decision:** It is decided that account registration will be provided through `POST /api/v1/auth/register/`. The request will accept `email`, `password`, and `timezone`; successful validation will create a user through the Django user manager and return a successful registration response without returning the password.  
**Rationale:** A dedicated registration endpoint makes the required inputs and account-creation boundary explicit.  
**Verification impact:** The API integration test will submit the three required fields and confirm that a user record is created.

---

#### ADS-FR-002-01 — Email validation during registration
**Status:** Accepted  
**Requirement reference:** FR-002  
**Decision:** It is decided that the registration serializer will require `email`, validate its format with Django REST Framework email validation, normalize it before comparison, and enforce case-insensitive uniqueness against existing accounts.  
**Rationale:** Validation must reject all three cases in the requirement while preventing differently cased versions of the same address from being registered twice.  
**Verification impact:** Validation tests will cover missing, malformed, and already-registered email addresses and will assert an `email` field error.

---

#### ADS-FR-003-01 — Password validation during registration
**Status:** Accepted  
**Requirement reference:** FR-003  
**Decision:** It is decided that the registration serializer will define `password` as a required, write-only field with a minimum length of eight characters and a maximum length of 128 characters, and will create the account by calling Django's password-setting API.  
**Rationale:** This enforces the stated minimum without exposing or directly storing the submitted password, and the maximum bounds the length of input passed to the password hasher.  
**Verification impact:** Validation tests will cover a missing password, a password shorter than eight characters, and a password longer than 128 characters.

---

#### ADS-FR-004-01 — Supported timezone validation
**Status:** Accepted  
**Requirement reference:** FR-004  
**Decision:** It is decided that registration will accept only IANA timezone identifiers present in the backend's supported timezone set, obtained through Python's timezone database. The submitted identifier will be stored exactly as the canonical supported value.  
**Rationale:** Using IANA identifiers supports reliable date and time conversion and avoids project-specific abbreviations.  
**Verification impact:** Validation tests will submit a supported identifier and an unsupported value and will assert a `timezone` field error for the unsupported value.

---

#### ADS-FR-005-01 — Login endpoint and credentials
**Status:** Accepted  
**Requirement reference:** FR-005  
**Decision:** It is decided that login will be provided through `POST /api/v1/auth/login/` using `email` and `password`.  
**Rationale:** A dedicated authentication endpoint provides one explicit contract for credential submission.  
**Verification impact:** An API integration test will submit valid and invalid `email` and `password` combinations to the login endpoint.

---

#### ADS-FR-005-02 — Login access-token response
**Status:** Accepted  
**Requirement reference:** FR-005  
**Decision:** It is decided that successful login will return the access token in the JSON field `access_token`.  
**Rationale:** Returning the short-lived access token in JSON allows the frontend to use bearer authentication without a JavaScript-readable authentication cookie.  
**Verification impact:** An API integration test will confirm that successful login returns `access_token` in the response body.

---

#### ADS-FR-005-03 — Login refresh-token cookie
**Status:** Accepted  
**Requirement reference:** FR-005  
**Decision:** It is decided that successful login will set the refresh token in the backend-issued `refresh_token` cookie using the accepted refresh-cookie security configuration. The refresh token will not be returned in JSON.  
**Rationale:** A backend-issued cookie keeps the longer-lived refresh token outside JavaScript-readable response data.  
**Verification impact:** An API integration test will verify refresh-cookie creation and confirm that the refresh token is absent from the response body.

---

#### ADS-FR-005-04 — Frontend access-token storage and transport
**Status:** Accepted  
**Requirement reference:** FR-005  
**Decision:** It is decided that the frontend will hold the access token only in application memory and will send it to protected endpoints through the `Authorization: Bearer <access_token>` header.  
**Rationale:** In-memory storage avoids persistent JavaScript-readable token storage while bearer transport keeps protected API authentication explicit.  
**Verification impact:** Frontend integration tests will verify bearer-header use and confirm that the access token is not written to persistent browser storage.

---

#### ADS-FR-005-05 — Generic invalid-credentials response
**Status:** Accepted  
**Requirement reference:** FR-005  
**Decision:** It is decided that invalid login credentials will return one generic authentication error regardless of whether the submitted email exists.  
**Rationale:** A generic error avoids disclosing account existence.  
**Verification impact:** API integration tests will confirm that unknown-email and incorrect-password attempts return the same status and response structure.

---

#### ADS-FR-005-06 — Access-token lifetime
**Status:** Accepted
**Requirement reference:** FR-005
**Decision:** It is decided that every access token will expire ten minutes after issuance.
**Rationale:** A ten-minute lifetime limits the period in which a leaked bearer token can be used while allowing the accepted refresh mechanism to maintain an active user session without repeated login.
**Verification impact:** Authentication tests will verify that the access token contains an expiration time ten minutes after issuance and is rejected after that expiration boundary.

---

#### ADS-FR-006-01 — Logout endpoint
**Status:** Accepted  
**Requirement reference:** FR-006  
**Decision:** It is decided that logout will be initiated through `POST /api/v1/auth/logout/` using the accepted credentialed-request and CSRF configuration.  
**Rationale:** A dedicated endpoint provides one explicit server-side logout operation.  
**Verification impact:** An API integration test will verify the endpoint method, route, credential handling, and CSRF enforcement.

---

#### ADS-FR-006-02 — Logout refresh-token invalidation
**Status:** Accepted  
**Requirement reference:** FR-006  
**Decision:** It is decided that the backend will invalidate a valid refresh token received during logout.  
**Rationale:** Invalidating the refresh token prevents reuse of the server-recognized session after logout.  
**Verification impact:** An API integration test will confirm that a refresh token used for logout cannot subsequently issue a new access token.

---

#### ADS-FR-006-09 — Access-token validity survives logout
**Status:** Accepted  
**Requirement reference:** FR-006  
**Decision:** It is decided that logout will not revoke an already-issued access token; a bearer access token obtained before logout remains valid, and continues to grant access to protected endpoints, until its own ten-minute expiration (`ADS-FR-005-06`).  
**Rationale:** The access token is a stateless, self-verifying JWT with no server-side revocation state by design (`ADS-FR-005-06`), and checking it against a denylist on every protected request would reintroduce the per-request database lookup that a short-lived stateless token exists to avoid. The exposure window this leaves open is bounded to the token's own ten-minute lifetime.  
**Verification impact:** An API integration test will confirm that an access token issued before logout continues to authenticate protected requests until its own expiration.

---

#### ADS-FR-006-03 — Logout refresh-cookie clearing
**Status:** Accepted  
**Requirement reference:** FR-006  
**Decision:** It is decided that the backend will clear the `refresh_token` cookie during logout using the same cookie identity and applicable security attributes used when the cookie was created.  
**Rationale:** Matching cookie attributes are required for reliable browser-side cookie removal.  
**Verification impact:** An API integration test will verify that the logout response expires the refresh cookie with the accepted cookie configuration.

---

#### ADS-FR-006-04 — Idempotent logout response
**Status:** Accepted  
**Requirement reference:** FR-006  
**Decision:** It is decided that `POST /api/v1/auth/logout/` will return `204 No Content` with an empty response body when the refresh cookie contains a valid, expired, revoked, or already invalid refresh token, or when the refresh cookie is missing.  
**Rationale:** One deterministic response lets the client complete logout without exposing refresh-token state and preserves idempotent behavior.  
**Verification impact:** API integration tests will verify `204 No Content` with an empty body for valid, missing, expired, revoked, and already invalid refresh tokens.

---

#### ADS-FR-006-05 — Immediate local session-state clearing
**Status:** Accepted  
**Requirement reference:** FR-006  
**Decision:** It is decided that the frontend will clear the in-memory access token and authenticated-user state immediately after the user selects logout and before sending the logout request.  
**Rationale:** Immediate local session-state clearing prevents continued authenticated interface and API activity without depending on backend availability.  
**Verification impact:** Frontend integration tests will verify that the access token and authenticated-user state are cleared before the logout request is sent.

---

#### ADS-FR-006-06 — Persistent logout-intent marker
**Status:** Accepted  
**Requirement reference:** FR-006  
**Decision:** It is decided that the frontend will write the non-sensitive value `true` under `medical_tracker.logout_intent` in `localStorage` before sending the logout request. While the marker exists, protected-application initialization will not attempt session restoration from the refresh-token cookie.  
**Rationale:** The marker preserves an explicit logout choice when the backend is unreachable and an `HttpOnly` refresh cookie cannot be cleared by frontend code.  
**Verification impact:** Frontend integration tests will verify marker creation and suppression of initialization refresh while the marker exists.

---

#### ADS-FR-006-07 — Logout-intent marker removal
**Status:** Accepted  
**Requirement reference:** FR-006  
**Decision:** It is decided that a later successful login will remove `medical_tracker.logout_intent` from `localStorage`.  
**Rationale:** Successful authentication establishes a new explicit session and ends the previous logout intent.  
**Verification impact:** A frontend integration test will confirm that successful login removes the marker.

---

#### ADS-FR-006-08 — Logout navigation outcome
**Status:** Accepted  
**Requirement reference:** FR-006  
**Decision:** It is decided that the frontend will navigate to the login page after the logout request succeeds, fails, or cannot reach the backend.  
**Rationale:** Completion of the user-visible logout flow must not depend on the availability or response of the backend.  
**Verification impact:** Frontend integration tests will verify login-page navigation after successful, failed, and unreachable logout requests.

---

#### ADS-FR-007-01 — Access-token refresh endpoint
**Status:** Accepted  
**Requirement reference:** FR-007  
**Decision:** It is decided that access-token renewal will be provided through `POST /api/v1/auth/refresh/` using the accepted credentialed-request and CSRF configuration, with the refresh token read from the `refresh_token` cookie.  
**Rationale:** A dedicated endpoint and one defined token source provide an unambiguous renewal contract.  
**Verification impact:** An API integration test will verify the endpoint route, method, CSRF enforcement, and refresh-token cookie input.

---

#### ADS-FR-007-02 — Refresh-token rotation
**Status:** Accepted  
**Requirement reference:** FR-007  
**Decision:** It is decided that every successful access-token refresh will rotate the submitted refresh token and invalidate the previous refresh token.  
**Rationale:** Rotation limits the period in which a copied refresh token can be reused.  
**Verification impact:** An API integration test will confirm that a successful refresh invalidates the previously submitted refresh token.

---

#### ADS-FR-007-03 — Replacement refresh-token cookie
**Status:** Accepted  
**Requirement reference:** FR-007  
**Decision:** It is decided that successful refresh-token rotation will set the replacement token in the `refresh_token` cookie using the accepted refresh-cookie security configuration.  
**Rationale:** Replacing the cookie preserves the session without exposing the refresh token to frontend JavaScript.  
**Verification impact:** An API integration test will verify replacement-cookie creation and its accepted attributes.

---

#### ADS-FR-007-04 — Refreshed access-token response
**Status:** Accepted  
**Requirement reference:** FR-007  
**Decision:** It is decided that successful refresh will return the new access token in the JSON field `access_token`.  
**Rationale:** A stable response field gives the frontend one explicit source for replacing its in-memory access token.  
**Verification impact:** An API integration test will confirm the `access_token` response field after valid refresh.

---

#### ADS-FR-007-05 — Invalid refresh-token response
**Status:** Accepted  
**Requirement reference:** FR-007  
**Decision:** It is decided that expired, revoked, malformed, missing, or otherwise invalid refresh tokens will be rejected without issuing new credentials, and the stale `refresh_token` cookie will be cleared.  
**Rationale:** Rejection prevents unauthorized renewal, while cookie clearing prevents repeated submission of a known unusable token.  
**Verification impact:** API integration tests will verify rejection without credential issuance and cookie clearing for each invalid-token condition.

---

#### ADS-FR-007-06 — Session restoration after page reload
**Status:** Accepted  
**Requirement reference:** FR-007  
**Decision:** It is decided that protected-application initialization may call the refresh endpoint once when no in-memory access token exists and `medical_tracker.logout_intent` is absent.  
**Rationale:** Initialization refresh restores a valid session after page reload because the access token is intentionally not persisted.  
**Verification impact:** A frontend integration test will verify one initialization refresh when the access token is absent and the logout-intent marker does not exist.

---

#### ADS-FR-007-07 — Refresh-session maximum lifetime
**Status:** Accepted  
**Requirement reference:** FR-007  
**Decision:** It is decided that the refresh-token session will have an absolute maximum lifetime of seven days from successful login. Refresh-token rotation will preserve the original session expiration and will not extend it.  
**Rationale:** A seven-day maximum supports intermittent use without permitting refresh-token rotation to maintain a session indefinitely.  
**Verification impact:** Authentication integration tests will verify that every rotated refresh token retains the original session-expiration boundary and that refresh is rejected after seven days from login.

---

#### ADS-FR-007-08 — Refresh-token session-start and expiry encoding
**Status:** Accepted  
**Requirement reference:** FR-007  
**Decision:** It is decided that every refresh token will carry a `session_start` claim set once at login and copied unchanged into every rotated token issued within that session, and an `exp` claim fixed at `session_start` plus seven days and computed identically at login and at every subsequent rotation rather than relative to the rotation time.  
**Rationale:** Encoding the absolute expiration in the token itself lets the seven-day-from-login boundary decided in `ADS-FR-007-07` be enforced from the token alone, without a database lookup, and keeps each login's session window independent of any other concurrent session belonging to the same user.  
**Verification impact:** Already verified by `TC-FR-007-10`, which mocks a login time and confirms refresh is rejected once seven days have elapsed regardless of intervening rotations.

---

#### ADS-FR-007-09 — Refresh-token revocation state
**Status:** Accepted  
**Requirement reference:** FR-007  
**Decision:** It is decided that the backend will persist revoked refresh tokens in a `RevokedRefreshToken` table keyed by the token's `jti` claim, with an `expires_at` value copied from the token's own `exp`. A refresh request is rejected as revoked when its `jti` is present in this table. Logout (`ADS-FR-006-02`) and successful rotation (`ADS-FR-007-02`) each insert the token they invalidate into this table. A row past its `expires_at` carries no further meaning and may be purged.  
**Rationale:** A `jti` denylist is the minimum server-side state that satisfies the already-accepted logout-invalidation, rotation-invalidation, and revoked-token-rejection decisions; it needs no session or device model beyond the token itself, and expired rows are self-identifying for cleanup.  
**Verification impact:** Already verified by `TC-FR-006-01` (a token used for logout is subsequently rejected) and `TC-FR-007-02` / `TC-FR-007-06` (a token superseded by rotation, or already revoked, is rejected on resubmission).

---

#### ADS-FR-008-01 — Active-session access-token recovery
**Status:** Accepted  
**Requirement reference:** FR-008  
**Decision:** It is decided that the frontend API client will attempt at most one refresh after an access-token authentication failure. When refresh succeeds, the client will replace the in-memory access token and repeat the original protected request once.  
**Rationale:** One bounded refresh and replay can recover an active session without creating retry loops.  
**Verification impact:** Frontend integration tests will verify one refresh attempt, access-token replacement, and one replay of the original request.

---

#### ADS-FR-008-02 — Failed active-session refresh outcome
**Status:** Accepted  
**Requirement reference:** FR-008  
**Decision:** It is decided that a failed refresh during an active session will clear authentication state, redirect to the login page, and display a session-expired message carried through navigation state.  
**Rationale:** The user must be informed when an active session can no longer be renewed.  
**Verification impact:** A frontend integration test will verify state clearing, login-page redirection, and the session-expired message after failed active-session refresh.

---

#### ADS-FR-008-03 — Failed initialization refresh outcome
**Status:** Accepted  
**Requirement reference:** FR-008  
**Decision:** It is decided that a failed initialization refresh after page reload will open the login page without a retry loop and without a session-expired message.  
**Rationale:** An unsuccessful restoration attempt on application startup is an unauthenticated load, not necessarily an expired active session.  
**Verification impact:** A frontend integration test will verify login-page navigation without repeated refresh requests or a session-expired message.

---

#### ADS-FR-008-04 — Single-flight refresh coordination
**Status:** Accepted  
**Requirement reference:** FR-008  
**Decision:** It is decided that the frontend API client will permit at most one access-token refresh request to be in progress within one frontend application instance. Protected requests that encounter an access-token authentication failure while that refresh is in progress will await the same refresh result and will not initiate another refresh request.  
**Rationale:** Sharing one in-progress refresh prevents concurrent requests from submitting the same rotating refresh token and producing inconsistent session outcomes.  
**Verification impact:** Frontend integration tests will issue multiple concurrent protected requests that receive access-token authentication failures and verify that exactly one refresh request is sent and that every affected request awaits the same refresh result.

---

#### ADS-FR-009-01 — Account timezone update
**Status:** Accepted  
**Requirement reference:** FR-009  
**Decision:** It is decided that the authenticated account resource will expose `PATCH /api/v1/account/` for updating `timezone`. The endpoint will accept only supported IANA identifiers and will permit the authenticated user to modify only their own account.  
**Rationale:** A partial-update account endpoint is sufficient for the single editable account preference in the MVP.  
**Verification impact:** The API integration test will update the timezone and then retrieve the account to confirm persistence.

---

#### ADS-FR-048-01 — Authenticated password change
**Status:** Accepted  
**Requirement reference:** FR-048  
**Decision:** It is decided that authenticated password change will be provided through `POST /api/v1/account/password/`, using the standard authenticated (bearer-token) domain-API permission with no CSRF requirement. The request will carry `current_password` and `new_password`. The backend will verify `current_password` against the stored hash and validate `new_password` against the password policy accepted in `ADS-FR-003-01` and `ADS-SEC-003-01` before calling Django's password-setting API; a failure of either check will reject the request without modifying the stored password. Success will return `200 OK` with an empty body. Password reset for an unauthenticated user is out of scope for the MVP.  
**Rationale:** Reusing the domain-API bearer-authentication pattern avoids a bespoke authentication path; verifying the current password prevents a bare access token from silently taking over the account; reusing the existing password policy keeps registration and change consistent. Password reset depends on out-of-band delivery (typically email), which is itself excluded from this MVP, so it is excluded alongside it rather than built on a non-standard substitute.  
**Verification impact:** An API integration test will submit a correct current password with a compliant new password and confirm subsequent login requires the new password; will submit an incorrect current password and confirm the stored password is unchanged; and will submit a new password failing the accepted policy and confirm rejection.

---

### 4.2 Examination Records

#### ADS-FR-010-01 — Draft examination creation
**Status:** Accepted  
**Requirement reference:** FR-010  
**Decision:** It is decided that `POST /api/v1/examinations/` will create a draft when `status` is `draft`. The serializer will require `title`, allow all other examination fields to be omitted, and preserve every valid optional value that is supplied.  
**Rationale:** Draft creation must support incomplete records without discarding information already known by the user.  
**Verification impact:** The integration test will create a draft with a title and selected optional values and confirm that the saved response preserves them.

---

#### ADS-FR-011-01 — Planned examination creation
**Status:** Accepted  
**Requirement reference:** FR-011  
**Decision:** It is decided that `POST /api/v1/examinations/` will create a planned examination when `status` is `planned`, `title` is present, and `scheduled_date` is present. `category` and `scheduled_time` will remain optional.  
**Rationale:** This directly implements the minimum data required for a planned record.  
**Verification impact:** The integration test will create a planned record with title and scheduled date only and confirm the stored status and values.

---

#### ADS-FR-012-01 — Examination status enumeration
**Status:** Accepted  
**Requirement reference:** FR-012  
**Decision:** It is decided that examination status will be stored in one constrained field using the values `draft`, `planned`, `completed`, `cancelled`, and `missed`.  
**Rationale:** A constrained enumeration provides one consistent representation of the examination lifecycle across the database, API, and user interface.  
**Verification impact:** Serializer validation tests will accept each listed value and reject every unlisted value.

---

#### ADS-FR-013-01 — Optional examination metadata
**Status:** Accepted  
**Requirement reference:** FR-013  
**Decision:** It is decided that `medical_specialty`, `location`, and `notes` will be nullable or blank optional fields on the examination record and writable through examination create and update serializers.  
**Rationale:** These fields store general organizational metadata without making any of them mandatory.  
**Verification impact:** The integration test will save, retrieve, update, and clear each optional field.

---

#### ADS-FR-014-01 — Status-dependent required fields
**Status:** Accepted  
**Requirement reference:** FR-014  
**Decision:** It is decided that examination validation will always require `title`; require `scheduled_date` when status is `planned`, `cancelled`, or `missed`; and require `completed_date` when status is `completed`. These rules will be enforced in backend serializer or domain validation for both create and update operations.  
**Rationale:** Central backend validation prevents clients from creating states that violate the requirement.  
**Verification impact:** Validation tests will omit each required field for each applicable status and assert the corresponding field error.

---

#### ADS-FR-014-02 — Future completion-date rejection
**Status:** Accepted  
**Requirement reference:** FR-014  
**Decision:** It is decided that a record whose status is `completed` must have a `completed_date` not later than the authenticated user's current local date. The backend will reject create and update requests that would produce a completed record with a future completion date.  
**Rationale:** A completed examination represents an event that has already occurred, and enforcing the boundary globally prevents invalid records from entering past, calendar, and dashboard results.  
**Verification impact:** Validation tests will freeze the user's local date and verify acceptance on that date and rejection on the following date for both create and update operations.

---

#### ADS-FR-015-01 — Category and status reference validation
**Status:** Accepted  
**Requirement reference:** FR-015  
**Decision:** It is decided that a supplied category identifier will be resolved only against existing system-defined category records and that status will be validated by the examination status enumeration before persistence.  
**Rationale:** Reference and enumeration validation prevent dangling categories and unsupported statuses.  
**Verification impact:** Validation tests will submit an unknown category identifier and an unsupported status and confirm rejection.

---

#### ADS-FR-016-01 — Draft-to-planned transition
**Status:** Accepted  
**Requirement reference:** FR-016  
**Decision:** It is decided that a draft will be changed to planned through the normal examination update endpoint. The update will succeed only when the resulting record contains a `scheduled_date`; category and scheduled time will not be required.  
**Rationale:** Using the standard update operation avoids a special transition endpoint for a simple MVP state change.  
**Verification impact:** The integration test will patch a draft with `status: planned` and a scheduled date and confirm the transition.

---

#### ADS-FR-017-01 — Draft reminder prohibition
**Status:** Accepted  
**Requirement reference:** FR-017  
**Decision:** It is decided that reminder creation and update validation will load the related examination and reject the operation when its status is `draft`.  
**Rationale:** The rule must be enforced by the backend rather than hidden only in the interface.  
**Verification impact:** The API validation test will attempt reminder creation for a draft and assert a business-rule error.

---

#### ADS-FR-018-01 — Draft recurrence prohibition
**Status:** Accepted  
**Requirement reference:** FR-018  
**Decision:** It is decided that recurrence creation and update validation will load the related examination and reject the operation when its status is `draft`.  
**Rationale:** The backend must prevent recurrence configuration regardless of the client used.  
**Verification impact:** The API validation test will attempt recurrence creation for a draft and assert a business-rule error.

---

#### ADS-FR-019-01 — Draft exclusion from time-based views
**Status:** Accepted  
**Requirement reference:** FR-019  
**Decision:** It is decided that upcoming, overdue, and calendar query builders will explicitly exclude records whose status is `draft` before applying date conditions.  
**Rationale:** An explicit exclusion prevents draft records with partially entered dates from leaking into scheduled views.  
**Verification impact:** Integration tests will create dated and undated drafts and verify that neither appears in the three affected results.

---

#### ADS-FR-020-01 — Examination list page states
**Status:** Accepted  
**Requirement reference:** FR-020  
**Decision:** It is decided that the examination list page will request the authenticated user's examination collection from `GET /api/v1/examinations/` and will render four mutually exclusive states: loading, empty, populated, and error.  
**Rationale:** Explicit states prevent ambiguous blank screens and satisfy the required frontend behavior.  
**Verification impact:** Frontend tests will independently render and verify each state.

---

#### ADS-FR-021-01 — Owned examination detail retrieval
**Status:** Accepted  
**Requirement reference:** FR-021  
**Decision:** It is decided that `GET /api/v1/examinations/{id}/` will retrieve an examination only from a queryset already restricted to the authenticated user and will return all approved stored fields plus approved derived fields.  
**Rationale:** Ownership filtering at query level prevents detail retrieval across accounts.  
**Verification impact:** The integration test will retrieve an owned record and compare the returned fields with stored values.

---

#### ADS-FR-022-01 — Owned examination update
**Status:** Accepted  
**Requirement reference:** FR-022  
**Decision:** It is decided that `PATCH /api/v1/examinations/{id}/` will be the primary edit operation, with optional full replacement through `PUT` only if retained in the documented API contract. The writable queryset will be restricted to the authenticated user and the resulting record will pass complete status-dependent validation.  
**Rationale:** Partial updates suit form editing while final-state validation preserves record consistency.  
**Verification impact:** The integration test will update an owned record and confirm persistence after a new retrieval.

---

#### ADS-FR-023-01 — Permanent examination deletion
**Status:** Accepted  
**Requirement reference:** FR-023  
**Decision:** It is decided that deleting an owned examination through `DELETE /api/v1/examinations/{id}/` will permanently remove the examination and its associated reminder and recurrence configuration through cascading deletion.  
**Rationale:** This keeps deletion behavior consistent and prevents dependent records from remaining after their examination is removed.  
**Verification impact:** An integration test will confirm that the examination, reminder, and recurrence configuration can no longer be retrieved after deletion.

---

#### ADS-FR-023-02 — Source-occurrence reference on deletion
**Status:** Accepted  
**Requirement reference:** FR-023  
**Decision:** It is decided that deleting an owned examination will set `source_occurrence` to null on every generated examination that referenced it, rather than deleting those generated examinations or blocking the deletion. The generated examinations, their own reminders, and their own recurrence rules remain otherwise unchanged.  
**Rationale:** A generated occurrence is an independent examination record that may already carry its own history, reminder, or recurrence configuration; deleting an unrelated source record should not silently destroy or block changes to it. This mirrors the existing pattern of nulling a derived reference when its basis is removed, such as `next_due_date` becoming null when `scheduled_date` is absent.  
**Verification impact:** An integration test will delete a source examination that has a generated next occurrence and confirm that the generated examination still exists, is otherwise unchanged, and has `source_occurrence` set to null.

---

#### ADS-FR-024-01 — Delete confirmation dialog
**Status:** Accepted  
**Requirement reference:** FR-024  
**Decision:** It is decided that the frontend will open a modal confirmation dialog before sending an examination delete request. The destructive action will not be executed on dialog opening or cancellation and will execute only after explicit confirmation.  
**Rationale:** A separate confirmation step reduces accidental permanent deletion.  
**Verification impact:** The frontend integration test will verify cancel and confirm paths and the number of delete requests sent.

---

#### ADS-FR-025-01 — Single system category relationship
**Status:** Accepted  
**Requirement reference:** FR-025  
**Decision:** It is decided that an examination will have one nullable foreign key to `ExaminationCategory`. The field will accept at most one category and category management endpoints will be read-only for MVP users.  
**Rationale:** A nullable many-to-one relationship supports one optional system category without introducing user-managed taxonomy.  
**Verification impact:** The integration test will assign one available category and confirm it is returned with the examination.

---

#### ADS-FR-026-01 — System category seed data
**Status:** Accepted  
**Requirement reference:** FR-026  
**Decision:** It is decided that the eight required categories will be inserted by an idempotent data migration using stable unique slugs. Their API resource will be read-only, and duplicate names or slugs will be prevented by database constraints.  
**Rationale:** Seeded stable records guarantee availability across environments and prevent duplicates.  
**Verification impact:** The integration test will retrieve the category collection and compare it with the required set exactly once each.

---

#### ADS-FR-027-01 — Uncategorized presentation fallback
**Status:** Accepted  
**Requirement reference:** FR-027  
**Decision:** It is decided that the API will represent an unassigned category as `null`, while shared frontend presentation logic will display the label `Uncategorized` whenever the category value is null.  
**Rationale:** Keeping null in the data model avoids creating a misleading database category while providing the required user-facing label.  
**Verification impact:** The component test will render a record with a null category and assert the fallback text.

---

#### ADS-FR-028-01 — Title search
**Status:** Accepted  
**Requirement reference:** FR-028  
**Decision:** It is decided that `GET /api/v1/examinations/` will support a `search` query parameter that performs a case-insensitive containment search against the authenticated user's examination titles.  
**Rationale:** A single title-specific search parameter is sufficient for the stated MVP requirement.  
**Verification impact:** The integration test will create distinct titles and verify exact inclusion and exclusion behavior.

---

#### ADS-FR-029-01 — Status and category filters
**Status:** Accepted  
**Requirement reference:** FR-029  
**Decision:** It is decided that the examination list endpoint will support `status=<status>` and `category=<category-id>` query parameters, validate supplied values, and combine both filters with AND semantics when both are present.  
**Rationale:** Standard query parameters allow filters to compose without separate endpoints.  
**Verification impact:** The integration test will verify each filter separately and in combination.

---

#### ADS-FR-030-01 — Scheduled-date ordering with nulls last
**Status:** Accepted  
**Requirement reference:** FR-030  
**Decision:** It is decided that the examination list endpoint will accept `ordering=scheduled_date` and `ordering=-scheduled_date`. Both database orderings will explicitly place null scheduled dates after all dated records, with a stable secondary ordering by identifier.  
**Rationale:** Explicit null placement avoids database-dependent ordering and keeps result ordering deterministic.  
**Verification impact:** The integration test will verify ascending, descending, null-last behavior, and deterministic ties.

---

### 4.3 Past, Upcoming, and Overdue Examinations

#### ADS-FR-031-01 — Past examination query
**Status:** Accepted  
**Requirement reference:** FR-031  
**Decision:** It is decided that past examinations will be requested through `GET /api/v1/examinations/?time_state=past`. The backend will include completed records whose `completed_date` is on or before the authenticated user's current local date and cancelled or missed records whose `scheduled_date` is on or before that date; it will exclude planned, draft, and future records.  
**Rationale:** A derived list filter centralizes ownership, serialization, and filtering.  
**Verification impact:** The integration test will freeze time and verify inclusion by the status-specific relevant date.

---

#### ADS-FR-032-01 — Upcoming examination query
**Status:** Accepted  
**Requirement reference:** FR-032  
**Decision:** It is decided that upcoming examinations will be requested through `GET /api/v1/examinations/?time_state=upcoming`. The backend will include only planned records that are not overdue: future-date records, current-date records without a scheduled time, and current-date records whose scheduled time has not passed in the user's timezone.  
**Rationale:** The query mirrors the requirement's date-only and time-specific boundary behavior.  
**Verification impact:** The integration test will freeze the user's local date and time and verify every boundary case.

---

#### ADS-FR-033-01 — Overdue is a derived state
**Status:** Accepted  
**Requirement reference:** FR-033  
**Decision:** It is decided that the application will derive an examination's overdue state when data is queried or presented by evaluating its `status`, `scheduled_date`, optional `scheduled_time`, the authenticated user's timezone, and the current time.  
**Rationale:** Deriving the state keeps the result current as time passes and makes rescheduling immediately reflected in examination lists, calendar views, and dashboard data.  
**Verification impact:** Tests will freeze time before and after a boundary and confirm that the same unchanged record changes derived state.

---

#### ADS-FR-033-02 — Overdue date and time boundary
**Status:** Accepted  
**Requirement reference:** FR-033  
**Decision:** It is decided that a planned examination is overdue when its scheduled date is before the user's current local date, or when its scheduled date equals the current local date and its scheduled time is present and earlier than the current local time. A current-date record without a scheduled time is not overdue.  
**Rationale:** Separate date and optional time fields require explicit boundary logic rather than comparison with one timestamp.  
**Verification impact:** The integration test will cover past date, current date with past time, current date with future time, and current date without time.

---

#### ADS-FR-034-01 — Overdue status restriction
**Status:** Accepted  
**Requirement reference:** FR-034  
**Decision:** It is decided that the overdue query will begin with `status = planned`; completed, cancelled, missed, and draft records will not be evaluated as overdue even when their dates are in the past.  
**Rationale:** Restricting by lifecycle status keeps overdue as a planning state rather than a general past-date label.  
**Verification impact:** The integration test will create past records in every status and confirm that only the planned record is returned.

---

### 4.4 In-Application Reminders

#### ADS-FR-035-01 — Reminder persistence and mutation
**Status:** Accepted  
**Requirement reference:** FR-035  
**Decision:** It is decided that each examination may have at most one reminder record containing `examination`, positive integer `offset_days`, `due_date`, `is_active`, and audit timestamps. Authenticated create, update, and disable operations will be exposed through a documented reminder endpoint and will be limited to the examination owner.  
**Rationale:** A one-to-one reminder model matches the single configurable reminder described for the MVP.  
**Verification impact:** Integration tests will create, update, and disable a reminder and reject zero, negative, decimal, and non-numeric offsets.

---

#### ADS-FR-035-02 — Reminder status restriction beyond drafts
**Status:** Accepted  
**Requirement reference:** FR-035  
**Decision:** It is decided that reminder creation, offset updates, and reactivation (setting `is_active` to `true`) will be validated against the related examination's current status and rejected whenever that status is not `planned`, covering `completed`, `cancelled`, and `missed` source examinations in addition to the `draft` case already rejected under ADS-FR-017-01. Disabling an existing reminder remains allowed regardless of examination status.  
**Rationale:** `domain_model.md` and `api_contract.md` restrict active reminder configuration to planned examinations generally, not only to excluding drafts; the reminder endpoint must enforce the full restriction rather than the draft-specific subset, matching the equivalent recurrence restriction in ADS-FR-039-01.  
**Verification impact:** Integration tests will attempt reminder creation, offset update, and reactivation for `completed`, `cancelled`, and `missed` source examinations and assert a business-rule error for each, and will confirm that disabling a reminder still succeeds regardless of examination status.

---

#### ADS-FR-036-01 — Reminder due-date calculation
**Status:** Accepted  
**Requirement reference:** FR-036  
**Decision:** It is decided that reminder `due_date` will be calculated as `scheduled_date - offset_days` using calendar-date arithmetic and stored as a nullable date. Recalculation will occur whenever the examination scheduled date or reminder offset changes, and `due_date` will be set to null when `scheduled_date` is absent.  
**Rationale:** The reminder uses a whole-number day offset and therefore does not require a timestamp, while a nullable value prevents an inactive retained reminder from exposing a stale due date after its examination loses its scheduled date.  
**Verification impact:** Integration tests will compare stored due dates with expected calculations, verify recalculation after date and offset changes, and verify a null due date when the examination has no scheduled date.

---

#### ADS-FR-037-01 — Due reminder query and display
**Status:** Accepted  
**Requirement reference:** FR-037  
**Decision:** It is decided that the frontend will request active reminders whose `due_date` is on or before the authenticated user's current local date and render only those reminders in the due-reminders area.  
**Rationale:** Filtering on the backend gives every client the same definition of currently due.  
**Verification impact:** The frontend integration test will receive due, future, and inactive reminder fixtures and verify that only due active items are displayed.

---

#### ADS-FR-038-01 — Automatic reminder deactivation
**Status:** Accepted  
**Requirement reference:** FR-038  
**Decision:** It is decided that changing an examination from `planned` to `draft`, `completed`, `cancelled`, or `missed` will set its associated reminder's `is_active` value to false within the same database transaction. Changing an examination to `planned` will not reactivate the reminder automatically.  
**Rationale:** An active reminder is valid only for a planned examination, while retaining the inactive record preserves the configured offset.  
**Verification impact:** Integration tests will verify deactivation for all four non-planned target statuses and confirm that a later transition to `planned` does not reactivate the reminder.

---

### 4.5 Recurring Examinations

#### ADS-FR-039-01 — Supported recurrence configuration
**Status:** Accepted  
**Requirement reference:** FR-039  
**Decision:** It is decided that each examination may have at most one recurrence rule whose interval field is constrained to `monthly`, `six_months`, or `yearly`. Creation and update will reject every other interval and every non-planned source examination.  
**Rationale:** A constrained one-to-one rule is sufficient for the three MVP recurrence patterns.  
**Verification impact:** Validation tests will accept the three values and reject unsupported intervals and invalid source statuses.

---

#### ADS-FR-039-02 — Recurrence persistence across status changes
**Status:** Accepted  
**Requirement reference:** FR-039  
**Decision:** It is decided that an existing recurrence rule will remain attached when its examination changes status. The status change will not delete or modify the recurrence rule.  
**Rationale:** Retaining the rule preserves the configured interval for later correction, replanning, or next-occurrence creation.  
**Verification impact:** Integration tests will change a recurring examination to each non-planned status and confirm that the same recurrence rule remains attached and unchanged.

---

#### ADS-FR-040-01 — Next-due-date arithmetic
**Status:** Accepted  
**Requirement reference:** FR-040  
**Decision:** It is decided that the backend will calculate recurrence with calendar-month arithmetic: add one month for `monthly`, six months for `six_months`, and one year for `yearly`. When the target month lacks the source day, the result will use the target month's last valid day; leap-day yearly recurrence will therefore resolve to the last valid February day in non-leap years.  
**Rationale:** Calendar arithmetic preserves expected monthly and yearly behavior better than fixed day counts.  
**Verification impact:** Integration tests will cover ordinary dates, month-end dates, February 29, and transitions into non-leap years.

---

#### ADS-FR-040-02 — Unavailable next due date
**Status:** Accepted  
**Requirement reference:** FR-040  
**Decision:** It is decided that the recurrence representation will return `next_due_date` as null when the source examination has no `scheduled_date`.  
**Rationale:** A retained recurrence rule can remain attached to a draft or completed examination whose scheduled date has been removed, so no recurrence date can be derived until a scheduled date exists.  
**Verification impact:** An integration test will retrieve a retained recurrence rule whose source has no scheduled date and confirm that `next_due_date` is null.

---

#### ADS-FR-041-01 — User-requested next occurrence creation
**Status:** Accepted  
**Requirement reference:** FR-041  
**Decision:** It is decided that `POST /api/v1/examinations/{id}/next-occurrence/` will create exactly one new planned examination from the source examination and its recurrence rule. The operation will run in a transaction, use the calculated next due date, and record the source occurrence so a repeated request cannot create a duplicate for the same due date.  
**Rationale:** An explicit action endpoint reflects that occurrence creation is user-triggered and must be protected against accidental duplicate submissions.  
**Verification impact:** The integration test will call the action, verify one created record and its date, then repeat the request and verify that no second duplicate is created.

---

#### ADS-FR-041-02 — Next-occurrence source status
**Status:** Accepted  
**Requirement reference:** FR-041  
**Decision:** It is decided that next-occurrence creation will accept source examinations with status `planned`, `completed`, `cancelled`, or `missed` and reject source examinations with status `draft`. The source must contain `scheduled_date` and an attached recurrence rule.  
**Rationale:** A completed, cancelled, or missed occurrence may still define the next scheduled occurrence, while a draft is not sufficiently planned to serve as a recurrence source.  
**Verification impact:** Integration tests will verify successful creation from each accepted source status and a business-rule error for a draft source.

---

#### ADS-FR-041-03 — Repeated next-occurrence request response
**Status:** Accepted  
**Requirement reference:** FR-041  
**Decision:** It is decided that a repeated next-occurrence request resolving to an existing generated occurrence for the same source examination and calculated due date will not create another record and will return `200 OK` with the existing generated examination representation. An initial successful creation will continue to return `201 Created`.  
**Rationale:** A repeated request is normally an accidental resubmission rather than an error, so returning the existing occurrence keeps the client's view correct without adding a second record or a new error status, while the differing success status still distinguishes a creation from a repeat.  
**Verification impact:** An API integration test will call the action twice for the same source and due date, assert `201 Created` followed by `200 OK`, and confirm that both responses describe the same single generated examination.

---

#### ADS-FR-041-04 — Generated next-occurrence field values
**Status:** Accepted  
**Requirement reference:** FR-041  
**Decision:** It is decided that a generated next occurrence will copy `title`, `category`, `medical_specialty`, `scheduled_time`, and `location` from its source examination; will set `status` to `planned`, `scheduled_date` to the calculated next due date, and `source_occurrence` to the source examination; and will leave `notes` and `completed_date` empty. No reminder and no recurrence rule will be created for the generated occurrence.  
**Rationale:** Copying the fields that identify a repeating appointment avoids re-entering unchanged information, while `notes` commonly describe one specific past visit and a planned occurrence has no completion date. Creating a reminder or recurrence rule automatically would attach dependent records the user did not request, and the contract provides no delete operation for either, so both remain explicit user actions on the new occurrence.  
**Verification impact:** An API integration test will create a next occurrence from a fully populated source and will assert each copied value, the planned status, the calculated scheduled date, the recorded source occurrence, empty `notes` and `completed_date`, and the absence of a reminder and recurrence rule.

---

### 4.6 Calendar

#### ADS-FR-042-01 — Monthly calendar data placement
**Status:** Accepted  
**Requirement reference:** FR-042  
**Decision:** It is decided that monthly calendar data will be obtained from a date-range API query. Planned, cancelled, and missed records will be assigned to `scheduled_date`; completed records will be assigned to `completed_date`; draft records and records lacking the required display date will be excluded.  
**Rationale:** A status-specific calendar date produces the required placement without duplicating examination records.  
**Verification impact:** The frontend integration test will render a selected month and verify each status on its designated date.

---

#### ADS-FR-042-02 — Calendar date-range parameter validation
**Status:** Accepted  
**Requirement reference:** FR-042  
**Decision:** It is decided that the calendar endpoint will require both `start_date` and `end_date` query parameters in `YYYY-MM-DD` format, will reject a request where either parameter is missing or malformed, and will reject a request where `start_date` is later than `end_date`.  
**Rationale:** The contract already promises this validation; stating it as an accepted decision gives it a requirement-level parent and makes it verifiable at the API layer rather than left implicit in `api_contract.md`.  
**Verification impact:** An API integration test will confirm rejection of a request missing either parameter, a request with a malformed date, and a request where `start_date` is later than `end_date`.

---

#### ADS-FR-043-01 — Calendar state indicators
**Status:** Accepted  
**Requirement reference:** FR-043  
**Decision:** It is decided that the calendar presentation will map `planned`, `completed`, `cancelled`, `missed`, and derived `overdue` to distinct combinations of label, icon or shape, and visual styling. Color will not be the sole differentiator.  
**Rationale:** Multiple cues preserve distinction for keyboard users and users with color-vision limitations.  
**Verification impact:** The component test will render each state and assert its semantic label and state-specific indicator.

---

### 4.7 Dashboard

#### ADS-FR-044-01 — Dashboard examination sections
**Status:** Accepted  
**Requirement reference:** FR-044  
**Decision:** It is decided that `GET /api/v1/dashboard/` will return separate collections named `upcoming`, `overdue`, and `recently_completed`. The frontend will render one dashboard section for each collection with its own loading-independent empty presentation.  
**Rationale:** One dashboard response reduces repeated startup requests while preserving separate section semantics.  
**Verification impact:** The frontend integration test will supply all three collections and confirm that each section renders the corresponding records.

---

#### ADS-FR-044-02 — Recently completed eligibility
**Status:** Accepted  
**Requirement reference:** FR-044  
**Decision:** It is decided that the dashboard `recently_completed` collection will include only examinations owned by the authenticated user whose status is `completed` and whose `completed_date` is between the authenticated user's current local date minus 29 days and the current local date, inclusive.  
**Rationale:** An explicit inclusive 30-date window gives recently completed a stable and testable meaning.  
**Verification impact:** An API integration test will freeze the user's local date and verify inclusion at both boundaries and exclusion immediately outside them.

---

#### ADS-FR-044-03 — Recently completed ordering
**Status:** Accepted  
**Requirement reference:** FR-044  
**Decision:** It is decided that `recently_completed` records will be ordered by `completed_date` descending and then by `id` descending.  
**Rationale:** The primary ordering shows the latest completions first, while the identifier tie-breaker makes results deterministic when multiple examinations have the same completion date.  
**Verification impact:** An API integration test will verify date ordering and deterministic identifier ordering for records sharing the same completion date.

---

#### ADS-FR-044-04 — Recently completed limit
**Status:** Accepted  
**Requirement reference:** FR-044  
**Decision:** It is decided that the dashboard `recently_completed` collection will contain at most five records after eligibility filtering and ordering have been applied. The collection will not be paginated.  
**Rationale:** The dashboard is a summary view rather than a replacement for the complete examination history.  
**Verification impact:** An API integration test will create more than five eligible records and confirm that only the first five ordered records are returned.

---

#### ADS-FR-045-01 — Dashboard status counts
**Status:** Accepted  
**Requirement reference:** FR-045  
**Decision:** It is decided that the dashboard response will contain a `status_counts` object with explicit keys for `draft`, `planned`, `completed`, `cancelled`, and `missed`. Missing database groups will be returned as zero rather than omitted.  
**Rationale:** A stable complete shape simplifies frontend charts and summary cards.  
**Verification impact:** The API integration test will compare each key with counts calculated from owned examination fixtures.

---

#### ADS-FR-046-01 — Dashboard category counts
**Status:** Accepted  
**Requirement reference:** FR-046  
**Decision:** It is decided that the dashboard response will contain `category_counts` with one count for every system-defined category and a separate `uncategorized_count` for records whose category is null. Categories with no examinations will still be returned with zero.  
**Rationale:** Returning the full category set and a stable `uncategorized_count` field provides predictable grouping and explicitly represents null categories.  
**Verification impact:** The API integration test will verify every category entry, zero-filled categories, and the `uncategorized_count` value.

---

#### ADS-FR-047-01 — Dashboard overdue count
**Status:** Accepted
**Requirement reference:** FR-047  
**Decision:** It is decided that the dashboard response will contain `overdue_count`, calculated with the same shared overdue query used by the examination list rather than with separate duplicated logic.  
**Rationale:** A shared query prevents disagreement between the dashboard count and overdue records shown elsewhere.  
**Verification impact:** The API integration test will compare `overdue_count` with the number of records returned by the overdue query for the same frozen time.

---

## 5. User Experience Design Decisions

#### ADS-UX-001-01 — Mobile-first responsive layout
**Status:** Accepted  
**Requirement reference:** UX-001  
**Decision:** It is decided that page layouts will be implemented mobile-first with base styles for phone widths and explicit tablet and desktop enhancements. Registration, login, examination list, examination form, calendar, and dashboard will avoid horizontal page scrolling at approved viewport widths.  
**Rationale:** Mobile-first rules provide a consistent minimum layout before additional space is used.  
**Verification impact:** The documented browser review will exercise the approved viewport widths and record any overflow or unusable controls.

---

#### ADS-UX-002-01 — Email field-level error presentation
**Status:** Accepted  
**Requirement reference:** UX-002  
**Decision:** It is decided that registration email errors returned by client validation or the registration API will be associated with the email control through shared form-error state and displayed immediately adjacent to that control. The field will expose the error through accessible descriptive attributes.  
**Rationale:** The user must be able to identify the exact invalid field and reason.  
**Verification impact:** Frontend tests will cover missing, malformed, and duplicate email responses and assert the rendered field association.

---

#### ADS-UX-003-01 — Password field-level error presentation
**Status:** Accepted  
**Requirement reference:** UX-003  
**Decision:** It is decided that the registration form will validate the password as required and at least eight characters before submission, while also displaying backend password errors adjacent to the password control using the same accessible field-error component.  
**Rationale:** Client validation gives immediate feedback while backend validation remains authoritative.  
**Verification impact:** Frontend tests will cover missing and short passwords and verify the field-level message.

---

#### ADS-UX-004-01 — Timezone field-level error presentation
**Status:** Accepted  
**Requirement reference:** UX-004  
**Decision:** It is decided that registration will use a required timezone selection control populated from supported values supplied by the application and will display missing or unsupported timezone errors adjacent to that control.  
**Rationale:** A constrained control reduces invalid input while preserving backend validation.  
**Verification impact:** Frontend tests will cover no selection and an API rejection for an unsupported value.

---

#### ADS-UX-005-01 — Draft examination form behavior
**Status:** Accepted  
**Requirement reference:** UX-005  
**Decision:** It is decided that the examination form will offer an explicit draft save action. In draft mode only the title field will be marked required; category, scheduled date, scheduled time, specialty, location, and notes will remain optional and their entered values will be submitted unchanged.  
**Rationale:** The form must not impose planned-record requirements on drafts.  
**Verification impact:** The frontend integration test will save a title-only draft and a draft containing selected optional information.

---

#### ADS-UX-006-01 — Planned examination form behavior
**Status:** Accepted  
**Requirement reference:** UX-006  
**Decision:** It is decided that planned mode will mark title and scheduled date as required and will leave category and scheduled time optional. The form will prevent submission only for missing required planned fields or backend validation failures.  
**Rationale:** This matches the exact planned-record minimum defined by the requirement.  
**Verification impact:** The frontend integration test will submit title and date only and verify successful creation.

---

#### ADS-UX-007-01 — Timezone-aware date and time presentation
**Status:** Accepted  
**Requirement reference:** UX-007  
**Decision:** It is decided that the authenticated account timezone will be held in application state and passed to a shared formatting utility. Timezone-aware timestamps will be converted to that zone; date-only values will be displayed as stored calendar dates and will not be shifted through UTC conversion.  
**Rationale:** Dates and instants have different semantics and must not be formatted through the same conversion path.  
**Verification impact:** Frontend tests will use fixed timestamps, date-only values, and selected timezones to verify expected output.

---

#### ADS-UX-008-01 — Input-method accessibility
**Status:** Accepted  
**Requirement reference:** UX-008  
**Decision:** It is decided that navigation and actions will use semantic interactive elements, visible keyboard focus, correctly labelled controls, focus-managed modal dialogs, and touch targets sized for practical use. No primary action will depend exclusively on hover, pointer gestures, or color.  
**Rationale:** Standard semantics support touch, mouse, and keyboard without parallel custom interaction systems.  
**Verification impact:** The documented interaction review will complete each primary flow with all three input methods.

---

## 6. Security Design Decisions

#### ADS-SEC-001-01 — Authentication required by default
**Status:** Accepted  
**Requirement reference:** SEC-001  
**Decision:** It is decided that Django REST Framework will use authenticated access as the default permission for domain APIs. Registration, login, CSRF-token retrieval, token refresh, and health check will be explicitly configured without bearer authentication. Logout will use refresh-token-cookie validation and CSRF protection instead of the default bearer permission. No other endpoint may override authenticated access without an accepted design change.  
**Rationale:** A secure default reduces the risk of accidentally exposing a new domain endpoint while allowing the authentication endpoints to use the credential appropriate to their operation.  
**Verification impact:** The API integration suite will enumerate protected endpoints, verify rejection without a valid bearer access token, and verify the separately defined refresh-cookie and CSRF controls on refresh and logout.

---

#### ADS-SEC-002-01 — Owner-scoped domain access
**Status:** Accepted  
**Requirement reference:** SEC-002  
**Decision:** It is decided that examination, reminder, and recurrence querysets will always be filtered by `request.user`; ownership fields will be assigned server-side and will not be writable by clients. Related-object validation will require the same owner.  
**Rationale:** Queryset scoping and server-assigned ownership enforce isolation for list and object operations.  
**Verification impact:** Authorization tests will attempt cross-user retrieval, update, deletion, and related-object attachment.

---

#### ADS-SEC-003-01 — Django password hashing
**Status:** Accepted  
**Requirement reference:** SEC-003  
**Decision:** It is decided that all account creation and password changes will call Django's `set_password` or approved user-manager methods and will never assign raw passwords to the model field. Registration validation will run Django's default password validators: `MinimumLengthValidator` (eight characters, matching `ADS-FR-003-01`), `CommonPasswordValidator`, `NumericPasswordValidator`, and `UserAttributeSimilarityValidator` compared against the account's email address.  
**Rationale:** Django's framework provides salted adaptive hashing and verification without custom cryptography, and its default validator set rejects common, fully numeric, and email-similar passwords without requiring bespoke validation logic.  
**Verification impact:** The backend test will inspect the stored value and verify it with Django's password-checking function, and validation tests will confirm registration is rejected for a commonly used password, an entirely numeric password, and a password matching the account's email address.

---

#### ADS-SEC-004-01 — Secrets from environment variables
**Status:** Accepted  
**Requirement reference:** SEC-004  
**Decision:** It is decided that Django secret keys, database credentials, JWT signing material, and deployment credentials will be read from environment variables. Local `.env` files will be excluded from version control and only placeholder example files may be committed.  
**Rationale:** Separating secrets from source code prevents repository disclosure and supports environment-specific deployment.  
**Verification impact:** The repository scan will search committed content for configured secrets and verify that required variables are documented without real values.

---

#### ADS-SEC-005-01 — Explicit CORS origin configuration
**Status:** Accepted  
**Requirement reference:** SEC-005  
**Decision:** It is decided that the backend will build its CORS allowlist from explicit frontend origins supplied through environment variables. Each origin will include its scheme, host, and port when applicable. Wildcard origins will not be used in production.  
**Rationale:** An explicit deployment-specific allowlist prevents arbitrary browser origins from being accepted by the backend.  
**Verification impact:** Deployment integration tests will verify that configured frontend origins are accepted, unconfigured origins are rejected, and production configuration contains no wildcard origin.

---

#### ADS-SEC-005-02 — Credentialed CORS requests and allowed headers
**Status:** Accepted  
**Requirement reference:** SEC-005  
**Decision:** It is decided that the backend will allow credentialed cross-origin requests only for origins in the configured CORS allowlist. CORS preflight responses will permit the `Authorization`, `Content-Type`, and `X-CSRFToken` request headers required by the API contract. The frontend will enable browser credentials for requests that receive, send, rotate, or clear authentication and CSRF cookies.  
**Rationale:** The selected authentication flow requires bearer authorization headers, JSON request bodies, CSRF headers, and browser-managed cookies across the deployed frontend and backend origins.  
**Verification impact:** Deployment integration tests will verify the exact allowed origin, credential support, permitted request headers, successful preflight handling, and rejection of credentialed requests from unconfigured origins.

---

#### ADS-SEC-005-03 — Django CSRF trusted-origin configuration
**Status:** Accepted  
**Requirement reference:** SEC-005  
**Decision:** It is decided that Django's CSRF trusted-origin list will be built from explicit frontend origins supplied through environment variables. Each trusted origin will include its scheme, host, and port when applicable. Wildcard trusted origins will not be used in production.  
**Rationale:** Django must explicitly trust the deployed frontend origins before accepting cross-origin state-changing requests protected by its CSRF validation.  
**Verification impact:** Deployment integration tests will verify that a valid CSRF token from a configured frontend origin is accepted and that the same request from an unconfigured origin is rejected.

---

#### ADS-SEC-005-04 — Refresh-token cookie attributes
**Status:** Accepted  
**Requirement reference:** SEC-005  
**Decision:** It is decided that the backend-issued `refresh_token` cookie will be `HttpOnly`, host-only, restricted to the `/api/v1/auth/` path, and configured to expire with the refresh token. In production it will use `Secure` and `SameSite=None`; local HTTP development may use `SameSite=Lax` without `Secure`. Cookie clearing will use the same name, path, and applicable security attributes as cookie creation.  
**Rationale:** These attributes prevent JavaScript access, limit cookie transmission to authentication routes, support the separately deployed frontend and backend, and ensure reliable cookie removal.  
**Verification impact:** Authentication integration tests will verify cookie creation, replacement, expiration, clearing, path restriction, `HttpOnly`, and the environment-specific `Secure` and `SameSite` values.

---

#### ADS-SEC-005-05 — CSRF-token bootstrap endpoint
**Status:** Accepted  
**Requirement reference:** SEC-005  
**Decision:** It is decided that the backend will expose `GET /api/v1/auth/csrf/` without bearer authentication. A credentialed request to this endpoint will set or renew the Django CSRF cookie and return the corresponding token in the JSON field `csrf_token`.  
**Rationale:** An explicit bootstrap endpoint gives the frontend the token required for subsequent CSRF-protected authentication requests.  
**Verification impact:** An authentication integration test will verify that a credentialed request succeeds without bearer authentication, sets or renews the CSRF cookie, and returns the corresponding `csrf_token` value.

---

#### ADS-SEC-005-06 — Frontend CSRF-token handling
**Status:** Accepted  
**Requirement reference:** SEC-005  
**Decision:** It is decided that the frontend will hold the `csrf_token` returned by `GET /api/v1/auth/csrf/` only in application memory and will send it in the `X-CSRFToken` header with credentialed login, refresh, and logout requests. The frontend will not read the CSRF cookie directly.  
**Rationale:** Memory-only handling supplies the required header value without making frontend behavior depend on direct cookie access.  
**Verification impact:** Frontend integration tests will verify in-memory token handling, `X-CSRFToken` transmission for login, refresh, and logout, and absence of direct CSRF-cookie reads.

---

#### ADS-SEC-005-07 — CSRF-cookie HttpOnly attribute
**Status:** Accepted  
**Requirement reference:** SEC-005  
**Decision:** It is decided that the Django CSRF cookie will use `HttpOnly=true` in local development and production.  
**Rationale:** The frontend obtains the CSRF token from the bootstrap response and therefore does not require JavaScript access to the cookie.  
**Verification impact:** Authentication integration tests will verify that the CSRF cookie is issued with `HttpOnly` in local development and production configurations.

---

#### ADS-SEC-005-08 — CSRF-cookie environment attributes
**Status:** Accepted  
**Requirement reference:** SEC-005  
**Decision:** It is decided that the Django CSRF cookie will use path `/api/v1/`. In production it will use `Secure` and `SameSite=None`; local HTTP development may use `SameSite=Lax` without `Secure`.  
**Rationale:** The environment-specific attributes support the separately deployed HTTPS frontend and backend while permitting local HTTP development.  
**Verification impact:** Configuration and authentication integration tests will verify the CSRF cookie path and the accepted production and local-development `Secure` and `SameSite` values.

---

#### ADS-SEC-006-01 — Uniform not-found behavior
**Status:** Accepted  
**Requirement reference:** SEC-006  
**Decision:** It is decided that examination object lookup will occur only inside the authenticated user's filtered queryset and will return the same HTTP 404 status and response structure when the identifier is absent or owned by another user.  
**Rationale:** The lookup sequence prevents object ownership from being disclosed.  
**Verification impact:** The integration test will compare both responses byte-for-structure except for any non-deterministic request identifier.

---

#### ADS-SEC-007-01 — Rate limits for unauthenticated authentication endpoints
**Status:** Accepted  
**Requirement reference:** SEC-007  
**Decision:** It is decided that `POST /api/v1/auth/register/` and `POST /api/v1/auth/login/` will each be limited to 10 requests per minute per client IP address, and `POST /api/v1/auth/refresh/` will be limited to 30 requests per minute per client IP address, enforced with Django REST Framework's throttling framework. A request over the limit will receive `429 Too Many Requests` with a `Retry-After` header giving the number of seconds until the limit window resets.  
**Rationale:** These three endpoints are unauthenticated, state-changing, and internet-exposed, making them the primary surface for credential stuffing and registration spam; per-IP throttling limits abuse before any account-scoped state exists. DRF's built-in throttling classes avoid a bespoke rate-limiting implementation.  
**Verification impact:** An API integration test will exceed each endpoint's configured limit and confirm that the next request returns `429 Too Many Requests` with a `Retry-After` header, and that requests succeed again once the window elapses.

---

## 7. Privacy Design Decisions

#### ADS-PRV-001-01 — Approved examination field whitelist
**Status:** Accepted  
**Requirement reference:** PRV-001  
**Decision:** It is decided that the examination model and writable serializers will contain only fields listed in the approved domain model. Adding any new stored examination field will require an approved requirements and design change before migration creation.  
**Rationale:** A controlled whitelist prevents silent expansion into sensitive clinical data.  
**Verification impact:** The data-model review will compare model and serializer fields with the approved domain model.

---

#### ADS-PRV-002-01 — Examination creation data boundary
**Status:** Accepted  
**Requirement reference:** PRV-002  
**Decision:** It is decided that examination creation will accept the appointment and examination metadata defined by the approved domain model and will apply validation to the fields required for the selected examination status.  
**Rationale:** This keeps the creation contract aligned with the approved domain model and the status-specific requirements.  
**Verification impact:** API integration tests will create each supported examination status using its required appointment and examination metadata.

---

#### ADS-PRV-003-01 — Non-clinical purpose statement
**Status:** Accepted  
**Requirement reference:** PRV-003  
**Decision:** It is decided that a dedicated informational page, reachable from unauthenticated and authenticated navigation, will display the statement that the application is an organizational tool and does not provide medical advice, diagnosis, treatment, or emergency assistance.  
**Rationale:** The limitation must be visible without requiring an account and remain reachable after login.  
**Verification impact:** The component test will render the designated page and assert all required limitations.

---

## 8. Technical and Operational Design Decisions

#### ADS-TECH-001-01 — Versioned documented JSON API
**Status:** Accepted  
**Requirement reference:** TECH-001  
**Decision:** It is decided that backend routes will be namespaced under `/api/v1/`, accept and return JSON for MVP domain operations, and be documented in an OpenAPI contract maintained with the implementation. The React application will consume the API only through that contract.  
**Rationale:** Versioning and a machine-readable contract support an interface independent of the frontend.  
**Verification impact:** Contract tests will exercise every documented MVP endpoint without using browser-specific rendering behavior.

---

#### ADS-TECH-002-01 — Date, time, and timestamp field types
**Status:** Accepted  
**Requirement reference:** TECH-002  
**Decision:** It is decided that scheduled calendar dates will use a database date field, optional scheduled times will use a separate nullable time field, and values representing real instants such as audit timestamps will use timezone-aware datetime fields with Django timezone support enabled.  
**Rationale:** Separate field types preserve date-only meaning and avoid inventing a time when none is known.  
**Verification impact:** Model tests will round-trip a date-only record, a date plus optional time, and a timezone-aware timestamp.

---

#### ADS-TECH-003-01 — Environment-specific settings
**Status:** Accepted  
**Requirement reference:** TECH-003  
**Decision:** It is decided that runtime configuration will be loaded from environment variables through a typed settings layer or explicit parser, with separate development and production defaults and fail-fast validation for required production values.  
**Rationale:** Typed environment loading reduces accidental string coercion and prevents silent production misconfiguration.  
**Verification impact:** Configuration tests will start the settings loader with development and production values and assert the resulting settings.

---

#### ADS-TECH-004-01 — Health-check endpoint
**Status:** Accepted  
**Requirement reference:** TECH-004  
**Decision:** It is decided that `GET /api/v1/health/` will be unauthenticated and return HTTP 200 with a minimal JSON body such as `{"status": "ok"}` when the web process is serving requests. It will not expose configuration or secret values.  
**Rationale:** A minimal endpoint supports deployment checks without leaking internal information.  
**Verification impact:** The integration test will call the route anonymously and assert its status and exact public response fields.

---

#### ADS-TECH-005-01 — Production debug disabled
**Status:** Accepted  
**Requirement reference:** TECH-005  
**Decision:** It is decided that production settings will set `DEBUG = False` unconditionally and will fail application startup when mandatory production configuration is absent rather than falling back to development settings.  
**Rationale:** Fail-fast production configuration prevents debug pages and accidental insecure defaults.  
**Verification impact:** The deployment configuration test will load production settings and assert that debug mode cannot be enabled by omission.

---

#### ADS-TECH-006-01 — HTTPS-only deployment
**Status:** Accepted  
**Requirement reference:** TECH-006  
**Decision:** It is decided that public frontend and backend deployment URLs will use HTTPS, the backend will trust only the configured reverse-proxy HTTPS header, and production security settings will mark authentication cookies secure and redirect direct HTTP requests where the platform supports it.  
**Rationale:** Transport encryption protects credentials and application data in transit.  
**Verification impact:** The deployment smoke test will verify HTTPS URLs and confirm that normal application flows do not require plain HTTP.

---

#### ADS-TECH-007-01 — Repository operating documentation
**Status:** Accepted  
**Requirement reference:** TECH-007  
**Decision:** It is decided that the repository will contain maintained instructions for local setup, environment variables, dependency installation, database migrations, backend and frontend tests, production builds, and deployment. Commands will be copyable and tied to the actual repository structure.  
**Rationale:** Operational documentation is part of the deliverable and must be executable by another developer.  
**Verification impact:** The clean-environment review will follow the instructions without undocumented corrective steps.

---

## 9. Change Control

A proposed design decision becomes accepted only after review.

When a design decision changes:

1. update only the decision attached to its single requirement;
2. confirm that the requirement remains satisfied;
3. update the domain model, API contract, user flow, test specification, and implementation tasks where applicable;
4. preserve the requirement identifier;
5. add another design decision under the same requirement when the new concern is separate rather than expanding one decision to cover another requirement.

## 10. Traceability Summary

- Requirement references represented: **73**
- Design decisions recorded: **117**
- Accepted design decisions: **117**
- Proposed design decisions: **0**
- Requirements with multiple design decisions: **FR-005, FR-006, FR-007, FR-008, FR-014, FR-023, FR-033, FR-035, FR-039, FR-040, FR-041, FR-042, FR-044, SEC-005**
- Design decisions linked to more than one requirement: **0**
- Requirement statements duplicated from `requirements_specification.md`: **0**