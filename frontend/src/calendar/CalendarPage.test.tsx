import { render, screen, within } from '@testing-library/react'
import { http, HttpResponse } from 'msw'
import { MemoryRouter } from 'react-router'
import { describe, expect, it } from 'vitest'

import type { CalendarEntry as Entry, CalendarState } from '../api/types'
import { API } from '../test/authApi'
import { signIn } from '../test/factories'
import { renderApp } from '../test/render'
import { server } from '../test/server'
import { CALENDAR_STATE_LABELS, CALENDAR_STATES, CalendarEntry } from './CalendarEntry'

let nextId = 500

function entry(
  state: CalendarState,
  calendarDate: string,
  overrides: Partial<Entry['examination']> = {},
): Entry {
  nextId += 1
  const status = state === 'overdue' ? 'planned' : state
  return {
    calendar_date: calendarDate,
    state,
    examination: {
      id: nextId,
      title: `A ${state} examination`,
      category: null,
      scheduled_date: calendarDate,
      scheduled_time: null,
      completed_date: state === 'completed' ? calendarDate : null,
      status,
      time_state: state === 'overdue' ? 'overdue' : state === 'planned' ? 'upcoming' : null,
      ...overrides,
    },
  }
}

/** Serve `entries` for August 2026 and check the request asks for that month. */
function mockAugust(entries: Entry[]) {
  const requested: string[] = []
  server.use(
    http.get(`${API}/calendar/`, ({ request }) => {
      requested.push(new URL(request.url).search)
      return HttpResponse.json(entries)
    }),
  )
  return requested
}

async function renderAugust() {
  signIn()
  const view = renderApp('/calendar?month=2026-08')
  await screen.findByRole('heading', { level: 2, name: 'August 2026' })
  await screen.findByRole('list', { name: 'Examinations in August 2026' })
  return view
}

function dayCell(container: HTMLElement, date: string) {
  const cell = container.querySelector<HTMLElement>(`[data-date="${date}"]`)
  expect(cell, `calendar cell for ${date}`).not.toBeNull()
  return cell!
}

async function expectPlacedOn(container: HTMLElement, title: string, date: string) {
  const cell = within(dayCell(container, date))
  expect(cell.getByRole('link', { name: new RegExp(title) })).toBeInTheDocument()
  const cells = container.querySelectorAll('[data-date]')
  const holding = Array.from(cells).filter((cell) => within(cell as HTMLElement).queryByText(title))
  expect(holding.map((cell) => cell.getAttribute('data-date'))).toEqual([date])
}

describe('monthly calendar placement', () => {
  it('TC-FR-042-01 — A planned record is placed on its scheduled date', async () => {
    const requested = mockAugust([entry('planned', '2026-08-15', { title: 'Dentist' })])
    const { container } = await renderAugust()

    await expectPlacedOn(container, 'Dentist', '2026-08-15')
    expect(requested).toEqual(['?start_date=2026-08-01&end_date=2026-08-31'])
  })

  it('TC-FR-042-02 — A cancelled record is placed on its scheduled date', async () => {
    mockAugust([entry('cancelled', '2026-08-03', { title: 'Cancelled scan' })])
    const { container } = await renderAugust()

    await expectPlacedOn(container, 'Cancelled scan', '2026-08-03')
  })

  it('TC-FR-042-03 — A missed record is placed on its scheduled date', async () => {
    mockAugust([entry('missed', '2026-08-31', { title: 'Missed vaccine' })])
    const { container } = await renderAugust()

    await expectPlacedOn(container, 'Missed vaccine', '2026-08-31')
  })

  it('TC-FR-042-04 — Completed records are placed on their completion date', async () => {
    mockAugust([
      entry('completed', '2026-08-20', {
        title: 'Blood test',
        scheduled_date: '2026-08-05',
        completed_date: '2026-08-20',
      }),
    ])
    const { container } = await renderAugust()

    await expectPlacedOn(container, 'Blood test', '2026-08-20')
    expect(within(dayCell(container, '2026-08-05')).queryByText('Blood test')).toBeNull()
  })
})

/** Render one entry per state; return each state's label text and indicator shape. */
function renderAllStates() {
  const rendered = render(
    <MemoryRouter>
      <ul>
        {CALENDAR_STATES.map((state) => (
          <li key={state}>
            <CalendarEntry entry={entry(state, '2026-08-10')} />
          </li>
        ))}
      </ul>
    </MemoryRouter>,
  )
  const byState = new Map<CalendarState, { label: string; indicator: string; name: string }>()
  for (const link of rendered.getAllByRole('link')) {
    const state = link.getAttribute('data-state') as CalendarState
    byState.set(state, {
      label: link.querySelector('span')!.textContent ?? '',
      indicator: link.querySelector('svg')?.getAttribute('data-indicator') ?? '',
      name: link.textContent ?? '',
    })
  }
  return byState
}

function expectDistinctIndicator(state: CalendarState) {
  const byState = renderAllStates()
  const own = byState.get(state)!
  expect(own.label).toBe(CALENDAR_STATE_LABELS[state])
  expect(own.name).toContain(CALENDAR_STATE_LABELS[state])
  expect(own.indicator).not.toBe('')
  for (const [other, rendered] of byState) {
    if (other === state) continue
    expect(rendered.indicator, `${state} vs ${other} indicator`).not.toBe(own.indicator)
    expect(rendered.label, `${state} vs ${other} label`).not.toBe(own.label)
  }
}

describe('calendar state indicators', () => {
  it('TC-FR-043-01 — A planned examination renders a distinct label and indicator', () => {
    expectDistinctIndicator('planned')
  })

  it('TC-FR-043-02 — A completed examination renders a distinct label and indicator', () => {
    expectDistinctIndicator('completed')
  })

  it('TC-FR-043-03 — A cancelled examination renders a distinct label and indicator', () => {
    expectDistinctIndicator('cancelled')
  })

  it('TC-FR-043-04 — A missed examination renders a distinct label and indicator', () => {
    expectDistinctIndicator('missed')
  })

  it('TC-FR-043-05 — An overdue examination renders a distinct label and indicator', () => {
    expectDistinctIndicator('overdue')
  })
})
