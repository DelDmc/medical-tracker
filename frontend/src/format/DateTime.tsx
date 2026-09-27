import { useAccountTimezone } from '../auth/useAccountTimezone'
import { formatCalendarDate, formatCalendarTime, formatInstant } from './datetime'

/** A real instant, shown in the account's timezone. */
export function Instant({ value }: { value: string }) {
  const timeZone = useAccountTimezone()
  return <time dateTime={value}>{formatInstant(value, timeZone)}</time>
}

/** A stored calendar date, shown exactly as stored. */
export function CalendarDate({ value, weekday }: { value: string; weekday?: boolean }) {
  return <time dateTime={value}>{formatCalendarDate(value, { weekday })}</time>
}

/** A stored local time, shown exactly as stored. */
export function CalendarTime({ value }: { value: string }) {
  return <time dateTime={value}>{formatCalendarTime(value)}</time>
}
