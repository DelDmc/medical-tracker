import { useMutation } from '@tanstack/react-query'
import { useState, type FormEvent } from 'react'
import { Link } from 'react-router'

import { register } from '../api/auth'
import type { Account } from '../api/types'
import type { FieldErrors } from '../forms/errors'
import { FormAlert, FormField } from '../forms/FormField'
import { TimeZoneSelect } from '../forms/TimeZoneSelect'
import { useFormErrors } from '../forms/useFormErrors'
import { detectedTimeZone } from '../lib/timezones'

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

type Values = { email: string; password: string; timezone: string }

/** Client-side checks before submission (ADS-UX-002-01, ADS-UX-003-01, ADS-UX-004-01). */
function validate(values: Values): FieldErrors {
  const errors: FieldErrors = {}
  const email = values.email.trim()
  if (!email) errors.email = ['Enter your email address.']
  else if (!EMAIL_PATTERN.test(email)) errors.email = ['Enter a valid email address.']
  if (!values.password) errors.password = ['Enter a password.']
  else if (values.password.length < 8) errors.password = ['Use at least 8 characters.']
  if (!values.timezone) errors.timezone = ['Select your timezone.']
  return errors
}

export function RegisterPage() {
  const [values, setValues] = useState<Values>(() => ({
    email: '',
    password: '',
    timezone: detectedTimeZone(),
  }))
  const [account, setAccount] = useState<Account | null>(null)
  const { errors, nonFieldErrors, setErrors, setErrorsFromFailure, clearErrors, formRef } =
    useFormErrors()

  const mutation = useMutation({
    mutationFn: register,
    onSuccess: (created) => {
      setValues((current) => ({ ...current, password: '' }))
      setAccount(created)
    },
    onError: setErrorsFromFailure,
  })

  const update = (field: keyof Values) => (value: string) =>
    setValues((current) => ({ ...current, [field]: value }))

  function onSubmit(event: FormEvent) {
    event.preventDefault()
    const clientErrors = validate(values)
    if (Object.keys(clientErrors).length) {
      setErrors(clientErrors)
      return
    }
    clearErrors()
    mutation.mutate({ ...values, email: values.email.trim() })
  }

  if (account) {
    return (
      <section className="page" aria-labelledby="register-title">
        <h1 id="register-title">Account created</h1>
        <div className="card stack" role="status">
          <p>
            Your account for <strong>{account.email}</strong> is ready. Log in to start tracking
            your examinations.
          </p>
          <p>
            <Link className="button button-primary" to="/login">
              Continue to log in
            </Link>
          </p>
        </div>
      </section>
    )
  }

  return (
    <section className="page" aria-labelledby="register-title">
      <h1 id="register-title">Create an account</h1>
      <form ref={formRef} className="card form" noValidate onSubmit={onSubmit}>
        <FormAlert messages={nonFieldErrors} />
        <FormField id="email" label="Email address" required errors={errors.email}>
          {(control) => (
            <input
              {...control}
              className="input"
              type="email"
              autoComplete="email"
              value={values.email}
              onChange={(event) => update('email')(event.target.value)}
            />
          )}
        </FormField>
        <FormField
          id="password"
          label="Password"
          required
          hint="At least 8 characters. Avoid common or all-number passwords."
          errors={errors.password}
        >
          {(control) => (
            <input
              {...control}
              className="input"
              type="password"
              autoComplete="new-password"
              value={values.password}
              onChange={(event) => update('password')(event.target.value)}
            />
          )}
        </FormField>
        <FormField
          id="timezone"
          label="Timezone"
          required
          hint="Used to decide what is upcoming or overdue for you."
          errors={errors.timezone}
        >
          {(control) => (
            <TimeZoneSelect {...control} value={values.timezone} onChange={update('timezone')} />
          )}
        </FormField>
        <div className="button-row">
          <button className="button button-primary" type="submit" disabled={mutation.isPending}>
            {mutation.isPending ? 'Creating account…' : 'Create account'}
          </button>
        </div>
        <p className="muted">
          Already registered? <Link to="/login">Log in</Link>
        </p>
      </form>
    </section>
  )
}
