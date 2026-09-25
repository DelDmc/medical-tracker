import { request } from './client'
import type { Account, RegistrationRequest } from './types'

/** `POST /api/v1/auth/register/` — needs no bearer token, credentials, or CSRF token. */
export function register(data: RegistrationRequest) {
  return request<Account>('/auth/register/', { method: 'POST', body: data })
}
