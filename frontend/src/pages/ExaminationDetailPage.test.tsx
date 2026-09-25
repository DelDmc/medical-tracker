import { screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { http, HttpResponse } from 'msw'
import { describe, expect, it } from 'vitest'

import { API } from '../test/authApi'
import { makeExamination, signIn } from '../test/factories'
import { renderApp } from '../test/render'
import { server } from '../test/server'

const record = makeExamination({ title: 'Annual dental checkup' })

/** Serve the record and count DELETE requests against it. */
function mockDetailApi() {
  const deletes: string[] = []
  server.use(
    http.get(`${API}/examinations/${record.id}/`, () => HttpResponse.json(record)),
    http.delete(`${API}/examinations/${record.id}/`, ({ request }) => {
      deletes.push(request.url)
      return new HttpResponse(null, { status: 204 })
    }),
    http.get(`${API}/examinations/`, () => HttpResponse.json([])),
  )
  return deletes
}

async function openDeleteDialog(user: ReturnType<typeof userEvent.setup>) {
  signIn()
  renderApp(`/examinations/${record.id}`)
  const trigger = await screen.findByRole('button', { name: 'Delete' })
  await user.click(trigger)
  const dialog = await screen.findByRole('alertdialog', { name: /delete this examination/i })
  return { trigger, dialog }
}

describe('delete confirmation', () => {
  it('TC-FR-024-01 — Cancelling the delete confirmation sends no delete request', async () => {
    const user = userEvent.setup()
    const deletes = mockDetailApi()
    const { trigger, dialog } = await openDeleteDialog(user)
    expect(dialog).toHaveAttribute('aria-modal', 'true')
    expect(within(dialog).getByRole('button', { name: 'Cancel' })).toHaveFocus()

    await user.click(within(dialog).getByRole('button', { name: 'Cancel' }))

    expect(screen.queryByRole('alertdialog')).not.toBeInTheDocument()
    expect(trigger).toHaveFocus()
    const heading = screen.getByRole('heading', { level: 1, name: 'Annual dental checkup' })
    expect(heading).toBeInTheDocument()
    expect(deletes).toHaveLength(0)
  })

  it('TC-FR-024-02 — Confirming the delete dialog sends exactly one delete request', async () => {
    const user = userEvent.setup()
    const deletes = mockDetailApi()
    const { dialog } = await openDeleteDialog(user)

    await user.click(within(dialog).getByRole('button', { name: /delete permanently/i }))

    expect(await screen.findByText(/“Annual dental checkup” was deleted/)).toBeInTheDocument()
    await waitFor(() => expect(deletes).toHaveLength(1))
    expect(deletes).toEqual([`${API}/examinations/${record.id}/`])
  })
})
