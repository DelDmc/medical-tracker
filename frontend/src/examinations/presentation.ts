import type { ExaminationStatus } from '../api/types'

export const STATUS_LABELS: Record<ExaminationStatus, string> = {
  draft: 'Draft',
  planned: 'Planned',
  completed: 'Completed',
  cancelled: 'Cancelled',
  missed: 'Missed',
}

export const TIME_STATE_LABELS = { upcoming: 'Upcoming', overdue: 'Overdue' } as const

/** The fields each status requires, besides the title (ADS-FR-014-01). */
export function requiredDateFor(
  status: ExaminationStatus,
): 'scheduled_date' | 'completed_date' | null {
  if (status === 'planned' || status === 'cancelled' || status === 'missed') {
    return 'scheduled_date'
  }
  if (status === 'completed') return 'completed_date'
  return null
}
