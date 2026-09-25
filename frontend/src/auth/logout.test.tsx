import { act, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { http, HttpResponse } from 'msw'
import { describe, expect, it, vi } from 'vitest'

import { apiRequest } from '../api/authenticated'
import { ACCESS_TOKEN, API, CSRF_TOKEN, logInThroughUi, mockAuthApi } from '../test/authApi'
import { renderApp } from '../test/render'
import { server } from '../test/server'
import { LOGOUT_INTENT_KEY } from './logoutIntent'
import { resetRestoreState } from './restore'
import { session } from './session'

async function logInAndOut(user: ReturnType<typeof userEvent.setup>) {
  renderApp('/login')
  await logInThroughUi(user)
  const nav = screen.getByRole('navigation', { name: 'Primary' })
  await user.click(within(nav).getByRole('button', { name: 'Log out' }))
}

async function expectLoginPage() {
  expect(await screen.findByRole('heading', { level: 1, name: 'Log in' })).toBeInTheDocument()
  expect(screen.queryByText(/your session has expired/i)).not.toBeInTheDocument()
}

/** Tear the application down and start it again, as a browser reload would. */
function reload(path: string) {
  // Memory is lost on reload; localStorage and the backend's cookies are not.
  session.reset()
  resetRestoreState()
  document.body.innerHTML = ''
  return renderApp(path)
}

describe('logout', () => {
  it('TC-FR-006-08 — Selecting logout clears local session state before the request is sent', async () => {
    const user = userEvent.setup()
    const stateWhenSent: unknown[] = []
    mockAuthApi()
    server.use(
      http.post(`${API}/auth/logout/`, () => {
        stateWhenSent.push({
          accessToken: session.getAccessToken(),
          user: session.getSnapshot().user,
        })
        return new HttpResponse(null, { status: 204 })
      }),
    )

    await logInAndOut(user)
    await expectLoginPage()

    expect(stateWhenSent).toEqual([{ accessToken: null, user: null }])
  })

  it('TC-FR-006-09 — Logout writes a logout-intent marker that suppresses session restoration', async () => {
    const user = userEvent.setup()
    const calls = mockAuthApi()
    await logInAndOut(user)
    await expectLoginPage()
    expect(window.localStorage.getItem(LOGOUT_INTENT_KEY)).toBe('true')

    reload('/dashboard')

    await expectLoginPage()
    await act(() => new Promise((resolve) => setTimeout(resolve, 50)))
    expect(calls.refresh).toHaveLength(0)
  })

  it('TC-FR-006-10 — A later successful login removes the logout-intent marker', async () => {
    const user = userEvent.setup()
    mockAuthApi()
    window.localStorage.setItem(LOGOUT_INTENT_KEY, 'true')
    renderApp('/login')

    await logInThroughUi(user)

    expect(window.localStorage.getItem(LOGOUT_INTENT_KEY)).toBeNull()
  })

  it('TC-FR-006-11 — Logout navigates to the login page after a successful response', async () => {
    const user = userEvent.setup()
    const calls = mockAuthApi()

    await logInAndOut(user)

    await expectLoginPage()
    expect(calls.logout).toHaveLength(1)
  })

  it('TC-FR-006-12 — Logout navigates to the login page after a failed response', async () => {
    const user = userEvent.setup()
    const calls = mockAuthApi({
      logout: () => HttpResponse.json({ detail: 'A server error occurred.' }, { status: 500 }),
    })

    await logInAndOut(user)

    await expectLoginPage()
    expect(calls.logout).toHaveLength(1)
    expect(session.getAccessToken()).toBeNull()
  })

  it('TC-FR-006-13 — Logout navigates to the login page when the backend is unreachable', async () => {
    const user = userEvent.setup()
    const calls = mockAuthApi({ logout: () => HttpResponse.error() })

    await logInAndOut(user)

    await expectLoginPage()
    expect(calls.logout).toHaveLength(1)
    expect(session.getAccessToken()).toBeNull()
  })
})

describe('CSRF token handling', () => {
  it('TC-SEC-005-11 — The frontend holds the CSRF token in memory and never reads the cookie directly', async () => {
    const user = userEvent.setup()
    // Record every read of document.cookie made from application code. (MSW's
    // request parsing reads it too, to emulate the browser; those reads are ignored.)
    const cookie = Object.getOwnPropertyDescriptor(Document.prototype, 'cookie')!
    const applicationReads: string[] = []
    vi.spyOn(Document.prototype, 'cookie', 'get').mockImplementation(function (this: Document) {
      const frames = (new Error().stack ?? '').split('\n').slice(2)
      const appFrame = frames.find(
        (frame) =>
          frame.includes('/frontend/src/') &&
          !frame.includes('/src/test/') &&
          !/\.test\.tsx?/.test(frame),
      )
      if (appFrame) applicationReads.push(appFrame.trim())
      return cookie.get!.call(this)
    })
    const calls = mockAuthApi({ refreshedTokens: ['refreshed-token'] })
    server.use(
      http.get(`${API}/categories/`, ({ request }) =>
        request.headers.get('authorization') === 'Bearer refreshed-token'
          ? HttpResponse.json([])
          : HttpResponse.json({ detail: 'expired' }, { status: 401 }),
      ),
    )

    renderApp('/login')
    await logInThroughUi(user) // login
    expect(session.getAccessToken()).toBe(ACCESS_TOKEN)
    await act(() => apiRequest('/categories/')) // refresh after a 401
    const nav = screen.getByRole('navigation', { name: 'Primary' })
    await user.click(within(nav).getByRole('button', { name: 'Log out' })) // logout
    await expectLoginPage()

    expect(calls.csrf).toHaveLength(1)
    for (const call of [calls.login[0], calls.refresh[0], calls.logout[0]]) {
      expect(call.headers['x-csrftoken']).toBe(CSRF_TOKEN)
      expect(call.credentials).toBe('include')
    }
    expect(applicationReads).toEqual([])

    // And no application source reads cookies at all.
    const sources = import.meta.glob(
      ['/src/**/*.{ts,tsx}', '!/src/**/*.test.{ts,tsx}', '!/src/test/**'],
      { query: '?raw', import: 'default', eager: true },
    ) as Record<string, string>
    expect(Object.keys(sources).length).toBeGreaterThan(10)
    for (const [file, source] of Object.entries(sources)) {
      expect(source, file).not.toMatch(/document\s*\.\s*cookie/)
      expect(source, file).not.toMatch(/csrftoken/) // Django's CSRF cookie name
    }
  })
})
