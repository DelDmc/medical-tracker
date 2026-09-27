import { expect } from 'vitest'

/**
 * Assert that `control` shows an error matching `message` immediately adjacent to it:
 * in the same field wrapper, and programmatically associated through
 * `aria-describedby` with `aria-invalid` set (ADS-UX-002-01).
 */
export function expectFieldError(control: HTMLElement, message: RegExp | string) {
  expect(control).toHaveAttribute('aria-invalid', 'true')
  const describedBy = control.getAttribute('aria-describedby') ?? ''
  const error = describedBy
    .split(/\s+/)
    .map((id) => document.getElementById(id))
    .find((element) => element?.classList.contains('field-error'))
  expect(error, 'error element referenced by aria-describedby').toBeTruthy()
  expect(error).toHaveTextContent(message)
  expect(control).toHaveAccessibleDescription(expect.stringMatching(message))
  const field = control.closest('.field')
  expect(field).toContainElement(error as HTMLElement)
}
