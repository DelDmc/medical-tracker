# Medical Tracker Application — Requirements Specification

## 1. Purpose

This document is the single source of truth for the testable requirements of the Medical Tracker Application MVP.

Each requirement contains:

- a unique identifier;
- a verification method describing how the requirement will be tested.

Verification statements identify the primary verification method. Detailed fixtures, test data, endpoint paths, and assertions belong in the test plan and test code.

## 2. Functional Requirements

### 2.1 Account and Session Management

**FR-001** — The application shall allow a new user to create an account using an email address, password, and timezone.
**Verification:** An API integration test shall submit valid registration data and confirm that the account is created.

**FR-002** — The application shall reject registration when the email address is missing, incorrectly formatted, or already registered.
**Verification:** An API validation test shall confirm that registration is rejected when the email address is missing, incorrectly formatted, or already associated with an existing account.

**FR-003** — The application shall reject registration when the password is missing, contains fewer than eight characters, or contains more than 128 characters.
**Verification:** An API validation test shall confirm that registration is rejected when the password is missing, shorter than eight characters, or longer than 128 characters.

**FR-004** — The application shall reject registration when the selected timezone is unsupported.
**Verification:** An API validation test shall confirm that registration is rejected when the submitted timezone is not included in the supported timezone set.

**FR-005** — The application shall allow a registered user to log in using valid credentials.
**Verification:** An API integration test shall confirm that valid credentials return authentication tokens and invalid credentials are rejected.

**FR-006** — The application shall allow an authenticated user to log out.
**Verification:** An API integration test shall confirm that logout invalidates the refresh token and clears the refresh-token cookie, and a frontend integration test shall confirm that logout clears the active client session and redirects the user to the login page.

**FR-007** — The application shall issue a new access token when a valid refresh token is submitted.
**Verification:** An API integration test shall confirm that a valid refresh token returns a new access token and that an expired or invalid refresh token is rejected.

**FR-008** — The application shall inform the user when their session has expired and cannot be refreshed.
**Verification:** A frontend integration test shall simulate a failed token refresh and confirm that the user is redirected to the login page with a session-expired message.

**FR-009** — The application shall allow an authenticated user to update the timezone associated with their account.
**Verification:** An API integration test shall update the account with a supported IANA timezone identifier and confirm that the selected timezone is saved.

### 2.2 Examination Records

**FR-010** — The application shall allow an authenticated user to create a draft examination record by providing a title and any available optional examination information.
**Verification:** An API integration test shall create a draft with a title and scheduled date but without a category or scheduled time and confirm that all submitted values are preserved.

**FR-011** — The application shall allow an authenticated user to create a planned examination record by providing a title and scheduled date.
**Verification:** An API integration test shall create a planned examination with a title and scheduled date but without a category or scheduled time and confirm that the record is saved with the `planned` status.

**FR-012** — The application shall support the examination statuses `draft`, `planned`, `completed`, `cancelled`, and `missed`.
**Verification:** A serializer validation test shall confirm that every supported status is accepted and that any other status is rejected.

**FR-013** — The application shall allow an authenticated user to store an optional medical specialty, location, and general notes for an examination record.
**Verification:** An API integration test shall save and retrieve an examination containing each optional field and confirm that the values are preserved.

**FR-014** — The application shall require a title for every examination record, a scheduled date for `planned`, `cancelled`, and `missed` records, and a completion date not later than the authenticated user's current local date for `completed` records.
**Verification:** API validation tests shall submit each status without its required title or date field and shall submit a completed record with a future completion date; each invalid record shall be rejected with the corresponding field error.

**FR-015** — The application shall reject an examination record when a supplied category does not exist or when its status is unsupported.
**Verification:** An API validation test shall submit a nonexistent category and an unsupported status and confirm that each value is rejected.

**FR-016** — The application shall allow an authenticated user to change a draft examination record to `planned` after providing a scheduled date.
**Verification:** An API integration test shall add a scheduled date to a draft without adding a category or scheduled time and confirm that its status changes to `planned`.

**FR-017** — The application shall reject reminder configuration for draft examination records.
**Verification:** An API validation test shall attempt to configure a reminder for a draft record and confirm that the request is rejected.

**FR-018** — The application shall reject recurrence configuration for draft examination records.
**Verification:** An API validation test shall attempt to configure a recurrence rule for a draft record and confirm that the request is rejected.

**FR-019** — The application shall exclude draft examination records from upcoming, overdue, and calendar results.
**Verification:** An API integration test shall create a draft record and confirm that it is absent from the upcoming, overdue, and calendar responses.

**FR-020** — The application shall display the authenticated user's examination records.
**Verification:** Frontend tests shall confirm that the examination list displays a loading indicator while records are being retrieved, an empty message when no records exist, the returned records after a successful request, and an error message when the request fails.

**FR-021** — The application shall allow an authenticated user to view the details of an examination record they own.
**Verification:** An API integration test shall retrieve a user-owned examination and confirm that its stored fields are returned.

**FR-022** — The application shall allow an authenticated user to update an examination record they own.
**Verification:** An API integration test shall update a user-owned examination and confirm that the changes are saved.

**FR-023** — The application shall allow an authenticated user to delete an examination record they own.
**Verification:** An API integration test shall delete a user-owned examination and confirm that the record can no longer be retrieved.

**FR-024** — The application shall request confirmation before deleting an examination record through the user interface.
**Verification:** A frontend integration test shall select the delete action and confirm that the record is not deleted until the user confirms the operation.

**FR-025** — The application shall allow an authenticated user to assign one system-defined category to an examination record.
**Verification:** An API integration test shall assign an available category to an examination and confirm that the category is returned with the saved record.

**FR-026** — The application shall provide the system-defined categories General medical appointment, Dental appointment, Specialist consultation, Laboratory test, Vaccination, Preventive examination, Follow-up, and Other.
**Verification:** An API integration test shall confirm that all required system-defined categories are available and that no category appears more than once.

**FR-027** — The application shall display an examination record without an assigned category as Uncategorized.
**Verification:** A frontend component test shall render an examination record without an assigned category and confirm that Uncategorized is displayed.

**FR-028** — The application shall allow an authenticated user to search their examination records by title.
**Verification:** An API integration test shall create examinations with different titles and confirm that a title search returns only matching records.

**FR-029** — The application shall allow an authenticated user to filter their examination records by status and category.
**Verification:** An API integration test shall create examinations with different statuses and categories and confirm that each filter returns the expected records.

**FR-030** — The application shall allow an authenticated user to order examination records by scheduled date in ascending or descending order, with records without a scheduled date placed after dated records.
**Verification:** An API integration test shall create dated and undated examinations and confirm both supported ordering directions and the placement of undated records.

### 2.3 Past, Upcoming, and Overdue Examinations

**FR-031** — The application shall allow an authenticated user to view completed, cancelled, and missed examinations whose relevant date is not later than the current date.
**Verification:** An API integration test shall confirm that the past-examinations response contains completed examinations by completion date and cancelled or missed examinations by scheduled date, and excludes future, planned, and draft records.

**FR-032** — The application shall allow an authenticated user to view planned examinations that are not overdue.
**Verification:** An API integration test shall confirm that the upcoming-examinations response contains planned records scheduled for the future and date-only records scheduled for the current date, and excludes overdue and non-planned records.

**FR-033** — The application shall identify a planned examination as overdue when its scheduled date is before the current date, or when its scheduled date is the current date and its specified scheduled time has passed.
**Verification:** An API integration test shall confirm that a past-date examination and a current-date examination with a past time are overdue, while a current-date examination without a scheduled time is not overdue.

**FR-034** — The application shall exclude completed, cancelled, missed, and draft examinations from the overdue examinations response.
**Verification:** An API integration test shall create past examinations with each supported status and confirm that only the `planned` examination is returned as overdue.

### 2.4 In-Application Reminders

**FR-035** — The application shall allow an authenticated user to enable, update, and disable an in-application reminder using a positive whole-number offset in days before a planned examination.
**Verification:** An API integration test shall create, update, and disable a reminder and shall confirm that zero, negative, and non-whole-number offsets are rejected, and that reminder creation, offset updates, and reactivation are rejected when the associated examination's status is not `planned`.

**FR-036** — The application shall calculate a reminder due date from the examination scheduled date and the configured reminder offset.
**Verification:** An API integration test shall use fixed scheduled dates and reminder offsets and confirm the calculated reminder due dates.

**FR-037** — The application shall display active reminders whose due date has been reached.
**Verification:** An API integration test shall confirm that the reminders endpoint's due-state filter returns only active reminders whose due date has been reached, and a frontend integration test shall provide due and non-due reminders and confirm that only due reminders are displayed.

**FR-038** — The application shall deactivate an examination reminder when the examination status changes from `planned` to `draft`, `completed`, `cancelled`, or `missed`.
**Verification:** An API integration test shall change a planned examination to each defined non-planned status and confirm that its reminder is inactive.

### 2.5 Recurring Examinations

**FR-039** — The application shall allow an authenticated user to configure a recurrence interval of monthly, every six months, or yearly for a planned examination.
**Verification:** An API validation test shall confirm that each supported recurrence interval is accepted for a planned examination and any other interval is rejected.

**FR-040** — The application shall calculate the next due date for a recurring examination.
**Verification:** An API integration test shall confirm the calculated next due date for each supported recurrence interval, including month-end and leap-year cases.

**FR-041** — The application shall create one next occurrence of a recurring examination when requested by the user.
**Verification:** An API integration test shall request the next occurrence and confirm that exactly one planned examination is created with the calculated date.

### 2.6 Calendar

**FR-042** — The application shall display planned, cancelled, and missed examinations on their scheduled date and completed examinations on their completion date in a monthly calendar.
**Verification:** A frontend integration test shall provide dated examinations for a selected month and confirm that each record appears on the date defined for its status.

**FR-043** — The application shall visually distinguish planned, completed, cancelled, missed, and overdue examinations in the calendar.
**Verification:** A frontend component test shall render examinations in each calendar state and confirm that each state has a distinct indicator.

### 2.7 Dashboard

**FR-044** — The application shall display upcoming examinations, overdue examinations, and recently completed examinations on the dashboard.
**Verification:** An API integration test shall freeze the authenticated user's local date and verify the recently completed eligibility boundaries, deterministic ordering, and five-record limit. A frontend integration test shall confirm that the dashboard displays each required examination section using the data returned by the API.

**FR-045** — The application shall display examination counts for each supported status on the dashboard.
**Verification:** An API integration test shall confirm that the dashboard response contains the correct count for draft, planned, completed, cancelled, and missed examinations.

**FR-046** — The application shall display examination counts for each system-defined category and for examinations without an assigned category on the dashboard.
**Verification:** An API integration test shall confirm that the dashboard response contains the correct count for each system-defined category and for uncategorized examinations.

**FR-047** — The application shall display the number of overdue examinations on the dashboard.
**Verification:** An API integration test shall confirm that the dashboard response contains the correct overdue examination count.

### 2.8 Account Management

**FR-048** — The application shall allow an authenticated user to change their password by submitting their current password and a new password.
**Verification:** An API integration test shall submit a correct current password with a valid new password and confirm the account can subsequently authenticate only with the new password, and shall confirm that an incorrect current password or a new password failing the accepted password policy is rejected without changing the stored password.

## 3. User Experience Requirements

**UX-001** — The application shall use a mobile-first responsive layout on phone, tablet, and desktop screen sizes.
**Verification:** A documented responsive-browser review shall confirm that registration, login, examination list, examination form, calendar, and dashboard pages remain usable at the approved mobile, tablet, and desktop viewport widths.

**UX-002** — The registration form shall display a field-level error when the email address is missing, incorrectly formatted, or already registered.
**Verification:** Frontend tests shall confirm that each email validation condition displays an error next to the email field.

**UX-003** — The registration form shall display a field-level error when the password is missing or contains fewer than eight characters.
**Verification:** Frontend tests shall confirm that each password validation condition displays an error next to the password field.

**UX-004** — The registration form shall display a field-level error when the timezone is missing or unsupported.
**Verification:** Frontend tests shall confirm that each timezone validation condition displays an error next to the timezone field.

**UX-005** — The examination form shall allow a draft examination record to be saved with a title and any available optional information.
**Verification:** A frontend integration test shall submit a draft with a title and without a category, scheduled date, or scheduled time and confirm that the record is saved.

**UX-006** — The examination form shall allow a planned examination record to be saved with a title and scheduled date without requiring a category or scheduled time.
**Verification:** A frontend integration test shall submit a planned examination with a title and scheduled date only and confirm that the record is saved.

**UX-007** — The application shall display examination dates and times using the timezone configured for the authenticated user.
**Verification:** A frontend test shall render a fixed UTC timestamp for a configured timezone and confirm that the expected local date and time are displayed.

**UX-008** — The application's primary navigation, forms, dialogs, and examination actions shall be operable using touch, mouse, and keyboard input.
**Verification:** A documented interaction review shall confirm that each primary action can be completed with touch, mouse, and keyboard input.

## 4. Security Requirements

**SEC-001** — The application shall require authentication before granting access to examination, reminder, recurrence, calendar, and dashboard data.
**Verification:** An API integration test shall send unauthenticated requests to every protected endpoint and confirm that each request is rejected.

**SEC-002** — The application shall restrict each user to examination, reminder, and recurrence records owned by their account.
**Verification:** An API authorization test shall confirm that one user cannot retrieve, update, or delete records owned by another user.

**SEC-003** — The application shall store user passwords using Django's password-hashing framework.
**Verification:** A backend test shall confirm that a registered user's stored password differs from the submitted password and is accepted by Django's password verification function.

**SEC-004** — The application shall load secret keys, credentials, and authentication secrets from environment variables.
**Verification:** An automated repository secret scan shall confirm that committed files contain no configured secret keys, credentials, or authentication tokens.

**SEC-005** — The deployed backend shall accept browser requests only from configured frontend origins.
**Verification:** A deployment integration test shall confirm that a configured origin is accepted and an unconfigured origin is rejected.

**SEC-006** — The application shall return an identical failure response regardless of the specific reason for failure, wherever a differing response would disclose whether a specific record or account exists. This applies at minimum to examination record lookup (identical `404 Not Found` for a missing record and a record owned by another user) and to login (identical `401 Unauthorized` for an unknown email and an incorrect password).
**Verification:** An API integration test shall confirm that both examination-lookup failure cases return the same HTTP status and response structure, and that both login failure cases return the same HTTP status and response structure.

**SEC-007** — The application shall rate-limit unauthenticated registration, login, and refresh requests and reject requests over the configured limit with `429 Too Many Requests`.
**Verification:** An API integration test shall exceed the configured limit for each endpoint and confirm that further requests receive `429 Too Many Requests` until the limit window resets.

## 5. Privacy Requirements

**PRV-001** — The application shall limit stored examination information to the appointment and examination metadata defined in the approved domain model.
**Verification:** A data-model review shall confirm that every stored examination field is included in the approved domain model.

**PRV-002** — The application shall require only appointment and examination metadata when creating an examination record.
**Verification:** An API integration test shall confirm that an examination record can be created without diagnoses, prescriptions, medical files, insurance information, or government identification data.

**PRV-003** — The application shall display a statement that it is an organizational tool and does not provide medical advice, diagnosis, treatment, or emergency assistance.
**Verification:** A frontend component test shall confirm that the statement is displayed on the designated informational page.

## 6. Technical and Operational Requirements

**TECH-001** — The application shall expose documented JSON REST API endpoints for authentication and domain data independently of the frontend interface.
**Verification:** An API contract test shall confirm that every documented MVP endpoint accepts and returns the defined JSON structures without requiring browser-specific behavior.

**TECH-002** — The application shall store scheduled dates separately from optional scheduled times and shall store timestamps that represent an instant as timezone-aware values.
**Verification:** A backend model test shall save and retrieve a date-only examination, an examination with an optional scheduled time, and a timezone-aware timestamp and confirm that each value retains its intended type and value.

**TECH-003** — The application shall load environment-specific configuration from environment variables.
**Verification:** A configuration test shall run the application with defined development and production environment values and confirm that the corresponding settings are applied.

**TECH-004** — The backend shall provide a health-check endpoint.
**Verification:** An API integration test shall call the health-check endpoint and confirm a successful response containing the expected health status.

**TECH-005** — The production backend shall run with debug mode disabled.
**Verification:** A deployment configuration test shall confirm that the production configuration sets Django debug mode to disabled.

**TECH-006** — The deployed frontend and backend shall be accessible through HTTPS.
**Verification:** A deployment smoke test shall confirm that the public frontend and API URLs use HTTPS.

**TECH-007** — The repository shall document local setup, test execution, database migration, build, and deployment procedures.
**Verification:** A clean-environment documentation review shall follow the documented procedures and confirm that the application can be started and its test commands can be executed.

## 7. Requirement Maintenance

- `requirements_specification.md` is the canonical requirements document.
- Requirement identifiers shall remain stable after implementation tasks or tests reference them.
- A changed requirement shall be edited in this file rather than duplicated in another document.
- Traceability between requirements, design decisions, and API operations shall be maintained in `traceability_matrix.md`.
- Implementation tasks and tests shall reference the applicable requirement identifiers.
- Detailed design documents and API contracts are not required to reproduce requirement or design-decision identifiers.
- New requirements shall receive the next available identifier within their category.
- Architecture decisions, technology selections, and release-governance rules shall be documented outside this requirements specification.