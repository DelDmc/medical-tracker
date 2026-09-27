import { Link } from 'react-router'

import type { Examination } from '../api/types'
import { CalendarDate, CalendarTime } from '../format/DateTime'
import { CategoryLabel, StatusBadge, TimeStateBadge } from './Badges'
import styles from './ExaminationItem.module.css'

/** The date that places a record: completion for completed records, else the schedule. */
function RecordDate({ examination }: { examination: Examination }) {
  if (examination.status === 'completed' && examination.completed_date) {
    return (
      <div>
        <dt>Completed</dt>
        <dd>
          <CalendarDate value={examination.completed_date} />
        </dd>
      </div>
    )
  }
  if (examination.scheduled_date) {
    return (
      <div>
        <dt>Scheduled</dt>
        <dd>
          <CalendarDate value={examination.scheduled_date} />
          {examination.scheduled_time ? (
            <>
              {' at '}
              <CalendarTime value={examination.scheduled_time} />
            </>
          ) : null}
        </dd>
      </div>
    )
  }
  return (
    <div>
      <dt>Scheduled</dt>
      <dd>No date yet</dd>
    </div>
  )
}

/** One examination in any collection: list, time-state views, dashboard sections. */
export function ExaminationItem({ examination }: { examination: Examination }) {
  return (
    <article className={styles.item} aria-labelledby={`examination-${examination.id}-title`}>
      <div className={styles.head}>
        <h3 className={styles.title} id={`examination-${examination.id}-title`}>
          <Link to={`/examinations/${examination.id}`}>{examination.title}</Link>
        </h3>
        <div className={styles.badges}>
          <StatusBadge status={examination.status} />
          <TimeStateBadge timeState={examination.time_state} />
        </div>
      </div>
      <dl className={styles.meta}>
        <RecordDate examination={examination} />
        <div>
          <dt>Category</dt>
          <dd>
            <CategoryLabel category={examination.category} />
          </dd>
        </div>
        {examination.location ? (
          <div>
            <dt>Location</dt>
            <dd>{examination.location}</dd>
          </div>
        ) : null}
      </dl>
    </article>
  )
}

export function ExaminationList({ examinations }: { examinations: Examination[] }) {
  return (
    <ul className={styles.list}>
      {examinations.map((examination) => (
        <li key={examination.id}>
          <ExaminationItem examination={examination} />
        </li>
      ))}
    </ul>
  )
}
