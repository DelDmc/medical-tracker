# TC-UX-008-01 — Input-Method Review, Touch

**Standing:** This is a non-normative verification record. It is evidence that the test case named below (`docs/test_specification.md`) was executed; it is not part of the source-of-truth hierarchy in `product_definition.md` §2, defines no behavior, and must never be cited as authority. When it disagrees with an authoritative document, that document wins and the review is repeated.

| | |
|---|---|
| **Test case** | `TC-UX-008-01` — Primary flows are completable using touch input |
| **Requirement** | `UX-008` (decision `ADS-UX-008-01`) |
| **Layer** | Documented review |
| **Date** | 2026-09-25 |
| **Viewport** | 768 CSS pixels (tablet width, where the navigation sits behind the Menu toggle) |
| **Build reviewed** | `feature/s17-ux-review` (Slice 17), frontend dev server against the local backend |
| **Browser** | Firefox 155.0.1, headless, driven through geckodriver with Selenium 4.49 |
| **Verdict** | **Pass** — 15 of 15 primary actions completed |

## 1. Method

Touch taps: W3C WebDriver pointer actions with pointer type `touch` (pointer down/up on the element's centre). Firefox dispatched the events as `pointerType: "touch"` — recorded for every action below. Text was entered as keystrokes into the tapped field, as an on-screen keyboard does. Scrolling to off-screen controls stood in for swiping.

A fresh account was registered through the UI at the start of the run, so every action ran on real data end to end, and each action was judged complete only when its outcome appeared in the application (right-hand column). The enumerated primary actions are those of `IMPLEMENTATION_PLAN.md` Task 17.2: navigate, register, log in, log out, create a draft, create a planned examination, edit, delete (with the confirmation dialog), configure and disable a reminder, configure recurrence, create a next occurrence, change month in the calendar, change the account timezone, and change the password.

## 2. Results

| Primary action | Completed | Pointer events observed | Outcome verified |
|---|:--:|---|---|
| Register | yes | touch | "Account created" confirmation for the new account |
| Log in | yes | touch | dashboard opens |
| Navigate (primary navigation) | yes | touch | Examinations, About and Dashboard pages each open from the primary navigation |
| Create a draft | yes | touch | "… was saved as a draft" message on the list |
| Create a planned examination | yes | touch | "“Annual checkup” was saved." message on the list |
| Edit an examination | yes | touch | "Your changes were saved." and the new location on the detail page |
| Configure a reminder | yes | touch | "The reminder is saved." and "3 days before" |
| Disable a reminder | yes | touch | "The reminder is off." |
| Configure recurrence | yes | touch | "The recurrence is saved." |
| Create the next occurrence | yes | touch | the new occurrence's detail page opens with its "This is the next occurrence" message |
| Delete, with the confirmation dialog | yes | touch | confirmation dialog opens; the record is deleted only on "Delete permanently" and the list reports it |
| Change month in the calendar | yes | touch | month heading moves forward, then back |
| Change the account timezone | yes | touch | "Timezone updated." after choosing Asia/Tokyo |
| Change the password | yes | touch | "Your password has been changed." |
| Log out | yes | touch | login page opens |
## 3. Dialog

The delete confirmation dialog opened on the tap, "Cancel" closed it without deleting (yes), and the record was deleted only after "Delete permanently".

## 4. Hover, Gesture and Colour Independence

- Nothing in the interface is revealed only on hover: every action above completed by touch, where there is no hover, and `:hover` styles only tint backgrounds.
- No action needs a gesture beyond a single tap or click: no swipe, drag, long press or multi-finger input exists.
- No state is conveyed by colour alone: statuses, time states and calendar states each carry a text label and a distinct shape (checked in detail by `TC-FR-043-01…05`); errors carry text and a marker next to the field.

## 5. Limits of This Review

- Touch was synthesised by WebDriver in a desktop browser, not performed on a physical touch screen; the review shows the controls respond to touch pointer input and are large enough (44 px, recorded in `TC-UX-001-*`), not how they feel on a device. A check on a real phone or tablet by the owner remains worthwhile.
- Native select pickers are operating-system widgets outside the page: the review opened each select with a tap, then chose the option through WebDriver.

## 6. Defects Found and Fixed

| # | Defect found during the review | Fix |
|---|---|---|
| 1 | After a successful timezone change the account form remounted (it was keyed on the timezone value), so the "Timezone updated." confirmation vanished at once. The change itself was saved. Found by the keyboard run, whose check waits for the confirmation. | The form is keyed on the account id; the confirmation now stays until the next edit. |

The fix was made before the recorded runs; it changed no documented behavior.

## 7. Verdict

**Pass.** Every primary action completed using touch input.
