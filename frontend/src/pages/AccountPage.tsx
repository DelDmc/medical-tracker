import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState, type FormEvent } from 'react'

import { getAccount, updateTimezone } from '../api/account'
import type { Account } from '../api/types'
import { session } from '../auth/session'
import { FormAlert, FormField } from '../forms/FormField'
import { TimeZoneSelect } from '../forms/TimeZoneSelect'
import { useFormErrors } from '../forms/useFormErrors'

export const ACCOUNT_QUERY_KEY = ['account']

function TimezoneForm({ account }: { account: Account }) {
  const queryClient = useQueryClient()
  const [timezone, setTimezone] = useState(account.timezone)
  const [saved, setSaved] = useState(false)
  const { errors, nonFieldErrors, setErrors, setErrorsFromFailure, clearErrors, formRef } =
    useFormErrors()

  const mutation = useMutation({
    mutationFn: updateTimezone,
    onSuccess: (updated) => {
      queryClient.setQueryData(ACCOUNT_QUERY_KEY, updated)
      // Presentation follows the new timezone immediately (user_flows.md §5 step 7).
      session.setUser({ id: updated.id, email: updated.email, timezone: updated.timezone })
      setSaved(true)
    },
    onError: setErrorsFromFailure,
  })

  function onSubmit(event: FormEvent) {
    event.preventDefault()
    setSaved(false)
    if (!timezone) {
      setErrors({ timezone: ['Select your timezone.'] })
      return
    }
    clearErrors()
    mutation.mutate(timezone)
  }

  return (
    <form ref={formRef} className="card form" noValidate onSubmit={onSubmit}>
      <h2>Timezone</h2>
      <p>
        Current timezone: <strong data-testid="current-timezone">{account.timezone}</strong>
      </p>
      <p className="muted">
        It decides what counts as today for upcoming, overdue and due items, and how times are
        shown. Dates you enter never shift.
      </p>
      <FormAlert messages={nonFieldErrors} />
      {saved ? (
        <div className="alert alert-success" role="status">
          <p>Timezone updated.</p>
        </div>
      ) : null}
      <FormField
        id="account-timezone"
        name="timezone"
        label="Timezone"
        required
        errors={errors.timezone}
      >
        {(control) => (
          <TimeZoneSelect
            {...control}
            value={timezone}
            onChange={(value) => {
              setSaved(false)
              setTimezone(value)
            }}
          />
        )}
      </FormField>
      <div className="button-row">
        <button className="button button-primary" type="submit" disabled={mutation.isPending}>
          {mutation.isPending ? 'Saving…' : 'Save timezone'}
        </button>
      </div>
    </form>
  )
}

export function AccountPage() {
  const query = useQuery({ queryKey: ACCOUNT_QUERY_KEY, queryFn: getAccount })

  return (
    <section className="page" aria-labelledby="account-title">
      <h1 id="account-title">Account settings</h1>
      {query.isPending ? (
        <p className="muted" role="status">
          Loading your account…
        </p>
      ) : query.isError ? (
        <div className="alert alert-error" role="alert">
          <p>Your account could not be loaded. Please try again.</p>
        </div>
      ) : (
        <>
          <div className="card">
            <p>
              Signed in as <strong>{query.data.email}</strong>
            </p>
          </div>
          <TimezoneForm key={query.data.timezone} account={query.data} />
        </>
      )}
    </section>
  )
}
