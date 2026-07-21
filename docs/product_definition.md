# Medical Tracker Application — Product Definition

## 1. Product Overview

The Medical Tracker Application is a portfolio pet project for organizing personal medical appointments and examination history.

Keeping track of medical checkups helps people stay informed about their health and plan future appointments. The application provides one place to record completed examinations, plan future examinations, save incomplete information for later, configure basic reminders, and review examination history.

The application is an organizational tool only. It does not provide medical advice, diagnoses, treatment recommendations, or emergency assistance.

## 2. Target User

The primary user is an adult who manages their own health-related appointments and wants a simple way to organize past and future examinations.

The application is designed for users who:

- want one place to track medical appointments and examination history;
- want reminders for upcoming or recurring examinations;
- prefer a clear and simple interface;
- do not have medical or technical expertise.

The application does not require users to understand medical terminology or healthcare systems.

## 3. Product Goals

The application is intended to:

- help users maintain a clear history of previous examinations;
- help users quickly save incomplete examination information and complete it later;
- help users plan upcoming examinations and appointments;
- make upcoming and overdue examinations easy to identify;
- support a consistent preventive-care routine through basic recurrence and reminders;
- demonstrate frontend, backend, database, testing, and deployment skills in a complete portfolio project.

## 4. Product Approach

The MVP will be delivered as a mobile-first responsive web application that works on phones, tablets, and desktop devices.

A native mobile application may be considered after the web MVP is complete. The backend API should remain independent from the web interface so that it can support another client later.

## 5. MVP Features

### 5.1 Account Access

Users can:

- create an account using an email address, password, and timezone;
- log in and log out;
- continue a session through token refresh;
- receive a clear response when a session has expired;
- update their account timezone;
- access only records associated with their own account.

### 5.2 Examination Records

Users can:

- create a draft examination by entering a title and any available optional information;
- create a planned examination by entering a title and scheduled date;
- view a list of examination records;
- view examination details;
- edit and delete their records;
- optionally assign a category;
- optionally add a scheduled time, medical specialty, location, and general notes;
- assign a status of `draft`, `planned`, `completed`, `cancelled`, or `missed`;
- search records by title;
- filter records by status and category;
- sort records by scheduled date.

Initial system-defined categories are:

- General medical appointment;
- Dental appointment;
- Specialist consultation;
- Laboratory test;
- Vaccination;
- Preventive examination;
- Follow-up;
- Other.

A record without an assigned category is shown as **Uncategorized**. Uncategorized is a display label, not a stored category.

### 5.3 Planning and Recurrence

Users can:

- schedule an examination for a future date with an optional time;
- view past, upcoming, and overdue examinations;
- define a basic recurrence interval for a planned examination;
- use recurrence intervals of monthly, every six months, or yearly;
- view the next due date;
- create the next occurrence when needed.

Draft records cannot use recurrence. The application will not generate an unlimited number of future records.

### 5.4 In-Application Reminders

Users can:

- enable, update, or disable a reminder for a planned examination;
- select a positive whole-number offset in days before the examination;
- view reminders that are currently due.

Draft records cannot use reminders. The MVP displays reminders inside the application and does not send email, SMS, browser, or mobile push notifications.

### 5.5 Calendar

Users can:

- view dated examinations in a monthly calendar;
- distinguish planned, completed, cancelled, missed, and overdue examinations.

Draft records are not displayed in the calendar.

### 5.6 Dashboard

Users can view:

- upcoming examinations;
- overdue examinations;
- recently completed examinations;
- examination counts for every supported status;
- examination counts for every system-defined category;
- the number of Uncategorized examinations;
- the number of overdue examinations.

The dashboard status counts include draft records so users can see that unfinished records require attention. Charts will be included only when they communicate useful information.

## 6. Requirements

Detailed system requirements and verification methods are defined in [requirements-specification.md](requirements-specification.md).

## 7. Explicit Exclusions

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
- day and week calendar views;
- opening records or starting record creation directly from the calendar;
- advanced recurrence patterns;
- unlimited generation of recurring records;
- user-defined categories;
- data export;
- multi-language support;
- audit history;
- account deletion and configurable data-retention controls;
- claims of HIPAA, GDPR, or other regulatory compliance without separate implementation and verification.

## 8. Primary User Flows

### 8.1 Register and Log In

1. The user opens the application.
2. The user enters an email address, password, and timezone.
3. The application validates the submitted data and creates the account.
4. The user logs in.
5. The application opens the authenticated dashboard.

### 8.2 Save a Draft Examination

1. The user selects **Add examination**.
2. The user enters a title and any other information currently available.
3. The user saves the record as `draft`.
4. The application stores all entered information.
5. The draft appears in the examination list and is included in the dashboard draft count.
6. The draft remains excluded from upcoming, overdue, reminder, recurrence, and calendar results.

### 8.3 Create or Complete a Planned Examination

1. The user creates a new examination or opens an existing draft.
2. The user enters a title and scheduled date.
3. The user optionally enters a scheduled time, category, specialty, location, and notes.
4. The user saves the record with the `planned` status.
5. The record appears in the examination list and relevant calendar and dashboard sections.
6. The user may optionally configure recurrence and a reminder.

### 8.4 Complete an Examination

1. The user opens a planned examination.
2. The user changes its status to `completed`.
3. The user enters or confirms the completion date.
4. The application saves the updated record and deactivates its reminder.
5. The record appears in examination history and recently completed dashboard data.
6. When recurrence is enabled, the application calculates the next due date.

### 8.5 Review Upcoming, Overdue, and Draft Examinations

1. The user opens the dashboard or examination list.
2. The application shows upcoming and overdue examinations.
3. The dashboard shows the number of unfinished draft records.
4. The user opens an examination and updates its information, status, or scheduled date.

### 8.6 Edit or Delete an Examination

1. The user opens one of their examination records.
2. The user edits the record or selects delete.
3. The application validates the request and record ownership.
4. The application saves the changes or requests confirmation before deletion.
5. The updated state appears in all relevant views.

## 9. Initial Business Rules

### 9.1 Ownership

- Every examination record belongs to one user.
- Users can view, update, and delete only their own records.
- Ownership is enforced by the backend.

### 9.2 Examination Status

- Supported statuses are `draft`, `planned`, `completed`, `cancelled`, and `missed`.
- A draft is an incomplete record that the user intends to update later.
- A planned examination is an examination expected to take place on a scheduled date.
- A missed examination means the user confirmed that the examination did not take place.
- Status changes are explicit user actions.

### 9.3 Required and Optional Information

- Every examination record has a title.
- A draft may omit its category, scheduled date, and scheduled time.
- A planned examination has a scheduled date.
- A scheduled time is optional.
- A cancelled or missed examination has a scheduled date.
- A completed examination has a completion date.
- Medical specialty, location, and notes are optional.

### 9.4 Upcoming and Overdue State

- Only planned examinations can be upcoming or overdue.
- A planned examination is overdue when its scheduled date is before the current date.
- A planned examination scheduled for the current date is overdue only when it has a scheduled time and that time has passed.
- A date-only examination scheduled for the current date is not overdue.
- `overdue` is calculated and is not stored as an examination status.
- Completed, cancelled, missed, and draft examinations are not overdue.

### 9.5 Categories

- The MVP uses a fixed set of system-defined categories.
- Category assignment is optional.
- A record without a category is displayed as **Uncategorized**.
- **Uncategorized** is not stored as a category.
- The `Other` category is selected explicitly when none of the predefined categories fit.

### 9.6 Notes and Medical Data

- Notes are optional and intended for general organizational information.
- The application does not require diagnoses, prescriptions, identification numbers, or detailed clinical information.
- The application does not interpret notes or provide medical recommendations.

### 9.7 Reminders

- A reminder is associated only with a planned examination.
- A reminder uses a positive whole-number offset in days before the scheduled date.
- Draft examinations cannot have reminders.
- A reminder becomes inactive when the examination is completed, cancelled, or missed.

### 9.8 Recurrence

- Recurrence is optional and applies only to planned examinations.
- Draft examinations cannot have recurrence rules.
- The MVP supports monthly, every-six-months, and yearly intervals.
- The application stores the recurrence rule and next due date.
- Future occurrences are created one at a time when requested by the user.

### 9.9 Dates, Times, and Timezones

- Scheduled dates and optional scheduled times are stored separately.
- The user selects a supported timezone during registration and can update it later.
- Dates and times are displayed using the timezone configured for the authenticated user.
- Timestamps representing a specific instant are stored as timezone-aware values.

### 9.10 Deletion

- Users can delete only their own records.
- Deleting an examination also removes its associated reminder and recurrence configuration.
- The application requests confirmation before deletion.
- The MVP uses permanent deletion.

## 10. Definition of Done

The MVP is complete when:

- users can register with an email address, password, and timezone;
- users can log in, refresh a session, log out, and update their timezone;
- authenticated users can create title-only drafts and preserve optional information entered with them;
- authenticated users can create planned examinations using a title and scheduled date without requiring a category or scheduled time;
- authenticated users can view, edit, and delete their examination records;
- users can manage draft, planned, completed, cancelled, and missed statuses;
- users can search, filter, and sort their examination records;
- users can view past, upcoming, and overdue examinations;
- users can configure basic recurrence and in-application reminders for planned examinations;
- users can view dated examinations in a monthly calendar with distinct state indicators;
- users can review upcoming, overdue, recently completed, status, category, Uncategorized, and draft information on the dashboard;
- users cannot access records owned by another account;
- the main user flows work on mobile and desktop screen sizes;
- critical backend and frontend behavior is covered by automated tests;
- the frontend and backend are deployed and their main integration flow is verified;
- local setup, testing, and deployment instructions are documented;
- the application clearly states its privacy boundary and non-clinical purpose.

## 11. Future Features

Possible future improvements include:

- a native Android and iOS application;
- Progressive Web App support;
- browser and mobile push notifications;
- email reminders;
- external calendar synchronization;
- day and week calendar views;
- opening records and starting record creation directly from the calendar;
- user-defined categories;
- data export;
- multi-language support;
- account deletion and data-retention controls;
- audit history;
- continuous integration and end-to-end browser testing.