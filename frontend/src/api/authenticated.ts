import { session } from '../auth/session'
import { refreshAccessToken } from './auth'
import { ApiError, request, type RequestOptions } from './client'

/** The session could not be renewed; the user has been sent to log in. */
export class SessionExpiredError extends Error {
  constructor() {
    super('Your session has expired.')
    this.name = 'SessionExpiredError'
  }
}

function send<T>(path: string, options: RequestOptions, token: string | null) {
  return request<T>(path, {
    ...options,
    credentials: false,
    headers: { ...options.headers, ...(token ? { Authorization: `Bearer ${token}` } : {}) },
  })
}

/**
 * A protected request: `Authorization: Bearer <access token>` from memory and no
 * browser credentials (api_contract.md §5.1).
 *
 * On a 401 it refreshes at most once and replays the original request at most once
 * (ADS-FR-008-01). Concurrent 401s share one in-flight refresh (ADS-FR-008-04); a
 * request whose token was already replaced by someone else's refresh just replays
 * with the current token. If the refresh is rejected, the session ends as expired and
 * the user is sent to log in with a session-expired message (ADS-FR-008-02).
 */
export async function apiRequest<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const tokenUsed = session.getAccessToken()
  try {
    return await send<T>(path, options, tokenUsed)
  } catch (error) {
    if (!(error instanceof ApiError) || error.status !== 401) throw error
  }

  let token = session.getAccessToken()
  if (!token || token === tokenUsed) {
    try {
      token = await refreshAccessToken()
    } catch (refreshError) {
      if (!(refreshError instanceof ApiError)) throw refreshError
      session.expire()
      throw new SessionExpiredError()
    }
  }
  // The one replay. A second 401 is returned to the caller; nothing loops.
  return send<T>(path, options, token)
}
