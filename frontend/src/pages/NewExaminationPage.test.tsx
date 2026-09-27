import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { http, HttpResponse } from 'msw'
import { describe, expect, it } from 'vitest'

import type { ExaminationInput } from '../api/types'
import { API } from '../test/authApi'
import { makeExamination, signIn } from '../test/factories'
import { renderApp } from '../test/render'
import { server } from '../test/server'

const EMPTY_OPTIONALS = {
  category_id: null,
  scheduled_date: null,
  scheduled_time: null,
  completed_date: null,
  medical_specialty: null,
  location: null,
  notes: null,
}

/** Accept creations, record their bodies, and list what was created. */
function mockExaminationApi() {
  const created: ExaminationInput[] = []
  server.use(
    http.post(`${API}/examinations/`, async ({ request }) => {
      const body = (await request.json()) as ExaminationInput
      created.push(body)
      return HttpResponse.json(
        makeExamination({ title: body.title, status: body.status, time_state: null }),
        { status: 201 },
      )
    }),
    http.get(`${API}/examinations/`, () =>
      HttpResponse.json(created.map((body) => makeExamination({ title: body.title }))),
    ),
  )
  return created
}

async function openForm() {
  signIn()
  renderApp('/examinations/new')
  return screen.findByRole('heading', { level: 1, name: 'Add examination' })
}

describe('examination form', () => {
  it('TC-UX-005-01 — A title-only draft can be saved', async () => {
    const user = userEvent.setup()
    const created = mockExaminationApi()
    await openForm()

    await user.type(screen.getByLabelText(/^title/i), 'Annual eye examination')
    await user.click(screen.getByRole('button', { name: 'Save draft' }))

    expect(await screen.findByText(/was saved as a draft/i)).toBeInTheDocument()
    expect(created).toEqual([
      { title: 'Annual eye examination', status: 'draft', ...EMPTY_OPTIONALS },
    ])
  })

  it('TC-UX-005-02 — A draft with additional optional information can be saved', async () => {
    const user = userEvent.setup()
    const created = mockExaminationApi()
    await openForm()

    await user.type(screen.getByLabelText(/^title/i), 'Annual eye examination')
    await user.selectOptions(screen.getByLabelText(/^category/i), 'Specialist consultation')
    await user.type(screen.getByLabelText(/^scheduled date/i), '2026-09-10')
    await user.type(screen.getByLabelText(/^location/i), 'City clinic')
    await user.type(screen.getByLabelText(/^medical specialty/i), 'Ophthalmology')
    await user.click(screen.getByRole('button', { name: 'Save draft' }))

    expect(await screen.findByText(/was saved as a draft/i)).toBeInTheDocument()
    expect(created).toEqual([
      {
        ...EMPTY_OPTIONALS,
        title: 'Annual eye examination',
        status: 'draft',
        category_id: 3,
        scheduled_date: '2026-09-10',
        location: 'City clinic',
        medical_specialty: 'Ophthalmology',
      },
    ])
  })

  it('TC-UX-006-01 — A planned examination can be saved with only title and scheduled date', async () => {
    const user = userEvent.setup()
    const created = mockExaminationApi()
    await openForm()

    expect(screen.getByLabelText(/^status/i)).toHaveValue('planned')
    expect(screen.getByLabelText(/^scheduled date/i)).toBeRequired()
    expect(screen.getByLabelText(/^category/i)).not.toBeRequired()
    expect(screen.getByLabelText(/^scheduled time/i)).not.toBeRequired()
    await user.type(screen.getByLabelText(/^title/i), 'Annual eye examination')
    await user.type(screen.getByLabelText(/^scheduled date/i), '2026-09-10')
    await user.click(screen.getByRole('button', { name: 'Save examination' }))

    expect(await screen.findByText(/“Annual eye examination” was saved\./)).toBeInTheDocument()
    expect(created).toEqual([
      {
        ...EMPTY_OPTIONALS,
        title: 'Annual eye examination',
        status: 'planned',
        scheduled_date: '2026-09-10',
      },
    ])
  })
})
