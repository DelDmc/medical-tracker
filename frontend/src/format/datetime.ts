/**
 * The shared date and time presentation utility (ADS-UX-007-01, ADS-TECH-002-01).
 *
 * Two deliberately separate paths that never meet (IMPLEMENTATION_PLAN.md R4):
 *
 * - `formatInstant` is for real instants (`created_at`, `updated_at`): it converts the
 *   ISO timestamp into the account's timezone.
 * - `formatCalendarDate` and `formatCalendarTime` are for calendar values
 *   (`scheduled_date`, `completed_date`, reminder `due_date`, `scheduled_time`): they
 *   work on the string itself and never build a `Date`, so no timezone offset can move
 *   a date to the previous or next day.
 *
 * Every component formats dates and times through this module only.
 */

const ISO_DATE = /^(\d{4})-(\d{2})-(\d{2})$/
const ISO_TIME = /^(\d{2}):(\d{2})(?::(\d{2})(?:\.\d+)?)?$/
const WEEKDAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

/** An instant, shown as `YYYY-MM-DD HH:mm` in `timeZone`. */
export function formatInstant(iso: string, timeZone: string): string {
  const instant = new Date(iso)
  if (Number.isNaN(instant.getTime())) return iso
  const parts = new Intl.DateTimeFormat('en-GB', {
    timeZone,
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hourCycle: 'h23',
  }).formatToParts(instant)
  const part = (type: Intl.DateTimeFormatPartTypes) =>
    parts.find((candidate) => candidate.type === type)?.value ?? ''
  return `${part('year')}-${part('month')}-${part('day')} ${part('hour')}:${part('minute')}`
}

/** A calendar date exactly as stored (`YYYY-MM-DD`), optionally with its weekday. */
export function formatCalendarDate(isoDate: string, options: { weekday?: boolean } = {}): string {
  const match = ISO_DATE.exec(isoDate)
  if (!match) return isoDate
  const [, year, month, day] = match
  const text = `${year}-${month}-${day}`
  return options.weekday ? `${WEEKDAYS[isoWeekdayIndex(isoDate)]} ${text}` : text
}

/** A local wall-clock time as stored, without seconds (`HH:mm`). */
export function formatCalendarTime(isoTime: string): string {
  const match = ISO_TIME.exec(isoTime)
  return match ? `${match[1]}:${match[2]}` : isoTime
}

/** Monday = 0 … Sunday = 6, by pure calendar arithmetic (no timezone involved). */
export function isoWeekdayIndex(isoDate: string): number {
  const match = ISO_DATE.exec(isoDate)
  if (!match) return 0
  const days = daysFromCivil(Number(match[1]), Number(match[2]), Number(match[3]))
  // 1970-01-01 was a Thursday (index 3).
  return (((days + 3) % 7) + 7) % 7
}

/** Days since 1970-01-01 for a proleptic Gregorian date (Howard Hinnant's algorithm). */
function daysFromCivil(year: number, month: number, day: number): number {
  const y = month <= 2 ? year - 1 : year
  const era = Math.floor(y / 400)
  const yearOfEra = y - era * 400
  const dayOfYear = Math.floor((153 * (month + (month > 2 ? -3 : 9)) + 2) / 5) + day - 1
  const dayOfEra =
    yearOfEra * 365 + Math.floor(yearOfEra / 4) - Math.floor(yearOfEra / 100) + dayOfYear
  return era * 146097 + dayOfEra - 719468
}

export function daysInMonth(year: number, month: number): number {
  const next = month === 12 ? daysFromCivil(year + 1, 1, 1) : daysFromCivil(year, month + 1, 1)
  return next - daysFromCivil(year, month, 1)
}

/** Today's calendar date in `timeZone`, as `YYYY-MM-DD`. */
export function currentDateIn(timeZone: string, now: Date = new Date()): string {
  const parts = new Intl.DateTimeFormat('en-CA', {
    timeZone,
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).formatToParts(now)
  const part = (type: Intl.DateTimeFormatPartTypes) =>
    parts.find((candidate) => candidate.type === type)?.value ?? ''
  return `${part('year')}-${part('month')}-${part('day')}`
}
