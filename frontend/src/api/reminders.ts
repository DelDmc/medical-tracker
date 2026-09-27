import { apiRequest } from './authenticated'
import { ApiError } from './client'
import type { Reminder } from './types'

const reminderPath = (examinationId: number) => `/examinations/${examinationId}/reminder/`

/** The examination's reminder, or `null` when it has none (the API answers 404). */
export async function getReminder(examinationId: number): Promise<Reminder | null> {
  try {
    return await apiRequest<Reminder>(reminderPath(examinationId))
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) return null
    throw error
  }
}

export function createReminder(examinationId: number, offsetDays: number) {
  return apiRequest<Reminder>(reminderPath(examinationId), {
    method: 'POST',
    body: { offset_days: offsetDays },
  })
}

export function updateReminder(
  examinationId: number,
  changes: { offset_days?: number; is_active?: boolean },
) {
  return apiRequest<Reminder>(reminderPath(examinationId), { method: 'PATCH', body: changes })
}

/** `GET /api/v1/reminders/?state=due` — the backend alone decides what is due. */
export function listDueReminders() {
  return apiRequest<Reminder[]>('/reminders/?state=due')
}

export const reminderKeys = {
  all: ['reminders'] as const,
  forExamination: (examinationId: number) => ['reminders', 'examination', examinationId] as const,
  due: ['reminders', 'due'] as const,
}
