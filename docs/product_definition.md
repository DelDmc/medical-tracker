# Medical Tracker Application — Product Definition

## 1. Product Overview

The Medical Tracker Application is a portfolio pet project for organizing personal medical appointments and examination history.

The application provides one place to record completed examinations, prepare draft records, plan future examinations, configure basic reminders, and review examination history.

The application is an organizational tool only. It does not provide medical advice, diagnoses, treatment recommendations, or emergency assistance.

## 2. Source-of-Truth Hierarchy

Detailed system behavior is defined in `requirements-specification.md`.

When documents differ, they have the following precedence:

1. `requirements-specification.md` — authoritative product and system requirements;
2. `product_definition.md` — product-level summary;
3. `docs/application-design-specification.md` — accepted implementation design decisions;
4. `docs/domain-model.md`, `docs/api-contract.md`, and `docs/user-flows.md` — detailed design artifacts;
5. `docs/application-test-specification.md` — verification design linked to requirements.

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

A native mobile application may be considered after the web MVP is complete. The backend API should remain independent from the web interface so that it can support another client later.

## 6. MVP Features

### 6.1 Account Access

Users can:

- create an account;
- log in and log out;
- continue a session through token refresh;
- receive a clear response when a session has expired;
- view and update their account timezone;
- access only records associated with their own account.

### 6.2 Examination Records

Users can:

- create an examination record;
- save an examination as a draft using a title and any available optional information;
- save a planned examination without assigning a category or scheduled date and time;
- view a list of examination records;
- view examination details;
- edit and delete their records;
- optionally assign a system-defined category;
- add a title, medical specialty, scheduled date and time, completion date, location, and general notes;
- assign a status of `draft`, `planned`, `completed`, `cancelled`, or `missed`;
- search, filter, and sort records.

Initial categories are:

- Dentist;
- General practitioner;
- Specialist;
- Laboratory test;
- Vaccination;
- Preventive examination;
- Follow-up;
- Other.

Records without a category are displayed as **Uncategorized** where category grouping or counting is used.

### 6.3 Planning and Recurrence

Users can:

- create a planned examination before its exact date, time, or category is known;
- schedule an examination for a future date and time;
- view upcoming and overdue examinations;
- define a basic recurrence interval;
- use recurrence intervals of monthly, every six months, or yearly;
- view the next due date;
- create the next occurrence when needed.

The application will not generate an unlimited number of future records.

### 6.4 In-Application Reminders

Users can:

- enable or disable a reminder for a planned examination that has a scheduled date and time;
- select from the reminder timing options defined by the application design;
- view reminders that are currently due.

The MVP displays reminders inside the application. It does not send email, SMS, browser, or mobile push notifications.

The exact predefined reminder offsets are an application design decision, not a product requirement.

### 6.5 Calendar

Users can:

- view examinations in a monthly calendar;
- distinguish draft, planned, completed, cancelled, missed, and overdue records where applicable;
- open an examination from the calendar;
- start creating an examination from a selected date.

Draft and unscheduled planned examinations do not appear on a dated calendar position until they have a scheduled date and time.

### 6.6 Dashboard

Users can view:

- upcoming examinations;
- overdue examinations;
- recently completed examinations;
- examination counts by category;
- an uncategorized examination count;
- total planned examinations;
- total completed examinations.

Charts will be included only when they communicate useful information.

## 7. Requirements

Detailed system requirements and verification methods are defined in [requirements-specification.md](requirements-specification.md).

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

1. The user opens the application.
2. The user creates an account.
3. The application validates the submitted data.
4. The user logs in.
5. The application opens the authenticated dashboard.

### 9.2 Update Account Timezone

1. The authenticated user opens account settings.
2. The application displays the currently selected timezone.
3. The user selects another supported timezone.
4. The application validates and saves the change.
5. Dates and times are subsequently presented using the updated timezone.

### 9.3 Save a Draft Examination

1. The user selects **Add examination**.
2. The user enters a title and any available optional information.
3. The user saves the record with status `draft`.
4. The application validates and saves the record.
5. The draft appears in the examination list.
6. The user can return later to complete the information or change its status.

### 9.4 Create a Planned Examination

1. The user selects **Add examination** or opens an existing draft.
2. The user enters the available examination information.
3. The user selects status `planned`.
4. Category and scheduled date and time remain optional.
5. Recurrence and reminders can be configured only when their own required information is available.
6. The application validates and saves the record.
7. The record appears in all applicable views.

### 9.5 Complete an Examination

1. The user opens a planned examination or creates a completed historical record.
2. The user changes its status to `completed`.
3. The user enters or confirms the completion date.
4. The application saves the updated record.
5. The record appears in examination history.
6. When recurrence is enabled, the application calculates the next due date according to the accepted recurrence design.

### 9.6 Review Upcoming and Overdue Examinations

1. The user opens the dashboard or examination list.
2. The application shows planned examinations with future scheduled dates as upcoming.
3. The application shows planned examinations with past scheduled dates as overdue.
4. Planned examinations without a scheduled date are neither upcoming nor overdue.
5. The user opens an examination and updates its status or scheduled date.

### 9.7 Edit or Delete an Examination

1. The user opens one of their examination records.
2. The user edits the record or selects delete.
3. The application validates the request and record ownership.
4. The application saves the changes or removes the record.
5. The updated state appears in all relevant views.

## 10. Initial Business Rules

### 10.1 Ownership

- Every examination record belongs to one user.
- Users can view, update, and delete only their own records.
- Ownership is enforced by the backend.

### 10.2 Account Timezone

- Every user account has one supported timezone.
- The timezone is required during registration.
- An authenticated user can update their own timezone.
- The timezone is used to present and interpret examination dates and times.
- Changing the timezone does not alter the stored instant represented by an existing timezone-aware datetime.

### 10.3 Examination Status

- Supported statuses are `draft`, `planned`, `completed`, `cancelled`, and `missed`.
- `draft` represents an incomplete record that the user intends to finish later.
- A draft requires a title and may contain any available optional information.
- A planned examination may be saved without a category or scheduled date and time.
- A completed examination has a completion date.
- Status changes are explicit user actions.

### 10.4 Upcoming and Overdue Time State

- A planned examination is upcoming when it has a scheduled date and time in the future.
- A planned examination is overdue when it has a scheduled date and time in the past.
- `overdue` is calculated from the current time and is not stored as an examination status.
- A planned examination without a scheduled date and time is neither upcoming nor overdue.
- Draft, completed, cancelled, and missed examinations are not overdue.

### 10.5 Categories

- The MVP uses a fixed set of system-defined categories.
- Category assignment is optional for draft and planned examinations.
- Records without a category are treated as uncategorized in the interface and dashboard counts.
- The `Other` category can be selected for examinations outside the predefined categories.

### 10.6 Notes and Medical Data

- Notes are optional and intended for general organizational information.
- The application does not require diagnoses, prescriptions, identification numbers, or detailed clinical information.
- The application does not interpret notes or provide medical recommendations.

### 10.7 Reminders

- A reminder is associated with a planned examination that has a scheduled date and time.
- A reminder is defined as a relative period before the examination.
- A reminder becomes inactive when the examination is completed, cancelled, or missed.
- Available reminder offsets are defined in the application design specification.

### 10.8 Recurrence

- Recurrence is optional.
- The MVP supports monthly, every-six-months, and yearly intervals.
- The application stores the recurrence rule and next due date.
- Future occurrences are created one at a time when needed.

### 10.9 Deletion

- Users can delete only their own records.
- Deleting an examination also removes its associated reminder and recurrence configuration.
- The application requests confirmation before deletion.
- The MVP uses permanent deletion.

## 11. Definition of Done

The MVP is complete when:

- users can register, log in, refresh a session, and log out;
- authenticated users can view and update their account timezone;
- authenticated users can create, view, edit, and delete examination records;
- users can save draft and planned records with the optionality defined by the requirements;
- users can manage examination statuses;
- users can view past, upcoming, and overdue examinations;
- users can configure basic recurrence and in-application reminders;
- users can view scheduled examinations in a monthly calendar;
- users can review upcoming, overdue, recent, category, uncategorized, planned-total, and completed-total information on a dashboard;
- users cannot access records owned by another account;
- the main user flows work on mobile and desktop screen sizes;
- critical backend and frontend behavior is covered by automated tests linked to requirements;
- the frontend and backend are deployed and their main integration flow is verified;
- local setup, testing, and deployment instructions are documented;
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