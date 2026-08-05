# Diagrams

PlantUML source diagrams supplementing the prose specification in `docs/`. These are illustrative, not authoritative — the source-of-truth hierarchy in the top-level `README.md` and `CLAUDE.md` still governs; if a diagram and a document disagree, the document wins and the diagram should be corrected.

Source only (`.puml`) — no rendered images are committed. Render with a local PlantUML installation, an IDE plugin, or an equivalent PlantUML-compatible tool.

| File | Diagrams | Covers |
|---|---|---|
| [`domain_class_diagram.puml`](domain_class_diagram.puml) | Domain class diagram | `User`, `ExaminationCategory`, `ExaminationRecord`, `Reminder`, `RecurrenceRule` and their relationships, from `docs/domain_model.md` §3–4 |
| [`examination_status_state_diagram.puml`](examination_status_state_diagram.puml) | Examination status state diagram | Status transitions, the derived `upcoming`/`overdue` sub-states of `planned`, and reminder/recurrence side effects, from `docs/domain_model.md` §5, §7, §9 |
| [`sequence_login.puml`](sequence_login.puml) | Login sequence | `docs/user_flows.md` §2 (login), FR-005/SEC-005 |
| [`sequence_refresh.puml`](sequence_refresh.puml) | Session restoration (page reload) + active-session refresh | `docs/user_flows.md` §3, FR-007/FR-008 |
| [`sequence_logout.puml`](sequence_logout.puml) | Logout sequence | `docs/user_flows.md` §4, FR-006/SEC-005 |
| [`sequence_password_change.puml`](sequence_password_change.puml) | Authenticated password change sequence | `docs/user_flows.md` §25, FR-048 |
