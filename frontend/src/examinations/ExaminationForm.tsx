import { useQuery } from '@tanstack/react-query'
import { useState, type FormEvent } from 'react'

import { CATEGORIES_QUERY_KEY, listCategories } from '../api/examinations'
import {
  EXAMINATION_STATUSES,
  type Examination,
  type ExaminationInput,
  type ExaminationStatus,
} from '../api/types'
import { useAccountTimezone } from '../auth/useAccountTimezone'
import { currentDateIn } from '../format/datetime'
import type { FieldErrors } from '../forms/errors'
import { FormAlert, FormField } from '../forms/FormField'
import { useFormErrors } from '../forms/useFormErrors'
import styles from './ExaminationForm.module.css'
import { requiredDateFor, STATUS_LABELS } from './presentation'

type Values = {
  title: string
  status: ExaminationStatus
  category_id: string
  scheduled_date: string
  scheduled_time: string
  completed_date: string
  medical_specialty: string
  location: string
  notes: string
}

function initialValues(examination?: Examination): Values {
  return {
    title: examination?.title ?? '',
    status: examination?.status ?? 'planned',
    category_id: examination?.category ? String(examination.category.id) : '',
    scheduled_date: examination?.scheduled_date ?? '',
    scheduled_time: examination?.scheduled_time?.slice(0, 5) ?? '',
    completed_date: examination?.completed_date ?? '',
    medical_specialty: examination?.medical_specialty ?? '',
    location: examination?.location ?? '',
    notes: examination?.notes ?? '',
  }
}

const orNull = (value: string) => (value.trim() ? value.trim() : null)

/** Entered values are submitted unchanged; an empty optional field is `null`. */
function toInput(values: Values, status: ExaminationStatus): ExaminationInput {
  return {
    title: values.title.trim(),
    status,
    category_id: values.category_id ? Number(values.category_id) : null,
    scheduled_date: values.scheduled_date || null,
    scheduled_time: values.scheduled_time || null,
    completed_date: values.completed_date || null,
    medical_specialty: orNull(values.medical_specialty),
    location: orNull(values.location),
    notes: orNull(values.notes),
  }
}

/**
 * Client-side checks for the chosen status (ADS-UX-005-01, ADS-UX-006-01): a draft
 * needs only a title; planned, cancelled and missed need a scheduled date; completed
 * needs a completion date. Category and time are never required.
 */
function validate(values: Values, status: ExaminationStatus): FieldErrors {
  const errors: FieldErrors = {}
  if (!values.title.trim()) errors.title = ['Enter a title.']
  const requiredDate = requiredDateFor(status)
  if (requiredDate === 'scheduled_date' && !values.scheduled_date) {
    errors.scheduled_date = ['Enter the scheduled date.']
  }
  if (requiredDate === 'completed_date' && !values.completed_date) {
    errors.completed_date = ['Enter the date the examination took place.']
  }
  return errors
}

type ExaminationFormProps = {
  examination?: Examination
  submitLabel: string
  /** Offer the explicit "Save as draft" action (new examinations). */
  allowDraftSave?: boolean
  onSubmit: (input: ExaminationInput) => Promise<unknown>
  onCancel?: () => void
}

export function ExaminationForm({
  examination,
  submitLabel,
  allowDraftSave = false,
  onSubmit,
  onCancel,
}: ExaminationFormProps) {
  const [values, setValues] = useState<Values>(() => initialValues(examination))
  const [pending, setPending] = useState(false)
  const { errors, nonFieldErrors, setErrors, setErrorsFromFailure, clearErrors, formRef } =
    useFormErrors()
  const timeZone = useAccountTimezone()
  const categories = useQuery({
    queryKey: CATEGORIES_QUERY_KEY,
    queryFn: listCategories,
    staleTime: Infinity,
  })

  const requiredDate = requiredDateFor(values.status)
  const update =
    (field: keyof Values) =>
    (event: { target: { value: string } }) => {
      const { value } = event.target
      setValues((current) => ({ ...current, [field]: value }))
    }

  async function save(status: ExaminationStatus) {
    const clientErrors = validate(values, status)
    if (Object.keys(clientErrors).length) {
      setErrors(clientErrors)
      return
    }
    clearErrors()
    setPending(true)
    try {
      await onSubmit(toInput(values, status))
    } catch (error) {
      setErrorsFromFailure(error)
      setPending(false)
    }
  }

  function onFormSubmit(event: FormEvent) {
    event.preventDefault()
    void save(values.status)
  }

  return (
    <form ref={formRef} className="card form" noValidate onSubmit={onFormSubmit}>
      <FormAlert messages={nonFieldErrors} />
      <div className={styles.grid}>
        <div className={styles.full}>
          <FormField id="title" label="Title" required errors={errors.title}>
            {(control) => (
              <input
                {...control}
                className="input"
                type="text"
                maxLength={200}
                value={values.title}
                onChange={update('title')}
              />
            )}
          </FormField>
        </div>
        <FormField
          id="status"
          label="Status"
          hint="Planned, cancelled and missed need a scheduled date; completed needs a completion date."
          errors={errors.status}
        >
          {(control) => (
            <select
              {...control}
              className="input"
              value={values.status}
              onChange={update('status')}
            >
              {EXAMINATION_STATUSES.map((status) => (
                <option key={status} value={status}>
                  {STATUS_LABELS[status]}
                </option>
              ))}
            </select>
          )}
        </FormField>
        <FormField id="category_id" label="Category" errors={errors.category_id}>
          {(control) => (
            <select
              {...control}
              className="input"
              value={values.category_id}
              onChange={update('category_id')}
            >
              <option value="">Uncategorized</option>
              {(categories.data ?? []).map((category) => (
                <option key={category.id} value={category.id}>
                  {category.name}
                </option>
              ))}
            </select>
          )}
        </FormField>
        <FormField
          id="scheduled_date"
          label="Scheduled date"
          required={requiredDate === 'scheduled_date'}
          errors={errors.scheduled_date}
        >
          {(control) => (
            <input
              {...control}
              className="input"
              type="date"
              value={values.scheduled_date}
              onChange={update('scheduled_date')}
            />
          )}
        </FormField>
        <FormField
          id="scheduled_time"
          label="Scheduled time"
          hint="Optional, in your local time."
          errors={errors.scheduled_time}
        >
          {(control) => (
            <input
              {...control}
              className="input"
              type="time"
              value={values.scheduled_time}
              onChange={update('scheduled_time')}
            />
          )}
        </FormField>
        <FormField
          id="completed_date"
          label="Completion date"
          required={requiredDate === 'completed_date'}
          hint="The day the examination took place; not later than today."
          errors={errors.completed_date}
        >
          {(control) => (
            <input
              {...control}
              className="input"
              type="date"
              max={currentDateIn(timeZone)}
              value={values.completed_date}
              onChange={update('completed_date')}
            />
          )}
        </FormField>
        <FormField
          id="medical_specialty"
          label="Medical specialty"
          errors={errors.medical_specialty}
        >
          {(control) => (
            <input
              {...control}
              className="input"
              type="text"
              maxLength={200}
              value={values.medical_specialty}
              onChange={update('medical_specialty')}
            />
          )}
        </FormField>
        <div className={styles.full}>
          <FormField id="location" label="Location" errors={errors.location}>
            {(control) => (
              <input
                {...control}
                className="input"
                type="text"
                maxLength={255}
                value={values.location}
                onChange={update('location')}
              />
            )}
          </FormField>
        </div>
        <div className={styles.full}>
          <FormField
            id="notes"
            label="Notes"
            hint="General organizational notes. Do not enter diagnoses or prescriptions."
            errors={errors.notes}
          >
            {(control) => (
              <textarea
                {...control}
                className="input"
                rows={4}
                value={values.notes}
                onChange={update('notes')}
              />
            )}
          </FormField>
        </div>
      </div>
      <div className="button-row">
        <button className="button button-primary" type="submit" disabled={pending}>
          {submitLabel}
        </button>
        {allowDraftSave ? (
          <button
            className="button button-secondary"
            type="button"
            disabled={pending}
            onClick={() => void save('draft')}
          >
            Save draft
          </button>
        ) : null}
        {onCancel ? (
          <button className="button button-secondary" type="button" onClick={onCancel}>
            Cancel
          </button>
        ) : null}
      </div>
    </form>
  )
}
