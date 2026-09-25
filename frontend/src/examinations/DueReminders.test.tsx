import { screen, within } from '@testing-library/react'
import { http, HttpResponse } from 'msw'
import { describe, expect, it } from 'vitest'

import type { Reminder } from '../api/types'
import { API } from '../test/authApi'
import { makeExamination, signIn } from '../test/factories'
import { renderApp } from '../test/render'
import { server } from '../test/server'

function reminder(overrides: Partial<Reminder>): Reminder {
  return {
    id: 1,
    examination: 1,
    offset_days: 7,
    due_date: '2000-01-01',
    is_active: true,
    created_at: '2026-07-21T04:10:00Z',
    updated_at: '2026-07-21T04:10:00Z',
    ...overrides,
  }
}

describe('due reminders', () => {
  it('TC-FR-037-01 — Only due, active reminders are displayed', async () => {
    const dueActive = makeExamination({ title: 'Due and active' })
    const futureActive = makeExamination({ title: 'Active but not yet due' })
    const dueInactive = makeExamination({ title: 'Due but turned off' })
    server.use(
      http.get(`${API}/reminders/`, () =>
        HttpResponse.json([
          reminder({ id: 1, examination: dueActive.id, due_date: '2000-01-01' }),
          reminder({ id: 2, examination: futureActive.id, due_date: '2999-12-31' }),
          reminder({ id: 3, examination: dueInactive.id, due_date: '2000-01-01', is_active: false }),
        ]),
      ),
      http.get(`${API}/examinations/`, () =>
        HttpResponse.json([dueActive, futureActive, dueInactive]),
      ),
    )
    signIn()
    renderApp('/dashboard')

    const area = await screen.findByRole('region', { name: 'Due reminders' })
    expect(await within(area).findByRole('link', { name: 'Due and active' })).toBeInTheDocument()
    expect(within(area).getByText('2000-01-01')).toBeInTheDocument()
    expect(within(area).getAllByRole('listitem')).toHaveLength(1)
    expect(within(area).queryByText('Active but not yet due')).not.toBeInTheDocument()
    expect(within(area).queryByText('Due but turned off')).not.toBeInTheDocument()
  })
})
