import { ApiError, NetworkError } from '../api/client'

/** Field name → messages, the api_contract.md §3.4 validation shape. */
export type FieldErrors = Record<string, string[]>

export const NON_FIELD = 'non_field_errors'

export function hasErrors(errors: FieldErrors) {
  return Object.values(errors).some((messages) => messages.length > 0)
}

/**
 * Turn a failed request into form errors: a 400 body maps onto its fields, anything
 * else becomes one form-level message.
 */
export function errorsFromFailure(error: unknown): FieldErrors {
  if (error instanceof ApiError && error.status === 400 && isRecord(error.body)) {
    const errors: FieldErrors = {}
    for (const [field, value] of Object.entries(error.body)) {
      if (Array.isArray(value)) errors[field] = value.map(String)
      else if (typeof value === 'string') errors[field] = [value]
    }
    if (hasErrors(errors)) return errors
  }
  if (error instanceof NetworkError) {
    return { [NON_FIELD]: ['The server could not be reached. Check your connection and try again.'] }
  }
  if (error instanceof ApiError && isRecord(error.body) && typeof error.body.detail === 'string') {
    return { [NON_FIELD]: [error.body.detail] }
  }
  return { [NON_FIELD]: ['Something went wrong. Please try again.'] }
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}
