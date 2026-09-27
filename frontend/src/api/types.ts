/** Shapes defined by docs/api_contract.md. */

export type Account = {
  id: number
  email: string
  timezone: string
}

export type RegistrationRequest = {
  email: string
  password: string
  timezone: string
}

export type ExaminationStatus = 'draft' | 'planned' | 'completed' | 'cancelled' | 'missed'

export const EXAMINATION_STATUSES: ExaminationStatus[] = [
  'draft',
  'planned',
  'completed',
  'cancelled',
  'missed',
]

/** The derived time state of a planned examination; `null` for every other record. */
export type TimeState = 'upcoming' | 'overdue' | null

export type Category = {
  id: number
  name: string
  slug: string
}

/** api_contract.md §8.1 */
export type Examination = {
  id: number
  user_id: number
  category: Category | null
  title: string
  medical_specialty: string | null
  scheduled_date: string | null
  scheduled_time: string | null
  completed_date: string | null
  status: ExaminationStatus
  location: string | null
  notes: string | null
  source_occurrence: number | null
  time_state: TimeState
  created_at: string
  updated_at: string
}

/** The writable fields of an examination (api_contract.md §8.1, §10). */
export type ExaminationInput = {
  category_id: number | null
  title: string
  medical_specialty: string | null
  scheduled_date: string | null
  scheduled_time: string | null
  completed_date: string | null
  status: ExaminationStatus
  location: string | null
  notes: string | null
}

/** api_contract.md §14 */
export type Reminder = {
  id: number
  examination: number
  offset_days: number
  due_date: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export type RecurrenceInterval = 'monthly' | 'six_months' | 'yearly'

/** api_contract.md §15 */
export type RecurrenceRule = {
  id: number
  examination: number
  interval: RecurrenceInterval
  next_due_date: string | null
  created_at: string
  updated_at: string
}

/** A calendar entry's state: the stored status, or `overdue` (api_contract.md §17). */
export type CalendarState = 'planned' | 'completed' | 'cancelled' | 'missed' | 'overdue'

export type CalendarEntry = {
  calendar_date: string
  state: CalendarState
  examination: Pick<
    Examination,
    | 'id'
    | 'title'
    | 'category'
    | 'scheduled_date'
    | 'scheduled_time'
    | 'completed_date'
    | 'status'
    | 'time_state'
  >
}

/** api_contract.md §18 */
export type Dashboard = {
  upcoming: Examination[]
  overdue: Examination[]
  recently_completed: Examination[]
  status_counts: Record<ExaminationStatus, number>
  category_counts: { category: Category; count: number }[]
  uncategorized_count: number
  overdue_count: number
}
