import { useQuery } from '@tanstack/react-query'
import { useSearchParams } from 'react-router'

import { calendarKeys, getCalendar } from '../api/calendar'
import type { CalendarEntry as Entry } from '../api/types'
import { useAccountTimezone } from '../auth/useAccountTimezone'
import { currentDateIn, formatCalendarDate, isoWeekdayIndex } from '../format/datetime'
import { CalendarEntry, CalendarLegend } from './CalendarEntry'
import styles from './CalendarPage.module.css'
import {
  datesOfMonth,
  formatMonthKey,
  leadingBlankDays,
  monthFromDate,
  monthLabel,
  monthRange,
  parseMonth,
  shiftMonth,
  WEEKDAY_NAMES,
  type Month,
} from './month'

function groupByDate(entries: Entry[]) {
  const byDate = new Map<string, Entry[]>()
  for (const entry of entries) {
    byDate.set(entry.calendar_date, [...(byDate.get(entry.calendar_date) ?? []), entry])
  }
  return byDate
}

type MonthGridProps = { month: Month; entries: Entry[]; today: string }

function MonthGrid({ month, entries, today }: MonthGridProps) {
  const byDate = groupByDate(entries)
  return (
    <>
      <ol className={styles.weekdays} aria-hidden="true">
        {WEEKDAY_NAMES.map((name) => (
          <li key={name}>{name.slice(0, 3)}</li>
        ))}
      </ol>
      <ol className={styles.grid} aria-label={`Examinations in ${monthLabel(month)}`}>
        {Array.from({ length: leadingBlankDays(month) }, (_, index) => (
          <li key={`blank-${index}`} className={styles.blank} aria-hidden="true" />
        ))}
        {datesOfMonth(month).map((date) => {
          const dayEntries = byDate.get(date) ?? []
          const classes = [styles.day, dayEntries.length ? '' : styles.empty]
          if (date === today) classes.push(styles.today)
          return (
            <li
              key={date}
              className={classes.join(' ')}
              data-date={date}
              aria-current={date === today ? 'date' : undefined}
            >
              <h3 className={styles.dayHeading}>
                <time dateTime={date}>
                  <span className={styles.phoneOnly}>
                    {WEEKDAY_NAMES[isoWeekdayIndex(date)]}{' '}
                  </span>
                  {formatCalendarDate(date)}
                </time>
              </h3>
              {dayEntries.length ? (
                <ul className={styles.entries}>
                  {dayEntries.map((entry) => (
                    <li key={`${entry.examination.id}-${entry.calendar_date}`}>
                      <CalendarEntry entry={entry} />
                    </li>
                  ))}
                </ul>
              ) : null}
            </li>
          )
        })}
      </ol>
    </>
  )
}

/**
 * The monthly calendar (user_flows.md §20): one request for the month's inclusive
 * range; each examination sits on the date the API places it.
 */
export function CalendarPage() {
  const timeZone = useAccountTimezone()
  const today = currentDateIn(timeZone)
  const [searchParams, setSearchParams] = useSearchParams()
  const month = parseMonth(searchParams.get('month')) ?? monthFromDate(today)
  const { startDate, endDate } = monthRange(month)
  const query = useQuery({
    queryKey: calendarKeys.range(startDate, endDate),
    queryFn: () => getCalendar(startDate, endDate),
  })

  const goTo = (target: Month) => setSearchParams({ month: formatMonthKey(target) })

  return (
    <section className="page" aria-labelledby="calendar-title">
      <h1 id="calendar-title">Calendar</h1>
      <div className={styles.toolbar}>
        <h2 aria-live="polite">{monthLabel(month)}</h2>
        <div className={styles.navigation}>
          <button
            className="button button-secondary"
            type="button"
            onClick={() => goTo(shiftMonth(month, -1))}
          >
            <span aria-hidden="true">‹</span> Previous month
          </button>
          <button
            className="button button-secondary"
            type="button"
            onClick={() => goTo(monthFromDate(today))}
          >
            This month
          </button>
          <button
            className="button button-secondary"
            type="button"
            onClick={() => goTo(shiftMonth(month, 1))}
          >
            Next month <span aria-hidden="true">›</span>
          </button>
        </div>
      </div>
      <CalendarLegend />
      {query.isPending ? (
        <p className="muted" role="status">
          Loading the calendar…
        </p>
      ) : query.isError ? (
        <div className="alert alert-error" role="alert">
          <p>The calendar could not be loaded.</p>
          <button
            className="button button-secondary"
            type="button"
            onClick={() => query.refetch()}
          >
            Try again
          </button>
        </div>
      ) : (
        <>
          {query.data.length ? null : (
            <p className="card muted">No examinations in {monthLabel(month)}.</p>
          )}
          <MonthGrid month={month} entries={query.data} today={today} />
        </>
      )}
    </section>
  )
}
