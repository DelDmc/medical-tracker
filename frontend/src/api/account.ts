import { apiRequest } from './authenticated'
import type { Account } from './types'

export function getAccount() {
  return apiRequest<Account>('/account/')
}

/** `PATCH /api/v1/account/` — only `timezone` is writable. */
export function updateTimezone(timezone: string) {
  return apiRequest<Account>('/account/', { method: 'PATCH', body: { timezone } })
}
