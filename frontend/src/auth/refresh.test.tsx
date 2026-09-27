import { act, screen, waitFor } from '@testing-library/react'
import { delay, http, HttpResponse } from 'msw'
import { describe, expect, it } from 'vitest'

import { apiRequest, SessionExpiredError } from '../api/authenticated'
import { API, CSRF_TOKEN, mockAuthApi } from '../test/authApi'
import { renderApp } from '../test/render'
import { server } from '../test/server'
import { session } from './session'

const EXPIRED_MESSAGE = /your session has expired/i

/** A protected endpoint that accepts only `validToken` and records every attempt. */
function protectedEndpoint(validToken: string) {
  const attempts: (string | null)[] = []
  server.use(
    http.get(`${API}/categories/`, ({ request }) => {
      const authorization = request.headers.get('authorization')
      attempts.push(authorization)
      if (authorization === `Bearer ${validToken}`) return HttpResponse.json([])
      return HttpResponse.json(
        { detail: 'The access token is invalid or expired.' },
        { status: 401 },
      )
    }),
  )
  return attempts
}

const rejectRefresh = () =>
  HttpResponse.json({ detail: 'Refresh token is invalid or expired.' }, { status: 401 })

/** Give any stray follow-up request (a retry loop) time to happen before counting. */
const settle = () => act(() => new Promise((resolve) => setTimeout(resolve, 50)))

describe('session refresh', () => {
  it('TC-FR-007-09 — Page reload restores a session with exactly one refresh request', async () => {
    const calls = mockAuthApi({ refreshedTokens: ['restored-access-token'] })
    // A reload: no in-memory token and no logout-intent marker.
    expect(session.getAccessToken()).toBeNull()

    renderApp('/dashboard')

    expect(await screen.findByRole('heading', { level: 1, name: 'Dashboard' })).toBeInTheDocument()
    await settle()
    expect(calls.refresh).toHaveLength(1)
    expect(calls.refresh[0].headers['x-csrftoken']).toBe(CSRF_TOKEN)
    expect(calls.refresh[0].credentials).toBe('include')
    expect(calls.refresh[0].body).toBe('')
    expect(session.getAccessToken()).toBe('restored-access-token')
  })

  it('TC-FR-008-01 — One failed protected request triggers exactly one refresh and one replay', async () => {
    const calls = mockAuthApi({ refreshedTokens: ['fresh-token'] })
    const attempts = protectedEndpoint('fresh-token')
    session.signIn('stale-token', { email: 'person@example.com' })

    await expect(apiRequest('/categories/')).resolves.toEqual([])

    expect(calls.refresh).toHaveLength(1)
    expect(attempts).toEqual(['Bearer stale-token', 'Bearer fresh-token'])
    expect(session.getAccessToken()).toBe('fresh-token')
  })

  it('TC-FR-008-02 — A failed active-session refresh shows a session-expired message', async () => {
    const calls = mockAuthApi({ refresh: rejectRefresh })
    const attempts = protectedEndpoint('never-valid')
    session.signIn('stale-token', { email: 'person@example.com' })
    renderApp('/dashboard')
    await screen.findByRole('heading', { level: 1, name: 'Dashboard' })

    await act(async () => {
      await expect(apiRequest('/categories/')).rejects.toBeInstanceOf(SessionExpiredError)
    })

    expect(await screen.findByRole('heading', { level: 1, name: 'Log in' })).toBeInTheDocument()
    expect(screen.getByText(EXPIRED_MESSAGE)).toBeInTheDocument()
    expect(session.getAccessToken()).toBeNull()
    expect(session.getSnapshot().user).toBeNull()
    await settle()
    expect(calls.refresh).toHaveLength(1)
    expect(attempts).toEqual(['Bearer stale-token'])
  })

  it('TC-FR-008-03 — A failed initialization refresh opens the login page without a session-expired message', async () => {
    const calls = mockAuthApi({ refresh: rejectRefresh })

    renderApp('/dashboard')

    expect(await screen.findByRole('heading', { level: 1, name: 'Log in' })).toBeInTheDocument()
    await settle()
    expect(calls.refresh).toHaveLength(1)
    expect(screen.queryByText(EXPIRED_MESSAGE)).not.toBeInTheDocument()
    expect(session.getAccessToken()).toBeNull()
  })

  it('TC-FR-008-04 — Concurrent authentication failures share a single refresh request', async () => {
    const calls = mockAuthApi()
    // Hold the refresh open so every failure arrives while it is in flight.
    server.use(
      http.post(`${API}/auth/refresh/`, async ({ request }) => {
        calls.refresh.push({
          method: request.method,
          url: request.url,
          headers: Object.fromEntries(request.headers.entries()),
          credentials: request.credentials,
          body: '',
        })
        await delay(30)
        return HttpResponse.json({ access_token: `token-${calls.refresh.length}` })
      }),
    )
    const attempts = protectedEndpoint('token-1')
    session.signIn('stale-token', { email: 'person@example.com' })

    const results = await Promise.all([
      apiRequest('/categories/'),
      apiRequest('/categories/'),
      apiRequest('/categories/'),
    ])

    expect(results).toEqual([[], [], []])
    expect(calls.refresh).toHaveLength(1)
    await waitFor(() => expect(attempts).toHaveLength(6))
    expect(attempts.filter((value) => value === 'Bearer stale-token')).toHaveLength(3)
    expect(attempts.filter((value) => value === 'Bearer token-1')).toHaveLength(3)
    expect(session.getAccessToken()).toBe('token-1')
  })
})
