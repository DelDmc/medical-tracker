import { useQueryClient } from '@tanstack/react-query'
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useSyncExternalStore,
} from 'react'
import type { ReactNode } from 'react'

import { useNavigate } from 'react-router'

import { login as apiLogin, logout as apiLogout } from '../api/auth'
import { clearLogoutIntent, setLogoutIntent } from './logoutIntent'
import { session, type SessionUser } from './session'

type AuthValue = {
  user: SessionUser | null
  isAuthenticated: boolean
  sessionExpired: boolean
  logIn: (email: string, password: string) => Promise<void>
  logOut: () => Promise<void>
}

const AuthContext = createContext<AuthValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const snapshot = useSyncExternalStore(session.subscribe, session.getSnapshot)
  const queryClient = useQueryClient()
  const navigate = useNavigate()

  // Another account's data must never outlive the session that fetched it.
  useEffect(() => {
    if (!snapshot.accessToken) queryClient.clear()
  }, [snapshot.accessToken, queryClient])

  const logIn = useCallback(async (email: string, password: string) => {
    const accessToken = await apiLogin(email, password)
    session.signIn(accessToken, { email })
    // A successful login ends any earlier logout intent (ADS-FR-006-07).
    clearLogoutIntent()
  }, [])

  /**
   * Log out (user_flows.md §4): write the logout-intent marker, clear the in-memory
   * session before anything is sent (ADS-FR-006-05, ADS-FR-006-06), then ask the
   * backend to revoke the refresh token. The login page opens whatever the outcome —
   * success, an error response, or an unreachable backend (ADS-FR-006-08).
   */
  const logOut = useCallback(async () => {
    setLogoutIntent()
    session.clear()
    try {
      await apiLogout()
    } catch {
      // The local session is already gone and the marker blocks restoration.
    }
    navigate('/login', { replace: true })
  }, [navigate])

  const value = useMemo<AuthValue>(
    () => ({
      user: snapshot.user,
      isAuthenticated: Boolean(snapshot.accessToken),
      sessionExpired: snapshot.expired,
      logIn,
      logOut,
    }),
    [snapshot, logIn, logOut],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthValue {
  const value = useContext(AuthContext)
  if (!value) throw new Error('useAuth must be used inside <AuthProvider>.')
  return value
}
