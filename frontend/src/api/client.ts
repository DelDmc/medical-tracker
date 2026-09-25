/**
 * The single HTTP layer between the frontend and the backend API (ADS-TECH-001-01).
 * Every request goes through `request`; nothing else calls `fetch`.
 */

export const API_BASE_URL = `${(import.meta.env.VITE_API_BASE_URL ?? '').replace(/\/+$/, '')}/api/v1`

/** The backend answered with a non-2xx status. `body` is the parsed JSON, if any. */
export class ApiError extends Error {
  readonly status: number
  readonly body: unknown

  constructor(status: number, body: unknown) {
    super(`The API responded with status ${status}.`)
    this.name = 'ApiError'
    this.status = status
    this.body = body
  }
}

/** The request never produced a response (backend unreachable, connection dropped). */
export class NetworkError extends Error {
  constructor(cause?: unknown) {
    super('The server could not be reached.', { cause })
    this.name = 'NetworkError'
  }
}

export type RequestOptions = {
  method?: 'GET' | 'POST' | 'PATCH' | 'DELETE'
  body?: unknown
  headers?: Record<string, string>
  /** Send and accept cookies (the auth and CSRF endpoints, api_contract.md §5.1). */
  credentials?: boolean
}

export async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = 'GET', body, headers = {}, credentials = false } = options
  const init: RequestInit = {
    method,
    headers: {
      Accept: 'application/json',
      ...(body === undefined ? {} : { 'Content-Type': 'application/json' }),
      ...headers,
    },
    credentials: credentials ? 'include' : 'omit',
  }
  if (body !== undefined) init.body = JSON.stringify(body)

  let response: Response
  try {
    response = await fetch(`${API_BASE_URL}${path}`, init)
  } catch (cause) {
    throw new NetworkError(cause)
  }

  const text = await response.text()
  let data: unknown = null
  if (text) {
    try {
      data = JSON.parse(text)
    } catch {
      data = text
    }
  }
  if (!response.ok) throw new ApiError(response.status, data)
  return data as T
}
