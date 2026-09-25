/**
 * The persistent logout-intent marker (ADS-FR-006-06, ADS-FR-006-07). It holds no
 * secret: its presence alone stops initialization from restoring a session.
 */

export const LOGOUT_INTENT_KEY = 'medical_tracker.logout_intent'

export function hasLogoutIntent(): boolean {
  try {
    return window.localStorage.getItem(LOGOUT_INTENT_KEY) !== null
  } catch {
    return false
  }
}

export function setLogoutIntent() {
  try {
    window.localStorage.setItem(LOGOUT_INTENT_KEY, 'true')
  } catch {
    // Storage unavailable: logout still proceeds; only reload-suppression is lost.
  }
}

export function clearLogoutIntent() {
  try {
    window.localStorage.removeItem(LOGOUT_INTENT_KEY)
  } catch {
    // Nothing to clear.
  }
}
