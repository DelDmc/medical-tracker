import type { ReactNode } from 'react'

/** Props every form control receives so its label, hint and error are associated. */
export type ControlProps = {
  id: string
  name: string
  required?: boolean
  'aria-invalid'?: true
  'aria-describedby'?: string
}

type FormFieldProps = {
  id: string
  name?: string
  label: string
  required?: boolean
  hint?: ReactNode
  errors?: string[]
  children: (control: ControlProps) => ReactNode
}

/**
 * A labelled control with its error rendered immediately adjacent and exposed through
 * `aria-describedby` / `aria-invalid` (ADS-UX-002-01). Client-side and API errors
 * both arrive through `errors`, so they render identically. Every form uses this.
 */
export function FormField({ id, name, label, required, hint, errors, children }: FormFieldProps) {
  const hintId = hint ? `${id}-hint` : undefined
  const errorId = errors?.length ? `${id}-error` : undefined
  const describedBy = [hintId, errorId].filter(Boolean).join(' ') || undefined

  return (
    <div className="field">
      <label className="field-label" htmlFor={id}>
        {label}
        {required ? (
          <>
            {' '}
            <span className="required-marker" aria-hidden="true">
              *
            </span>
            <span className="visually-hidden">(required)</span>
          </>
        ) : null}
      </label>
      {hint ? (
        <span id={hintId} className="field-hint">
          {hint}
        </span>
      ) : null}
      {children({
        id,
        name: name ?? id,
        required: required || undefined,
        'aria-invalid': errorId ? true : undefined,
        'aria-describedby': describedBy,
      })}
      <FieldError id={errorId} messages={errors} />
    </div>
  )
}

export function FieldError({ id, messages }: { id?: string; messages?: string[] }) {
  if (!id || !messages?.length) return null
  return (
    <p id={id} className="field-error">
      {messages.join(' ')}
    </p>
  )
}

/** Errors that belong to the whole form rather than one field (`non_field_errors`). */
export function FormAlert({ messages }: { messages?: string[] }) {
  if (!messages?.length) return null
  return (
    <div className="alert alert-error" role="alert">
      {messages.map((message) => (
        <p key={message}>{message}</p>
      ))}
    </div>
  )
}
