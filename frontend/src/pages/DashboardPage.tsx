import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router'

import { DASHBOARD_QUERY_KEY, getDashboard } from '../api/dashboard'
import { EXAMINATION_STATUSES, type Dashboard, type Examination } from '../api/types'
import { DueReminders } from '../examinations/DueReminders'
import { ExaminationList } from '../examinations/ExaminationItem'
import { STATUS_LABELS } from '../examinations/presentation'
import styles from './DashboardPage.module.css'

type SectionProps = {
  id: string
  title: string
  records: Examination[]
  empty: string
}

/** One dashboard collection, with its own empty presentation (ADS-FR-044-01). */
function RecordSection({ id, title, records, empty }: SectionProps) {
  return (
    <section className={styles.section} aria-labelledby={id} data-section={id}>
      <h2 id={id}>{title}</h2>
      {records.length ? (
        <ExaminationList examinations={records} />
      ) : (
        <p className="card muted" data-empty="true">
          {empty}
        </p>
      )}
    </section>
  )
}

function Counts({ dashboard }: { dashboard: Dashboard }) {
  return (
    <div className={`card ${styles.summary}`}>
      <h2 id="counts-title">At a glance</h2>
      <dl className={styles.tiles} aria-labelledby="counts-title">
        <div className={`${styles.tile} ${dashboard.overdue_count ? styles.alertTile : ''}`}>
          <dt>Overdue</dt>
          <dd data-count="overdue">{dashboard.overdue_count}</dd>
        </div>
        {EXAMINATION_STATUSES.map((status) => (
          <div key={status} className={styles.tile}>
            <dt>{STATUS_LABELS[status]}</dt>
            <dd data-count={status}>{dashboard.status_counts[status]}</dd>
          </div>
        ))}
      </dl>
      <h3 id="category-counts-title">By category</h3>
      <dl className={styles.categories} aria-labelledby="category-counts-title">
        {dashboard.category_counts.map(({ category, count }) => (
          <div key={category.id}>
            <dt>{category.name}</dt>
            <dd>{count}</dd>
          </div>
        ))}
        <div>
          <dt>Uncategorized</dt>
          <dd data-count="uncategorized">{dashboard.uncategorized_count}</dd>
        </div>
      </dl>
    </div>
  )
}

/** The dashboard (user_flows.md §21), built from one `GET /api/v1/dashboard/`. */
export function DashboardPage() {
  const query = useQuery({ queryKey: DASHBOARD_QUERY_KEY, queryFn: getDashboard })

  return (
    <section className="page" aria-labelledby="dashboard-title">
      <div className="page-header">
        <h1 id="dashboard-title">Dashboard</h1>
        <Link className="button button-primary" to="/examinations/new">
          Add examination
        </Link>
      </div>
      {query.isPending ? (
        <p className="muted" role="status">
          Loading your dashboard…
        </p>
      ) : query.isError ? (
        <div className="alert alert-error" role="alert">
          <p>Your dashboard could not be loaded.</p>
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
          <div className={styles.sections}>
            <RecordSection
              id="overdue-title"
              title="Overdue"
              records={query.data.overdue}
              empty="Nothing is overdue."
            />
            <RecordSection
              id="upcoming-title"
              title="Upcoming"
              records={query.data.upcoming}
              empty="Nothing is coming up."
            />
            <RecordSection
              id="recently-completed-title"
              title="Recently completed"
              records={query.data.recently_completed}
              empty="Nothing completed in the last 30 days."
            />
          </div>
          <Counts dashboard={query.data} />
        </>
      )}
      <DueReminders />
    </section>
  )
}
