import { useCallback, useEffect, useRef, useState } from 'react'

import { errorsFromFailure, hasErrors, NON_FIELD, type FieldErrors } from './errors'

/**
 * Shared form-error state. After errors are shown, focus moves to the first invalid
 * control so keyboard and screen-reader users land on the problem.
 */
export function useFormErrors() {
  const [errors, setErrorState] = useState<FieldErrors>({})
  const [focusRequest, setFocusRequest] = useState(0)
  const formRef = useRef<HTMLFormElement>(null)

  useEffect(() => {
    if (!focusRequest) return
    const form = formRef.current
    const target =
      form?.querySelector<HTMLElement>('[aria-invalid="true"]') ??
      form?.querySelector<HTMLElement>('[role="alert"]')
    target?.focus()
  }, [focusRequest])

  const setErrors = useCallback((next: FieldErrors) => {
    setErrorState(next)
    if (hasErrors(next)) setFocusRequest((count) => count + 1)
  }, [])

  const setErrorsFromFailure = useCallback(
    (error: unknown) => setErrors(errorsFromFailure(error)),
    [setErrors],
  )

  const clearErrors = useCallback(() => setErrorState({}), [])

  return {
    errors,
    nonFieldErrors: errors[NON_FIELD],
    setErrors,
    setErrorsFromFailure,
    clearErrors,
    formRef,
  }
}
