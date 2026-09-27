import { screen, within } from '@testing-library/react'
import { http, HttpResponse } from 'msw'
import { describe, expect, it } from 'vitest'

import { API } from '../test/authApi'
import { makeExamination, signIn } from '../test/factories'
import { renderApp } from '../test/render'
import { emptyDashboard, server } from '../test/server'

describe('dashboard', () => {
  it('TC-FR-044-10 — Each dashboard section renders its own empty presentation independently', async () => {
    server.use(
      http.get(`${API}/dashboard/`, () =>
        HttpResponse.json({
          ...emptyDashboard(),
          upcoming: [makeExamination({ title: 'Dental checkup', time_state: 'upcoming' })],
          overdue: [],
          recently_completed: [
            makeExamination({
              title: 'Blood test',
              status: 'completed',
              completed_date: '2026-08-01',
              time_state: null,
            }),
          ],
          status_counts: { draft: 0, planned: 1, completed: 1, cancelled: 0, missed: 0 },
          overdue_count: 0,
        }),
      ),
    )
    signIn()
    renderApp('/dashboard')

    const overdue = await screen.findByRole('region', { name: 'Overdue' })
    const upcoming = screen.getByRole('region', { name: 'Upcoming' })
    const recent = screen.getByRole('region', { name: 'Recently completed' })

    expect(within(overdue).getByText('Nothing is overdue.')).toBeInTheDocument()
    expect(within(overdue).queryAllByRole('article')).toHaveLength(0)

    expect(within(upcoming).getByRole('link', { name: 'Dental checkup' })).toBeInTheDocument()
    expect(within(upcoming).queryByText(/nothing is coming up/i)).not.toBeInTheDocument()

    expect(within(recent).getByRole('link', { name: 'Blood test' })).toBeInTheDocument()
    expect(within(recent).queryByText(/nothing completed/i)).not.toBeInTheDocument()

    // Zero counts are shown as 0, not left out.
    expect(document.querySelector('[data-count="overdue"]')).toHaveTextContent('0')
    expect(document.querySelector('[data-count="cancelled"]')).toHaveTextContent('0')
    expect(document.querySelector('[data-count="uncategorized"]')).toHaveTextContent('0')
  })
})
