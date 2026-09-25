import { apiRequest } from './authenticated'
import { ApiError } from './client'
import type { RecurrenceInterval, RecurrenceRule } from './types'

const recurrencePath = (examinationId: number) => `/examinations/${examinationId}/recurrence/`

/** The examination's recurrence rule, or `null` when it has none (the API answers 404). */
export async function getRecurrence(examinationId: number): Promise<RecurrenceRule | null> {
  try {
    return await apiRequest<RecurrenceRule>(recurrencePath(examinationId))
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) return null
    throw error
  }
}

export function saveRecurrence(
  examinationId: number,
  interval: RecurrenceInterval,
  existing: boolean,
) {
  return apiRequest<RecurrenceRule>(recurrencePath(examinationId), {
    method: existing ? 'PATCH' : 'POST',
    body: { interval },
  })
}

export const recurrenceKeys = {
  forExamination: (examinationId: number) => ['recurrence', examinationId] as const,
}
