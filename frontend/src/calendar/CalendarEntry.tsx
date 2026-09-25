import { Link } from 'react-router'

import type { CalendarEntry as Entry, CalendarState } from '../api/types'
import { StateIcon } from '../examinations/StateIcon'
import { CalendarTime } from '../format/DateTime'
import styles from './CalendarEntry.module.css'

export const CALENDAR_STATES: CalendarState[] = [
  'planned',
  'completed',
  'cancelled',
  'missed',
  'overdue',
]

export const CALENDAR_STATE_LABELS: Record<CalendarState, string> = {
  planned: 'Planned',
  completed: 'Completed',
  cancelled: 'Cancelled',
  missed: 'Missed',
  overdue: 'Overdue',
}

/**
 * One examination in the calendar. Each state has its own text label, its own shape
 * and its own styling, so no two states are told apart by colour alone
 * (ADS-FR-043-01).
 */
export function CalendarEntry({ entry }: { entry: Entry }) {
  const { state, examination } = entry
  return (
    <Link
      to={`/examinations/${examination.id}`}
      className={`${styles.entry} ${styles[state]}`}
      data-state={state}
    >
      <StateIcon state={state} className={styles.icon} />
      <span className={styles.label}>{CALENDAR_STATE_LABELS[state]}</span>
      <span className={styles.title}>
        {examination.scheduled_time && state !== 'completed' ? (
          <>
            <CalendarTime value={examination.scheduled_time} />{' '}
          </>
        ) : null}
        {examination.title}
      </span>
    </Link>
  )
}

/** The key to the five indicators, shown above the calendar. */
export function CalendarLegend() {
  return (
    <ul className={styles.legend} aria-label="Calendar legend">
      {CALENDAR_STATES.map((state) => (
        <li key={state} className={`${styles.legendItem} ${styles[state]}`}>
          <StateIcon state={state} className={styles.icon} />
          <span className={styles.label}>{CALENDAR_STATE_LABELS[state]}</span>
        </li>
      ))}
    </ul>
  )
}
