import type { Category, ExaminationStatus, TimeState } from '../api/types'
import styles from './Badges.module.css'
import { STATUS_LABELS, TIME_STATE_LABELS } from './presentation'
import { StateIcon } from './StateIcon'

/** The shared category presentation: `null` reads "Uncategorized" (ADS-FR-027-01). */
export function CategoryLabel({ category }: { category: Category | null }) {
  return <span>{category ? category.name : 'Uncategorized'}</span>
}

/** The stored lifecycle status, as a text label with its own shape. */
export function StatusBadge({ status }: { status: ExaminationStatus }) {
  return (
    <span className={`${styles.badge} ${styles[status]}`} data-status={status}>
      <StateIcon state={status} className={styles.icon} />
      {STATUS_LABELS[status]}
    </span>
  )
}

/** The derived time state of a planned record; renders nothing when it is `null`. */
export function TimeStateBadge({ timeState }: { timeState: TimeState }) {
  if (!timeState) return null
  return (
    <span className={`${styles.badge} ${styles[timeState]}`} data-time-state={timeState}>
      <StateIcon state={timeState} className={styles.icon} />
      {TIME_STATE_LABELS[timeState]}
    </span>
  )
}
