# TC-UX-001-02 — Responsive Review, Tablet Width (768 CSS px)

**Standing:** This is a non-normative verification record. It is evidence that the test case named below (`docs/test_specification.md`) was executed; it is not part of the source-of-truth hierarchy in `product_definition.md` §2, defines no behavior, and must never be cited as authority. When it disagrees with an authoritative document, that document wins and the review is repeated.

| | |
|---|---|
| **Test case** | `TC-UX-001-02` — Primary pages remain usable at the approved tablet viewport width |
| **Requirement** | `UX-001` (decisions `ADS-UX-001-01`, `ADS-UX-001-02`) |
| **Layer** | Documented review |
| **Date** | 2026-09-25 |
| **Viewport width** | **768 CSS pixels** (tablet; the approved widths are 320, 768 and 1280 — `ADS-UX-001-02`) |
| **Build reviewed** | `feature/s17-ux-review` (Slice 17), frontend dev server against the local backend |
| **Browser** | Firefox 155.0.1, headless, driven through geckodriver with Selenium 4.49 |
| **Verdict** | **Pass** — no page requires horizontal scrolling and every control is usable |

## 1. Method

- A review account was seeded with seven examinations covering every status (draft, planned — one upcoming, one due today, one overdue — completed, cancelled, missed), a due reminder, a recurrence rule, uncategorized and categorized records, and deliberately long text (a 90-character title and a long location), so every page rendered populated.
- The Firefox window was sized so that `window.innerWidth` is exactly 768 CSS pixels (asserted before measuring).
- Each page was loaded after logging in through the login page (the registration and login pages before). For each page the review recorded: `document.documentElement.scrollWidth` against `clientWidth` (horizontal page scrolling), every rendered element whose box extends past either viewport edge, and every rendered link, button and form control shorter than 44 px or narrower than 24 px.
- A full-page screenshot of every page was inspected by eye for clipped, overlapping, truncated or otherwise unusable controls.
- The six pages named by `UX-001` were reviewed; the examination detail page was added because the reminder, recurrence and next-occurrence controls live there.

## 2. Results

| Page | Path | Measured viewport | Horizontal scrolling (scroll / client width) | Elements beyond the viewport | Every control usable | Notes |
|---|---|---:|---|---:|:--:|---|
| Registration | `/register` | 768 | absent (768 / 768) | 0 | yes | Form within the content width. Links under 44 px tall: About this app, Log in — all inside a sentence. |
| Login | `/login` | 768 | absent (768 / 768) | 0 | yes | Form within the content width. Links under 44 px tall: About this app, Create an account — all inside a sentence. |
| Examination list | `/examinations` | 768 | absent (756 / 756) | 0 | yes | Filters in three columns; record metadata in columns. Links under 44 px tall: About this app — all inside a sentence. |
| Examination form | `/examinations/new` | 768 | absent (756 / 756) | 0 | yes | Fields in two columns. Links under 44 px tall: About this app — all inside a sentence. |
| Calendar | `/calendar` | 768 | absent (768 / 768) | 0 | yes | Agenda layout (the seven-column grid starts at 1024 px). Links under 44 px tall: About this app — all inside a sentence. |
| Dashboard | `/dashboard` | 768 | absent (756 / 756) | 0 | yes | Sections stack; count tiles five per row. Links under 44 px tall: About this app — all inside a sentence. |
| Examination detail (supplementary) | `/examinations/{id}` | 768 | absent (756 / 756) | 0 | yes | Details in two columns. Links under 44 px tall: About this app — all inside a sentence. |

"Links under 44 px tall" lists only links inside running text ("Already registered? Log in", the footer's "About this app"), which are sized by the surrounding line of text; every stand-alone control — buttons, inputs, selects, navigation, record titles, calendar entries — is at least 44 px tall.

## 3. Defects Found and Fixed

The review was run at all three approved widths together; the table lists everything it found at any width.

| # | Defect found during the review | Width(s) | Fix |
|---|---|---|---|
| 1 | The global stylesheet loaded after the component styles, so `.button { display: inline-flex }` overrode the rule hiding the Menu toggle: the toggle stayed visible beside the full navigation and was squeezed to "Men/u". | 768, 1280 | `src/main.tsx` imports `global.css` before any component; the hiding rule gained specificity. |
| 2 | The six authenticated navigation items do not fit on one line beside the brand at 768 px; the header wrapped into two cramped rows. | 768 | The navigation stays behind the Menu toggle below 1024 px and becomes a single row from 1024 px. |
| 3 | The seven-column month grid left about 100 px per day at 768 px; state labels and titles broke mid-word ("PLAN/NED", "Blood / d test"). | 768 | Below 1024 px the calendar is an agenda of the days that have examinations; the grid starts at 1024 px. |
| 4 | `overflow-wrap: anywhere` on `body` split words even where a line break would do, and the calendar entry title shared its column with the icon. | 1280 | `overflow-wrap: break-word`; the entry icon moved onto the label row so the title spans the entry; `hyphens: auto` as a last resort. |
| 5 | Dashboard count tiles stacked one per row at 320 px. | 320 | Tile minimum width 7rem: two per row. |
| 6 | Two stand-alone links were only 23–24 px tall: the detail page's back link and the due-reminder titles. | all | Both are 44 px tall now; the back link reads "‹ All examinations". |
| 7 | Record metadata split each label and value onto separate lines in three narrow columns. | 768 | Metadata columns are at least 15rem wide. |

Every defect was fixed before the final measurement recorded above; none required a change to documented behavior.

## 4. Verdict

**Pass.** At 768 CSS pixels none of the reviewed pages requires horizontal page scrolling, no element extends past the viewport, and every control is present, unclipped and usable.
