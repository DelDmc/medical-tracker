import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState, type FormEvent } from 'react'

import { createReminder, getReminder, reminderKeys, updateReminder } from '../api/reminders'
import type { Examination, Reminder } from '../api/types'
import { CalendarDate } from '../format/DateTime'
import { FormAlert, FormField } from '../forms/FormField'
import { useFormErrors } from '../forms/useFormErrors'
import styles from './SettingsSection.module.css'

const WHOLE_NUMBER = /^\d+$/

function parseOffset(value: string): number | null {
  const trimmed = value.trim()
  if (!WHOLE_NUMBER.test(trimmed)) return null
  const days = Number(trimmed)
  return days > 0 ? days : null
}

function submitLabel(reminder: Reminder | null) {
  if (!reminder) return 'Turn on reminder'
  return reminder.is_active ? 'Save reminder' : 'Turn reminder back on'
}

function ReminderStatus({ reminder }: { reminder: Reminder }) {
  return (
    <p className={styles.status}>
      <span className={`${styles.pill} ${reminder.is_active ? styles.on : styles.off}`}>
        {reminder.is_active ? 'On' : 'Off'}
      </span>
      <span>
        {reminder.offset_days} {reminder.offset_days === 1 ? 'day' : 'days'} before
        {' · '}
        {reminder.due_date ? (
          <>
            due <CalendarDate value={reminder.due_date} />
          </>
        ) : (
          'no due date until the examination has a scheduled date'
        )}
      </span>
    </p>
  )
}

/**
 * The in-application reminder of one examination (user_flows.md §16). Setting one up,
 * changing its offset and turning it back on are offered only while the examination
 * is planned; turning it off is always available — the same rule the backend enforces
 * (ADS-FR-035-02), whose messages are shown as they arrive.
 */
export function ReminderSection({ examination }: { examination: Examination }) {
  const queryClient = useQueryClient()
  const key = reminderKeys.forExamination(examination.id)
  const query = useQuery({ queryKey: key, queryFn: () => getReminder(examination.id) })
  const [offset, setOffset] = useState('')
  const [notice, setNotice] = useState<string | null>(null)
  const { errors, nonFieldErrors, setErrors, setErrorsFromFailure, clearErrors, formRef } =
    useFormErrors()
  const planned = examination.status === 'planned'

  const mutation = useMutation({
    mutationFn: async (action: { kind: 'create' | 'update' | 'disable'; days?: number }) => {
      if (action.kind === 'create') return createReminder(examination.id, action.days!)
      if (action.kind === 'disable') return updateReminder(examination.id, { is_active: false })
      return updateReminder(examination.id, { offset_days: action.days!, is_active: true })
    },
    onSuccess: (reminder, action) => {
      queryClient.setQueryData(key, reminder)
      void queryClient.invalidateQueries({ queryKey: reminderKeys.due })
      setOffset('')
      setNotice(action.kind === 'disable' ? 'The reminder is off.' : 'The reminder is saved.')
    },
    onError: setErrorsFromFailure,
  })

  function submitOffset(event: FormEvent, reminder: Reminder | null) {
    event.preventDefault()
    setNotice(null)
    const text = offset.trim() || (reminder ? String(reminder.offset_days) : '')
    const days = parseOffset(text)
    if (days === null) {
      setErrors({ offset_days: ['Enter a whole number of days greater than zero.'] })
      return
    }
    clearErrors()
    mutation.mutate({ kind: reminder ? 'update' : 'create', days })
  }

  function disable() {
    setNotice(null)
    clearErrors()
    mutation.mutate({ kind: 'disable' })
  }

  let body
  if (query.isPending) {
    body = (
      <p className="muted" role="status">
        Loading reminder…
      </p>
    )
  } else if (query.isError) {
    body = (
      <p className="alert alert-error" role="alert">
        The reminder could not be loaded.
      </p>
    )
  } else {
    const reminder = query.data
    body = (
      <>
        {reminder ? (
          <ReminderStatus reminder={reminder} />
        ) : (
          <p className="muted">No reminder set.</p>
        )}
        {planned ? (
          <form
            ref={formRef}
            className="stack"
            noValidate
            onSubmit={(event) => submitOffset(event, reminder)}
          >
            <FormAlert messages={nonFieldErrors} />
            <div className={styles.row}>
              <FormField
                id="reminder-offset"
                name="offset_days"
                label="Days before"
                required={!reminder}
                errors={errors.offset_days}
              >
                {(control) => (
                  <input
                    {...control}
                    className="input"
                    type="number"
                    inputMode="numeric"
                    min={1}
                    step={1}
                    placeholder={reminder ? String(reminder.offset_days) : '7'}
                    value={offset}
                    onChange={(event) => setOffset(event.target.value)}
                  />
                )}
              </FormField>
              <button className="button button-primary" type="submit" disabled={mutation.isPending}>
                {submitLabel(reminder)}
              </button>
              {reminder?.is_active ? (
                <button
                  className="button button-secondary"
                  type="button"
                  onClick={disable}
                  disabled={mutation.isPending}
                >
                  Turn off
                </button>
              ) : null}
            </div>
          </form>
        ) : (
          <div className="stack">
            <FormAlert messages={nonFieldErrors} />
            <p className="muted">
              Reminders can be set up or changed only while the examination is planned.
            </p>
            {reminder?.is_active ? (
              <div className="button-row">
                <button
                  className="button button-secondary"
                  type="button"
                  onClick={disable}
                  disabled={mutation.isPending}
                >
                  Turn off reminder
                </button>
              </div>
            ) : null}
          </div>
        )}
        {notice ? (
          <p className="muted" role="status">
            {notice}
          </p>
        ) : null}
      </>
    )
  }

  return (
    <section className={`card ${styles.section}`} aria-labelledby="reminder-title">
      <h2 id="reminder-title">Reminder</h2>
      {body}
    </section>
  )
}
