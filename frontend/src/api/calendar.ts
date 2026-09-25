import { apiRequest } from './authenticated'
import type { CalendarEntry } from './types'

/** `GET /api/v1/calendar/` for an inclusive `YYYY-MM-DD` range. */
export function getCalendar(startDate: string, endDate: string) {
  const query = new URLSearchParams({ start_date: startDate, end_date: endDate })
  return apiRequest<CalendarEntry[]>(`/calendar/?${query}`)
}

export const calendarKeys = {
  range: (startDate: string, endDate: string) => ['calendar', startDate, endDate] as const,
}
