import { getAccount } from '../api/account'
import { session } from './session'

/**
 * Hold the account — and so its timezone (ADS-UX-007-01) — in the session. A failure
 * leaves the session usable; views fall back to the browser's timezone meanwhile.
 */
export async function loadAccount() {
  try {
    const account = await getAccount()
    session.setUser({ id: account.id, email: account.email, timezone: account.timezone })
  } catch {
    // Keep the session; the account loads again on the next sign-in or reload.
  }
}
