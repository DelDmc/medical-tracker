# Medical Tracker Application — Application Test Specification

## 1. Purpose

This document defines the test cases that verify the requirements recorded in `requirements_specification.md` for the Medical Tracker Application MVP.

`requirements_specification.md` remains the source of truth for required behavior. This document translates each requirement's stated verification method into concrete, executable test cases. It references requirement identifiers for traceability but does not restate requirement text; where a concrete field name, endpoint, status code, or boundary value is needed to make a test case executable, it is drawn from `api_contract.md`, `domain_model.md`, and the accepted decisions in `design_specification.md`.

This document occupies position 5 in the source-of-truth hierarchy defined in `product_definition.md`. It must not introduce, weaken, or contradict behavior defined by a higher-precedence document.

## 2. Document Status

**Status:** Accepted

Every test case recorded in this document is accepted for implementation. Section 11 records the current test-case count and traceability summary.

## 3. Conventions

### 3.1 Test case identifier

Each test case has a unique identifier in the form `TC-<requirement-id>-NN`, for example `TC-FR-001-01`, `TC-SEC-002-03`. The identifier's requirement segment names the single requirement the test case verifies. `NN` is a two-digit sequence number, unique within that requirement.

### 3.2 Given/When/Then format

Each test case is written in standard three-part BDD form:

- **Given** — the system state and preconditions before the action;
- **When** — the single action or event under test;
- **Then** — the expected, observable outcome.

A test case may use **And** to chain an additional Given, When, or Then step of the same kind. Distinct conditions (for example, separate boundary values) are written as separate test cases rather than as a branch inside one test case.

### 3.3 Layer

Each test case states the verification layer that exercises it, matching the terminology already used by `requirements_specification.md` and `design_specification.md`: `API integration test`, `API validation test`, `API authorization test`, `Backend model test`, `Frontend integration test`, `Frontend component test`, `Configuration test`, `Deployment integration test`, `Deployment smoke test`, `Data-model review`, `Repository secret scan`, `Contract test`, or `Documented review` (a manual, recorded review rather than an automated test).

### 3.4 Linking test code to test cases

When a test case is implemented in code, the test's name or docstring must include its `TC-<requirement-id>-NN` identifier so the mapping between a written test and this specification remains traceable in both directions. One test case may be implemented by exactly one automated test; a manual `Documented review` test case is satisfied by the recorded review artifact instead of code.

## 4. Traceability Rules

1. Each test case references exactly one requirement.
2. One requirement may have more than one test case when full coverage of its stated verification method requires separate scenarios.
3. A test case must not reference or combine multiple requirements.
4. Test case identifiers remain stable once referenced by test code; a superseded test case is marked **Superseded** rather than renumbered.
5. Requirement statements are not reproduced in this document; they remain only in `requirements_specification.md`.
6. When a requirement changes, the test cases referencing that requirement are reviewed for direct impact. Secondary impacts on other requirements are handled through separate test cases under those requirements.

## 5. Test Cases — Functional Requirements

### 5.1 Account and Session Management

#### TC-FR-001-01 — Registration with all required fields creates an account
**Requirement reference:** FR-001  
**Layer:** API integration test  
**Given** no account exists for the email `person@example.com`  
**When** the client submits `POST /api/v1/auth/register/` with a valid `email`, `password`, and supported `timezone`  
**Then** the response is `201 Created` and returns `id`, `email`, and `timezone` without a password field, and the account can subsequently log in with the submitted credentials.

---

#### TC-FR-002-01 — Registration rejects a missing email
**Requirement reference:** FR-002  
**Layer:** API validation test  
**Given** a registration request with `email` omitted  
**When** the client submits `POST /api/v1/auth/register/`  
**Then** the response is `400 Bad Request` with an `email` field error and no account is created.

---

#### TC-FR-002-02 — Registration rejects a malformed email
**Requirement reference:** FR-002  
**Layer:** API validation test  
**Given** a registration request with `email` set to `not-an-email`  
**When** the client submits `POST /api/v1/auth/register/`  
**Then** the response is `400 Bad Request` with an `email` field error and no account is created.

---

#### TC-FR-002-03 — Registration rejects an already-registered email regardless of case
**Requirement reference:** FR-002  
**Layer:** API validation test  
**Given** an existing account registered with `person@example.com`  
**When** the client submits `POST /api/v1/auth/register/` with `email` set to `Person@Example.com` and a valid password and timezone  
**Then** the response is `400 Bad Request` with an `email` field error and no second account is created.

---

#### TC-FR-003-01 — Registration rejects a missing password
**Requirement reference:** FR-003  
**Layer:** API validation test  
**Given** a registration request with `password` omitted  
**When** the client submits `POST /api/v1/auth/register/`  
**Then** the response is `400 Bad Request` with a `password` field error and no account is created.

---

#### TC-FR-003-02 — Registration rejects a password shorter than eight characters
**Requirement reference:** FR-003  
**Layer:** API validation test  
**Given** a registration request with `password` set to `short12` (seven characters)  
**When** the client submits `POST /api/v1/auth/register/`  
**Then** the response is `400 Bad Request` with a `password` field error and no account is created.

---

#### TC-FR-003-03 — Registration rejects a password longer than 128 characters
**Requirement reference:** FR-003  
**Layer:** API validation test  
**Given** a registration request with `password` set to a 129-character value  
**When** the client submits `POST /api/v1/auth/register/`  
**Then** the response is `400 Bad Request` with a `password` field error and no account is created.

---

#### TC-FR-004-01 — Registration rejects an unsupported timezone
**Requirement reference:** FR-004  
**Layer:** API validation test  
**Given** a registration request with `timezone` set to a value outside the backend's supported IANA timezone set  
**When** the client submits `POST /api/v1/auth/register/`  
**Then** the response is `400 Bad Request` with a `timezone` field error and no account is created.

---

#### TC-FR-005-01 — Valid credentials log in and return an access token
**Requirement reference:** FR-005  
**Layer:** API integration test  
**Given** a registered account with known credentials  
**When** the client submits a credentialed `POST /api/v1/auth/login/` with the correct `email`, `password`, and a valid `X-CSRFToken`  
**Then** the response is `200 OK` and its JSON body contains `access_token`.

---

#### TC-FR-005-02 — Successful login sets the refresh token only in the cookie
**Requirement reference:** FR-005  
**Layer:** API integration test  
**Given** a registered account with known credentials  
**When** the client submits a valid, CSRF-protected `POST /api/v1/auth/login/`  
**Then** the response sets the `refresh_token` cookie and the JSON body does not contain a refresh token in any field.

---

#### TC-FR-005-03 — Login with an unknown email returns a generic authentication error
**Requirement reference:** FR-005  
**Layer:** API integration test  
**Given** no account exists for `unknown@example.com`  
**When** the client submits a CSRF-protected `POST /api/v1/auth/login/` with `email: unknown@example.com` and any password  
**Then** the response is `401 Unauthorized` with body `{"detail": "Invalid credentials."}`.

---

#### TC-FR-005-04 — Login with an incorrect password returns a generic authentication error
**Requirement reference:** FR-005  
**Layer:** API integration test  
**Given** a registered account with a known email and password  
**When** the client submits a CSRF-protected `POST /api/v1/auth/login/` with the correct email and an incorrect password  
**Then** the response is `401 Unauthorized` with body `{"detail": "Invalid credentials."}`.

---

#### TC-FR-005-05 — Access token expires ten minutes after issuance
**Requirement reference:** FR-005  
**Layer:** API integration test  
**Given** a successful login at a mocked issuance time T, producing an `access_token`  
**When** the token's `exp` claim is inspected, the token is presented to a protected endpoint with the clock mocked to T + 9 minutes 59 seconds, and the token is presented again with the clock mocked to T + 10 minutes 1 second  
**Then** the `exp` claim equals T + 10 minutes, the first request is accepted, and the second request is rejected with an authentication failure.

---

#### TC-FR-005-06 — Frontend holds the access token only in memory
**Requirement reference:** FR-005  
**Layer:** Frontend integration test  
**Given** a successful login  
**When** the application state is inspected immediately afterward  
**Then** `access_token` is present only in in-memory application state, is absent from `localStorage` and `sessionStorage`, and subsequent protected requests carry it via `Authorization: Bearer <access_token>`.

---

#### TC-FR-005-07 — Access token is signed with the accepted algorithm and claim set
**Requirement reference:** FR-005  
**Layer:** API integration test  
**Given** a successful login producing an `access_token`  
**When** the token header and payload are decoded, a copy with its header `alg` changed to `none` or `HS512` is presented to a protected endpoint, and a valid refresh token (`token_type: "refresh"`) is presented as a bearer credential to a protected endpoint  
**Then** the decoded token is signed with `HS256` and carries `sub`, `token_type: "access"`, `iat`, and `exp`; the algorithm-substituted copy is rejected; and the refresh token is rejected as a bearer credential.

---

#### TC-FR-006-01 — Logout invalidates the refresh token
**Requirement reference:** FR-006  
**Layer:** API integration test  
**Given** an authenticated session with a valid `refresh_token` cookie  
**When** the client submits a CSRF-protected `POST /api/v1/auth/logout/`  
**Then** a subsequent `POST /api/v1/auth/refresh/` using the same refresh token is rejected.

---

#### TC-FR-006-02 — Logout clears the refresh-token cookie
**Requirement reference:** FR-006  
**Layer:** API integration test  
**Given** an authenticated session with a valid `refresh_token` cookie  
**When** the client submits a CSRF-protected `POST /api/v1/auth/logout/`  
**Then** the response clears the `refresh_token` cookie using its accepted name, path, and security attributes.

---

#### TC-FR-006-03 — Logout with a valid refresh token returns an empty 204 response
**Requirement reference:** FR-006  
**Layer:** API integration test  
**Given** an authenticated session with a valid `refresh_token` cookie  
**When** the client submits a CSRF-protected `POST /api/v1/auth/logout/`  
**Then** the response is `204 No Content` with an empty body.

---

#### TC-FR-006-04 — Logout is idempotent for a missing refresh token
**Requirement reference:** FR-006  
**Layer:** API integration test  
**Given** a CSRF-protected logout request with no `refresh_token` cookie present  
**When** the client submits `POST /api/v1/auth/logout/`  
**Then** the response is `204 No Content` with an empty body.

---

#### TC-FR-006-05 — Logout is idempotent for an expired refresh token
**Requirement reference:** FR-006  
**Layer:** API integration test  
**Given** a CSRF-protected logout request where the `refresh_token` cookie holds an expired token  
**When** the client submits `POST /api/v1/auth/logout/`  
**Then** the response is `204 No Content` with an empty body.

---

#### TC-FR-006-06 — Logout is idempotent for a revoked refresh token
**Requirement reference:** FR-006  
**Layer:** API integration test  
**Given** a CSRF-protected logout request where the `refresh_token` cookie holds a previously revoked token  
**When** the client submits `POST /api/v1/auth/logout/`  
**Then** the response is `204 No Content` with an empty body.

---

#### TC-FR-006-07 — Logout is idempotent for an already-invalid refresh token
**Requirement reference:** FR-006  
**Layer:** API integration test  
**Given** a CSRF-protected logout request where the `refresh_token` cookie holds a token that is already invalid  
**When** the client submits `POST /api/v1/auth/logout/`  
**Then** the response is `204 No Content` with an empty body.

---

#### TC-FR-006-08 — Selecting logout clears local session state before the request is sent
**Requirement reference:** FR-006  
**Layer:** Frontend integration test  
**Given** an authenticated frontend session  
**When** the user selects **Log out**  
**Then** the in-memory access token and authenticated-user state are cleared before the `POST /api/v1/auth/logout/` request is dispatched.

---

#### TC-FR-006-09 — Logout writes a logout-intent marker that suppresses session restoration
**Requirement reference:** FR-006  
**Layer:** Frontend integration test  
**Given** an authenticated frontend session  
**When** the user selects **Log out**  
**And** the application is then reloaded before a new login  
**Then** `localStorage` contains `medical_tracker.logout_intent = "true"`, and protected-application initialization does not attempt a refresh request while the marker is present.

---

#### TC-FR-006-10 — A later successful login removes the logout-intent marker
**Requirement reference:** FR-006  
**Layer:** Frontend integration test  
**Given** `medical_tracker.logout_intent` is set in `localStorage` after a prior logout  
**When** the user subsequently logs in successfully  
**Then** `medical_tracker.logout_intent` is removed from `localStorage`.

---

#### TC-FR-006-11 — Logout navigates to the login page after a successful response
**Requirement reference:** FR-006  
**Layer:** Frontend integration test  
**Given** an authenticated frontend session  
**When** the user selects **Log out** and the logout request succeeds  
**Then** the frontend navigates to the login page.

---

#### TC-FR-006-12 — Logout navigates to the login page after a failed response
**Requirement reference:** FR-006  
**Layer:** Frontend integration test  
**Given** an authenticated frontend session  
**When** the user selects **Log out** and the logout request receives an error response  
**Then** the frontend navigates to the login page.

---

#### TC-FR-006-13 — Logout navigates to the login page when the backend is unreachable
**Requirement reference:** FR-006  
**Layer:** Frontend integration test  
**Given** an authenticated frontend session and an unreachable backend  
**When** the user selects **Log out**  
**Then** the frontend navigates to the login page.

---

#### TC-FR-006-14 — A pre-logout access token remains valid until its own expiration
**Requirement reference:** FR-006  
**Layer:** API integration test  
**Given** an access token issued before logout, with logout completed and the refresh token invalidated  
**When** the client submits a protected request using that access token before its ten-minute expiration has elapsed  
**Then** the request succeeds.

---

#### TC-FR-007-01 — A valid refresh token returns a new access token
**Requirement reference:** FR-007  
**Layer:** API integration test  
**Given** a valid `refresh_token` cookie from an active session  
**When** the client submits a CSRF-protected `POST /api/v1/auth/refresh/`  
**Then** the response is `200 OK` with a new `access_token` in the JSON body.

---

#### TC-FR-007-02 — Refresh rotates and invalidates the previous refresh token
**Requirement reference:** FR-007  
**Layer:** API integration test  
**Given** a valid `refresh_token`  
**When** the client submits a successful `POST /api/v1/auth/refresh/` and then resubmits the original refresh token in a second refresh request  
**Then** the first request succeeds and the second request is rejected.

---

#### TC-FR-007-03 — Successful refresh replaces the refresh-token cookie
**Requirement reference:** FR-007  
**Layer:** API integration test  
**Given** a valid `refresh_token` cookie  
**When** the client submits a successful `POST /api/v1/auth/refresh/`  
**Then** the response sets a replacement `refresh_token` cookie using the accepted cookie attributes.

---

#### TC-FR-007-04 — Refreshed access token is returned in the documented field
**Requirement reference:** FR-007  
**Layer:** API integration test  
**Given** a valid `refresh_token`  
**When** the client submits a successful `POST /api/v1/auth/refresh/`  
**Then** the JSON response body contains the new token in the `access_token` field.

---

#### TC-FR-007-05 — Refresh is rejected for an expired refresh token
**Requirement reference:** FR-007  
**Layer:** API integration test  
**Given** a `refresh_token` cookie holding an expired token  
**When** the client submits `POST /api/v1/auth/refresh/`  
**Then** the response is `401 Unauthorized`, no new access or refresh token is issued, and the stale `refresh_token` cookie is cleared.

---

#### TC-FR-007-06 — Refresh is rejected for a revoked refresh token
**Requirement reference:** FR-007  
**Layer:** API integration test  
**Given** a `refresh_token` cookie holding a previously revoked token  
**When** the client submits `POST /api/v1/auth/refresh/`  
**Then** the response is `401 Unauthorized`, no new access or refresh token is issued, and the stale `refresh_token` cookie is cleared.

---

#### TC-FR-007-07 — Refresh is rejected for a malformed refresh token
**Requirement reference:** FR-007  
**Layer:** API integration test  
**Given** a `refresh_token` cookie holding a malformed token value  
**When** the client submits `POST /api/v1/auth/refresh/`  
**Then** the response is `401 Unauthorized`, no new access or refresh token is issued, and the stale `refresh_token` cookie is cleared.

---

#### TC-FR-007-08 — Refresh is rejected for a missing refresh token
**Requirement reference:** FR-007  
**Layer:** API integration test  
**Given** no `refresh_token` cookie is present  
**When** the client submits `POST /api/v1/auth/refresh/`  
**Then** the response is `401 Unauthorized` and no new access or refresh token is issued.

---

#### TC-FR-007-09 — Page reload restores a session with exactly one refresh request
**Requirement reference:** FR-007  
**Layer:** Frontend integration test  
**Given** a valid `refresh_token` cookie, no in-memory access token, and no `medical_tracker.logout_intent` marker  
**When** the protected application initializes after a page reload  
**Then** exactly one `POST /api/v1/auth/refresh/` request is sent and the session is restored on success.

---

#### TC-FR-007-10 — Refresh is rejected after the seven-day absolute session lifetime
**Requirement reference:** FR-007  
**Layer:** API integration test  
**Given** a session established by login at a mocked time T, refreshed successfully several times with the clock mocked to points before T + 7 days  
**When** the client submits `POST /api/v1/auth/refresh/` with the clock mocked to T + 7 days and 1 second  
**Then** the request is rejected, confirming that rotation preserved the original session-expiration boundary rather than extending it.

---

#### TC-FR-007-11 — Refresh token is signed with the accepted algorithm and claim set
**Requirement reference:** FR-007  
**Layer:** API integration test  
**Given** a successful login producing a `refresh_token` cookie  
**When** the token header and payload are decoded, a copy with its header `alg` changed to `none` or `HS512` is submitted to `POST /api/v1/auth/refresh/`, and a valid access token (`token_type: "access"`) is submitted as the refresh token to `POST /api/v1/auth/refresh/`  
**Then** the decoded token is signed with `HS256` and carries `sub`, `token_type: "refresh"`, `jti`, `session_start`, `iat`, and `exp`; the algorithm-substituted copy is rejected; and the access token is rejected when submitted as a refresh token.

---

#### TC-FR-008-01 — One failed protected request triggers exactly one refresh and one replay
**Requirement reference:** FR-008  
**Layer:** Frontend integration test  
**Given** an in-memory access token that the backend rejects  
**When** the frontend API client issues a protected request that receives an access-token authentication failure  
**Then** the client sends exactly one refresh request, replaces the in-memory access token on success, and replays the original request exactly once with the new token.

---

#### TC-FR-008-02 — A failed active-session refresh shows a session-expired message
**Requirement reference:** FR-008  
**Layer:** Frontend integration test  
**Given** an authenticated session whose refresh token is no longer valid  
**When** the frontend API client issues a protected request that receives an access-token authentication failure, sends its one refresh request, and that refresh request also fails  
**Then** the frontend clears authentication state, redirects to the login page, and displays a session-expired message carried through navigation state.

---

#### TC-FR-008-03 — A failed initialization refresh opens the login page without a session-expired message
**Requirement reference:** FR-008  
**Layer:** Frontend integration test  
**Given** no in-memory access token, no logout-intent marker, and an invalid or missing refresh token on page load  
**When** protected-application initialization attempts its one refresh request  
**Then** the frontend opens the login page without a retry loop and without a session-expired message.

---

#### TC-FR-008-04 — Concurrent authentication failures share a single refresh request
**Requirement reference:** FR-008  
**Layer:** Frontend integration test  
**Given** an in-memory access token that the backend rejects  
**When** the frontend issues several protected requests concurrently and all receive an access-token authentication failure  
**Then** exactly one refresh request is sent, and every affected request awaits and uses that same refresh result.

---

#### TC-FR-009-01 — Updating the account timezone persists the new value
**Requirement reference:** FR-009  
**Layer:** API integration test  
**Given** an authenticated user whose account timezone is `Asia/Makassar`  
**When** the client submits `PATCH /api/v1/account/` with `timezone: "Europe/Warsaw"`  
**Then** the response is `200 OK` with `timezone: "Europe/Warsaw"`, and a subsequent `GET /api/v1/account/` confirms the change persisted.

---

#### TC-FR-009-02 — Updating the account timezone rejects an unsupported value
**Requirement reference:** FR-009  
**Layer:** API validation test  
**Given** an authenticated user whose account timezone is `Asia/Makassar`  
**When** the client submits `PATCH /api/v1/account/` with an unsupported `timezone` value  
**Then** the response is `400 Bad Request` with a `timezone` field error and the account's stored timezone remains `Asia/Makassar`.

---

#### TC-FR-048-01 — Password change succeeds with a correct current password and a compliant new password
**Requirement reference:** FR-048  
**Layer:** API integration test  
**Given** an authenticated user  
**When** the client submits `POST /api/v1/account/password/` with the correct `current_password` and a `new_password` that satisfies the accepted password policy  
**Then** the response is `200 OK` with an empty body, and a subsequent login succeeds only with the new password.

---

#### TC-FR-048-02 — Password change is rejected for an incorrect current password
**Requirement reference:** FR-048  
**Layer:** API validation test  
**Given** an authenticated user  
**When** the client submits `POST /api/v1/account/password/` with an incorrect `current_password`  
**Then** the response is `400 Bad Request` with a field-level error, and the stored password is unchanged.

---

#### TC-FR-048-03 — Password change is rejected when the new password fails the accepted policy
**Requirement reference:** FR-048  
**Layer:** API validation test  
**Given** an authenticated user and the correct `current_password`  
**When** the client submits `POST /api/v1/account/password/` with a `new_password` that fails the accepted password policy (for example, shorter than eight characters)  
**Then** the response is `400 Bad Request` with a field-level error, and the stored password is unchanged.

---

### 5.2 Examination Records

#### TC-FR-010-01 — Draft creation preserves title and supplied optional information
**Requirement reference:** FR-010  
**Layer:** API integration test  
**Given** an authenticated user  
**When** the client submits `POST /api/v1/examinations/` with `status: "draft"`, a `title`, and a `scheduled_date` but no `category_id` or `scheduled_time`  
**Then** the response is `201 Created`, the record is stored with `status: "draft"`, and every submitted value is preserved.

---

#### TC-FR-011-01 — Minimal planned creation succeeds with only title and scheduled date
**Requirement reference:** FR-011  
**Layer:** API integration test  
**Given** an authenticated user  
**When** the client submits `POST /api/v1/examinations/` with `status: "planned"`, a `title`, and a `scheduled_date`, omitting `category_id` and `scheduled_time`  
**Then** the response is `201 Created` with `status: "planned"` and the submitted values are stored.

---

#### TC-FR-012-01 — The draft status value is accepted
**Requirement reference:** FR-012  
**Layer:** API validation test  
**Given** an authenticated user  
**When** the client submits an examination with `status: "draft"` and a valid resulting record  
**Then** the request succeeds and the record is stored with `status: "draft"`.

---

#### TC-FR-012-02 — The planned status value is accepted
**Requirement reference:** FR-012  
**Layer:** API validation test  
**Given** an authenticated user  
**When** the client submits an examination with `status: "planned"` and a valid resulting record  
**Then** the request succeeds and the record is stored with `status: "planned"`.

---

#### TC-FR-012-03 — The completed status value is accepted
**Requirement reference:** FR-012  
**Layer:** API validation test  
**Given** an authenticated user  
**When** the client submits an examination with `status: "completed"` and a valid resulting record  
**Then** the request succeeds and the record is stored with `status: "completed"`.

---

#### TC-FR-012-04 — The cancelled status value is accepted
**Requirement reference:** FR-012  
**Layer:** API validation test  
**Given** an authenticated user  
**When** the client submits an examination with `status: "cancelled"` and a valid resulting record  
**Then** the request succeeds and the record is stored with `status: "cancelled"`.

---

#### TC-FR-012-05 — The missed status value is accepted
**Requirement reference:** FR-012  
**Layer:** API validation test  
**Given** an authenticated user  
**When** the client submits an examination with `status: "missed"` and a valid resulting record  
**Then** the request succeeds and the record is stored with `status: "missed"`.

---

#### TC-FR-012-06 — An unsupported status value is rejected
**Requirement reference:** FR-012  
**Layer:** API validation test  
**Given** an authenticated user  
**When** the client submits an examination with `status: "archived"`  
**Then** the response is `400 Bad Request` with a `status` field error.

---

#### TC-FR-013-01 — Optional metadata fields are saved and retrieved
**Requirement reference:** FR-013  
**Layer:** API integration test  
**Given** an authenticated user  
**When** the client creates an examination with `medical_specialty`, `location`, and `notes` populated  
**Then** a subsequent `GET` of the record returns the same values for all three fields.

---

#### TC-FR-013-02 — Optional metadata fields can be cleared
**Requirement reference:** FR-013  
**Layer:** API integration test  
**Given** an examination with `medical_specialty`, `location`, and `notes` populated  
**When** the client submits `PATCH /api/v1/examinations/{id}/` setting all three fields to `null`  
**Then** the response confirms all three fields are `null` and a subsequent `GET` confirms persistence.

---

#### TC-FR-014-01 — Missing title is rejected for any status
**Requirement reference:** FR-014  
**Layer:** API validation test  
**Given** an authenticated user  
**When** the client submits a `planned` examination with `title` omitted but a valid `scheduled_date`  
**Then** the response is `400 Bad Request` with a `title` field error.

---

#### TC-FR-014-02 — A planned examination without a scheduled date is rejected
**Requirement reference:** FR-014  
**Layer:** API validation test  
**Given** an authenticated user  
**When** the client submits `status: "planned"` with a `title` but no `scheduled_date`  
**Then** the response is `400 Bad Request` with a `scheduled_date` field error.

---

#### TC-FR-014-03 — A cancelled examination without a scheduled date is rejected
**Requirement reference:** FR-014  
**Layer:** API validation test  
**Given** an authenticated user  
**When** the client submits `status: "cancelled"` with a `title` but no `scheduled_date`  
**Then** the response is `400 Bad Request` with a `scheduled_date` field error.

---

#### TC-FR-014-04 — A missed examination without a scheduled date is rejected
**Requirement reference:** FR-014  
**Layer:** API validation test  
**Given** an authenticated user  
**When** the client submits `status: "missed"` with a `title` but no `scheduled_date`  
**Then** the response is `400 Bad Request` with a `scheduled_date` field error.

---

#### TC-FR-014-05 — A completed examination without a completion date is rejected
**Requirement reference:** FR-014  
**Layer:** API validation test  
**Given** an authenticated user  
**When** the client submits `status: "completed"` with a `title` but no `completed_date`  
**Then** the response is `400 Bad Request` with a `completed_date` field error.

---

#### TC-FR-014-06 — A completion date equal to the current local date is accepted
**Requirement reference:** FR-014  
**Layer:** API validation test  
**Given** the authenticated user's current local date is frozen at `2026-08-04`  
**When** the client creates an examination with `status: "completed"` and `completed_date: "2026-08-04"`  
**Then** the response is `201 Created` and the record is saved.

---

#### TC-FR-014-07 — A completion date after the current local date is rejected
**Requirement reference:** FR-014  
**Layer:** API validation test  
**Given** the authenticated user's current local date is frozen at `2026-08-04`  
**When** the client submits `status: "completed"` with `completed_date: "2026-08-05"`  
**Then** the response is `400 Bad Request` with a `completed_date` field error.

---

#### TC-FR-015-01 — A nonexistent category is rejected
**Requirement reference:** FR-015  
**Layer:** API validation test  
**Given** an authenticated user and no category with id `9999`  
**When** the client submits an examination with `category_id: 9999`  
**Then** the response is `400 Bad Request` with a `category_id` field error.

---

#### TC-FR-015-02 — An unsupported status value is rejected during category and status validation
**Requirement reference:** FR-015  
**Layer:** API validation test  
**Given** an authenticated user  
**When** the client submits an examination with `status: "archived"` and a valid category  
**Then** the response is `400 Bad Request` with a `status` field error.

---

#### TC-FR-016-01 — A draft becomes planned when a scheduled date is added
**Requirement reference:** FR-016  
**Layer:** API integration test  
**Given** an owned draft examination with only a title  
**When** the client submits `PATCH /api/v1/examinations/{id}/` with `status: "planned"` and a `scheduled_date`, omitting category and scheduled time  
**Then** the response is `200 OK` with `status: "planned"` and the supplied `scheduled_date`.

---

#### TC-FR-016-02 — Changing a draft to planned without a scheduled date is rejected
**Requirement reference:** FR-016  
**Layer:** API validation test  
**Given** an owned draft examination with only a title  
**When** the client submits `PATCH /api/v1/examinations/{id}/` with `status: "planned"` and no `scheduled_date`  
**Then** the response is `400 Bad Request` with a `scheduled_date` field error and the record remains a draft.

---

#### TC-FR-017-01 — Reminder creation is rejected for a draft examination
**Requirement reference:** FR-017  
**Layer:** API validation test  
**Given** an owned draft examination  
**When** the client submits `POST /api/v1/examinations/{id}/reminder/` with a valid `offset_days`  
**Then** the response is `400 Bad Request` with a business-rule error and no reminder is created.

---

#### TC-FR-017-02 — Reminder offset update is rejected for a draft examination
**Requirement reference:** FR-017  
**Layer:** API validation test  
**Given** an owned draft examination with an existing inactive reminder  
**When** the client submits `PATCH /api/v1/examinations/{id}/reminder/` with a new `offset_days`  
**Then** the response is `400 Bad Request` with a business-rule error and the reminder's `offset_days` is unchanged.

---

#### TC-FR-017-03 — Reminder reactivation is rejected for a draft examination
**Requirement reference:** FR-017  
**Layer:** API validation test  
**Given** an owned draft examination with an existing inactive reminder  
**When** the client submits `PATCH /api/v1/examinations/{id}/reminder/` with `is_active: true`  
**Then** the response is `400 Bad Request` with a business-rule error and the reminder remains inactive.

---

#### TC-FR-018-01 — Recurrence creation is rejected for a draft examination
**Requirement reference:** FR-018  
**Layer:** API validation test  
**Given** an owned draft examination  
**When** the client submits `POST /api/v1/examinations/{id}/recurrence/` with a valid `interval`  
**Then** the response is `400 Bad Request` with a business-rule error and no recurrence rule is created.

---

#### TC-FR-018-02 — Recurrence update is rejected for a draft examination
**Requirement reference:** FR-018  
**Layer:** API validation test  
**Given** an owned draft examination with an existing `monthly` recurrence rule  
**When** the client submits `PATCH /api/v1/examinations/{id}/recurrence/` with `interval: "yearly"`  
**Then** the response is `400 Bad Request` with a business-rule error and the recurrence rule's `interval` remains `monthly`.

---

#### TC-FR-019-01 — A dated draft is excluded from upcoming results
**Requirement reference:** FR-019  
**Layer:** API integration test  
**Given** a draft examination with a future `scheduled_date`  
**When** the client requests `GET /api/v1/examinations/?time_state=upcoming`  
**Then** the response does not include the draft record.

---

#### TC-FR-019-02 — A dated draft is excluded from overdue results
**Requirement reference:** FR-019  
**Layer:** API integration test  
**Given** a draft examination with a past `scheduled_date`  
**When** the client requests `GET /api/v1/examinations/?time_state=overdue`  
**Then** the response does not include the draft record.

---

#### TC-FR-019-03 — A dated draft is excluded from calendar results
**Requirement reference:** FR-019  
**Layer:** API integration test  
**Given** a draft examination with a `scheduled_date` inside a requested calendar range  
**When** the client requests `GET /api/v1/calendar/` for that date range  
**Then** the response does not include an entry for the draft record.

---

#### TC-FR-020-01 — The examination list shows a loading state while the request is pending
**Requirement reference:** FR-020  
**Layer:** Frontend integration test  
**Given** the examination list page is opened  
**When** the `GET /api/v1/examinations/` request is pending  
**Then** the page renders the loading state and no other state.

---

#### TC-FR-020-02 — The examination list shows an empty state when no records exist
**Requirement reference:** FR-020  
**Layer:** Frontend integration test  
**Given** `GET /api/v1/examinations/` resolves with an empty array  
**When** the response is received  
**Then** the page renders the empty state and no other state.

---

#### TC-FR-020-03 — The examination list shows a populated state with returned records
**Requirement reference:** FR-020  
**Layer:** Frontend integration test  
**Given** `GET /api/v1/examinations/` resolves with one or more records  
**When** the response is received  
**Then** the page renders the populated state listing the returned records.

---

#### TC-FR-020-04 — The examination list shows an error state when the request fails
**Requirement reference:** FR-020  
**Layer:** Frontend integration test  
**Given** `GET /api/v1/examinations/` fails  
**When** the failure is received  
**Then** the page renders the error state and no other state.

---

#### TC-FR-021-01 — Retrieving an owned examination returns its stored fields
**Requirement reference:** FR-021  
**Layer:** API integration test  
**Given** an owned examination with known field values  
**When** the client requests `GET /api/v1/examinations/{id}/`  
**Then** the response is `200 OK` and its fields match the stored values.

---

#### TC-FR-022-01 — Updating an owned examination persists the change
**Requirement reference:** FR-022  
**Layer:** API integration test  
**Given** an owned examination  
**When** the client submits `PATCH /api/v1/examinations/{id}/` changing `location`  
**Then** the response is `200 OK` with the new value, and a subsequent `GET` confirms persistence.

---

#### TC-FR-023-01 — Deleting an owned examination removes it permanently
**Requirement reference:** FR-023  
**Layer:** API integration test  
**Given** an owned examination  
**When** the client submits `DELETE /api/v1/examinations/{id}/`  
**Then** the response is `204 No Content` and a subsequent `GET /api/v1/examinations/{id}/` returns `404 Not Found`.

---

#### TC-FR-023-02 — Deleting an examination cascades to its reminder and recurrence rule
**Requirement reference:** FR-023  
**Layer:** API integration test  
**Given** an owned examination with an attached reminder and recurrence rule  
**When** the client submits `DELETE /api/v1/examinations/{id}/`  
**Then** subsequent `GET` requests for the examination's reminder and recurrence rule both return `404 Not Found`.

---

#### TC-FR-023-03 — Deleting a source examination nulls, rather than deletes, a generated occurrence's source reference
**Requirement reference:** FR-023  
**Layer:** API integration test  
**Given** an examination with a generated next occurrence whose `source_occurrence` points to it  
**When** the client submits `DELETE /api/v1/examinations/{id}/` for the source examination  
**Then** the generated occurrence still exists and is retrievable, and its `source_occurrence` field is `null`.

---

#### TC-FR-024-01 — Cancelling the delete confirmation sends no delete request
**Requirement reference:** FR-024  
**Layer:** Frontend integration test  
**Given** the delete confirmation dialog is open for an owned examination  
**When** the user selects cancel  
**Then** the dialog closes and no `DELETE` request is sent.

---

#### TC-FR-024-02 — Confirming the delete dialog sends exactly one delete request
**Requirement reference:** FR-024  
**Layer:** Frontend integration test  
**Given** the delete confirmation dialog is open for an owned examination  
**When** the user selects confirm  
**Then** exactly one `DELETE /api/v1/examinations/{id}/` request is sent.

---

#### TC-FR-025-01 — Assigning an available category is saved and returned
**Requirement reference:** FR-025  
**Layer:** API integration test  
**Given** an authenticated user and an existing category  
**When** the client creates an examination with that category's `category_id`  
**Then** the response returns the assigned `category` object matching the chosen category.

---

#### TC-FR-026-01 — The category collection contains exactly the required system-defined categories
**Requirement reference:** FR-026  
**Layer:** API integration test  
**Given** an authenticated user  
**When** the client requests `GET /api/v1/categories/`  
**Then** the response contains exactly the eight required category names, each appearing once.

---

#### TC-FR-027-01 — An examination without a category displays Uncategorized
**Requirement reference:** FR-027  
**Layer:** Frontend component test  
**Given** an examination record with `category: null`  
**When** the record is rendered  
**Then** the component displays **Uncategorized**.

---

#### TC-FR-028-01 — Title search performs a case-insensitive containment match
**Requirement reference:** FR-028  
**Layer:** API integration test  
**Given** owned examinations titled `Annual dental checkup` and `Eye exam`  
**When** the client requests `GET /api/v1/examinations/?search=dental`  
**Then** the response includes only `Annual dental checkup`.

---

#### TC-FR-029-01 — The status filter returns only matching records
**Requirement reference:** FR-029  
**Layer:** API integration test  
**Given** owned examinations with statuses `planned` and `completed`  
**When** the client requests `GET /api/v1/examinations/?status=planned`  
**Then** the response includes only the `planned` record.

---

#### TC-FR-029-02 — The category filter returns only matching records
**Requirement reference:** FR-029  
**Layer:** API integration test  
**Given** owned examinations assigned to two different categories  
**When** the client requests `GET /api/v1/examinations/?category=<id>` for one category  
**Then** the response includes only records assigned to that category.

---

#### TC-FR-029-03 — Combined status and category filters use AND semantics
**Requirement reference:** FR-029  
**Layer:** API integration test  
**Given** owned examinations covering every combination of two statuses and two categories  
**When** the client requests `GET /api/v1/examinations/?status=planned&category=<id>`  
**Then** the response includes only records matching both the status and the category.

---

#### TC-FR-030-01 — Ascending scheduled-date ordering places undated records last
**Requirement reference:** FR-030  
**Layer:** API integration test  
**Given** owned examinations with dated and undated `scheduled_date` values  
**When** the client requests `GET /api/v1/examinations/?ordering=scheduled_date`  
**Then** dated records appear in ascending order followed by all undated records.

---

#### TC-FR-030-02 — Descending scheduled-date ordering places undated records last
**Requirement reference:** FR-030  
**Layer:** API integration test  
**Given** owned examinations with dated and undated `scheduled_date` values  
**When** the client requests `GET /api/v1/examinations/?ordering=-scheduled_date`  
**Then** dated records appear in descending order followed by all undated records.

---

#### TC-FR-030-03 — Records sharing the same scheduled date use a deterministic tiebreak
**Requirement reference:** FR-030  
**Layer:** API integration test  
**Given** two owned examinations sharing the same `scheduled_date`  
**When** the client requests either ordering direction repeatedly  
**Then** the two records appear in the same relative order every time, ordered by identifier.

---

### 5.3 Past, Upcoming, and Overdue Examinations

#### TC-FR-031-01 — A completed record is included in the past collection by completion date
**Requirement reference:** FR-031  
**Layer:** API integration test  
**Given** the user's current local date is frozen at `2026-08-04` and a `completed` record has `completed_date: "2026-08-04"`  
**When** the client requests `GET /api/v1/examinations/?time_state=past`  
**Then** the response includes that record.

---

#### TC-FR-031-02 — A cancelled record is included in the past collection by scheduled date
**Requirement reference:** FR-031  
**Layer:** API integration test  
**Given** the user's current local date is frozen at `2026-08-04` and a `cancelled` record has `scheduled_date: "2026-08-03"`  
**When** the client requests `GET /api/v1/examinations/?time_state=past`  
**Then** the response includes that record.

---

#### TC-FR-031-03 — A missed record is included in the past collection by scheduled date
**Requirement reference:** FR-031  
**Layer:** API integration test  
**Given** the user's current local date is frozen at `2026-08-04` and a `missed` record has `scheduled_date: "2026-08-03"`  
**When** the client requests `GET /api/v1/examinations/?time_state=past`  
**Then** the response includes that record.

---

#### TC-FR-031-04 — A planned record is excluded from the past collection
**Requirement reference:** FR-031  
**Layer:** API integration test  
**Given** the user's current local date is frozen at `2026-08-04` and the user owns a `planned` record  
**When** the client requests `GET /api/v1/examinations/?time_state=past`  
**Then** the response excludes that record.

---

#### TC-FR-031-05 — A draft record is excluded from the past collection
**Requirement reference:** FR-031  
**Layer:** API integration test  
**Given** the user's current local date is frozen at `2026-08-04` and the user owns a `draft` record  
**When** the client requests `GET /api/v1/examinations/?time_state=past`  
**Then** the response excludes that record.

---

#### TC-FR-031-06 — A completed record with a future completion date is excluded from the past collection
**Requirement reference:** FR-031  
**Layer:** API integration test  
**Given** the user's current local date is frozen at `2026-08-04` and a `completed` record has `completed_date: "2026-08-05"`  
**When** the client requests `GET /api/v1/examinations/?time_state=past`  
**Then** the response excludes that record.

---

#### TC-FR-032-01 — A future-dated planned record is included in upcoming
**Requirement reference:** FR-032  
**Layer:** API integration test  
**Given** the user's current local date is frozen at `2026-08-04` and a `planned` record has `scheduled_date: "2026-08-10"`  
**When** the client requests `GET /api/v1/examinations/?time_state=upcoming`  
**Then** the response includes that record.

---

#### TC-FR-032-02 — A current-date planned record without a scheduled time is included in upcoming
**Requirement reference:** FR-032  
**Layer:** API integration test  
**Given** the user's current local date is frozen at `2026-08-04` and a `planned` record has `scheduled_date: "2026-08-04"` with `scheduled_time` null  
**When** the client requests `GET /api/v1/examinations/?time_state=upcoming`  
**Then** the response includes that record.

---

#### TC-FR-032-03 — A current-date planned record with an unpassed scheduled time is included in upcoming
**Requirement reference:** FR-032  
**Layer:** API integration test  
**Given** the user's current local time is frozen at `2026-08-04T09:00` and a `planned` record has `scheduled_date: "2026-08-04"`, `scheduled_time: "11:00:00"`  
**When** the client requests `GET /api/v1/examinations/?time_state=upcoming`  
**Then** the response includes that record.

---

#### TC-FR-032-04 — An overdue planned record is excluded from upcoming
**Requirement reference:** FR-032  
**Layer:** API integration test  
**Given** the user's current local date is frozen at `2026-08-04` and a `planned` record has `scheduled_date: "2026-08-03"`  
**When** the client requests `GET /api/v1/examinations/?time_state=upcoming`  
**Then** the response excludes that record.

---

#### TC-FR-032-05 — A completed record is excluded from upcoming
**Requirement reference:** FR-032  
**Layer:** API integration test  
**Given** the user's current local date is frozen at `2026-08-04` and a `completed` record has `completed_date: "2026-08-03"`  
**When** the client requests `GET /api/v1/examinations/?time_state=upcoming`  
**Then** the response excludes that record.

---

#### TC-FR-033-01 — A planned record scheduled before the current local date is overdue
**Requirement reference:** FR-033  
**Layer:** API integration test  
**Given** the user's current local date is frozen at `2026-08-04` and a `planned` record has `scheduled_date: "2026-08-03"`  
**When** the client requests `GET /api/v1/examinations/?time_state=overdue`  
**Then** the response includes that record.

---

#### TC-FR-033-02 — A current-date planned record whose scheduled time has passed is overdue
**Requirement reference:** FR-033  
**Layer:** API integration test  
**Given** the user's current local time is frozen at `2026-08-04T11:00` and a `planned` record has `scheduled_date: "2026-08-04"`, `scheduled_time: "09:00:00"`  
**When** the client requests `GET /api/v1/examinations/?time_state=overdue`  
**Then** the response includes that record.

---

#### TC-FR-033-03 — A current-date planned record whose scheduled time has not passed is not overdue
**Requirement reference:** FR-033  
**Layer:** API integration test  
**Given** the user's current local time is frozen at `2026-08-04T09:00` and a `planned` record has `scheduled_date: "2026-08-04"`, `scheduled_time: "11:00:00"`  
**When** the client requests `GET /api/v1/examinations/?time_state=overdue`  
**Then** the response excludes that record.

---

#### TC-FR-033-04 — A current-date planned record without a scheduled time is not overdue
**Requirement reference:** FR-033  
**Layer:** API integration test  
**Given** the user's current local date is frozen at `2026-08-04` and a `planned` record has `scheduled_date: "2026-08-04"` with `scheduled_time` null  
**When** the client requests `GET /api/v1/examinations/?time_state=overdue`  
**Then** the response excludes that record.

---

#### TC-FR-033-05 — The same unchanged record's derived state changes as time passes its boundary
**Requirement reference:** FR-033  
**Layer:** API integration test  
**Given** an unmodified `planned` record with `scheduled_date: "2026-08-04"`, `scheduled_time: "09:00:00"`  
**When** the overdue query is evaluated at `2026-08-04T08:59` and again at `2026-08-04T09:01` without modifying the record  
**Then** the record is excluded from the first evaluation and included in the second.

---

#### TC-FR-034-01 — Only the planned record among same-dated records of every status is overdue
**Requirement reference:** FR-034  
**Layer:** API integration test  
**Given** the user's current local date is frozen at `2026-08-04` and the user owns a past-dated record in each of `draft`, `planned`, `completed`, `cancelled`, and `missed` status  
**When** the client requests `GET /api/v1/examinations/?time_state=overdue`  
**Then** the response includes only the `planned` record.

---

### 5.4 In-Application Reminders

#### TC-FR-035-01 — Creating a reminder on a planned examination succeeds
**Requirement reference:** FR-035  
**Layer:** API integration test  
**Given** an owned `planned` examination with no existing reminder  
**When** the client submits `POST /api/v1/examinations/{id}/reminder/` with `offset_days: 7`  
**Then** the response is `201 Created` with `is_active: true`.

---

#### TC-FR-035-02 — Updating the offset of an existing reminder succeeds
**Requirement reference:** FR-035  
**Layer:** API integration test  
**Given** an owned `planned` examination with an existing reminder  
**When** the client submits `PATCH /api/v1/examinations/{id}/reminder/` with a new `offset_days`  
**Then** the response is `200 OK` with the updated `offset_days`.

---

#### TC-FR-035-03 — Disabling a reminder succeeds while the examination is planned
**Requirement reference:** FR-035  
**Layer:** API integration test  
**Given** an owned `planned` examination with an active reminder  
**When** the client submits `PATCH /api/v1/examinations/{id}/reminder/` with `is_active: false`  
**Then** the response is `200 OK` with `is_active: false`.

---

#### TC-FR-035-04 — Disabling a reminder succeeds while the examination is completed
**Requirement reference:** FR-035  
**Layer:** API integration test  
**Given** an owned `completed` examination with an active reminder  
**When** the client submits `PATCH /api/v1/examinations/{id}/reminder/` with `is_active: false`  
**Then** the response is `200 OK` with `is_active: false`.

---

#### TC-FR-035-05 — A zero offset is rejected
**Requirement reference:** FR-035  
**Layer:** API validation test  
**Given** an owned `planned` examination  
**When** the client submits `POST /api/v1/examinations/{id}/reminder/` with `offset_days: 0`  
**Then** the response is `400 Bad Request` with an `offset_days` field error.

---

#### TC-FR-035-06 — A negative offset is rejected
**Requirement reference:** FR-035  
**Layer:** API validation test  
**Given** an owned `planned` examination  
**When** the client submits `POST /api/v1/examinations/{id}/reminder/` with `offset_days: -3`  
**Then** the response is `400 Bad Request` with an `offset_days` field error.

---

#### TC-FR-035-07 — A non-whole-number offset is rejected
**Requirement reference:** FR-035  
**Layer:** API validation test  
**Given** an owned `planned` examination  
**When** the client submits `POST /api/v1/examinations/{id}/reminder/` with `offset_days: 2.5`  
**Then** the response is `400 Bad Request` with an `offset_days` field error.

---

#### TC-FR-035-08 — Reminder creation is rejected for a draft examination
**Requirement reference:** FR-035  
**Layer:** API validation test  
**Given** an owned `draft` examination with no existing reminder  
**When** the client submits `POST /api/v1/examinations/{id}/reminder/` with a valid `offset_days`  
**Then** the response is rejected with a business-rule error and no reminder is created.

---

#### TC-FR-035-09 — Reminder offset update is rejected for a draft examination
**Requirement reference:** FR-035  
**Layer:** API validation test  
**Given** an owned `draft` examination with an existing inactive reminder  
**When** the client submits `PATCH /api/v1/examinations/{id}/reminder/` with a new `offset_days`  
**Then** the response is rejected with a business-rule error and the reminder's `offset_days` is unchanged.

---

#### TC-FR-035-10 — Reminder reactivation is rejected for a draft examination
**Requirement reference:** FR-035  
**Layer:** API validation test  
**Given** an owned `draft` examination with an existing inactive reminder  
**When** the client submits `PATCH /api/v1/examinations/{id}/reminder/` with `is_active: true`  
**Then** the response is rejected with a business-rule error and the reminder remains inactive.

---

#### TC-FR-035-11 — Reminder creation is rejected for a completed examination
**Requirement reference:** FR-035  
**Layer:** API validation test  
**Given** an owned `completed` examination with no existing reminder  
**When** the client submits `POST /api/v1/examinations/{id}/reminder/` with a valid `offset_days`  
**Then** the response is rejected with a business-rule error and no reminder is created.

---

#### TC-FR-035-12 — Reminder offset update is rejected for a completed examination
**Requirement reference:** FR-035  
**Layer:** API validation test  
**Given** an owned `completed` examination with an existing inactive reminder  
**When** the client submits `PATCH /api/v1/examinations/{id}/reminder/` with a new `offset_days`  
**Then** the response is rejected with a business-rule error and the reminder's `offset_days` is unchanged.

---

#### TC-FR-035-13 — Reminder reactivation is rejected for a completed examination
**Requirement reference:** FR-035  
**Layer:** API validation test  
**Given** an owned `completed` examination with an existing inactive reminder  
**When** the client submits `PATCH /api/v1/examinations/{id}/reminder/` with `is_active: true`  
**Then** the response is rejected with a business-rule error and the reminder remains inactive.

---

#### TC-FR-035-14 — Reminder creation is rejected for a cancelled examination
**Requirement reference:** FR-035  
**Layer:** API validation test  
**Given** an owned `cancelled` examination with no existing reminder  
**When** the client submits `POST /api/v1/examinations/{id}/reminder/` with a valid `offset_days`  
**Then** the response is rejected with a business-rule error and no reminder is created.

---

#### TC-FR-035-15 — Reminder offset update is rejected for a cancelled examination
**Requirement reference:** FR-035  
**Layer:** API validation test  
**Given** an owned `cancelled` examination with an existing inactive reminder  
**When** the client submits `PATCH /api/v1/examinations/{id}/reminder/` with a new `offset_days`  
**Then** the response is rejected with a business-rule error and the reminder's `offset_days` is unchanged.

---

#### TC-FR-035-16 — Reminder reactivation is rejected for a cancelled examination
**Requirement reference:** FR-035  
**Layer:** API validation test  
**Given** an owned `cancelled` examination with an existing inactive reminder  
**When** the client submits `PATCH /api/v1/examinations/{id}/reminder/` with `is_active: true`  
**Then** the response is rejected with a business-rule error and the reminder remains inactive.

---

#### TC-FR-035-17 — Reminder creation is rejected for a missed examination
**Requirement reference:** FR-035  
**Layer:** API validation test  
**Given** an owned `missed` examination with no existing reminder  
**When** the client submits `POST /api/v1/examinations/{id}/reminder/` with a valid `offset_days`  
**Then** the response is rejected with a business-rule error and no reminder is created.

---

#### TC-FR-035-18 — Reminder offset update is rejected for a missed examination
**Requirement reference:** FR-035  
**Layer:** API validation test  
**Given** an owned `missed` examination with an existing inactive reminder  
**When** the client submits `PATCH /api/v1/examinations/{id}/reminder/` with a new `offset_days`  
**Then** the response is rejected with a business-rule error and the reminder's `offset_days` is unchanged.

---

#### TC-FR-035-19 — Reminder reactivation is rejected for a missed examination
**Requirement reference:** FR-035  
**Layer:** API validation test  
**Given** an owned `missed` examination with an existing inactive reminder  
**When** the client submits `PATCH /api/v1/examinations/{id}/reminder/` with `is_active: true`  
**Then** the response is rejected with a business-rule error and the reminder remains inactive.

---

#### TC-FR-036-01 — Reminder due date is calculated from the scheduled date and offset
**Requirement reference:** FR-036  
**Layer:** API integration test  
**Given** an owned `planned` examination with `scheduled_date: "2026-08-15"`  
**When** the client creates a reminder with `offset_days: 7`  
**Then** the reminder's `due_date` is `2026-08-08`.

---

#### TC-FR-036-02 — Reminder due date recalculates when the scheduled date changes
**Requirement reference:** FR-036  
**Layer:** API integration test  
**Given** an owned `planned` examination with an active reminder  
**When** the client updates the examination's `scheduled_date`  
**Then** the reminder's `due_date` reflects the new `scheduled_date` minus its `offset_days`.

---

#### TC-FR-036-03 — Reminder due date recalculates when the offset changes
**Requirement reference:** FR-036  
**Layer:** API integration test  
**Given** an owned `planned` examination with an active reminder  
**When** the client updates the reminder's `offset_days`  
**Then** the reminder's `due_date` reflects the examination's unchanged `scheduled_date` minus the new `offset_days`.

---

#### TC-FR-036-04 — Reminder due date is null when the examination has no scheduled date
**Requirement reference:** FR-036  
**Layer:** API integration test  
**Given** an examination whose `scheduled_date` has been removed while a reminder remains attached  
**When** the client retrieves the reminder  
**Then** `due_date` is `null`.

---

#### TC-FR-037-01 — Only due, active reminders are displayed
**Requirement reference:** FR-037  
**Layer:** Frontend integration test  
**Given** `GET /api/v1/reminders/?state=due` returns a due active reminder, a future active reminder, and a due inactive reminder  
**When** the due-reminders area renders  
**Then** only the due active reminder is displayed.

---

#### TC-FR-037-02 — The reminders endpoint's due-state filter returns only due, active reminders
**Requirement reference:** FR-037  
**Layer:** API integration test  
**Given** an owned active reminder whose `due_date` is on or before the user's current local date, an owned active reminder whose `due_date` is in the future, and an owned inactive reminder whose `due_date` is on or before the user's current local date  
**When** the client requests `GET /api/v1/reminders/?state=due`  
**Then** the response includes only the due, active reminder.

---

#### TC-FR-038-01 — Changing a planned examination to draft deactivates its reminder
**Requirement reference:** FR-038  
**Layer:** API integration test  
**Given** a `planned` examination with an active reminder  
**When** the client submits `PATCH /api/v1/examinations/{id}/` with `status: "draft"`  
**Then** the reminder's `is_active` becomes `false` in the same operation.

---

#### TC-FR-038-02 — Changing a planned examination to completed deactivates its reminder
**Requirement reference:** FR-038  
**Layer:** API integration test  
**Given** a `planned` examination with an active reminder  
**When** the client submits `PATCH /api/v1/examinations/{id}/` with `status: "completed"` and a valid `completed_date`  
**Then** the reminder's `is_active` becomes `false` in the same operation.

---

#### TC-FR-038-03 — Changing a planned examination to cancelled deactivates its reminder
**Requirement reference:** FR-038  
**Layer:** API integration test  
**Given** a `planned` examination with an active reminder  
**When** the client submits `PATCH /api/v1/examinations/{id}/` with `status: "cancelled"`  
**Then** the reminder's `is_active` becomes `false` in the same operation.

---

#### TC-FR-038-04 — Changing a planned examination to missed deactivates its reminder
**Requirement reference:** FR-038  
**Layer:** API integration test  
**Given** a `planned` examination with an active reminder  
**When** the client submits `PATCH /api/v1/examinations/{id}/` with `status: "missed"`  
**Then** the reminder's `is_active` becomes `false` in the same operation.

---

#### TC-FR-038-05 — Returning an examination to planned does not reactivate its reminder
**Requirement reference:** FR-038  
**Layer:** API integration test  
**Given** an examination whose reminder was deactivated by a prior status change  
**When** the client submits `PATCH /api/v1/examinations/{id}/` with `status: "planned"` and a valid `scheduled_date`  
**Then** the reminder's `is_active` remains `false`.

---

### 5.5 Recurring Examinations

#### TC-FR-039-01 — A monthly recurrence interval is accepted for a planned examination
**Requirement reference:** FR-039  
**Layer:** API validation test  
**Given** an owned `planned` examination with a `scheduled_date`  
**When** the client submits `POST /api/v1/examinations/{id}/recurrence/` with `interval: "monthly"`  
**Then** the response is `201 Created`.

---

#### TC-FR-039-02 — A six-month recurrence interval is accepted for a planned examination
**Requirement reference:** FR-039  
**Layer:** API validation test  
**Given** an owned `planned` examination with a `scheduled_date`  
**When** the client submits `POST /api/v1/examinations/{id}/recurrence/` with `interval: "six_months"`  
**Then** the response is `201 Created`.

---

#### TC-FR-039-03 — A yearly recurrence interval is accepted for a planned examination
**Requirement reference:** FR-039  
**Layer:** API validation test  
**Given** an owned `planned` examination with a `scheduled_date`  
**When** the client submits `POST /api/v1/examinations/{id}/recurrence/` with `interval: "yearly"`  
**Then** the response is `201 Created`.

---

#### TC-FR-039-04 — An unsupported recurrence interval is rejected
**Requirement reference:** FR-039  
**Layer:** API validation test  
**Given** an owned `planned` examination  
**When** the client submits `POST /api/v1/examinations/{id}/recurrence/` with `interval: "weekly"`  
**Then** the response is `400 Bad Request` with an `interval` field error.

---

#### TC-FR-039-05 — Recurrence creation is rejected for a draft examination
**Requirement reference:** FR-039  
**Layer:** API validation test  
**Given** an owned `draft` examination  
**When** the client submits `POST /api/v1/examinations/{id}/recurrence/` with a valid `interval`  
**Then** the response is rejected with a business-rule error.

---

#### TC-FR-039-06 — Recurrence creation is rejected for a completed examination
**Requirement reference:** FR-039  
**Layer:** API validation test  
**Given** an owned `completed` examination  
**When** the client submits `POST /api/v1/examinations/{id}/recurrence/` with a valid `interval`  
**Then** the response is rejected with a business-rule error.

---

#### TC-FR-039-07 — Recurrence creation is rejected for a cancelled examination
**Requirement reference:** FR-039  
**Layer:** API validation test  
**Given** an owned `cancelled` examination  
**When** the client submits `POST /api/v1/examinations/{id}/recurrence/` with a valid `interval`  
**Then** the response is rejected with a business-rule error.

---

#### TC-FR-039-08 — Recurrence creation is rejected for a missed examination
**Requirement reference:** FR-039  
**Layer:** API validation test  
**Given** an owned `missed` examination  
**When** the client submits `POST /api/v1/examinations/{id}/recurrence/` with a valid `interval`  
**Then** the response is rejected with a business-rule error.

---

#### TC-FR-039-09 — An existing recurrence rule remains attached and unchanged across status changes
**Requirement reference:** FR-039  
**Layer:** API integration test  
**Given** a `planned` examination with a `yearly` recurrence rule  
**When** the client changes the examination's status to `completed`, submitting a valid `completed_date` in the same request  
**Then** the recurrence rule remains attached with `interval: "yearly"` unchanged.

---

#### TC-FR-039-10 — Recurrence update is rejected once the examination is no longer planned
**Requirement reference:** FR-039  
**Layer:** API validation test  
**Given** a `planned` examination with an existing `monthly` recurrence rule, whose status is then changed to `completed` with a valid `completed_date`  
**When** the client submits `PATCH /api/v1/examinations/{id}/recurrence/` with `interval: "yearly"`  
**Then** the response is rejected with a business-rule error and the recurrence rule's `interval` remains `monthly`.

---

#### TC-FR-040-01 — Monthly recurrence adds one calendar month
**Requirement reference:** FR-040  
**Layer:** API integration test  
**Given** a `planned` examination with `scheduled_date: "2026-03-15"` and a `monthly` recurrence rule  
**When** the client retrieves the recurrence rule  
**Then** `next_due_date` is `2026-04-15`.

---

#### TC-FR-040-02 — Six-month recurrence adds six calendar months
**Requirement reference:** FR-040  
**Layer:** API integration test  
**Given** a `planned` examination with `scheduled_date: "2026-03-15"` and a `six_months` recurrence rule  
**When** the client retrieves the recurrence rule  
**Then** `next_due_date` is `2026-09-15`.

---

#### TC-FR-040-03 — Yearly recurrence adds one calendar year
**Requirement reference:** FR-040  
**Layer:** API integration test  
**Given** a `planned` examination with `scheduled_date: "2026-03-15"` and a `yearly` recurrence rule  
**When** the client retrieves the recurrence rule  
**Then** `next_due_date` is `2027-03-15`.

---

#### TC-FR-040-04 — A month-end source date clamps to the target month's last valid day
**Requirement reference:** FR-040  
**Layer:** API integration test  
**Given** a `planned` examination with `scheduled_date: "2026-01-31"` and a `monthly` recurrence rule  
**When** the client retrieves the recurrence rule  
**Then** `next_due_date` is `2026-02-28` (the last valid day of February in a non-leap year).

---

#### TC-FR-040-05 — Yearly recurrence from February 29 resolves to February 28 in a non-leap year
**Requirement reference:** FR-040  
**Layer:** API integration test  
**Given** a `planned` examination with `scheduled_date: "2028-02-29"` and a `yearly` recurrence rule  
**When** the client retrieves the recurrence rule  
**Then** `next_due_date` is `2029-02-28`.

---

#### TC-FR-040-06 — Next due date is null when the source has no scheduled date
**Requirement reference:** FR-040  
**Layer:** API integration test  
**Given** an examination with an attached recurrence rule whose `scheduled_date` has been removed  
**When** the client retrieves the recurrence rule  
**Then** `next_due_date` is `null`.

---

#### TC-FR-041-01 — Requesting the next occurrence creates exactly one new planned examination
**Requirement reference:** FR-041  
**Layer:** API integration test  
**Given** a `planned` source examination with a `scheduled_date` and a recurrence rule  
**When** the client submits `POST /api/v1/examinations/{id}/next-occurrence/`  
**Then** the response is `201 Created`, exactly one new examination exists with `status: "planned"` and `scheduled_date` equal to the calculated next due date.

---

#### TC-FR-041-02 — Next-occurrence creation is accepted from a completed source examination
**Requirement reference:** FR-041  
**Layer:** API integration test  
**Given** a `completed` source examination with a `scheduled_date` and a recurrence rule  
**When** the client submits `POST /api/v1/examinations/{id}/next-occurrence/`  
**Then** the response is `201 Created`.

---

#### TC-FR-041-03 — Next-occurrence creation is accepted from a cancelled source examination
**Requirement reference:** FR-041  
**Layer:** API integration test  
**Given** a `cancelled` source examination with a `scheduled_date` and a recurrence rule  
**When** the client submits `POST /api/v1/examinations/{id}/next-occurrence/`  
**Then** the response is `201 Created`.

---

#### TC-FR-041-04 — Next-occurrence creation is accepted from a missed source examination
**Requirement reference:** FR-041  
**Layer:** API integration test  
**Given** a `missed` source examination with a `scheduled_date` and a recurrence rule  
**When** the client submits `POST /api/v1/examinations/{id}/next-occurrence/`  
**Then** the response is `201 Created`.

---

#### TC-FR-041-05 — Next-occurrence creation is rejected for a draft source examination
**Requirement reference:** FR-041  
**Layer:** API validation test  
**Given** a `draft` source examination with a recurrence rule  
**When** the client submits `POST /api/v1/examinations/{id}/next-occurrence/`  
**Then** the response is `400 Bad Request` and no examination is created.

---

#### TC-FR-041-06 — A repeated next-occurrence request returns the existing occurrence instead of a duplicate
**Requirement reference:** FR-041  
**Layer:** API integration test  
**Given** a source examination for which a next occurrence has already been created for the current calculated due date  
**When** the client submits `POST /api/v1/examinations/{id}/next-occurrence/` again  
**Then** the response is `200 OK` describing the same previously generated examination, and no second record is created.

---

#### TC-FR-041-07 — The generated occurrence copies the documented fields and leaves the rest empty
**Requirement reference:** FR-041  
**Layer:** API integration test  
**Given** a fully populated `planned` source examination with a recurrence rule  
**When** the client submits `POST /api/v1/examinations/{id}/next-occurrence/`  
**Then** the generated examination has `title`, `category`, `medical_specialty`, `scheduled_time`, and `location` copied from the source; `status: "planned"`; `scheduled_date` equal to the calculated due date; `source_occurrence` equal to the source's id; `notes` and `completed_date` empty; and no reminder or recurrence rule attached.

---

### 5.6 Calendar

#### TC-FR-042-01 — A planned record is placed on its scheduled date
**Requirement reference:** FR-042  
**Layer:** Frontend integration test  
**Given** an owned `planned` record with a `scheduled_date` inside the selected month  
**When** the calendar for that month is rendered  
**Then** the record appears on its `scheduled_date`.

---

#### TC-FR-042-02 — A cancelled record is placed on its scheduled date
**Requirement reference:** FR-042  
**Layer:** Frontend integration test  
**Given** an owned `cancelled` record with a `scheduled_date` inside the selected month  
**When** the calendar for that month is rendered  
**Then** the record appears on its `scheduled_date`.

---

#### TC-FR-042-03 — A missed record is placed on its scheduled date
**Requirement reference:** FR-042  
**Layer:** Frontend integration test  
**Given** an owned `missed` record with a `scheduled_date` inside the selected month  
**When** the calendar for that month is rendered  
**Then** the record appears on its `scheduled_date`.

---

#### TC-FR-042-04 — Completed records are placed on their completion date
**Requirement reference:** FR-042  
**Layer:** Frontend integration test  
**Given** an owned `completed` record with `completed_date` inside the selected month  
**When** the calendar for that month is rendered  
**Then** the record appears on its `completed_date`.

---

#### TC-FR-042-05 — A draft record is excluded from calendar results
**Requirement reference:** FR-042  
**Layer:** API integration test  
**Given** a draft record within the requested range  
**When** the client requests `GET /api/v1/calendar/?start_date={date}&end_date={date}`  
**Then** the record does not appear in the response.

---

#### TC-FR-042-06 — A record missing its required display date is excluded from calendar results
**Requirement reference:** FR-042  
**Layer:** API integration test  
**Given** a `completed` record with no `completed_date`, within the requested range  
**When** the client requests `GET /api/v1/calendar/?start_date={date}&end_date={date}`  
**Then** the record does not appear in the response.

---

#### TC-FR-042-07 — A missing date-range parameter is rejected
**Requirement reference:** FR-042  
**Layer:** API integration test  
**Given** an authenticated user  
**When** the client requests `GET /api/v1/calendar/` with only one of `start_date` or `end_date` supplied  
**Then** the response is a validation error and no calendar data is returned.

---

#### TC-FR-042-08 — A malformed date-range parameter is rejected
**Requirement reference:** FR-042  
**Layer:** API integration test  
**Given** an authenticated user  
**When** the client requests `GET /api/v1/calendar/?start_date={not-a-date}&end_date={date}`  
**Then** the response is a validation error and no calendar data is returned.

---

#### TC-FR-042-09 — A start date after the end date is rejected
**Requirement reference:** FR-042  
**Layer:** API integration test  
**Given** an authenticated user  
**When** the client requests `GET /api/v1/calendar/?start_date={later-date}&end_date={earlier-date}`  
**Then** the response is a validation error and no calendar data is returned.

---

#### TC-FR-043-01 — A planned examination renders a distinct label and indicator
**Requirement reference:** FR-043  
**Layer:** Frontend component test  
**Given** a calendar entry in `planned` state  
**When** the calendar renders that entry  
**Then** it has its own semantic label and a non-color indicator (icon or shape) distinguishing it from every other state.

---

#### TC-FR-043-02 — A completed examination renders a distinct label and indicator
**Requirement reference:** FR-043  
**Layer:** Frontend component test  
**Given** a calendar entry in `completed` state  
**When** the calendar renders that entry  
**Then** it has its own semantic label and a non-color indicator (icon or shape) distinguishing it from every other state.

---

#### TC-FR-043-03 — A cancelled examination renders a distinct label and indicator
**Requirement reference:** FR-043  
**Layer:** Frontend component test  
**Given** a calendar entry in `cancelled` state  
**When** the calendar renders that entry  
**Then** it has its own semantic label and a non-color indicator (icon or shape) distinguishing it from every other state.

---

#### TC-FR-043-04 — A missed examination renders a distinct label and indicator
**Requirement reference:** FR-043  
**Layer:** Frontend component test  
**Given** a calendar entry in `missed` state  
**When** the calendar renders that entry  
**Then** it has its own semantic label and a non-color indicator (icon or shape) distinguishing it from every other state.

---

#### TC-FR-043-05 — An overdue examination renders a distinct label and indicator
**Requirement reference:** FR-043  
**Layer:** Frontend component test  
**Given** a calendar entry in derived `overdue` state  
**When** the calendar renders that entry  
**Then** it has its own semantic label and a non-color indicator (icon or shape) distinguishing it from every other state.

---

### 5.7 Dashboard

#### TC-FR-044-01 — The dashboard's upcoming collection matches the shared upcoming query
**Requirement reference:** FR-044  
**Layer:** API integration test  
**Given** an authenticated user with a record eligible for the upcoming collection  
**When** the client requests `GET /api/v1/dashboard/` and separately `GET /api/v1/examinations/?time_state=upcoming`  
**Then** the dashboard's `upcoming` array matches the records returned by the separate upcoming query.

---

#### TC-FR-044-02 — The dashboard's overdue collection matches the shared overdue query
**Requirement reference:** FR-044  
**Layer:** API integration test  
**Given** an authenticated user with a record eligible for the overdue collection  
**When** the client requests `GET /api/v1/dashboard/` and separately `GET /api/v1/examinations/?time_state=overdue`  
**Then** the dashboard's `overdue` array matches the records returned by the separate overdue query.

---

#### TC-FR-044-03 — The dashboard's recently-completed collection matches the shared past query
**Requirement reference:** FR-044  
**Layer:** API integration test  
**Given** an authenticated user with a record eligible for the recently-completed collection  
**When** the client requests `GET /api/v1/dashboard/`  
**Then** the dashboard's `recently_completed` array contains that record.

---

#### TC-FR-044-04 — A completion date exactly 29 days before today is included in recently completed
**Requirement reference:** FR-044  
**Layer:** API integration test  
**Given** the user's current local date is frozen at `2026-08-04` and a `completed` record has `completed_date: "2026-07-06"` (29 days earlier)  
**When** the client requests `GET /api/v1/dashboard/`  
**Then** `recently_completed` includes that record.

---

#### TC-FR-044-05 — A completion date equal to today is included in recently completed
**Requirement reference:** FR-044  
**Layer:** API integration test  
**Given** the user's current local date is frozen at `2026-08-04` and a `completed` record has `completed_date: "2026-08-04"`  
**When** the client requests `GET /api/v1/dashboard/`  
**Then** `recently_completed` includes that record.

---

#### TC-FR-044-06 — A completion date 30 days before today is excluded from recently completed
**Requirement reference:** FR-044  
**Layer:** API integration test  
**Given** the user's current local date is frozen at `2026-08-04` and a `completed` record has `completed_date: "2026-07-05"` (30 days earlier)  
**When** the client requests `GET /api/v1/dashboard/`  
**Then** `recently_completed` excludes that record.

---

#### TC-FR-044-07 — Recently completed is ordered by completion date descending
**Requirement reference:** FR-044  
**Layer:** API integration test  
**Given** eligible `completed` records with distinct `completed_date` values  
**When** the client requests `GET /api/v1/dashboard/`  
**Then** `recently_completed` is ordered by `completed_date` descending.

---

#### TC-FR-044-08 — Recently completed breaks same-date ties by identifier descending
**Requirement reference:** FR-044  
**Layer:** API integration test  
**Given** two eligible `completed` records sharing the same `completed_date`  
**When** the client requests `GET /api/v1/dashboard/`  
**Then** the two records appear in `recently_completed` ordered by `id` descending.

---

#### TC-FR-044-09 — Recently completed is limited to five records without pagination
**Requirement reference:** FR-044  
**Layer:** API integration test  
**Given** more than five eligible `completed` records  
**When** the client requests `GET /api/v1/dashboard/`  
**Then** `recently_completed` contains exactly the first five records after ordering, with no pagination metadata.

---

#### TC-FR-044-10 — Each dashboard section renders its own empty presentation independently
**Requirement reference:** FR-044  
**Layer:** Frontend integration test  
**Given** `GET /api/v1/dashboard/` returns an empty `overdue` array alongside populated `upcoming` and `recently_completed` arrays  
**When** the dashboard renders  
**Then** the overdue section shows its own empty presentation while the other two sections render their records.

---

#### TC-FR-045-01 — Status counts include all five statuses with correct and zero values
**Requirement reference:** FR-045  
**Layer:** API integration test  
**Given** an authenticated user with records in some but not all statuses  
**When** the client requests `GET /api/v1/dashboard/`  
**Then** `status_counts` contains all five keys, each with the correct count, and zero for statuses with no records.

---

#### TC-FR-046-01 — Category counts include every system-defined category including zero values
**Requirement reference:** FR-046  
**Layer:** API integration test  
**Given** an authenticated user with records assigned to some but not all categories  
**When** the client requests `GET /api/v1/dashboard/`  
**Then** `category_counts` contains one entry per system-defined category, each with the correct count, including zero-count categories.

---

#### TC-FR-046-02 — Uncategorized count reflects records with a null category
**Requirement reference:** FR-046  
**Layer:** API integration test  
**Given** an authenticated user with two records whose `category` is `null`  
**When** the client requests `GET /api/v1/dashboard/`  
**Then** `uncategorized_count` is `2`.

---

#### TC-FR-047-01 — Overdue count matches the shared overdue query
**Requirement reference:** FR-047  
**Layer:** API integration test  
**Given** the user's current local time is frozen and a known number of records satisfy the overdue query  
**When** the client requests `GET /api/v1/dashboard/` and separately `GET /api/v1/examinations/?time_state=overdue`  
**Then** `overdue_count` equals the number of records returned by the overdue query.

---

## 6. Test Cases — User Experience Requirements

#### TC-UX-001-01 — Primary pages remain usable at the approved phone viewport width
**Requirement reference:** UX-001  
**Layer:** Documented review  
**Given** the approved phone viewport width  
**When** registration, login, examination list, examination form, calendar, and dashboard pages are reviewed at that width  
**Then** no page requires horizontal scrolling and every control remains usable.

---

#### TC-UX-001-02 — Primary pages remain usable at the approved tablet viewport width
**Requirement reference:** UX-001  
**Layer:** Documented review  
**Given** the approved tablet viewport width  
**When** registration, login, examination list, examination form, calendar, and dashboard pages are reviewed at that width  
**Then** no page requires horizontal scrolling and every control remains usable.

---

#### TC-UX-001-03 — Primary pages remain usable at the approved desktop viewport width
**Requirement reference:** UX-001  
**Layer:** Documented review  
**Given** the approved desktop viewport width  
**When** registration, login, examination list, examination form, calendar, and dashboard pages are reviewed at that width  
**Then** no page requires horizontal scrolling and every control remains usable.

---

#### TC-UX-002-01 — A missing email shows a field-level error
**Requirement reference:** UX-002  
**Layer:** Frontend integration test  
**Given** the registration form with the email field left empty  
**When** the user submits the form  
**Then** an error is displayed adjacent to the email field.

---

#### TC-UX-002-02 — A malformed email shows a field-level error
**Requirement reference:** UX-002  
**Layer:** Frontend integration test  
**Given** the registration form with `not-an-email` entered in the email field  
**When** the user submits the form  
**Then** an error is displayed adjacent to the email field.

---

#### TC-UX-002-03 — A backend-rejected duplicate email shows a field-level error
**Requirement reference:** UX-002  
**Layer:** Frontend integration test  
**Given** the registration API rejects the submitted email as already registered  
**When** the response is received  
**Then** an error is displayed adjacent to the email field.

---

#### TC-UX-003-01 — A missing password shows a field-level error
**Requirement reference:** UX-003  
**Layer:** Frontend integration test  
**Given** the registration form with the password field left empty  
**When** the user submits the form  
**Then** an error is displayed adjacent to the password field.

---

#### TC-UX-003-02 — A password under eight characters shows a field-level error
**Requirement reference:** UX-003  
**Layer:** Frontend integration test  
**Given** the registration form with a seven-character password entered  
**When** the user submits the form  
**Then** an error is displayed adjacent to the password field.

---

#### TC-UX-004-01 — No timezone selection shows a field-level error
**Requirement reference:** UX-004  
**Layer:** Frontend integration test  
**Given** the registration form with no timezone selected  
**When** the user submits the form  
**Then** an error is displayed adjacent to the timezone field.

---

#### TC-UX-004-02 — A backend-rejected unsupported timezone shows a field-level error
**Requirement reference:** UX-004  
**Layer:** Frontend integration test  
**Given** the registration API rejects the submitted timezone as unsupported  
**When** the response is received  
**Then** an error is displayed adjacent to the timezone field.

---

#### TC-UX-005-01 — A title-only draft can be saved
**Requirement reference:** UX-005  
**Layer:** Frontend integration test  
**Given** the examination form with only a title entered  
**When** the user selects **Save draft**  
**Then** the draft is saved successfully.

---

#### TC-UX-005-02 — A draft with additional optional information can be saved
**Requirement reference:** UX-005  
**Layer:** Frontend integration test  
**Given** the examination form with a title and selected optional fields entered  
**When** the user selects **Save draft**  
**Then** the draft is saved successfully with the entered optional values.

---

#### TC-UX-006-01 — A planned examination can be saved with only title and scheduled date
**Requirement reference:** UX-006  
**Layer:** Frontend integration test  
**Given** the examination form set to planned mode with only a title and scheduled date entered  
**When** the user submits the form  
**Then** the examination is saved successfully without requiring category or scheduled time.

---

#### TC-UX-007-01 — A fixed timestamp displays in the user's configured timezone
**Requirement reference:** UX-007  
**Layer:** Frontend integration test  
**Given** a fixed UTC timestamp and an account timezone of `Europe/Warsaw`  
**When** the timestamp is rendered  
**Then** the displayed local date and time match the expected conversion to `Europe/Warsaw`.

---

#### TC-UX-007-02 — A date-only value displays as stored without timezone conversion
**Requirement reference:** UX-007  
**Layer:** Frontend integration test  
**Given** a `scheduled_date` of `2026-08-15` and an account timezone other than UTC  
**When** the date is rendered  
**Then** the displayed date is `2026-08-15`, unshifted by timezone conversion.

---

#### TC-UX-008-01 — Primary flows are completable using touch input
**Requirement reference:** UX-008  
**Layer:** Documented review  
**Given** the primary navigation, forms, dialogs, and examination actions  
**When** each is operated using touch input  
**Then** every primary action completes successfully.

---

#### TC-UX-008-02 — Primary flows are completable using mouse input
**Requirement reference:** UX-008  
**Layer:** Documented review  
**Given** the primary navigation, forms, dialogs, and examination actions  
**When** each is operated using mouse input  
**Then** every primary action completes successfully.

---

#### TC-UX-008-03 — Primary flows are completable using keyboard input alone
**Requirement reference:** UX-008  
**Layer:** Documented review  
**Given** the primary navigation, forms, dialogs, and examination actions  
**When** each is operated using keyboard input only, with no hover or pointer gesture  
**Then** every primary action completes successfully with visible keyboard focus at each step.

---

## 7. Test Cases — Security Requirements

#### TC-SEC-001-01 — Unauthenticated requests to the examination endpoint are rejected
**Requirement reference:** SEC-001  
**Layer:** API integration test  
**Given** no authentication credentials  
**When** the client requests `GET /api/v1/examinations/`  
**Then** the response is `401 Unauthorized`.

---

#### TC-SEC-001-02 — Unauthenticated requests to the reminder endpoint are rejected
**Requirement reference:** SEC-001  
**Layer:** API integration test  
**Given** no authentication credentials  
**When** the client requests `GET /api/v1/examinations/{id}/reminder/`  
**Then** the response is `401 Unauthorized`.

---

#### TC-SEC-001-03 — Unauthenticated requests to the recurrence endpoint are rejected
**Requirement reference:** SEC-001  
**Layer:** API integration test  
**Given** no authentication credentials  
**When** the client requests `GET /api/v1/examinations/{id}/recurrence/`  
**Then** the response is `401 Unauthorized`.

---

#### TC-SEC-001-04 — Unauthenticated requests to the calendar endpoint are rejected
**Requirement reference:** SEC-001  
**Layer:** API integration test  
**Given** no authentication credentials  
**When** the client requests `GET /api/v1/calendar/?start_date={date}&end_date={date}`  
**Then** the response is `401 Unauthorized`.

---

#### TC-SEC-001-05 — Unauthenticated requests to the dashboard endpoint are rejected
**Requirement reference:** SEC-001  
**Layer:** API integration test  
**Given** no authentication credentials  
**When** the client requests `GET /api/v1/dashboard/`  
**Then** the response is `401 Unauthorized`.

---

#### TC-SEC-001-06 — Unauthenticated requests to the account endpoint are rejected
**Requirement reference:** SEC-001  
**Layer:** API integration test  
**Given** no authentication credentials  
**When** the client requests `GET /api/v1/account/`  
**Then** the response is `401 Unauthorized`.

---

#### TC-SEC-001-07 — Registration does not require a bearer token
**Requirement reference:** SEC-001  
**Layer:** API integration test  
**Given** no bearer access token  
**When** the client submits `POST /api/v1/auth/register/` with an otherwise-valid request  
**Then** the request is not rejected for missing bearer authentication.

---

#### TC-SEC-001-08 — CSRF bootstrap does not require a bearer token
**Requirement reference:** SEC-001  
**Layer:** API integration test  
**Given** no bearer access token  
**When** the client requests `GET /api/v1/auth/csrf/`  
**Then** the request is not rejected for missing bearer authentication.

---

#### TC-SEC-001-09 — Login does not require a bearer token
**Requirement reference:** SEC-001  
**Layer:** API integration test  
**Given** no bearer access token  
**When** the client submits `POST /api/v1/auth/login/` with an otherwise-valid request  
**Then** the request is not rejected for missing bearer authentication.

---

#### TC-SEC-001-10 — Refresh does not require a bearer token
**Requirement reference:** SEC-001  
**Layer:** API integration test  
**Given** no bearer access token  
**When** the client submits `POST /api/v1/auth/refresh/` with an otherwise-valid request  
**Then** the request is not rejected for missing bearer authentication.

---

#### TC-SEC-001-11 — Health check does not require a bearer token
**Requirement reference:** SEC-001  
**Layer:** API integration test  
**Given** no bearer access token  
**When** the client requests `GET /api/v1/health/`  
**Then** the request is not rejected for missing bearer authentication.

---

#### TC-SEC-002-01 — A user cannot retrieve another user's examination
**Requirement reference:** SEC-002  
**Layer:** API authorization test  
**Given** an examination owned by User A  
**When** User B requests `GET /api/v1/examinations/{id}/` for that examination  
**Then** the response is `404 Not Found`.

---

#### TC-SEC-002-02 — A user cannot update another user's examination
**Requirement reference:** SEC-002  
**Layer:** API authorization test  
**Given** an examination owned by User A  
**When** User B submits `PATCH /api/v1/examinations/{id}/` for that examination  
**Then** the response is `404 Not Found` and the record is unchanged.

---

#### TC-SEC-002-03 — A user cannot delete another user's examination
**Requirement reference:** SEC-002  
**Layer:** API authorization test  
**Given** an examination owned by User A  
**When** User B submits `DELETE /api/v1/examinations/{id}/` for that examination  
**Then** the response is `404 Not Found` and the record still exists.

---

#### TC-SEC-002-04 — A user cannot attach a reminder to another user's examination
**Requirement reference:** SEC-002  
**Layer:** API authorization test  
**Given** an examination owned by User A  
**When** User B submits `POST /api/v1/examinations/{id}/reminder/` for that examination  
**Then** the request is rejected and no data from User A's account is disclosed.

---

#### TC-SEC-002-05 — A user cannot attach a recurrence rule to another user's examination
**Requirement reference:** SEC-002  
**Layer:** API authorization test  
**Given** an examination owned by User A  
**When** User B submits `POST /api/v1/examinations/{id}/recurrence/` for that examination  
**Then** the request is rejected and no data from User A's account is disclosed.

---

#### TC-SEC-003-01 — Stored passwords are hashed, not stored in plaintext
**Requirement reference:** SEC-003  
**Layer:** Backend model test  
**Given** a newly registered account with a known plaintext password  
**When** the stored password value is inspected  
**Then** it differs from the submitted plaintext and is accepted by Django's password-checking function for that plaintext.

---

#### TC-SEC-003-02 — Registration rejects a commonly used password
**Requirement reference:** SEC-003  
**Layer:** API validation test  
**Given** a registration request with `password` set to a value on Django's common-password list (for example, `password123`)  
**When** the client submits `POST /api/v1/auth/register/`  
**Then** the response is `400 Bad Request` with a `password` field error and no account is created.

---

#### TC-SEC-003-03 — Registration rejects an entirely numeric password
**Requirement reference:** SEC-003  
**Layer:** API validation test  
**Given** a registration request with `password` set to a value containing only digits  
**When** the client submits `POST /api/v1/auth/register/`  
**Then** the response is `400 Bad Request` with a `password` field error and no account is created.

---

#### TC-SEC-003-04 — Registration rejects a password matching the account's email address
**Requirement reference:** SEC-003  
**Layer:** API validation test  
**Given** a registration request whose `password` closely resembles the submitted `email` address  
**When** the client submits `POST /api/v1/auth/register/`  
**Then** the response is `400 Bad Request` with a `password` field error and no account is created.

---

#### TC-SEC-004-01 — No committed file contains a configured secret
**Requirement reference:** SEC-004  
**Layer:** Repository secret scan  
**Given** the repository's committed history and current tree  
**When** an automated secret scan runs  
**Then** no secret key, database credential, or authentication token is found in committed content.

---

#### TC-SEC-005-01 — A configured frontend origin is accepted
**Requirement reference:** SEC-005  
**Layer:** Deployment integration test  
**Given** a frontend origin present in the backend's CORS allowlist  
**When** a credentialed cross-origin request is sent from that origin  
**Then** the request is accepted.

---

#### TC-SEC-005-02 — An unconfigured origin is rejected
**Requirement reference:** SEC-005  
**Layer:** Deployment integration test  
**Given** a frontend origin absent from the backend's CORS allowlist  
**When** a credentialed cross-origin request is sent from that origin  
**Then** the request is rejected.

---

#### TC-SEC-005-03 — Production CORS configuration contains no wildcard origin
**Requirement reference:** SEC-005  
**Layer:** Configuration test  
**Given** the production CORS configuration  
**When** the allowlist is inspected  
**Then** it contains explicit origins only, with no wildcard entry.

---

#### TC-SEC-005-04 — Preflight responses permit the required credentialed headers
**Requirement reference:** SEC-005  
**Layer:** Deployment integration test  
**Given** a configured frontend origin  
**When** the client sends a CORS preflight request for a credentialed API call  
**Then** the response permits the `Authorization`, `Content-Type`, and `X-CSRFToken` headers.

---

#### TC-SEC-005-05 — A credentialed request from an unconfigured origin is rejected
**Requirement reference:** SEC-005  
**Layer:** Deployment integration test  
**Given** a frontend origin absent from the backend's CORS allowlist  
**When** the client sends a credentialed request from that origin  
**Then** the request is rejected and no cookies are set.

---

#### TC-SEC-005-06 — A valid CSRF token from a configured origin is accepted
**Requirement reference:** SEC-005  
**Layer:** Deployment integration test  
**Given** a CSRF token and cookie obtained from a configured frontend origin  
**When** the client submits a CSRF-protected request with a matching `X-CSRFToken` header  
**Then** the request passes CSRF validation.

---

#### TC-SEC-005-07 — A CSRF-protected request from an unconfigured origin is rejected
**Requirement reference:** SEC-005  
**Layer:** Deployment integration test  
**Given** a frontend origin absent from the CSRF trusted-origin list  
**When** the client submits a CSRF-protected request from that origin  
**Then** the request is rejected.

---

#### TC-SEC-005-08 — The refresh-token cookie carries its production attributes
**Requirement reference:** SEC-005  
**Layer:** API integration test  
**Given** a successful login under production configuration  
**When** the `refresh_token` cookie is inspected  
**Then** it is `HttpOnly`, host-only, scoped to path `/api/v1/auth/`, `Secure`, and `SameSite=None`.

---

#### TC-SEC-005-09 — The refresh-token cookie carries its local-development attributes
**Requirement reference:** SEC-005  
**Layer:** API integration test  
**Given** a successful login under local-development configuration  
**When** the `refresh_token` cookie is inspected  
**Then** it is `HttpOnly`, host-only, scoped to path `/api/v1/auth/`, not `Secure`, and `SameSite=Lax`.

---

#### TC-SEC-005-10 — The CSRF bootstrap endpoint sets the cookie and returns a matching token
**Requirement reference:** SEC-005  
**Layer:** API integration test  
**Given** no bearer authentication and a credentialed request  
**When** the client requests `GET /api/v1/auth/csrf/`  
**Then** the response is `200 OK`, sets or renews the CSRF cookie, and returns `csrf_token` corresponding to that cookie.

---

#### TC-SEC-005-11 — The frontend holds the CSRF token in memory and never reads the cookie directly
**Requirement reference:** SEC-005  
**Layer:** Frontend integration test  
**Given** a `csrf_token` obtained from the bootstrap endpoint  
**When** the frontend sends login, refresh, and logout requests  
**Then** each request carries the token in the `X-CSRFToken` header, and the frontend code never reads the CSRF cookie value directly.

---

#### TC-SEC-005-12 — The CSRF cookie is HttpOnly under production configuration
**Requirement reference:** SEC-005  
**Layer:** API integration test  
**Given** production configuration  
**When** the client submits a credentialed request to `GET /api/v1/auth/csrf/`  
**Then** the CSRF cookie is issued with `HttpOnly: true`.

---

#### TC-SEC-005-13 — The CSRF cookie is HttpOnly under local-development configuration
**Requirement reference:** SEC-005  
**Layer:** API integration test  
**Given** local-development configuration  
**When** the client submits a credentialed request to `GET /api/v1/auth/csrf/`  
**Then** the CSRF cookie is issued with `HttpOnly: true`.

---

#### TC-SEC-005-14 — The CSRF cookie uses its documented production attributes
**Requirement reference:** SEC-005  
**Layer:** Configuration test  
**Given** production configuration  
**When** the CSRF cookie is issued  
**Then** it uses path `/api/v1/`, `Secure`, and `SameSite=None`.

---

#### TC-SEC-005-15 — The CSRF cookie uses its documented local-development attributes
**Requirement reference:** SEC-005  
**Layer:** Configuration test  
**Given** local-development configuration  
**When** the CSRF cookie is issued  
**Then** it uses path `/api/v1/`, is not `Secure`, and uses `SameSite=Lax`.

---

#### TC-SEC-006-01 — A missing examination and another user's examination return identical not-found responses
**Requirement reference:** SEC-006  
**Layer:** API integration test  
**Given** an examination id that does not exist and a separate examination id owned by another user  
**When** the authenticated user requests `GET /api/v1/examinations/{id}/` for each  
**Then** both responses have the identical `404 Not Found` status and body structure.

---

#### TC-SEC-006-02 — An unknown email and an incorrect password return identical login failure responses
**Requirement reference:** SEC-006  
**Layer:** API integration test  
**Given** a login attempt with an unknown email and a login attempt with a registered account's correct email but an incorrect password  
**When** both requests are submitted to `POST /api/v1/auth/login/`  
**Then** both responses have the identical `401 Unauthorized` status and body structure.

---

#### TC-SEC-007-01 — Requests exceeding the configured limit are throttled
**Requirement reference:** SEC-007  
**Layer:** API integration test  
**Given** a client IP address that has reached the configured request limit for `POST /api/v1/auth/login/`  
**When** the client sends one more request to that endpoint  
**Then** the response is `429 Too Many Requests` with a `Retry-After` header.

---

#### TC-SEC-007-02 — The rate limit resets after the throttle window elapses
**Requirement reference:** SEC-007  
**Layer:** API integration test  
**Given** a client IP address that has been throttled on `POST /api/v1/auth/login/`  
**When** the client retries after the `Retry-After` interval has elapsed  
**Then** the request is accepted and evaluated normally.

---

## 8. Test Cases — Privacy Requirements

#### TC-PRV-001-01 — Stored and writable examination fields match the approved domain model
**Requirement reference:** PRV-001  
**Layer:** Data-model review  
**Given** the `ExaminationRecord` model and its create/update serializers  
**When** their field sets are compared against the approved domain model in `domain_model.md`  
**Then** every stored and writable field is present in the approved domain model and no additional field exists.

---

#### TC-PRV-002-01 — An examination can be created without clinical or identity data
**Requirement reference:** PRV-002  
**Layer:** API integration test  
**Given** an authenticated user  
**When** the client creates an examination using only appointment and examination metadata fields, supplying no diagnosis, prescription, medical file, insurance, or government identification data  
**Then** the record is created successfully.

---

#### TC-PRV-003-01 — The non-clinical purpose statement is displayed
**Requirement reference:** PRV-003  
**Layer:** Frontend component test  
**Given** the designated informational page  
**When** the page is rendered  
**Then** it states that the application is an organizational tool and does not provide medical advice, diagnosis, treatment, or emergency assistance.

---

#### TC-PRV-003-02 — The informational page is reachable from unauthenticated navigation
**Requirement reference:** PRV-003  
**Layer:** Frontend integration test  
**Given** an unauthenticated visitor  
**When** the visitor navigates the application  
**Then** the informational page is reachable.

---

#### TC-PRV-003-03 — The informational page is reachable from authenticated navigation
**Requirement reference:** PRV-003  
**Layer:** Frontend integration test  
**Given** an authenticated user  
**When** the user navigates the application  
**Then** the informational page is reachable.

---

## 9. Test Cases — Technical and Operational Requirements

#### TC-TECH-001-01 — Every documented endpoint matches its contract without browser-specific behavior
**Requirement reference:** TECH-001  
**Layer:** Contract test  
**Given** the OpenAPI contract maintained with the implementation  
**When** each documented MVP endpoint is exercised directly over HTTP  
**Then** each accepts and returns the documented JSON structures without relying on browser-specific behavior.

---

#### TC-TECH-002-01 — A date-only examination field round-trips correctly
**Requirement reference:** TECH-002  
**Layer:** Backend model test  
**Given** an examination with `scheduled_date: "2026-08-15"` and no `scheduled_time`  
**When** the record is saved and retrieved  
**Then** `scheduled_date` remains a date value equal to `2026-08-15` with no time or timezone component.

---

#### TC-TECH-002-02 — An examination with an optional scheduled time stores date and time separately
**Requirement reference:** TECH-002  
**Layer:** Backend model test  
**Given** an examination with `scheduled_date: "2026-08-15"` and `scheduled_time: "10:30:00"`  
**When** the record is saved and retrieved  
**Then** both values are retained as separate date and time fields with their original values.

---

#### TC-TECH-002-03 — A timezone-aware audit timestamp round-trips as an instant
**Requirement reference:** TECH-002  
**Layer:** Backend model test  
**Given** a newly created examination  
**When** its `created_at` value is saved and retrieved  
**Then** it is a timezone-aware datetime representing the same instant, unaffected by the account's configured timezone.

---

#### TC-TECH-003-01 — Development environment values apply development settings
**Requirement reference:** TECH-003  
**Layer:** Configuration test  
**Given** a defined set of development environment variables  
**When** the settings loader starts with those values  
**Then** the resulting settings match the expected development configuration.

---

#### TC-TECH-003-02 — Production environment values apply production settings
**Requirement reference:** TECH-003  
**Layer:** Configuration test  
**Given** a defined set of production environment variables  
**When** the settings loader starts with those values  
**Then** the resulting settings match the expected production configuration.

---

#### TC-TECH-003-03 — A missing required production value fails startup
**Requirement reference:** TECH-003  
**Layer:** Configuration test  
**Given** the production environment with one mandatory configuration value omitted  
**When** the application starts  
**Then** startup fails rather than falling back to a default or to development settings.

---

#### TC-TECH-004-01 — The health-check endpoint returns a minimal successful response
**Requirement reference:** TECH-004  
**Layer:** API integration test  
**Given** the web process is serving requests  
**When** an anonymous client requests `GET /api/v1/health/`  
**Then** the response is `200 OK` with body `{"status": "ok"}` and no configuration, environment, or secret value.

---

#### TC-TECH-005-01 — Production settings cannot enable debug mode by omission
**Requirement reference:** TECH-005  
**Layer:** Configuration test  
**Given** production settings loaded without an explicit debug override  
**When** the settings are inspected  
**Then** `DEBUG` is `False`.

---

#### TC-TECH-006-01 — Public frontend and backend URLs use HTTPS
**Requirement reference:** TECH-006  
**Layer:** Deployment smoke test  
**Given** the deployed environment  
**When** the public frontend and API URLs are requested  
**Then** both are served over HTTPS.

---

#### TC-TECH-006-02 — Normal application flows do not require plain HTTP
**Requirement reference:** TECH-006  
**Layer:** Deployment smoke test  
**Given** the deployed environment  
**When** the primary user flows are exercised end to end  
**Then** none of them require a plain HTTP request, and authentication cookies are marked `Secure`.

---

#### TC-TECH-007-01 — Documented procedures succeed in a clean environment
**Requirement reference:** TECH-007  
**Layer:** Documented review  
**Given** a clean environment and the repository's documented setup, migration, test, build, and deployment instructions  
**When** the instructions are followed in order  
**Then** the application starts and its test commands run successfully without undocumented corrective steps.

---

## 10. Change Control

A test case becomes part of this specification only after it is recorded here with a stable identifier.

When a test case changes:

1. update only the test case attached to its single requirement;
2. confirm that the requirement's stated verification method remains satisfied;
3. preserve the test case identifier so existing test code linked to it stays traceable, unless the scenario it verifies no longer applies, in which case mark it **Superseded** rather than reusing or renumbering the identifier;
4. add another test case under the same requirement when a new scenario is separate rather than expanding one test case to cover another requirement.

## 11. Traceability Summary

- Requirement references represented: **73**
- Test cases recorded: **272**
- Requirements verified by more than one test case: **FR-002, FR-003, FR-005, FR-006, FR-007, FR-008, FR-009, FR-012, FR-013, FR-014, FR-015, FR-016, FR-017, FR-018, FR-019, FR-020, FR-023, FR-024, FR-029, FR-030, FR-031, FR-032, FR-033, FR-035, FR-036, FR-037, FR-038, FR-039, FR-040, FR-041, FR-042, FR-043, FR-044, FR-046, FR-048, UX-001, UX-002, UX-003, UX-004, UX-005, UX-007, UX-008, SEC-001, SEC-002, SEC-003, SEC-005, SEC-006, SEC-007, PRV-003, TECH-002, TECH-003, TECH-006**
- Requirements verified by exactly one test case: all remaining requirement identifiers.
- Test cases linked to more than one requirement: **0**
