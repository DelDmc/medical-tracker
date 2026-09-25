import { useState, type FormEvent } from 'react'
import { Link, useLocation, useNavigate } from 'react-router'

import { ApiError } from '../api/client'
import { useAuth } from '../auth/AuthContext'
import { NON_FIELD, type FieldErrors } from '../forms/errors'
import { FormAlert, FormField } from '../forms/FormField'
import { useFormErrors } from '../forms/useFormErrors'

type LocationState = { from?: string; sessionExpired?: boolean } | null

export const SESSION_EXPIRED_MESSAGE = 'Your session has expired. Please log in again.'

function validate(email: string, password: string): FieldErrors {
  const errors: FieldErrors = {}
  if (!email.trim()) errors.email = ['Enter your email address.']
  if (!password) errors.password = ['Enter your password.']
  return errors
}

export function LoginPage() {
  const { logIn } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const state = location.state as LocationState
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [pending, setPending] = useState(false)
  const { errors, nonFieldErrors, setErrors, setErrorsFromFailure, clearErrors, formRef } =
    useFormErrors()

  async function onSubmit(event: FormEvent) {
    event.preventDefault()
    const clientErrors = validate(email, password)
    if (Object.keys(clientErrors).length) {
      setErrors(clientErrors)
      return
    }
    clearErrors()
    setPending(true)
    try {
      await logIn(email.trim(), password)
      navigate(state?.from ?? '/dashboard', { replace: true })
    } catch (error) {
      setPending(false)
      setPassword('')
      if (error instanceof ApiError && error.status === 401) {
        // One generic message, whatever the reason (ADS-SEC-006-02).
        setErrors({ [NON_FIELD]: ['The email address or password is incorrect.'] })
      } else {
        setErrorsFromFailure(error)
      }
    }
  }

  return (
    <section className="page" aria-labelledby="login-title">
      <h1 id="login-title">Log in</h1>
      {state?.sessionExpired ? (
        <div className="alert alert-info" role="status">
          <p>{SESSION_EXPIRED_MESSAGE}</p>
        </div>
      ) : null}
      <form ref={formRef} className="card form" noValidate onSubmit={onSubmit}>
        <FormAlert messages={nonFieldErrors} />
        <FormField id="email" label="Email address" required errors={errors.email}>
          {(control) => (
            <input
              {...control}
              className="input"
              type="email"
              autoComplete="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
            />
          )}
        </FormField>
        <FormField id="password" label="Password" required errors={errors.password}>
          {(control) => (
            <input
              {...control}
              className="input"
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
            />
          )}
        </FormField>
        <div className="button-row">
          <button className="button button-primary" type="submit" disabled={pending}>
            {pending ? 'Logging in…' : 'Log in'}
          </button>
        </div>
        <p className="muted">
          New here? <Link to="/register">Create an account</Link>
        </p>
      </form>
    </section>
  )
}
