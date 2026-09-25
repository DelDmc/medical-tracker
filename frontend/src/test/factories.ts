import type { Category, Examination } from '../api/types'
import { session } from '../auth/session'

export const CATEGORIES: Category[] = [
  { id: 1, name: 'General medical appointment', slug: 'general-medical-appointment' },
  { id: 2, name: 'Dental appointment', slug: 'dental-appointment' },
  { id: 3, name: 'Specialist consultation', slug: 'specialist-consultation' },
  { id: 4, name: 'Laboratory test', slug: 'laboratory-test' },
  { id: 5, name: 'Vaccination', slug: 'vaccination' },
  { id: 6, name: 'Preventive examination', slug: 'preventive-examination' },
  { id: 7, name: 'Follow-up', slug: 'follow-up' },
  { id: 8, name: 'Other', slug: 'other' },
]

let nextId = 100

export function makeExamination(overrides: Partial<Examination> = {}): Examination {
  nextId += 1
  return {
    id: nextId,
    user_id: 1,
    category: null,
    title: `Examination ${nextId}`,
    medical_specialty: null,
    scheduled_date: '2026-09-10',
    scheduled_time: null,
    completed_date: null,
    status: 'planned',
    location: null,
    notes: null,
    source_occurrence: null,
    time_state: 'upcoming',
    created_at: '2026-07-21T04:10:00Z',
    updated_at: '2026-07-21T04:10:00Z',
    ...overrides,
  }
}

/** Start the test with an authenticated in-memory session. */
export function signIn(timezone = 'Europe/Warsaw') {
  session.signIn('test-access-token', { id: 1, email: 'person@example.com', timezone })
}
