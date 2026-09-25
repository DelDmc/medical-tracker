import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router'

import { examinationKeys, listExaminations } from '../api/examinations'
import { listDueReminders, reminderKeys } from '../api/reminders'
import type { Reminder } from '../api/types'
import { useAccountTimezone } from '../auth/useAccountTimezone'
import { CalendarDate } from '../format/DateTime'
import { currentDateIn } from '../format/datetime'
import styles from './DueReminders.module.css'

/** Active and due on or before the user's local date (ADS-FR-037-01, §6.6). */
function isDue(reminder: Reminder, today: string) {
  return reminder.is_active && reminder.due_date !== null && reminder.due_date <= today
}

/**
 * The due-reminders area (user_flows.md §17). It asks the backend for due reminders
 * and renders only reminders that are active and due today or earlier in the account
 * timezone. The reminder representation carries only the examination's id, so titles
 * come from the examination list.
 */
export function DueReminders() {
  const timeZone = useAccountTimezone()
  const reminders = useQuery({ queryKey: reminderKeys.due, queryFn: listDueReminders })
  const examinations = useQuery({
    queryKey: examinationKeys.list({}),
    queryFn: () => listExaminations({}),
  })

  let body
  if (reminders.isPending) {
    body = (
      <p className="muted" role="status">
        Loading reminders…
      </p>
    )
  } else if (reminders.isError) {
    body = (
      <p className="alert alert-error" role="alert">
        Reminders could not be loaded.
      </p>
    )
  } else {
    const today = currentDateIn(timeZone)
    const due = reminders.data.filter((reminder) => isDue(reminder, today))
    const titles = new Map((examinations.data ?? []).map((record) => [record.id, record.title]))
    body = due.length ? (
      <ul className={styles.list}>
        {due.map((reminder) => (
          <li key={reminder.id} className={styles.item} data-reminder-id={reminder.id}>
            <Link to={`/examinations/${reminder.examination}`}>
              {titles.get(reminder.examination) ?? `Examination #${reminder.examination}`}
            </Link>
            <span>
              Reminder due <CalendarDate value={reminder.due_date!} />
            </span>
          </li>
        ))}
      </ul>
    ) : (
      <p className="muted">No reminders are due.</p>
    )
  }

  return (
    <section className="card stack" aria-labelledby="due-reminders-title">
      <h2 id="due-reminders-title">Due reminders</h2>
      {body}
    </section>
  )
}
