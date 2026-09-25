import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useState, type ReactNode } from 'react'
import { Link, useLocation, useNavigate } from 'react-router'

import { deleteExamination, examinationKeys } from '../api/examinations'
import type { Examination } from '../api/types'
import { ConfirmDialog } from '../components/ConfirmDialog'
import { CategoryLabel, StatusBadge, TimeStateBadge } from '../examinations/Badges'
import { ExaminationLoadError, ExaminationNotFound } from '../examinations/ExaminationStatusView'
import { TIME_STATE_LABELS } from '../examinations/presentation'
import { NextOccurrenceAction } from '../examinations/NextOccurrenceAction'
import { RecurrenceSection } from '../examinations/RecurrenceSection'
import { ReminderSection } from '../examinations/ReminderSection'
import { useExaminationFromRoute } from '../examinations/useExamination'
import { CalendarDate, CalendarTime, Instant } from '../format/DateTime'
import styles from './ExaminationDetailPage.module.css'

type DetailProps = { label: string; children: ReactNode; wide?: boolean }

function Detail({ label, children, wide }: DetailProps) {
  return (
    <div className={wide ? styles.wide : undefined}>
      <dt>{label}</dt>
      <dd>{children}</dd>
    </div>
  )
}

const notSet = <span className="muted">Not set</span>

function ExaminationDetails({ examination }: { examination: Examination }) {
  return (
    <dl className={`card ${styles.details}`}>
      <Detail label="Category">
        <CategoryLabel category={examination.category} />
      </Detail>
      <Detail label="Scheduled date">
        {examination.scheduled_date ? (
          <CalendarDate value={examination.scheduled_date} weekday />
        ) : (
          notSet
        )}
      </Detail>
      <Detail label="Scheduled time">
        {examination.scheduled_time ? <CalendarTime value={examination.scheduled_time} /> : notSet}
      </Detail>
      <Detail label="Completion date">
        {examination.completed_date ? (
          <CalendarDate value={examination.completed_date} weekday />
        ) : (
          notSet
        )}
      </Detail>
      <Detail label="Time state">
        {examination.time_state ? TIME_STATE_LABELS[examination.time_state] : notSet}
      </Detail>
      <Detail label="Medical specialty">{examination.medical_specialty ?? notSet}</Detail>
      <Detail label="Location" wide>
        {examination.location ?? notSet}
      </Detail>
      <Detail label="Notes" wide>
        {examination.notes ?? notSet}
      </Detail>
      {examination.source_occurrence ? (
        <Detail label="Generated from">
          <Link to={`/examinations/${examination.source_occurrence}`}>The previous occurrence</Link>
        </Detail>
      ) : null}
      <Detail label="Created">
        <Instant value={examination.created_at} />
      </Detail>
      <Detail label="Last updated">
        <Instant value={examination.updated_at} />
      </Detail>
    </dl>
  )
}

export function ExaminationDetailPage() {
  const { examinationId, query, notFound } = useExaminationFromRoute()
  const location = useLocation()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [confirmingDelete, setConfirmingDelete] = useState(false)
  const message = (location.state as { message?: string } | null)?.message

  const removal = useMutation({
    mutationFn: () => deleteExamination(examinationId),
    onSuccess: async () => {
      const title = query.data?.title ?? 'The examination'
      queryClient.removeQueries({ queryKey: examinationKeys.detail(examinationId) })
      await queryClient.invalidateQueries({ queryKey: examinationKeys.all })
      navigate('/examinations', { replace: true, state: { message: `“${title}” was deleted.` } })
    },
  })

  if (notFound) return <ExaminationNotFound />
  if (query.isPending) {
    return (
      <p className="muted" role="status">
        Loading examination…
      </p>
    )
  }
  if (query.isError) return <ExaminationLoadError onRetry={() => query.refetch()} />

  const examination = query.data
  return (
    <section className="page" aria-labelledby="examination-title">
      <div className={styles.header}>
        <p className="muted">
          <Link to="/examinations">Examinations</Link>
        </p>
        <h1 id="examination-title">{examination.title}</h1>
        <div className={styles.badges}>
          <StatusBadge status={examination.status} />
          <TimeStateBadge timeState={examination.time_state} />
        </div>
      </div>
      {message ? (
        <div className="alert alert-success" role="status">
          <p>{message}</p>
        </div>
      ) : null}
      <div className="button-row">
        <Link className="button button-primary" to={`/examinations/${examination.id}/edit`}>
          Edit
        </Link>
        <button
          className="button button-secondary"
          type="button"
          onClick={() => setConfirmingDelete(true)}
        >
          Delete
        </button>
      </div>
      <ExaminationDetails examination={examination} />
      <ReminderSection
        key={`${examination.id}-${examination.status}`}
        examination={examination}
      />
      <RecurrenceSection
        key={`recurrence-${examination.id}-${examination.status}`}
        examination={examination}
      >
        {(rule) =>
          rule && examination.scheduled_date && examination.status !== 'draft' ? (
            <NextOccurrenceAction examination={examination} />
          ) : null
        }
      </RecurrenceSection>
      <ConfirmDialog
        open={confirmingDelete}
        title="Delete this examination?"
        confirmLabel={removal.isPending ? 'Deleting…' : 'Delete permanently'}
        pending={removal.isPending}
        onConfirm={() => removal.mutate()}
        onCancel={() => setConfirmingDelete(false)}
      >
        <p>
          “{examination.title}” will be deleted permanently, together with its reminder and
          recurrence settings. This cannot be undone.
        </p>
        {removal.isError ? (
          <p className="field-error" role="alert">
            The examination could not be deleted. Please try again.
          </p>
        ) : null}
      </ConfirmDialog>
    </section>
  )
}
