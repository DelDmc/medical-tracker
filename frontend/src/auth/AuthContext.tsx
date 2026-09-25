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

import { login as apiLogin } from '../api/auth'
import { clearLogoutIntent } from './logoutIntent'
import { session, type SessionUser } from './session'

type AuthValue = {
  user: SessionUser | null
  isAuthenticated: boolean
  sessionExpired: boolean
  logIn: (email: string, password: string) => Promise<void>
}

const AuthContext = createContext<AuthValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const snapshot = useSyncExternalStore(session.subscribe, session.getSnapshot)
  const queryClient = useQueryClient()

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

  const value = useMemo<AuthValue>(
    () => ({
      user: snapshot.user,
      isAuthenticated: Boolean(snapshot.accessToken),
      sessionExpired: snapshot.expired,
      logIn,
    }),
    [snapshot, logIn],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthValue {
  const value = useContext(AuthContext)
  if (!value) throw new Error('useAuth must be used inside <AuthProvider>.')
  return value
}
