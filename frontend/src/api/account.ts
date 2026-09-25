import { apiRequest } from './authenticated'
import type { Account } from './types'

export function getAccount() {
  return apiRequest<Account>('/account/')
}

/** `PATCH /api/v1/account/` — only `timezone` is writable. */
export function updateTimezone(timezone: string) {
  return apiRequest<Account>('/account/', { method: 'PATCH', body: { timezone } })
}

/** `POST /api/v1/account/password/` — 200 with an empty body on success. */
export async function changePassword(currentPassword: string, newPassword: string) {
  await apiRequest<null>('/account/password/', {
    method: 'POST',
    body: { current_password: currentPassword, new_password: newPassword },
  })
}
