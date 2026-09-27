# TC-PRV-001-01 — Examination Field-Boundary Data-Model Review

**Standing:** This is a non-normative verification record. It is evidence that test case `TC-PRV-001-01` (`docs/test_specification.md`) was executed; it is not part of the source-of-truth hierarchy in `product_definition.md` §2, defines no behavior, and must never be cited as authority. When it disagrees with `docs/domain_model.md`, the domain model wins and this review is repeated.

| | |
|---|---|
| **Test case** | `TC-PRV-001-01` — Stored and writable examination fields match the approved domain model |
| **Requirement** | `PRV-001` (decision `ADS-PRV-001-01`) |
| **Layer** | Data-model review |
| **Date** | 2026-09-25 |
| **Reviewed code** | `backend/examinations/models.py` (`ExaminationRecord`), `backend/examinations/serializers.py` (`ExaminationSerializer`, which serves both create and update) |
| **Approved model** | `docs/domain_model.md` §3.3 |

## 1. Method

The stored fields were read from the model's concrete field list (`ExaminationRecord._meta.concrete_fields`) and the request fields from the serializer's declared fields, rather than from the source text, so that inherited fields (the audit timestamps come from an abstract base class) are included. Each field was then matched against the §3.3 field table.

## 2. Stored fields — model against domain model

| `domain_model.md` §3.3 field | Domain type | Model field | Column type | Nullable | Match |
|---|---|---|---|---|---|
| `id` | Identifier | `id` | `BigAutoField` | no | yes |
| `user` | User reference | `user` | `ForeignKey(User)` | no | yes |
| `category` | ExaminationCategory reference, optional | `category` | `ForeignKey(ExaminationCategory)` | yes | yes |
| `title` | Text, required | `title` | `CharField` | no | yes |
| `medical_specialty` | Text, optional | `medical_specialty` | `CharField` | yes | yes |
| `scheduled_date` | Date, conditional | `scheduled_date` | `DateField` | yes | yes |
| `scheduled_time` | Time, optional | `scheduled_time` | `TimeField` | yes | yes |
| `completed_date` | Date, conditional | `completed_date` | `DateField` | yes | yes |
| `status` | Enumeration, required | `status` | `CharField` with choices and a check constraint | no | yes |
| `location` | Text, optional | `location` | `CharField` | yes | yes |
| `notes` | Long text, optional | `notes` | `TextField` | yes | yes |
| `source_occurrence` | ExaminationRecord reference, optional | `source_occurrence` | `ForeignKey("self", on_delete=SET_NULL)` | yes | yes |
| `created_at` | Timezone-aware datetime | `created_at` | `DateTimeField` (`USE_TZ = True`) | no | yes |
| `updated_at` | Timezone-aware datetime | `updated_at` | `DateTimeField` (`USE_TZ = True`) | no | yes |

**14 of 14** domain-model fields are stored, and the model stores **no field outside the table**. `overdue` is not stored anywhere (domain model §5, §7).

## 3. Request fields — create and update serializer against domain model

Fields a client may write:

| Serializer field | Maps to stored field | In §3.3 | Match |
|---|---|---|---|
| `category_id` (write-only) | `category` | yes | yes |
| `title` | `title` | yes | yes |
| `medical_specialty` | `medical_specialty` | yes | yes |
| `scheduled_date` | `scheduled_date` | yes | yes |
| `scheduled_time` | `scheduled_time` | yes | yes |
| `completed_date` | `completed_date` | yes | yes |
| `status` | `status` | yes | yes |
| `location` | `location` | yes | yes |
| `notes` | `notes` | yes | yes |

Fields that are read-only in the representation (`api_contract.md` §8.1): `id`, `user_id` (the `user` reference), `category` (the nested category object), `source_occurrence`, `time_state`, `created_at`, `updated_at`. A request carrying `user_id`, `source_occurrence`, `time_state`, `created_at` or `updated_at` is rejected with a field error (`api_contract.md` §10). `time_state` is a derived response value computed by `examinations/time_state.py` and is not stored.

**9 writable fields**, every one of them present in §3.3; **no writable field outside the approved model**, and no field for diagnoses, prescriptions, medical files, insurance, or government identification.

## 4. Verdict

**Pass.** Every stored and every writable examination field is present in the approved domain model, and no additional field exists. No finding is raised.
