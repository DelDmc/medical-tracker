import { screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { http, HttpResponse } from 'msw'
import { describe, expect, it } from 'vitest'

import { apiRequest } from '../api/authenticated'
import { ACCESS_TOKEN, API, CSRF_TOKEN, logInThroughUi, mockAuthApi } from '../test/authApi'
import { renderApp } from '../test/render'
import { server } from '../test/server'
import { session } from './session'

function storedValues(storage: Storage) {
  return Array.from({ length: storage.length }, (_, index) => {
    const key = storage.key(index) as string
    return `${key}=${storage.getItem(key)}`
  })
}

describe('login', () => {
  it('TC-FR-005-06 — Frontend holds the access token only in memory', async () => {
    const user = userEvent.setup()
    const calls = mockAuthApi()
    renderApp('/login')

    await logInThroughUi(user)

    // The login request carried the in-memory CSRF token with browser credentials.
    expect(calls.login).toHaveLength(1)
    expect(calls.login[0].headers['x-csrftoken']).toBe(CSRF_TOKEN)
    expect(calls.login[0].credentials).toBe('include')

    // The token is in in-memory application state and nowhere persistent.
    expect(session.getAccessToken()).toBe(ACCESS_TOKEN)
    for (const storage of [window.localStorage, window.sessionStorage]) {
      expect(storedValues(storage).join('\n')).not.toContain(ACCESS_TOKEN)
    }
    expect(document.cookie).not.toContain(ACCESS_TOKEN)

    // Subsequent protected requests carry it as a bearer token.
    const authorization: (string | null)[] = []
    server.use(
      http.get(`${API}/categories/`, ({ request }) => {
        authorization.push(request.headers.get('authorization'))
        return HttpResponse.json([])
      }),
    )
    await apiRequest('/categories/')
    expect(authorization).toEqual([`Bearer ${ACCESS_TOKEN}`])
  })

  it('TC-PRV-003-03 — The informational page is reachable from authenticated navigation', async () => {
    const user = userEvent.setup()
    mockAuthApi()
    renderApp('/login')
    await logInThroughUi(user)

    const nav = screen.getByRole('navigation', { name: 'Primary' })
    expect(within(nav).getByRole('link', { name: 'Dashboard' })).toBeInTheDocument()
    await user.click(within(nav).getByRole('link', { name: 'About' }))

    expect(
      await screen.findByRole('heading', { level: 1, name: 'About Medical Tracker' }),
    ).toBeInTheDocument()
    expect(screen.getByText(/is an organizational tool/i)).toBeInTheDocument()
    expect(session.getAccessToken()).toBe(ACCESS_TOKEN)
  })
})
