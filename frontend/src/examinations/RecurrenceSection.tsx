import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState, type FormEvent, type ReactNode } from 'react'

import { getRecurrence, recurrenceKeys, saveRecurrence } from '../api/recurrence'
import type { Examination, RecurrenceInterval, RecurrenceRule } from '../api/types'
import { CalendarDate } from '../format/DateTime'
import { FormAlert, FormField } from '../forms/FormField'
import { useFormErrors } from '../forms/useFormErrors'
import styles from './SettingsSection.module.css'

export const INTERVAL_LABELS: Record<RecurrenceInterval, string> = {
  monthly: 'Every month',
  six_months: 'Every six months',
  yearly: 'Every year',
}

function RuleSummary({ rule }: { rule: RecurrenceRule }) {
  return (
    <p className={styles.status}>
      <span className={`${styles.pill} ${styles.on}`}>{INTERVAL_LABELS[rule.interval]}</span>
      <span>
        Next due date:{' '}
        {rule.next_due_date ? (
          <CalendarDate value={rule.next_due_date} />
        ) : (
          <strong>not available</strong>
        )}
        {rule.next_due_date ? null : ' until the examination has a scheduled date'}
      </span>
    </p>
  )
}

/**
 * The recurrence rule of one examination (user_flows.md §18). The rule is shown in
 * every status; it can be created or changed only while the examination is planned
 * (ADS-FR-039-01), which the backend enforces too.
 */
export function RecurrenceSection({
  examination,
  children,
}: {
  examination: Examination
  children?: (rule: RecurrenceRule | null) => ReactNode
}) {
  const queryClient = useQueryClient()
  const key = recurrenceKeys.forExamination(examination.id)
  const query = useQuery({ queryKey: key, queryFn: () => getRecurrence(examination.id) })
  const [interval, setChosenInterval] = useState<RecurrenceInterval | ''>('')
  const [saved, setSaved] = useState(false)
  const { errors, nonFieldErrors, setErrors, setErrorsFromFailure, clearErrors, formRef } =
    useFormErrors()
  const planned = examination.status === 'planned'

  const mutation = useMutation({
    mutationFn: (choice: RecurrenceInterval) =>
      saveRecurrence(examination.id, choice, Boolean(query.data)),
    onSuccess: (rule) => {
      queryClient.setQueryData(key, rule)
      setSaved(true)
    },
    onError: setErrorsFromFailure,
  })

  function onSubmit(event: FormEvent) {
    event.preventDefault()
    setSaved(false)
    const choice = interval || query.data?.interval
    if (!choice) {
      setErrors({ interval: ['Choose how often the examination repeats.'] })
      return
    }
    clearErrors()
    mutation.mutate(choice)
  }

  let body
  if (query.isPending) {
    body = (
      <p className="muted" role="status">
        Loading recurrence…
      </p>
    )
  } else if (query.isError) {
    body = (
      <p className="alert alert-error" role="alert">
        The recurrence could not be loaded.
      </p>
    )
  } else {
    const rule = query.data
    body = (
      <>
        {rule ? <RuleSummary rule={rule} /> : <p className="muted">Does not repeat.</p>}
        {planned ? (
          <form ref={formRef} className="stack" noValidate onSubmit={onSubmit}>
            <FormAlert messages={nonFieldErrors} />
            <div className={styles.row}>
              <FormField
                id="recurrence-interval"
                name="interval"
                label="Repeats"
                required={!rule}
                errors={errors.interval}
              >
                {(control) => (
                  <select
                    {...control}
                    className="input"
                    value={interval || rule?.interval || ''}
                    onChange={(event) => {
                      setSaved(false)
                      setChosenInterval(event.target.value as RecurrenceInterval)
                    }}
                  >
                    {rule ? null : <option value="">Choose…</option>}
                    {(Object.keys(INTERVAL_LABELS) as RecurrenceInterval[]).map((value) => (
                      <option key={value} value={value}>
                        {INTERVAL_LABELS[value]}
                      </option>
                    ))}
                  </select>
                )}
              </FormField>
              <button
                className="button button-primary"
                type="submit"
                disabled={mutation.isPending}
              >
                {rule ? 'Save recurrence' : 'Set recurrence'}
              </button>
            </div>
            {saved ? (
              <p className="muted" role="status">
                The recurrence is saved.
              </p>
            ) : null}
          </form>
        ) : (
          <p className="muted">
            {rule
              ? 'The rule is kept, but it can be changed only while the examination is planned.'
              : 'Recurrence can be set up only while the examination is planned.'}
          </p>
        )}
        {children?.(rule)}
      </>
    )
  }

  return (
    <section className={`card ${styles.section}`} aria-labelledby="recurrence-title">
      <h2 id="recurrence-title">Recurrence</h2>
      {body}
    </section>
  )
}
