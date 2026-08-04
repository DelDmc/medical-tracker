# Medical Tracker Application — User Flows

## 1. Purpose

This document describes the user-visible and system-level flows for the Medical Tracker Application MVP.

The requirements specification is authoritative. This document applies the accepted application design decisions without changing or extending the required behavior.

## 2. Register and Log In

**Requirement references:** FR-001–FR-005, SEC-005, UX-002–UX-004

### Preconditions

- the user is not authenticated.

### Registration flow

1. The user opens the registration page.
2. The user enters an email address, password, and timezone.
3. The frontend validates the submitted fields.
4. The frontend sends `POST /api/v1/auth/register/`.
5. The backend requires all three fields, validates the email format, normalizes the email for case-insensitive uniqueness checking, validates the password minimum length, and validates the timezone against the supported IANA timezone set.
6. The backend creates the account through the Django user manager without returning the password.
7. The application presents a successful registration result and allows the user to log in.

### Login flow

1. The user opens the login page and enters their email address and password.
2. When no CSRF token is held in application memory, the frontend sends a credentialed `GET /api/v1/auth/csrf/` request.
3. The backend sets or renews the `HttpOnly` CSRF cookie and returns the corresponding token in `csrf_token`.
4. The frontend holds `csrf_token` only in application memory and does not read the CSRF cookie directly.
5. The frontend sends a credentialed `POST /api/v1/auth/login/` request with the email and password and sends the in-memory token through `X-CSRFToken`.
6. The backend validates the CSRF token and credentials.
7. Valid credentials return `access_token` in JSON and set the refresh token only in the `HttpOnly` `refresh_token` cookie.
8. The frontend holds `access_token` only in application memory and sends it to protected endpoints through `Authorization: Bearer <access_token>`.
9. The frontend removes `medical_tracker.logout_intent` from `localStorage`.
10. The authenticated dashboard opens.

### Failure behavior

- a missing, incorrectly formatted, or already registered email displays an error adjacent to the email field;
- a missing password or a password shorter than eight characters displays an error adjacent to the password field;
- a missing or unsupported timezone displays an error adjacent to the timezone field;
- missing or mismatched CSRF data rejects login without creating an authenticated session;
- invalid login credentials return one generic authentication error and do not disclose whether the account exists;
- network or server failure displays an error without creating an authenticated client session.

## 3. Restore or Refresh an Authenticated Session

**Requirement references:** FR-007, FR-008, SEC-005

### Session restoration after page reload

1. Protected-application initialization finds no access token because access tokens are not persisted outside application memory.
2. The frontend checks `medical_tracker.logout_intent` in `localStorage`.
3. When the marker exists, the frontend does not attempt session restoration and opens the login page.
4. When the marker is absent, the frontend obtains a CSRF token through a credentialed `GET /api/v1/auth/csrf/` request and holds the returned token in application memory.
5. The frontend makes one credentialed request to `POST /api/v1/auth/refresh/` with the in-memory token in `X-CSRFToken`; the request has no JSON body.
6. The backend reads the refresh token from the `refresh_token` cookie.
7. When the refresh token is valid, the backend invalidates it, issues a replacement refresh token in the cookie, and returns a new `access_token` in JSON.
8. The frontend stores the returned access token only in application memory and continues loading the protected application.
9. When initialization refresh fails, the frontend opens the login page without another refresh attempt and without a session-expired message.

### Active-session refresh

1. A protected API request using `Authorization: Bearer <access_token>` fails because the access token is no longer valid.
2. The frontend API client makes at most one credentialed request to `POST /api/v1/auth/refresh/` with the in-memory CSRF token in `X-CSRFToken`.
3. When the refresh token is valid, the backend rotates it, invalidates the previous token, sets the replacement `refresh_token` cookie, and returns a new `access_token`.
4. The frontend replaces the in-memory access token and repeats the original protected request once with the new bearer token.
5. The frontend does not enter a repeated refresh or request-replay loop.
6. When the refresh token is expired, revoked, malformed, missing, or otherwise invalid, the backend issues no credentials and clears the stale refresh cookie.
7. The frontend clears authentication state, redirects to the login page, and displays a session-expired message.
8. When no refresh request is in progress, the frontend creates one shared refresh operation. 
9. When a refresh request is already in progress, every other protected request with an access-token authentication failure waits for that same operation and does not send another refresh request.

## 4. Log Out

**Requirement references:** FR-006, SEC-005

### Preconditions

- the user is authenticated.

1. The user selects **Log out**.
2. The frontend writes `true` to `medical_tracker.logout_intent` in `localStorage`.
3. The frontend immediately clears the in-memory access token and authenticated-user state. The in-memory CSRF token remains available for the logout request.
4. The frontend sends a credentialed `POST /api/v1/auth/logout/` request with the in-memory CSRF token in `X-CSRFToken`; the request has no JSON body and does not require a bearer access token.
5. When the refresh cookie contains a valid token, the backend invalidates it.
6. The backend clears the `refresh_token` cookie for valid, expired, revoked, already invalid, and missing refresh-token states.
7. The backend returns `204 No Content` with an empty response body for each of those states.
8. The frontend navigates to the login page after the request succeeds, fails, or cannot reach the backend.
9. While `medical_tracker.logout_intent` exists, later protected-application initialization does not attempt session restoration.
10. A later successful login removes the logout-intent marker.

## 5. Update Account Timezone

**Requirement references:** FR-009, UX-007

### Preconditions

- the user is authenticated.

1. The user opens account settings.
2. The frontend requests `GET /api/v1/account/`.
3. The application displays the account's current timezone.
4. The user selects a supported IANA timezone identifier.
5. The frontend sends `PATCH /api/v1/account/` with the new `timezone` value.
6. The backend validates the value and updates only the authenticated user's account.
7. The application updates the timezone held in client state.
8. Timezone-aware timestamps are subsequently converted to the selected timezone for presentation.
9. Date-only values remain the stored calendar dates and are not shifted through UTC conversion.
10. Upcoming, overdue, past, and due-reminder calculations use the updated timezone's current local date and time.

### Failure behavior

- an unsupported timezone is rejected and the previously stored timezone remains unchanged;
- an unauthenticated request follows the session-expiration or authentication-failure flow.

## 6. Load System-Defined Categories

**Requirement references:** FR-025–FR-027

1. The examination form requests `GET /api/v1/categories/`.
2. The application provides exactly these categories:
   - General medical appointment;
   - Dental appointment;
   - Specialist consultation;
   - Laboratory test;
   - Vaccination;
   - Preventive examination;
   - Follow-up;
   - Other.
3. The user may assign at most one category to an examination.
4. Category assignment is optional.
5. A missing category is represented by `null` in application data and displayed as **Uncategorized**.
6. The user cannot create, update, or delete category definitions.

## 7. Save a Draft Examination

**Requirement references:** FR-010, FR-013, FR-017–FR-019, UX-005

### Preconditions

- the user is authenticated.

### Main flow

1. The user selects **Add examination**.
2. The application displays the examination form.
3. The user enters a title and any available optional information.
4. The user selects **Save draft**.
5. The frontend sends `POST /api/v1/examinations/` with `status` set to `draft`.
6. The backend authenticates the request and assigns the authenticated user as owner.
7. The backend requires the title and validates every optional value that was supplied.
8. The backend preserves the valid optional information and stores the record.
9. The API returns a successful creation response.
10. The draft appears in the examination list.
11. The draft is excluded from upcoming, overdue, and calendar results, including when it contains a scheduled date.

### Failure behavior

- a missing title displays a field-level error;
- an invalid optional value displays the corresponding validation error;
- reminder configuration for the draft is rejected;
- recurrence configuration for the draft is rejected;
- expired authentication follows the session-expiration flow.

## 8. Create a Planned Examination

**Requirement references:** FR-011, FR-013–FR-015, UX-006

### Preconditions

- the user is authenticated.

### Main flow

1. The user opens a new examination form.
2. The user enters a title and a scheduled date.
3. The user sets the status to `planned`.
4. The user may leave the category and scheduled time empty.
5. The user may enter optional medical specialty, location, and general notes.
6. The frontend sends `POST /api/v1/examinations/`.
7. The backend assigns the authenticated user as owner and validates the complete record.
8. The backend stores `scheduled_date` as a date and stores `scheduled_time`, when provided, as a separate optional time value.
9. The record appears in the examination list and on its scheduled date in the monthly calendar.
10. When the record has no category, the interface displays **Uncategorized**.
11. The record appears in either upcoming or overdue results according to the user's current local date and time.
12. Dashboard sections and counts reflect the new record.

### Failure behavior

- a missing title is rejected;
- a missing scheduled date is rejected;
- an unsupported status is rejected;
- a supplied category that does not exist is rejected;
- category and scheduled time are not required.

## 9. Change a Draft to Planned

**Requirement reference:** FR-016

### Preconditions

- the user owns a draft examination.

1. The user opens the draft.
2. The user provides a scheduled date.
3. The user changes the status to `planned`.
4. Category and scheduled time remain optional.
5. The frontend sends `PATCH /api/v1/examinations/{id}/`.
6. The backend validates the complete resulting record.
7. The backend saves the status change when the resulting record contains a title and scheduled date.
8. Any retained reminder remains inactive until the user explicitly reactivates it.
9. Any retained recurrence rule becomes eligible for update and next-occurrence creation.
10. The record is then included in applicable calendar, upcoming, overdue, and dashboard results.

### Failure behavior

- the transition is rejected when the resulting record has no scheduled date;
- ownership and authentication failures follow the common protected-resource behavior.

## 10. View the Examination List

**Requirement references:** FR-020, FR-027–FR-030

### Main flow

1. The user opens the examination list.
2. The frontend requests `GET /api/v1/examinations/`.
3. The backend returns only records owned by the authenticated user.
4. The frontend displays exactly one applicable page state:
   - loading while the request is pending;
   - empty when the request succeeds with no records;
   - populated when records are returned;
   - error when the request fails.
5. Each record displays its stored lifecycle status.
6. A null category is displayed as **Uncategorized**.
7. Planned records display their derived upcoming or overdue state where applicable.

### Search, filter, and ordering flows

- title search: `GET /api/v1/examinations/?search=<text>` performs a case-insensitive containment search on the user's examination titles;
- status filter: `GET /api/v1/examinations/?status=<status>`;
- category filter: `GET /api/v1/examinations/?category=<category-id>`;
- combined status and category filters use AND semantics;
- ascending scheduled-date ordering: `GET /api/v1/examinations/?ordering=scheduled_date`;
- descending scheduled-date ordering: `GET /api/v1/examinations/?ordering=-scheduled_date`;
- records without a scheduled date are placed after dated records in both ordering directions;
- ordering ties use a stable secondary ordering by identifier.

Invalid filter or ordering values are rejected with a validation error.

## 11. View Past, Upcoming, and Overdue Examinations

**Requirement references:** FR-031–FR-034

### Past flow

1. The user selects the past-examinations view.
2. The frontend requests `GET /api/v1/examinations/?time_state=past`.
3. The backend uses the authenticated user's current local date.
4. The response includes:
   - completed records whose `completed_date` is on or before the current local date;
   - cancelled or missed records whose `scheduled_date` is on or before the current local date.
5. Planned, draft, and future records are excluded.

### Upcoming flow

1. The user selects the upcoming-examinations view.
2. The frontend requests `GET /api/v1/examinations/?time_state=upcoming`.
3. The response includes only planned records that are not overdue:
   - records with a future scheduled date;
   - records on the current local date without a scheduled time;
   - records on the current local date with a scheduled time that has not passed.
4. Draft, completed, cancelled, missed, and overdue records are excluded.

### Overdue flow

1. The user selects the overdue-examinations view.
2. The frontend requests `GET /api/v1/examinations/?time_state=overdue`.
3. The response includes only planned records for which:
   - `scheduled_date` is before the user's current local date; or
   - `scheduled_date` is the current local date, `scheduled_time` is present, and that time has passed.
4. A current-date planned record without a scheduled time is not overdue.
5. Draft, completed, cancelled, and missed records are excluded.

### Derived-state refresh behavior

1. The database retains the lifecycle status, scheduled date, and optional scheduled time.
2. The backend derives upcoming or overdue whenever the data is queried or presented.
3. The same unchanged planned record can move from upcoming to overdue as the user's local time passes its scheduled boundary.
4. No database lifecycle-status update is performed merely because time passes.
5. Rescheduling immediately changes the derived result on the next evaluation.
6. The user explicitly selects `completed`, `cancelled`, or `missed`; time passing does not select a lifecycle outcome.

## 12. View Examination Details

**Requirement reference:** FR-021

1. The user opens an examination from an applicable view.
2. The frontend requests `GET /api/v1/examinations/{id}/`.
3. The backend searches only within the authenticated user's examinations.
4. The API returns the approved stored fields and approved derived fields for an owned record.
5. The application displays the examination details.

## 13. Edit an Examination

**Requirement references:** FR-013–FR-016, FR-022

1. The user opens an examination they own.
2. The user changes one or more fields.
3. The frontend sends `PATCH /api/v1/examinations/{id}/`.
4. The backend restricts the writable queryset to the authenticated user.
5. The backend validates the complete resulting record, not only the submitted fields.
6. The backend applies the status-dependent title and date rules, including rejection of a future `completed_date` for a completed record.
7. The backend saves the changes.
8. The frontend refreshes the affected examination list, calendar, reminder, recurrence, and dashboard data.

## 14. Change a Planned Examination to a Non-Planned Status

**Requirement references:** FR-012–FR-014, FR-022, FR-031, FR-034, FR-038–FR-041

### Return a planned examination to draft

1. The user opens a planned examination they own.
2. The user changes its status to `draft`.
3. The frontend sends `PATCH /api/v1/examinations/{id}/`.
4. The backend validates the complete resulting draft.
5. Within the same database transaction, the backend saves the status change and deactivates the associated reminder when one exists.
6. Any recurrence rule remains attached and unchanged.
7. While the examination remains draft, the reminder cannot be reactivated, the recurrence rule cannot be modified, and next-occurrence creation is rejected.
8. The examination is excluded from upcoming, overdue, and calendar results.

### Complete an examination

1. The user opens an examination they own.
2. The user sets the status to `completed`.
3. The user provides a `completed_date` not later than their current local date.
4. The frontend submits the update through `PATCH /api/v1/examinations/{id}/`.
5. The backend validates the complete resulting record and rejects a future `completed_date` with a field-level validation error.
6. The backend saves the valid record.
7. Within the same database transaction, the backend deactivates the associated reminder when one exists.
8. Any recurrence rule remains attached and unchanged, and may be used to create the next occurrence.
9. The examination is removed from upcoming and overdue results and appears in the past collection.
10. The monthly calendar places it on its completion date.
11. It appears in `recently_completed` when its completion date is within the inclusive 30-date dashboard window and it is among the first five records after dashboard ordering.

### Cancel or mark an examination as missed

1. The user opens an examination they own.
2. The user sets the status to `cancelled` or `missed`.
3. The resulting record must contain a scheduled date.
4. The frontend sends `PATCH /api/v1/examinations/{id}/`.
5. The backend validates and saves the record.
6. Within the same database transaction, the backend deactivates the associated reminder when one exists.
7. Any recurrence rule remains attached and unchanged, and may be used to create the next occurrence.
8. The examination is excluded from overdue results.
9. It appears in the past collection when its scheduled date is not later than the user's current local date.
10. The monthly calendar retains it on its scheduled date with the corresponding status indicator.

## 15. Delete an Examination

**Requirement references:** FR-023, FR-024

1. The user selects delete for an examination they own.
2. The frontend opens a modal confirmation dialog.
3. When the user cancels, the dialog closes and no delete request is sent.
4. When the user confirms, the frontend sends `DELETE /api/v1/examinations/{id}/`.
5. The backend searches within the authenticated user's examinations.
6. The examination is permanently deleted.
7. The associated reminder and recurrence rule are deleted through cascading deletion.
8. The deleted examination and dependent records can no longer be retrieved.
9. The frontend removes the examination from every applicable view and refreshes affected dashboard data.

## 16. Configure an In-Application Reminder

**Requirement references:** FR-017, FR-035, FR-036

### Preconditions

- the user is authenticated;
- the user owns the examination;
- the examination status is `planned`.

### Enable or update flow

1. The user opens reminder settings for the planned examination.
2. The user enters a positive whole-number offset in days before the scheduled date.
3. When no reminder exists, the frontend sends `POST /api/v1/examinations/{id}/reminder/` with `offset_days`.
4. When a reminder already exists, the frontend sends `PATCH /api/v1/examinations/{id}/reminder/` with the updated `offset_days` and, when needed, `is_active` set to `true`.
5. The backend verifies examination ownership and planned status.
6. The backend enforces at most one reminder for the examination.
7. The backend calculates `due_date` as `scheduled_date - offset_days` using calendar-date arithmetic.
8. The backend stores or updates the reminder as active.
9. When the examination scheduled date or reminder offset changes, the backend recalculates the due date.

### Disable flow

1. The user disables the reminder.
2. The frontend sends `PATCH /api/v1/examinations/{id}/reminder/` with `is_active` set to `false`.
3. The backend sets the reminder to inactive.
4. The inactive reminder no longer appears in due-reminder results.

### Failure behavior

- zero, negative, decimal, and non-numeric offsets are rejected;
- reminder creation or update for a draft or another non-planned examination is rejected;
- an examination owned by another user cannot be used to create or modify a reminder.

## 17. View Due Reminders

**Requirement reference:** FR-037

1. The user opens the due-reminders area.
2. The frontend requests `GET /api/v1/reminders/?state=due`.
3. The backend uses the user's current local date.
4. The response includes reminders for which `is_active` is true and `due_date` is on or before the current local date.
5. Future and inactive reminders are excluded.
6. The frontend displays only the due active reminders.

## 18. Configure Recurrence

**Requirement references:** FR-018, FR-039, FR-040

### Preconditions

- the user is authenticated;
- the user owns the examination;
- the examination status is `planned`.

1. The user opens recurrence settings for the planned examination.
2. The user selects `monthly`, `six_months`, or `yearly`.
3. When no recurrence rule exists, the frontend sends `POST /api/v1/examinations/{id}/recurrence/` with the selected `interval`.
4. When a recurrence rule already exists, the frontend sends `PATCH /api/v1/examinations/{id}/recurrence/` with the updated `interval`.
5. The backend verifies examination ownership and planned status.
6. The backend enforces at most one recurrence rule for the examination.
7. The backend stores the supported interval.
8. The backend calculates the next due date from the source examination's scheduled date:
   - one calendar month for `monthly`;
   - six calendar months for `six_months`;
   - one calendar year for `yearly`.
9. When the target month does not contain the source day, the calculation uses the target month's last valid day.
10. A February 29 yearly recurrence resolves to the last valid February day in a non-leap year.

### Failure behavior

- unsupported recurrence intervals are rejected;
- recurrence configuration for a draft or another non-planned examination is rejected;
- an existing recurrence rule remains retrievable but cannot be modified while its examination is non-planned;
- an examination owned by another user cannot be used to create or modify a recurrence rule.

## 19. Create the Next Recurring Occurrence

**Requirement reference:** FR-041

### Preconditions

- the source examination status is `planned`, `completed`, `cancelled`, or `missed`;
- the examination has a recurrence rule;
- the examination contains `scheduled_date`;
- the next due date can be calculated.

1. The user requests creation of the next occurrence.
2. The frontend sends `POST /api/v1/examinations/{id}/next-occurrence/`.
3. The backend verifies ownership and loads the source examination and recurrence rule.
4. The backend calculates the next due date using calendar arithmetic.
5. Within a database transaction, the backend creates exactly one new examination with status `planned` and the calculated scheduled date.
6. The backend copies `title`, `category`, `medical_specialty`, `scheduled_time`, and `location` from the source examination and leaves `notes` and `completed_date` empty.
7. The backend records the source occurrence relationship.
8. The generated occurrence has no reminder and no recurrence rule. The user may configure either one explicitly because the generated occurrence is planned.
9. The new examination appears in applicable list, calendar, upcoming or overdue, and dashboard results.
10. Repeating the same request does not create another occurrence for the same source occurrence and due date; the application receives the existing occurrence instead.

### Failure behavior

- a draft source examination is rejected with a business-rule error;
- a source examination without `scheduled_date` or without a recurrence rule is rejected;
- an examination owned by another user follows the common not-found behavior.

## 20. View the Monthly Calendar

**Requirement references:** FR-019, FR-042, FR-043

1. The user opens the monthly calendar and selects a month.
2. The frontend requests `GET /api/v1/calendar/?start_date={date}&end_date={date}` for the selected month's inclusive date range.
3. The backend returns owned records applicable to the requested date range.
4. The calendar places:
   - planned, cancelled, and missed examinations on `scheduled_date`;
   - completed examinations on `completed_date`.
5. Draft examinations are excluded.
6. A record lacking the date required for its calendar status is excluded.
7. Planned, completed, cancelled, missed, and derived overdue states use distinct labels and state indicators.
8. Color is not the sole method used to distinguish calendar states.

## 21. View the Dashboard

**Requirement references:** FR-044–FR-047

1. The authenticated user opens the dashboard.
2. The frontend requests `GET /api/v1/dashboard/`.
3. The backend returns only data derived from the authenticated user's records.
4. The response contains separate `upcoming`, `overdue`, and `recently_completed` collections.
5. For `recently_completed`, the backend selects completed examinations whose `completed_date` is between the user's current local date minus 29 days and the current local date, inclusive.
6. The backend orders eligible records by `completed_date` descending and then by `id` descending.
7. The backend returns the first five ordered records without pagination.
8. The frontend renders a separate section for each collection, including an empty presentation when that collection has no records.
9. The response contains `status_counts` with explicit keys for `draft`, `planned`, `completed`, `cancelled`, and `missed`.
10. A status with no matching records is returned with a zero count rather than being omitted.
11. The response contains `category_counts` with one count for every system-defined category and a separate `uncategorized_count` for records whose category is `null`.
12. A category with no matching records is returned with a zero count.
13. The response contains `overdue_count`, calculated with the same shared overdue logic used by the examination list.

## 22. Protected-Resource and Ownership Failure

**Requirement references:** SEC-001, SEC-002, SEC-006

### Unauthenticated request

1. A client requests examination, reminder, recurrence, calendar, or dashboard data without valid authentication.
2. The backend rejects the request.
3. The frontend either presents the authentication error or follows the session-expiration flow when an existing session cannot be refreshed.

### Missing or another user's examination

1. User B requests an examination identifier that does not exist or belongs to User A.
2. The backend searches only within User B's owner-scoped queryset.
3. The lookup fails without revealing whether the record exists for another account.
4. The API returns the same `404 Not Found` status and response structure for both cases.

### Related-object ownership

1. A user attempts to attach or modify a reminder or recurrence rule for another user's examination.
2. The backend rejects the operation because the related examination does not belong to the authenticated user.
3. No data from the other account is disclosed.

## 23. View the Non-Clinical Purpose Statement

**Requirement reference:** PRV-003

1. A visitor or authenticated user opens the designated informational page.
2. The page states that the application is an organizational tool.
3. The page states that the application does not provide medical advice, diagnosis, treatment, or emergency assistance.
4. The page remains reachable from both unauthenticated and authenticated navigation.

## 24. Shared User-Experience Behavior

**Requirement references:** UX-001, UX-008

- registration, login, examination list, examination form, calendar, and dashboard flows remain usable at the approved phone, tablet, and desktop viewport widths;
- primary navigation, forms, dialogs, and examination actions are operable using touch, mouse, and keyboard input;
- primary actions use semantic controls, visible keyboard focus, correctly labelled fields, and focus-managed modal dialogs;
- no primary action depends exclusively on hover, pointer gestures, or color.