# TC-UX-008-02 — Input-Method Review, Mouse

**Standing:** This is a non-normative verification record. It is evidence that the test case named below (`docs/test_specification.md`) was executed; it is not part of the source-of-truth hierarchy in `product_definition.md` §2, defines no behavior, and must never be cited as authority. When it disagrees with an authoritative document, that document wins and the review is repeated.

| | |
|---|---|
| **Test case** | `TC-UX-008-02` — Primary flows are completable using mouse input |
| **Requirement** | `UX-008` (decision `ADS-UX-008-01`) |
| **Layer** | Documented review |
| **Date** | 2026-09-25 |
| **Viewport** | 1280 CSS pixels (desktop width) |
| **Build reviewed** | `feature/s17-ux-review` (Slice 17), frontend dev server against the local backend |
| **Browser** | Firefox 155.0.1, headless, driven through geckodriver with Selenium 4.49 |
| **Verdict** | **Pass** — 15 of 15 primary actions completed |

## 1. Method

Mouse clicks: W3C WebDriver pointer actions with pointer type `mouse` (move to the element, then click). Firefox dispatched the events as `pointerType: "mouse"` — recorded for every action below. Text was typed into the clicked field. Scrolling to off-screen controls stood in for the mouse wheel.

A fresh account was registered through the UI at the start of the run, so every action ran on real data end to end, and each action was judged complete only when its outcome appeared in the application (right-hand column). The enumerated primary actions are those of `IMPLEMENTATION_PLAN.md` Task 17.2: navigate, register, log in, log out, create a draft, create a planned examination, edit, delete (with the confirmation dialog), configure and disable a reminder, configure recurrence, create a next occurrence, change month in the calendar, change the account timezone, and change the password.

## 2. Results

| Primary action | Completed | Pointer events observed | Outcome verified |
|---|:--:|---|---|
| Register | yes | mouse | "Account created" confirmation for the new account |
| Log in | yes | mouse | dashboard opens |
| Navigate (primary navigation) | yes | mouse | Examinations, About and Dashboard pages each open from the primary navigation |
| Create a draft | yes | mouse | "… was saved as a draft" message on the list |
| Create a planned examination | yes | mouse | "“Annual checkup” was saved." message on the list |
| Edit an examination | yes | mouse | "Your changes were saved." and the new location on the detail page |
| Configure a reminder | yes | mouse | "The reminder is saved." and "3 days before" |
| Disable a reminder | yes | mouse | "The reminder is off." |
| Configure recurrence | yes | mouse | "The recurrence is saved." |
| Create the next occurrence | yes | mouse | the new occurrence's detail page opens with its "This is the next occurrence" message |
| Delete, with the confirmation dialog | yes | mouse | confirmation dialog opens; the record is deleted only on "Delete permanently" and the list reports it |
| Change month in the calendar | yes | mouse | month heading moves forward, then back |
| Change the account timezone | yes | mouse | "Timezone updated." after choosing Asia/Tokyo |
| Change the password | yes | mouse | "Your password has been changed." |
| Log out | yes | mouse | login page opens |
## 3. Dialog

The delete confirmation dialog opened on the click, "Cancel" closed it without deleting (yes), and the record was deleted only after "Delete permanently".

## 4. Hover, Gesture and Colour Independence

- Nothing in the interface is revealed only on hover: every action above completed by a plain click, and `:hover` styles only tint backgrounds.
- No action needs a gesture beyond a single tap or click: no swipe, drag, long press or multi-finger input exists.
- No state is conveyed by colour alone: statuses, time states and calendar states each carry a text label and a distinct shape (checked in detail by `TC-FR-043-01…05`); errors carry text and a marker next to the field.

## 5. Limits of This Review

- The browser ran headless; a person using a physical mouse would reach the same controls, but no human operated them.
- Native select pickers are operating-system widgets outside the page: the review opened each select with a click, then chose the option through WebDriver.

## 6. Defects Found and Fixed

| # | Defect found during the review | Fix |
|---|---|---|
| 1 | After a successful timezone change the account form remounted (it was keyed on the timezone value), so the "Timezone updated." confirmation vanished at once. The change itself was saved. Found by the keyboard run, whose check waits for the confirmation. | The form is keyed on the account id; the confirmation now stays until the next edit. |

The fix was made before the recorded runs; it changed no documented behavior.

## 7. Verdict

**Pass.** Every primary action completed using mouse input.
