# Medical Tracker Application — Requirements Specification

## 1. Purpose

This document is the single source of truth for the testable requirements of the Medical Tracker Application MVP.

Each requirement contains:

- a unique identifier;
- one requirement statement using `shall`;
- one verification method describing how the requirement will be tested.

Verification statements identify the primary verification method. Detailed fixtures, test data, endpoint paths, and assertions belong in the test plan and test code.

## 2. Functional Requirements

### 2.1 Account and Session Management

**FR-001** — The application shall allow a new user to create an account using an email address, password, and timezone.
**Verification:** An API integration test shall submit valid registration data and confirm that the account is created.

**FR-002** — The application shall reject registration when the email address is missing, incorrectly formatted, or already registered; when the password is missing or shorter than eight characters; or when the timezone is unsupported.
**Verification:** An API validation test shall submit each defined invalid registration case and confirm that the account is not created and the corresponding field error is returned.

**FR-003** — The application shall allow a registered user to log in using valid credentials.
**Verification:** An API integration test shall confirm that valid credentials return authentication tokens and invalid credentials are rejected.

**FR-004** — The application shall allow an authenticated user to log out.
**Verification:** A frontend integration test shall confirm that logout clears the active client session and redirects the user to the login page.

**FR-005** — The application shall issue a new access token when a valid refresh token is submitted.
**Verification:** An API integration test shall confirm that a valid refresh token returns a new access token and that an expired or invalid refresh token is rejected.

**FR-006** — The application shall inform the user when their session has expired and cannot be refreshed.
**Verification:** A frontend integration test shall simulate a failed token refresh and confirm that the user is redirected to the login page with a session-expired message.

**FR-007** — The application shall allow an authenticated user to update the timezone associated with their account.
**Verification:** An API integration test shall update the account with a supported IANA timezone identifier and confirm that the selected timezone is saved.

### 2.2 Examination Records

**FR-008** — The application shall allow an authenticated user to create an examination record with a title, category, and scheduled date and time.
**Verification:** An API integration test shall submit valid examination data and confirm that the record is created for the authenticated user.

**FR-009** — The application shall support the examination statuses `planned`, `completed`, `cancelled`, and `missed`.
**Verification:** A serializer validation test shall confirm that every supported status is accepted and that any other status is rejected.

**FR-010** — The application shall assign the `planned` status when an examination record is created without an explicitly selected status.
**Verification:** An API integration test shall create an examination without a status and confirm that the returned record has the `planned` status.

**FR-011** — The application shall allow an authenticated user to store an optional medical specialty, completion date, location, and general notes for an examination record.
**Verification:** An API integration test shall save and retrieve an examination containing each optional field and confirm that the values are preserved.

**FR-012** — The application shall reject an examination record when the title, category, or scheduled date and time is missing, when the category does not exist, or when the status is unsupported.
**Verification:** An API validation test shall submit each defined invalid examination case and confirm that the record is not created and the corresponding field error is returned.

**FR-013** — The application shall require a completion date when an examination is marked as `completed`.
**Verification:** An API validation test shall confirm that a completed examination without a completion date is rejected and that a completed examination with a completion date is accepted.

**FR-014** — The application shall display the authenticated user's examination records.
**Verification:** Frontend tests shall confirm that the examination list displays a loading indicator while records are being retrieved, an empty message when no records exist, the returned records after a successful request, and an error message when the request fails.

**FR-015** — The application shall allow an authenticated user to view the details of an examination record they own.
**Verification:** An API integration test shall retrieve a user-owned examination and confirm that its stored fields are returned.

**FR-016** — The application shall allow an authenticated user to update an examination record they own.
**Verification:** An API integration test shall update a user-owned examination and confirm that the changes are saved.

**FR-017** — The application shall allow an authenticated user to delete an examination record they own.
**Verification:** An API integration test shall delete a user-owned examination and confirm that the record can no longer be retrieved.

**FR-018** — The application shall request confirmation before deleting an examination record through the user interface.
**Verification:** A frontend integration test shall select the delete action and confirm that the record is not deleted until the user confirms the operation.

**FR-019** — The application shall allow an authenticated user to assign one system-defined category to an examination record.
**Verification:** An API integration test shall assign an available category to an examination and confirm that the category is returned with the saved record.

**FR-020** — The application shall provide the system-defined categories Dentist, General practitioner, Specialist, Laboratory test, Vaccination, Preventive examination, Follow-up, and Other.
**Verification:** An API integration test shall confirm that all required system-defined categories are available and that no category appears more than once.

**FR-021** — The application shall allow an authenticated user to search their examination records by title.
**Verification:** An API integration test shall create examinations with different titles and confirm that a title search returns only matching records.

**FR-022** — The application shall allow an authenticated user to filter their examination records by status and category.
**Verification:** An API integration test shall create examinations with different statuses and categories and confirm that each filter returns the expected records.

**FR-023** — The application shall allow an authenticated user to order examination records by scheduled date in ascending or descending order.
**Verification:** An API integration test shall create examinations with different scheduled dates and confirm both supported ordering directions.

### 2.3 Past, Upcoming, and Overdue Examinations

**FR-024** — The application shall allow an authenticated user to view past examinations.
**Verification:** An API integration test shall confirm that the past-examinations response contains records with scheduled dates earlier than the current time and excludes future records.

**FR-025** — The application shall allow an authenticated user to view upcoming examinations.
**Verification:** An API integration test shall confirm that the upcoming-examinations response contains planned records with scheduled dates later than the current time and excludes past or non-planned records.

**FR-026** — The application shall identify a planned examination as overdue when its scheduled date and time is earlier than the current time.
**Verification:** An API integration test shall confirm that a past planned examination is returned as overdue and a future planned examination is not.

**FR-027** — The application shall exclude completed, cancelled, and missed examinations from the overdue examinations response.
**Verification:** An API integration test shall create past examinations with each supported status and confirm that only the `planned` examination is returned as overdue.

### 2.4 In-Application Reminders

**FR-028** — The application shall allow an authenticated user to enable, update, and disable an in-application reminder using a positive whole-number offset in days before a planned examination.
**Verification:** An API integration test shall create, update, and disable a reminder and shall confirm that zero, negative, and non-whole-number offsets are rejected.

**FR-029** — The application shall calculate a reminder due time from the examination date and the configured reminder offset.
**Verification:** An API integration test shall use fixed examination dates and reminder offsets and confirm the calculated due times.

**FR-030** — The application shall display active reminders whose due time has been reached.
**Verification:** A frontend integration test shall provide due and non-due reminders and confirm that only due reminders are displayed.

**FR-031** — The application shall deactivate an examination reminder when the examination is marked as `completed`, `cancelled`, or `missed`.
**Verification:** An API integration test shall change an examination to each defined terminal status and confirm that its reminder is inactive.

### 2.5 Recurring Examinations

**FR-032** — The application shall allow an authenticated user to configure a recurrence interval of monthly, every six months, or yearly for an examination.
**Verification:** An API validation test shall confirm that each supported recurrence interval is accepted and any other interval is rejected.

**FR-033** — The application shall calculate the next due date for a recurring examination.
**Verification:** An API integration test shall confirm the calculated next due date for each supported recurrence interval, including month-end and leap-year cases.

**FR-034** — The application shall create one next occurrence of a recurring examination when requested by the user.
**Verification:** An API integration test shall request the next occurrence and confirm that exactly one planned examination is created with the calculated date.

### 2.6 Calendar

**FR-035** — The application shall allow an authenticated user to view their examinations in a monthly calendar.
**Verification:** A frontend integration test shall provide examination records for a selected month and confirm that each record appears on its scheduled date.

**FR-036** — The application shall visually distinguish examinations in the calendar according to their current state.
**Verification:** A frontend component test shall render examinations in each supported state and confirm that each state has a distinct indicator.

### 2.7 Dashboard

**FR-037** — The application shall display upcoming examinations, overdue examinations, and recently completed examinations on the dashboard
**Verification:** A frontend integration test shall provide representative examination data and confirm that each record appears in the appropriate dashboard section.

**FR-038** — The application shall display examination counts by category and totals for planned and completed examinations on the dashboard.
**Verification:** A frontend integration test shall provide known dashboard totals and confirm that every returned value is displayed in the corresponding dashboard section.

## 3. User Experience Requirements

**UX-001** — The application shall use a mobile-first responsive layout on phone, tablet, and desktop screen sizes.
**Verification:** A documented responsive-browser review shall confirm that registration, login, examination list, examination form, calendar, and dashboard pages remain usable at the approved mobile, tablet, and desktop viewport widths.

**UX-002** — The registration form shall display a field-level error for a missing or invalid email address, a duplicate email address, a missing or short password, and a missing or unsupported timezone.
**Verification:** A frontend component test shall submit each defined invalid registration case and confirm that the corresponding field-level error is displayed.

**UX-003** — The examination form shall display a field-level error for a missing title, missing category, missing scheduled date and time, unsupported status, and missing completion date for a completed examination.
**Verification:** A frontend component test shall submit each defined invalid examination case and confirm that the corresponding field-level error is displayed.

**UX-004** — The application shall display examination dates and times using the timezone configured for the authenticated user.
**Verification:** A frontend test shall render a fixed UTC timestamp for a configured timezone and confirm that the expected local date and time are displayed.

**UX-005** — The application's primary navigation, forms, dialogs, and examination actions shall be operable using touch, mouse, and keyboard input.
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

**SEC-006** — The application shall return the same not-found response when a requested examination record does not exist or belongs to another user.
**Verification:** An API integration test shall confirm that both requests return the same HTTP status and response structure.

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

**TECH-002** — The application shall store examination, reminder, and recurrence dates and times as timezone-aware values.
**Verification:** A backend model test shall save timezone-aware values and confirm that they remain timezone-aware when retrieved.

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

- `requirements-specification.md` is the canonical requirements document.
- Requirement identifiers shall remain stable after implementation tasks or tests reference them.
- A changed requirement shall be edited in this file rather than duplicated in another document.
- Design documents, API contracts, implementation tasks, and tests shall reference the applicable requirement identifiers.
- New requirements shall receive the next available identifier within their category.
- Architecture decisions, technology selections, and release-governance rules shall be documented outside this requirements specification.