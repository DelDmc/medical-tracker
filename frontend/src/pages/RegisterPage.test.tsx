import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { http, HttpResponse } from 'msw'
import { describe, expect, it } from 'vitest'

import { expectFieldError } from '../test/assertions'
import { renderApp } from '../test/render'
import { server } from '../test/server'

const REGISTER_URL = 'http://api.test/api/v1/auth/register/'

function fields() {
  return {
    email: screen.getByLabelText(/email address/i),
    password: screen.getByLabelText(/^password/i),
    timezone: screen.getByLabelText(/timezone/i),
    submit: screen.getByRole('button', { name: /create account/i }),
  }
}

async function fillForm(
  user: ReturnType<typeof userEvent.setup>,
  {
    email = 'person@example.com',
    password = 'correct-horse-battery',
    timezone = 'Europe/Warsaw',
  } = {},
) {
  const form = fields()
  if (email) await user.type(form.email, email)
  if (password) await user.type(form.password, password)
  await user.selectOptions(form.timezone, timezone)
  return form
}

/** Count registration requests; a client-side rejection must not send one. */
function countRegistrations(
  response: () => Response = () => HttpResponse.json({}, { status: 500 }),
) {
  const calls: unknown[] = []
  server.use(
    http.post(REGISTER_URL, async ({ request }) => {
      calls.push(await request.json())
      return response()
    }),
  )
  return calls
}

describe('registration form', () => {
  it('TC-UX-002-01 — A missing email shows a field-level error', async () => {
    const user = userEvent.setup()
    const calls = countRegistrations()
    renderApp('/register')

    const form = await fillForm(user, { email: '' })
    await user.click(form.submit)

    expectFieldError(form.email, /enter your email address/i)
    expect(form.email).toHaveFocus()
    expect(calls).toHaveLength(0)
  })

  it('TC-UX-002-02 — A malformed email shows a field-level error', async () => {
    const user = userEvent.setup()
    const calls = countRegistrations()
    renderApp('/register')

    const form = await fillForm(user, { email: 'not-an-email' })
    await user.click(form.submit)

    expectFieldError(form.email, /valid email address/i)
    expect(calls).toHaveLength(0)
  })

  it('TC-UX-002-03 — A backend-rejected duplicate email shows a field-level error', async () => {
    const user = userEvent.setup()
    const calls = countRegistrations(() =>
      HttpResponse.json(
        { email: ['An account with this email address already exists.'] },
        { status: 400 },
      ),
    )
    renderApp('/register')

    const form = await fillForm(user)
    await user.click(form.submit)

    const email = await screen.findByLabelText(/email address/i, {
      selector: '[aria-invalid="true"]',
    })
    expectFieldError(email, /already exists/i)
    expect(calls).toHaveLength(1)
  })

  it('TC-UX-003-01 — A missing password shows a field-level error', async () => {
    const user = userEvent.setup()
    const calls = countRegistrations()
    renderApp('/register')

    const form = await fillForm(user, { password: '' })
    await user.click(form.submit)

    expectFieldError(form.password, /enter a password/i)
    expect(calls).toHaveLength(0)
  })

  it('TC-UX-003-02 — A password under eight characters shows a field-level error', async () => {
    const user = userEvent.setup()
    const calls = countRegistrations()
    renderApp('/register')

    const form = await fillForm(user, { password: 'short12' })
    await user.click(form.submit)

    expectFieldError(form.password, /at least 8 characters/i)
    expect(calls).toHaveLength(0)
  })

  it('TC-UX-004-01 — No timezone selection shows a field-level error', async () => {
    const user = userEvent.setup()
    const calls = countRegistrations()
    renderApp('/register')

    const form = await fillForm(user, { timezone: '' })
    expect(form.timezone).toHaveValue('')
    await user.click(form.submit)

    expectFieldError(form.timezone, /select your timezone/i)
    expect(calls).toHaveLength(0)
  })

  it('TC-UX-004-02 — A backend-rejected unsupported timezone shows a field-level error', async () => {
    const user = userEvent.setup()
    const calls = countRegistrations(() =>
      HttpResponse.json({ timezone: ['Select a supported timezone.'] }, { status: 400 }),
    )
    renderApp('/register')

    const form = await fillForm(user, { timezone: 'Europe/Warsaw' })
    await user.click(form.submit)

    const timezone = await screen.findByLabelText(/timezone/i, {
      selector: '[aria-invalid="true"]',
    })
    expectFieldError(timezone, /supported timezone/i)
    expect(calls).toEqual([
      { email: 'person@example.com', password: 'correct-horse-battery', timezone: 'Europe/Warsaw' },
    ])
  })
})
