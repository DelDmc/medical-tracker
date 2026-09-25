/**
 * The authenticated session, held only in application memory (ADS-FR-005-04,
 * ADS-SEC-005-06). Nothing here is ever written to localStorage, sessionStorage or a
 * cookie: a page reload starts with an empty session, which Slice 3's initialization
 * refresh restores from the backend's HttpOnly refresh cookie.
 */

export type SessionUser = {
  id?: number
  email: string
  timezone?: string
}

export type SessionState = {
  accessToken: string | null
  user: SessionUser | null
}

const EMPTY: SessionState = { accessToken: null, user: null }

let state: SessionState = EMPTY
let csrfToken: string | null = null
const listeners = new Set<() => void>()

function emit() {
  for (const listener of listeners) listener()
}

export const session = {
  subscribe(listener: () => void) {
    listeners.add(listener)
    return () => listeners.delete(listener)
  },
  getSnapshot: (): SessionState => state,
  getAccessToken: () => state.accessToken,

  signIn(accessToken: string, user: SessionUser | null) {
    state = { accessToken, user }
    emit()
  },
  setAccessToken(accessToken: string) {
    state = { ...state, accessToken }
    emit()
  },
  setUser(user: SessionUser) {
    state = { ...state, user }
    emit()
  },
  /** Drop the access token and user. The CSRF token deliberately survives (§4 step 3). */
  clear() {
    state = EMPTY
    emit()
  },

  getCsrfToken: () => csrfToken,
  setCsrfToken(token: string | null) {
    csrfToken = token
  },

  /** Forget everything, including the CSRF token (tests start from a fresh load). */
  reset() {
    state = EMPTY
    csrfToken = null
    emit()
  },
}
