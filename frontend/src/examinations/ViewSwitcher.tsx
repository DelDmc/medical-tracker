import { Link } from 'react-router'

import styles from './ViewSwitcher.module.css'

export type ExaminationView = '' | 'upcoming' | 'overdue' | 'past'

export const VIEWS: { value: ExaminationView; label: string; empty: string }[] = [
  { value: '', label: 'All', empty: 'You have no examinations yet.' },
  { value: 'upcoming', label: 'Upcoming', empty: 'Nothing is coming up.' },
  { value: 'overdue', label: 'Overdue', empty: 'Nothing is overdue.' },
  { value: 'past', label: 'Past', empty: 'No past examinations yet.' },
]

/** The all / upcoming / overdue / past views of the examination list (FR-031–FR-033). */
export function ViewSwitcher({
  current,
  searchParams,
}: {
  current: ExaminationView
  searchParams: URLSearchParams
}) {
  return (
    <nav aria-label="Examination views">
      <ul className={styles.views}>
        {VIEWS.map((view) => {
          const next = new URLSearchParams(searchParams)
          if (view.value) next.set('time_state', view.value)
          else next.delete('time_state')
          const search = next.toString()
          return (
            <li key={view.label}>
              <Link
                className={styles.view}
                to={{ pathname: '/examinations', search: search ? `?${search}` : '' }}
                aria-current={view.value === current ? 'page' : undefined}
              >
                {view.label}
              </Link>
            </li>
          )
        })}
      </ul>
    </nav>
  )
}
