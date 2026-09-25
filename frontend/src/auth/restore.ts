import { ensureCsrfToken, refreshAccessToken } from '../api/auth'
import { loadAccount } from './loadAccount'
import { hasLogoutIntent } from './logoutIntent'
import { session } from './session'

let attempted = false
let restoring: Promise<boolean> | null = null

/**
 * Whether protected-application initialization may try to restore the session: only
 * once per application instance, only without an in-memory token, and never while the
 * logout-intent marker exists (ADS-FR-007-06, ADS-FR-006-06).
 */
export function canRestoreSession(): boolean {
  return !attempted && !session.getAccessToken() && !hasLogoutIntent()
}

/**
 * The initialization refresh after a page reload: bootstrap the CSRF token, then one
 * refresh (user_flows.md §3). Resolves `false` on any failure; the caller opens the
 * login page without a retry and without a session-expired message (ADS-FR-008-03).
 */
export function restoreSession(): Promise<boolean> {
  if (!restoring) {
    attempted = true
    restoring = (async () => {
      try {
        await ensureCsrfToken()
        const accessToken = await refreshAccessToken()
        session.signIn(accessToken, session.getSnapshot().user)
      } catch {
        session.clear()
        return false
      }
      await loadAccount()
      return true
    })()
  }
  return restoring
}

/** Tests only: behave like a fresh page load. */
export function resetRestoreState() {
  attempted = false
  restoring = null
}
