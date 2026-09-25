import { session } from '../auth/session'
import { ApiError, request } from './client'
import type { Account, RegistrationRequest } from './types'

/** `POST /api/v1/auth/register/` — needs no bearer token, credentials, or CSRF token. */
export function register(data: RegistrationRequest) {
  return request<Account>('/auth/register/', { method: 'POST', body: data })
}

/**
 * The CSRF token for login, refresh and logout. It comes from the bootstrap response
 * body and is held in memory only; the HttpOnly CSRF cookie is never read
 * (ADS-SEC-005-06).
 */
export async function ensureCsrfToken(): Promise<string> {
  const existing = session.getCsrfToken()
  if (existing) return existing
  const { csrf_token } = await request<{ csrf_token: string }>('/auth/csrf/', {
    credentials: true,
  })
  session.setCsrfToken(csrf_token)
  return csrf_token
}

/**
 * A credentialed, CSRF-protected auth request. If the in-memory token no longer
 * matches the CSRF cookie (403), it is bootstrapped again and the request retried once.
 */
async function csrfProtected<T>(path: string, body?: unknown): Promise<T> {
  const send = async () =>
    request<T>(path, {
      method: 'POST',
      body,
      credentials: true,
      headers: { 'X-CSRFToken': await ensureCsrfToken() },
    })
  try {
    return await send()
  } catch (error) {
    if (!(error instanceof ApiError) || error.status !== 403) throw error
    session.setCsrfToken(null)
    return send()
  }
}

/** `POST /api/v1/auth/login/` — returns the access token; the refresh token stays in its cookie. */
export async function login(email: string, password: string): Promise<string> {
  const { access_token } = await csrfProtected<{ access_token: string }>('/auth/login/', {
    email,
    password,
  })
  return access_token
}

let refreshInFlight: Promise<string> | null = null

/**
 * `POST /api/v1/auth/refresh/` — rotate the refresh cookie and store the new access
 * token in memory. At most one refresh is in flight per application instance; every
 * caller during that time awaits the same result (ADS-FR-008-04).
 */
export function refreshAccessToken(): Promise<string> {
  if (!refreshInFlight) {
    refreshInFlight = csrfProtected<{ access_token: string }>('/auth/refresh/')
      .then(({ access_token }) => {
        session.setAccessToken(access_token)
        return access_token
      })
      .finally(() => {
        refreshInFlight = null
      })
  }
  return refreshInFlight
}
