/**
 * Month arithmetic on calendar values only — year/month numbers and `YYYY-MM-DD`
 * strings — so no timezone offset can move a day (IMPLEMENTATION_PLAN.md R4).
 */

import { daysInMonth, isoWeekdayIndex } from '../format/datetime'

export type Month = { year: number; month: number }

const MONTH_NAMES = [
  'January',
  'February',
  'March',
  'April',
  'May',
  'June',
  'July',
  'August',
  'September',
  'October',
  'November',
  'December',
]

export const WEEKDAY_NAMES = [
  'Monday',
  'Tuesday',
  'Wednesday',
  'Thursday',
  'Friday',
  'Saturday',
  'Sunday',
]

const pad = (value: number) => String(value).padStart(2, '0')

export function parseMonth(value: string | null): Month | null {
  const match = /^(\d{4})-(\d{2})$/.exec(value ?? '')
  if (!match) return null
  const month = Number(match[2])
  return month >= 1 && month <= 12 ? { year: Number(match[1]), month } : null
}

export function monthFromDate(isoDate: string): Month {
  return { year: Number(isoDate.slice(0, 4)), month: Number(isoDate.slice(5, 7)) }
}

export function formatMonthKey({ year, month }: Month) {
  return `${year}-${pad(month)}`
}

export function monthLabel({ year, month }: Month) {
  return `${MONTH_NAMES[month - 1]} ${year}`
}

export function shiftMonth({ year, month }: Month, delta: number): Month {
  const index = year * 12 + (month - 1) + delta
  return { year: Math.floor(index / 12), month: (index % 12) + 1 }
}

/** Every date of the month, as `YYYY-MM-DD` strings. */
export function datesOfMonth({ year, month }: Month): string[] {
  return Array.from(
    { length: daysInMonth(year, month) },
    (_, index) => `${year}-${pad(month)}-${pad(index + 1)}`,
  )
}

export function monthRange(month: Month) {
  const dates = datesOfMonth(month)
  return { startDate: dates[0], endDate: dates[dates.length - 1] }
}

/** Empty cells before the 1st in a Monday-first week. */
export function leadingBlankDays(month: Month) {
  return isoWeekdayIndex(datesOfMonth(month)[0])
}
