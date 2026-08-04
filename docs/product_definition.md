# Medical Tracker Application — Product Definition

## 1. Product Overview

The Medical Tracker Application is a portfolio pet project for organizing personal medical appointments and examination history.

The application provides one place to record completed examinations, prepare draft records, plan examinations, configure basic reminders and recurrence, and review examination history.

The application is an organizational tool only. It does not provide medical advice, diagnoses, treatment recommendations, or emergency assistance.

## 2. Source-of-Truth Hierarchy

Detailed system behavior is defined in `requirements_specification.md`.

When documents differ, they have the following precedence:

1. `requirements_specification.md` — authoritative product and system requirements;
2. `product_definition.md` — product-level summary;
3. `design_specification.md` — accepted implementation design decisions;
4. `domain_model.md`, `api_contract.md`, and `user_flows.md` — detailed design artifacts;
5. `test_specification.md` — verification design linked to requirements.

The product definition must be updated when an accepted requirement changes the product-level description.

## 3. Target User

The primary user is an adult who manages their own health-related appointments and wants a simple way to organize past and future examinations.

The application is designed for users who:

- want one place to track medical appointments and examination history;
- want reminders for upcoming or recurring examinations;
- prefer a clear and simple interface;
- do not have medical or technical expertise.

The application does not require users to understand medical terminology or healthcare systems.

## 4. Product Goals

The application is intended to:

- help users maintain a clear history of previous examinations;
- help users plan upcoming examinations and appointments;
- make upcoming and overdue examinations easy to identify;
- support a consistent preventive-care routine through basic recurrence and reminders;
- demonstrate frontend, backend, database, testing, and deployment skills in a complete portfolio project.

## 5. Product Approach

The MVP will be delivered as a mobile-first responsive web application that works on phones, tablets, and desktop devices.

A native mobile application may be considered after the web MVP is complete. The backend API remains independent from the web interface so that it can support another client later.

## 6. MVP Features

### 6.1 Account Access

Users can:

- create an account using an email address, password, and supported timezone;
- log in and log out;
- continue a session through token refresh;
- receive a clear response when a session has expired;
- view and update their account timezone;
- access only records associated with their own account.

### 6.2 Examination Records

Users can:

- create an examination record;
- save a draft using a title and any available optional information;
- save a planned examination using a title and scheduled date without requiring a category or scheduled time;
- view a list of examination records and individual examination details;
- edit and permanently delete their records;
- optionally assign one system-defined category;
- store a title, optional medical specialty, scheduled date, optional scheduled time, completion date, location, and general notes according to the selected status;
- assign a status of `draft`, `planned`, `completed`, `cancelled`, or `missed`;
- search records by title, filter by status and category, and order by scheduled date.

System-defined categories are:

- General medical appointment;
- Dental appointment;
- Specialist consultation;
- Laboratory test;
- Vaccination;
- Preventive examination;
- Follow-up;
- Other.

Records without a category are represented by a null category and displayed as **Uncategorized**.

### 6.3 Planning and Recurrence

Users can:

- create a planned examination when its scheduled date is known, while leaving its exact time and category unspecified;
- view planned examinations as upcoming or overdue according to their scheduled date, optional scheduled time, current local date and time, and account timezone;
- configure one recurrence interval of monthly, every six months, or yearly for a planned examination;
- retain the recurrence rule when the examination status changes;
- view the calculated next due date;
- create exactly one next occurrence from a planned, completed, cancelled, or missed examination when requested.

Future occurrences are created one at a time and are not generated automatically without a user request.

### 6.4 In-Application Reminders

Users can:

- enable or update one reminder for a planned examination using a positive whole-number `offset_days` value;
- disable the reminder, or re-enable it after the examination is planned;
- view active reminders whose due date has been reached.

The reminder due date is calculated as the examination's `scheduled_date` minus `offset_days`. A scheduled time is not required for reminder configuration.

The MVP displays reminders inside the application. It does not send email, SMS, browser, or mobile push notifications.

### 6.5 Calendar

Users can:

- view examinations in a monthly calendar;
- view planned, cancelled, and missed examinations on `scheduled_date`;
- view completed examinations on `completed_date`;
- distinguish planned, completed, cancelled, missed, and derived overdue states through state-specific indicators.

Draft examinations are excluded from calendar results. Color is not the sole method used to distinguish calendar states.

### 6.6 Dashboard

Users can view:

- upcoming examinations;
- overdue examinations;
- recently completed examinations;
- `status_counts` for `draft`, `planned`, `completed`, `cancelled`, and `missed`;
- `category_counts` for every system-defined category;
- `uncategorized_count` for examinations whose category is null;
- `overdue_count` calculated with the same overdue rules used elsewhere.

Counts with no matching records are returned as zero rather than omitted.

## 7. Requirements

Detailed system requirements and verification methods are defined in [requirements_specification.md](requirements_specification.md).

This document summarizes those requirements and must not introduce conflicting behavior.

## 8. Explicit Exclusions

The following features are outside the MVP:

- medical advice, diagnoses, treatment recommendations, or clinical decision support;
- emergency guidance;
- prescriptions or medication management;
- detailed medical records;
- medical document or laboratory-result uploads;
- insurance information;
- government identification data;
- email, SMS, browser, or native push notifications;
- external calendar synchronization;
- advanced recurrence patterns;
- unlimited generation of recurring records;
- user-defined categories;
- data export;
- multi-language support;
- audit history;
- account deletion and configurable data-retention controls;
- claims of HIPAA, GDPR, or other regulatory compliance without separate implementation and verification.

## 9. Primary User Flows

### 9.1 Register and Log In

1. The user creates an account using an email address, password, and supported timezone.
2. The application validates the submitted fields and creates the account.
3. The user logs in using valid credentials.
4. The application establishes the authenticated session and opens the dashboard.

### 9.2 Update Account Timezone

1. The authenticated user opens account settings.
2. The application displays the currently selected timezone.
3. The user selects another supported IANA timezone.
4. The application validates and saves the change.
5. Timezone-aware timestamps are presented in the updated timezone, while date-only values remain unchanged.
6. Time-based collections and due-reminder calculations use the updated local date and time.

### 9.3 Save a Draft Examination

1. The user selects **Add examination**.
2. The user enters a title and any available optional information.
3. The user saves the record with status `draft`.
4. The application validates and saves the record.
5. The draft appears in the examination list and remains excluded from upcoming, overdue, and calendar results.

### 9.4 Create a Planned Examination

1. The user opens a new examination form or an existing draft.
2. The user provides a title and scheduled date.
3. The user selects status `planned`.
4. Category and scheduled time remain optional.
5. The application validates and saves the complete record.
6. The record appears in the examination list, calendar, applicable upcoming or overdue collection, and dashboard data.

### 9.5 Complete an Examination

1. The user opens an examination they own.
2. The user changes its status to `completed` and provides `completed_date`.
3. The application validates and saves the complete resulting record.
4. The associated reminder is deactivated in the same transaction when one exists.
5. Any recurrence rule remains attached and may be used to create the next occurrence.
6. The record is excluded from upcoming and overdue results and appears in the past collection when its completion date is not later than the user's current local date.
7. The calendar places the record on `completed_date`.

### 9.6 Review Past, Upcoming, and Overdue Examinations

1. The user opens the relevant examination collection or dashboard section.
2. The application derives each collection using the account timezone and current local date and time.
3. Completed examinations use `completed_date` for past inclusion; cancelled and missed examinations use `scheduled_date`.
4. A planned examination is overdue when its scheduled date is before the current local date, or when it is scheduled for the current date and its specified scheduled time has passed.
5. A current-date planned examination without a scheduled time is upcoming rather than overdue.
6. Draft, completed, cancelled, and missed examinations are not overdue.

### 9.7 Edit or Delete an Examination

1. The user opens one of their examination records.
2. The application validates ownership through the authenticated-user queryset.
3. An edit validates the complete resulting record before saving it.
4. Changing a planned examination to any non-planned status deactivates its reminder and retains its recurrence rule.
5. Changing an examination to planned does not reactivate an inactive reminder.
6. A deletion requires explicit confirmation and permanently removes the examination and its associated reminder and recurrence rule.
7. The updated state appears in all relevant views.

## 10. Initial Business Rules

### 10.1 Ownership

- Every examination record belongs to one user.
- Ownership is assigned by the backend and is not writable by clients.
- Users can view, update, and delete only their own records.
- Reminder and recurrence ownership is inherited from the associated examination.
- A missing examination and another user's examination return the same not-found response.

### 10.2 Account Timezone

- Every user account has one supported IANA timezone.
- The timezone is required during registration and may be updated by the authenticated user.
- The timezone determines the current local date and time used for upcoming, overdue, past, and due-reminder calculations.
- Timezone-aware timestamps are converted to the account timezone for presentation.
- Date-only values are displayed as stored and are not shifted through UTC conversion.
- Changing the timezone does not alter the stored instant represented by an existing timezone-aware datetime.

### 10.3 Examination Status and Required Fields

- Supported statuses are `draft`, `planned`, `completed`, `cancelled`, and `missed`.
- Every examination requires a title.
- A draft may contain only a title or any valid optional examination information.
- A planned, cancelled, or missed examination requires `scheduled_date`.
- A completed examination requires `completed_date`.
- Category and scheduled time remain optional for a planned examination.
- Every create or update validates the complete resulting record.
- Status changes are explicit user actions.

### 10.4 Upcoming and Overdue Time State

- Only a planned examination can be upcoming or overdue.
- A planned examination is overdue when `scheduled_date` is before the user's current local date.
- A planned examination scheduled for the current local date is overdue only when `scheduled_time` is present and has passed.
- A current-date planned examination without `scheduled_time` is upcoming.
- `overdue` is derived when data is queried or presented and is not stored as an examination status.
- Draft, completed, cancelled, and missed examinations are not overdue.

### 10.5 Categories

- The MVP uses the fixed set of system-defined categories listed in Section 6.2.
- An examination may have zero or one category.
- Category assignment is optional.
- Category absence is represented by null and displayed as **Uncategorized**.
- `Uncategorized` is not a stored category resource.

### 10.6 Notes and Medical Data

- Medical specialty, location, and notes are optional organizational metadata.
- The application does not require diagnoses, prescriptions, identification numbers, medical files, insurance information, or detailed clinical information.
- The application does not interpret notes or provide medical recommendations.

### 10.7 Reminders

- An examination may have zero or one reminder.
- A reminder record may remain attached regardless of examination status.
- A reminder may be active only for a planned examination.
- Reminder creation, offset updates, and reactivation are allowed only for a planned examination.
- `offset_days` must be a positive whole number.
- `due_date` is calculated as `scheduled_date - offset_days`, recalculated when either value changes, and set to null when `scheduled_date` is absent.
- Changing a planned examination to draft, completed, cancelled, or missed deactivates its reminder.
- Changing an examination to planned does not reactivate its reminder automatically.

### 10.8 Recurrence

- An examination may have zero or one recurrence rule.
- A recurrence rule remains attached when the examination status changes.
- Recurrence creation and update are allowed only for a planned examination.
- Supported intervals are `monthly`, `six_months`, and `yearly`.
- The next due date is derived from the source examination's `scheduled_date` using calendar-month arithmetic and is unavailable when `scheduled_date` is absent.
- When the target month lacks the source day, the target month's last valid day is used.
- Future occurrences are created exactly one at a time after an explicit user request.
- Next-occurrence creation is allowed from planned, completed, cancelled, and missed examinations and rejected for drafts.
- A repeated request does not create another occurrence for the same source occurrence and due date.

### 10.9 Deletion

- Users can delete only examinations they own.
- The user interface requests explicit confirmation before deletion.
- Deletion is permanent in the MVP.
- Deleting an examination also deletes its associated reminder and recurrence rule through cascading deletion.

## 11. Definition of Done

The MVP is complete when:

- users can register, log in, refresh a session, and log out;
- authenticated users can view and update their account timezone;
- authenticated users can create, view, edit, and permanently delete examination records;
- users can save drafts and planned records with the required and optional fields defined by the requirements;
- users can manage the five supported examination statuses;
- users can search, filter, and order their examination records;
- users can view past, upcoming, and overdue examination collections;
- users can configure one in-application reminder and one recurrence rule for a planned examination;
- users can create one next recurring occurrence when requested;
- users can view applicable examinations in a monthly calendar;
- users can review upcoming, overdue, recently completed, status-count, category-count, `uncategorized_count`, and `overdue_count` dashboard information;
- users cannot access examinations, reminders, or recurrence rules owned by another account;
- the main user flows work on phone, tablet, and desktop screen sizes and with touch, mouse, and keyboard input;
- critical backend and frontend behavior is covered by automated tests linked to requirements;
- the frontend and backend are deployed and their main integration flow is verified;
- local setup, testing, database migration, build, and deployment instructions are documented;
- the application clearly states its privacy boundary and non-clinical purpose.

## 12. Future Features

Possible future improvements include:

- a native Android and iOS application;
- Progressive Web App support;
- browser and mobile push notifications;
- email reminders;
- external calendar synchronization;
- user-defined categories;
- data export;
- multi-language support;
- account deletion and data-retention controls;
- audit history;
- continuous integration and end-to-end browser testing.