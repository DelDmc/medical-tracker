# Medical Tracker Application — Product Definition

## 1. Product Overview

The Medical Tracker Application is a portfolio pet project for organizing personal medical appointments and examination history.

Keeping track of medical checkups helps people stay informed about their health and plan future appointments. The application provides one place to record completed examinations, schedule future examinations, configure basic reminders, and review examination history.

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

- create an account;
- log in and log out;
- continue a session through token refresh;
- receive a clear response when a session has expired;
- access only records associated with their own account.

### 5.2 Examination Records

Users can:

- create an examination record;
- view a list of examination records;
- view examination details;
- edit and delete their records;
- assign a category;
- add a title, medical specialty, scheduled date and time, completion date, location, and general notes;
- assign a status of `planned`, `completed`, `cancelled`, or `missed`;
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

### 5.3 Planning and Recurrence

Users can:

- schedule an examination for a future date and time;
- view past, upcoming, and overdue examinations;
- define a basic recurrence interval;
- use recurrence intervals of monthly, every six months, or yearly;
- view the next due date;
- create the next occurrence when needed.

The application will not generate an unlimited number of future records.

### 5.4 In-Application Reminders

Users can:

- enable or disable a reminder for a planned examination;
- select how long before an examination the reminder becomes due;
- view reminders that are currently due.

The MVP displays reminders inside the application. It does not send email, SMS, browser, or mobile push notifications.

### 5.5 Calendar

Users can:

- view examinations in a monthly calendar;
- distinguish planned, completed, cancelled, missed, and overdue examinations;
- open an examination from the calendar;
- start creating an examination from a selected date.

### 5.6 Dashboard

Users can view:

- upcoming examinations;
- overdue examinations;
- recently completed examinations;
- examination counts by category;
- completed and planned examination totals.

Charts will be included only when they communicate useful information.

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
2. The user creates an account.
3. The application validates the submitted data.
4. The user logs in.
5. The application opens the authenticated dashboard.

### 8.2 Create a Planned Examination

1. The user selects **Add examination**.
2. The user enters the examination information.
3. The user keeps the status as `planned`.
4. The user optionally configures recurrence and a reminder.
5. The application validates and saves the record.
6. The record appears in the examination list, calendar, and dashboard.

### 8.3 Complete an Examination

1. The user opens a planned examination.
2. The user changes its status to `completed`.
3. The user enters or confirms the completion date.
4. The application saves the updated record.
5. The record appears in examination history.
6. When recurrence is enabled, the application calculates the next due date.

### 8.4 Review Upcoming and Overdue Examinations

1. The user opens the dashboard or examination list.
2. The application shows upcoming examinations ordered by date.
3. Planned examinations with past scheduled dates are shown as overdue.
4. The user opens an examination and updates its status or scheduled date.

### 8.5 Edit or Delete an Examination

1. The user opens one of their examination records.
2. The user edits the record or selects delete.
3. The application validates the request and record ownership.
4. The application saves the changes or removes the record.
5. The updated state appears in all relevant views.

## 9. Initial Business Rules

### 9.1 Ownership

- Every examination record belongs to one user.
- Users can view, update, and delete only their own records.
- Ownership is enforced by the backend.

### 9.2 Examination Status

- Supported statuses are `planned`, `completed`, `cancelled`, and `missed`.
- A future examination is created with the `planned` status by default.
- A completed examination has a completion date.
- Status changes are explicit user actions.

### 9.3 Upcoming and Overdue State

- A planned examination is upcoming when its scheduled date and time is in the future.
- A planned examination is overdue when its scheduled date and time is in the past.
- `overdue` is calculated and is not stored as an examination status.
- Completed, cancelled, and missed examinations are not overdue.

### 9.4 Categories

- The MVP uses a fixed set of system-defined categories.
- Every examination has one category.
- The `Other` category covers examinations outside the predefined categories.

### 9.5 Notes and Medical Data

- Notes are optional and intended for general organizational information.
- The application does not require diagnoses, prescriptions, identification numbers, or detailed clinical information.
- The application does not interpret notes or provide medical recommendations.

### 9.6 Reminders

- A reminder is associated with a planned examination that has a scheduled date and time.
- A reminder is defined as a relative period before the examination.
- A reminder becomes inactive when the examination is completed, cancelled, or missed.

### 9.7 Recurrence

- Recurrence is optional.
- The MVP supports monthly, every-six-months, and yearly intervals.
- The application stores the recurrence rule and next due date.
- Future occurrences are created one at a time when needed.

### 9.8 Deletion

- Users can delete only their own records.
- Deleting an examination also removes its associated reminder and recurrence configuration.
- The application requests confirmation before deletion.
- The MVP uses permanent deletion.

## 10. Definition of Done

The MVP is complete when:

- users can register, log in, refresh a session, and log out;
- authenticated users can create, view, edit, and delete examination records;
- users can manage examination statuses;
- users can view past, upcoming, and overdue examinations;
- users can configure basic recurrence and in-application reminders;
- users can view examinations in a monthly calendar;
- users can review upcoming, overdue, and recent activity on a dashboard;
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
- user-defined categories;
- data export;
- multi-language support;
- account deletion and data-retention controls;
- audit history;
- continuous integration and end-to-end browser testing.