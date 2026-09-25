# TC-UX-008-03 — Input-Method Review, Keyboard

**Standing:** This is a non-normative verification record. It is evidence that the test case named below (`docs/test_specification.md`) was executed; it is not part of the source-of-truth hierarchy in `product_definition.md` §2, defines no behavior, and must never be cited as authority. When it disagrees with an authoritative document, that document wins and the review is repeated.

| | |
|---|---|
| **Test case** | `TC-UX-008-03` — Primary flows are completable using keyboard input alone |
| **Requirement** | `UX-008` (decision `ADS-UX-008-01`) |
| **Layer** | Documented review |
| **Date** | 2026-09-25 |
| **Viewport** | 1280 CSS pixels (desktop width; repeated at 768 CSS px to cover the Menu toggle) |
| **Build reviewed** | `feature/s17-ux-review` (Slice 17), frontend dev server against the local backend |
| **Browser** | Firefox 155.0.1, headless, driven through geckodriver with Selenium 4.49 |
| **Verdict** | **Pass** — 15 of 15 primary actions completed |

## 1. Method

Keyboard only: every control was reached with Tab / Shift+Tab and operated with Enter, typing, and the arrow keys (options in a select; type-ahead for the long timezone list). No element was clicked, focused or scrolled by script. At every focus stop the review checked that the focused element matched `:focus-visible` and rendered a visible indicator (an outline of at least 2 px or a box shadow). No pointer events occurred during the run.

A fresh account was registered through the UI at the start of the run, so every action ran on real data end to end, and each action was judged complete only when its outcome appeared in the application (right-hand column). The enumerated primary actions are those of `IMPLEMENTATION_PLAN.md` Task 17.2: navigate, register, log in, log out, create a draft, create a planned examination, edit, delete (with the confirmation dialog), configure and disable a reminder, configure recurrence, create a next occurrence, change month in the calendar, change the account timezone, and change the password.

## 2. Results

| Primary action | Completed | Pointer events observed | Outcome verified |
|---|:--:|---|---|
| Register | yes | none (keyboard only) | "Account created" confirmation for the new account |
| Log in | yes | none (keyboard only) | dashboard opens |
| Navigate (primary navigation) | yes | none (keyboard only) | Examinations, About and Dashboard pages each open from the primary navigation |
| Create a draft | yes | none (keyboard only) | "… was saved as a draft" message on the list |
| Create a planned examination | yes | none (keyboard only) | "“Annual checkup” was saved." message on the list |
| Edit an examination | yes | none (keyboard only) | "Your changes were saved." and the new location on the detail page |
| Configure a reminder | yes | none (keyboard only) | "The reminder is saved." and "3 days before" |
| Disable a reminder | yes | none (keyboard only) | "The reminder is off." |
| Configure recurrence | yes | none (keyboard only) | "The recurrence is saved." |
| Create the next occurrence | yes | none (keyboard only) | the new occurrence's detail page opens with its "This is the next occurrence" message |
| Delete, with the confirmation dialog | yes | none (keyboard only) | confirmation dialog opens; the record is deleted only on "Delete permanently" and the list reports it |
| Change month in the calendar | yes | none (keyboard only) | month heading moves forward, then back |
| Change the account timezone | yes | none (keyboard only) | "Timezone updated." after choosing Asia/Tokyo |
| Change the password | yes | none (keyboard only) | "Your password has been changed." |
| Log out | yes | none (keyboard only) | login page opens |
## 3. Keyboard Focus

- **Visible focus at every step:** 194 focus stops at 1280 CSS px and 197 at 768 CSS px; every one matched `:focus-visible` and showed the 3 px focus outline. Stops without a visible indicator: **0**.
- **Delete confirmation dialog:** focus moved into the dialog on opening (yes), onto **Cancel**; four Tab and three Shift+Tab presses kept focus inside it (yes); Escape closed it (yes) and focus returned to the Delete button that opened it (yes). The dialog was then reopened and confirmed with the keyboard.
- **Menu toggle:** at 768 CSS px the primary navigation and Log out were reached by Tab to "Menu", Enter, then Tab into the revealed links; all 15 of 15 actions passed at that width too.

## 4. Hover, Gesture and Colour Independence

- Nothing in the interface is revealed only on hover: every action above completed by keyboard, where there is no pointer at all, and `:hover` styles only tint backgrounds.
- No action needs a gesture beyond a single tap or click: no swipe, drag, long press or multi-finger input exists.
- No state is conveyed by colour alone: statuses, time states and calendar states each carry a text label and a distinct shape (checked in detail by `TC-FR-043-01…05`); errors carry text and a marker next to the field.

## 5. Limits of This Review

- The browser ran headless; a person using a physical keyboard would reach the same controls, but no human operated them.
- Firefox reserves "/" for Quick Find outside text fields, so the long timezone list was searched with type-ahead on the part before the slash, then the arrow keys.

## 6. Defects Found and Fixed

| # | Defect found during the review | Fix |
|---|---|---|
| 1 | After a successful timezone change the account form remounted (it was keyed on the timezone value), so the "Timezone updated." confirmation vanished at once. The change itself was saved. Found by the keyboard run, whose check waits for the confirmation. | The form is keyed on the account id; the confirmation now stays until the next edit. |

The fix was made before the recorded runs; it changed no documented behavior.

## 7. Verdict

**Pass.** Every primary action completed using keyboard input, with visible keyboard focus at every step.
