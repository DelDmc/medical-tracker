import { screen } from '@testing-library/react'
import type userEvent from '@testing-library/user-event'
import { http, HttpResponse } from 'msw'

import { server } from './server'

export const API = 'http://api.test/api/v1'
export const CSRF_TOKEN = 'csrf-token-from-bootstrap'
export const ACCESS_TOKEN = 'access-token-from-login'

export type RecordedRequest = {
  method: string
  url: string
  headers: Record<string, string>
  credentials: RequestCredentials
  body: string
}

async function record(request: Request): Promise<RecordedRequest> {
  return {
    method: request.method,
    url: request.url,
    headers: Object.fromEntries(request.headers.entries()),
    credentials: request.credentials,
    body: await request.clone().text(),
  }
}

/**
 * Fake the auth endpoints and record every call. `refresh` / `logout` default to
 * success; pass a response factory to make them fail.
 */
export function mockAuthApi(
  options: {
    accessToken?: string
    refreshedTokens?: string[]
    refresh?: () => Response | Promise<Response>
    logout?: () => Response | Promise<Response>
  } = {},
) {
  const calls = {
    csrf: [] as RecordedRequest[],
    login: [] as RecordedRequest[],
    refresh: [] as RecordedRequest[],
    logout: [] as RecordedRequest[],
  }
  const refreshed = [...(options.refreshedTokens ?? ['access-token-from-refresh'])]
  server.use(
    http.get(`${API}/auth/csrf/`, async ({ request }) => {
      calls.csrf.push(await record(request))
      return HttpResponse.json({ csrf_token: CSRF_TOKEN })
    }),
    http.post(`${API}/auth/login/`, async ({ request }) => {
      calls.login.push(await record(request))
      return HttpResponse.json({ access_token: options.accessToken ?? ACCESS_TOKEN })
    }),
    http.post(`${API}/auth/refresh/`, async ({ request }) => {
      calls.refresh.push(await record(request))
      if (options.refresh) return options.refresh()
      return HttpResponse.json({ access_token: refreshed.shift() ?? 'another-refreshed-token' })
    }),
    http.post(`${API}/auth/logout/`, async ({ request }) => {
      calls.logout.push(await record(request))
      if (options.logout) return options.logout()
      return new HttpResponse(null, { status: 204 })
    }),
  )
  return calls
}

/** Log in through the login page, as a user would, and wait for the dashboard. */
export async function logInThroughUi(
  user: ReturnType<typeof userEvent.setup>,
  email = 'person@example.com',
  password = 'correct-horse-battery',
) {
  await user.type(await screen.findByLabelText(/email address/i), email)
  await user.type(screen.getByLabelText(/^password/i), password)
  await user.click(screen.getByRole('button', { name: /log in/i }))
  await screen.findByRole('heading', { level: 1, name: 'Dashboard' })
}
