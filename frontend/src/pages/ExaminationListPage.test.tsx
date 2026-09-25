import { render, screen } from '@testing-library/react'
import { delay, http, HttpResponse } from 'msw'
import { MemoryRouter } from 'react-router'
import { describe, expect, it } from 'vitest'

import { ExaminationItem } from '../examinations/ExaminationItem'
import { API } from '../test/authApi'
import { makeExamination, signIn } from '../test/factories'
import { renderApp } from '../test/render'
import { server } from '../test/server'

const STATES = ['loading', 'empty', 'populated', 'error']

/** The one rendered list state, asserting that no other state is present. */
function expectOnlyState(container: HTMLElement, expected: string) {
  const rendered = Array.from(container.querySelectorAll('[data-state]')).map((element) =>
    element.getAttribute('data-state'),
  )
  expect(rendered).toEqual([expected])
  for (const other of STATES.filter((state) => state !== expected)) {
    expect(container.querySelector(`[data-state="${other}"]`)).toBeNull()
  }
}

function respondWith(resolver: Parameters<typeof http.get>[1]) {
  server.use(http.get(`${API}/examinations/`, resolver))
}

describe('examination list', () => {
  it('TC-FR-020-01 — The examination list shows a loading state while the request is pending', async () => {
    respondWith(async () => {
      await delay('infinite')
      return HttpResponse.json([])
    })
    signIn()
    const { container } = renderApp('/examinations')

    expect(await screen.findByText(/loading examinations/i)).toBeInTheDocument()
    expectOnlyState(container, 'loading')
  })

  it('TC-FR-020-02 — The examination list shows an empty state when no records exist', async () => {
    respondWith(() => HttpResponse.json([]))
    signIn()
    const { container } = renderApp('/examinations')

    expect(await screen.findByText(/you have no examinations yet/i)).toBeInTheDocument()
    expectOnlyState(container, 'empty')
  })

  it('TC-FR-020-03 — The examination list shows a populated state with returned records', async () => {
    const records = [
      makeExamination({ title: 'Annual dental checkup' }),
      makeExamination({ title: 'Eye exam', status: 'draft', time_state: null }),
    ]
    respondWith(() => HttpResponse.json(records))
    signIn()
    const { container } = renderApp('/examinations')

    expect(await screen.findByRole('link', { name: 'Annual dental checkup' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Eye exam' })).toBeInTheDocument()
    expect(screen.getAllByRole('article')).toHaveLength(2)
    expectOnlyState(container, 'populated')
  })

  it('TC-FR-020-04 — The examination list shows an error state when the request fails', async () => {
    respondWith(() => HttpResponse.json({ detail: 'A server error occurred.' }, { status: 500 }))
    signIn()
    const { container } = renderApp('/examinations')

    expect(await screen.findByRole('alert')).toHaveTextContent(/could not be loaded/i)
    expectOnlyState(container, 'error')
  })

  it('TC-FR-027-01 — An examination without a category displays Uncategorized', () => {
    render(
      <MemoryRouter>
        <ExaminationItem examination={makeExamination({ title: 'Blood test', category: null })} />
      </MemoryRouter>,
    )

    const record = screen.getByRole('article', { name: 'Blood test' })
    expect(record).toHaveTextContent('Uncategorized')
  })
})
