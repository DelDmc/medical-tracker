import { useEffect, useState } from 'react'
import { Navigate, Outlet, useLocation } from 'react-router'

import { useAuth } from './AuthContext'
import { canRestoreSession, restoreSession } from './restore'

/**
 * Routes that need a session. Without an in-memory token the session is restored
 * once from the refresh cookie; if that is not possible the visitor is sent to log in,
 * with the session-expired message only when an active session was lost.
 */
export function RequireAuth() {
  const { isAuthenticated, sessionExpired } = useAuth()
  const location = useLocation()
  const [restoring, setRestoring] = useState(() => !isAuthenticated && canRestoreSession())

  useEffect(() => {
    if (!restoring) return
    let active = true
    restoreSession().then(() => {
      if (active) setRestoring(false)
    })
    return () => {
      active = false
    }
  }, [restoring])

  if (isAuthenticated) return <Outlet />
  if (restoring) {
    return (
      <p className="muted" role="status">
        Loading your session…
      </p>
    )
  }
  return (
    <Navigate
      to="/login"
      replace
      state={{ from: location.pathname + location.search, sessionExpired }}
    />
  )
}

/** Login and registration: an authenticated user goes straight to the dashboard. */
export function PublicOnly() {
  const { isAuthenticated } = useAuth()
  if (isAuthenticated) return <Navigate to="/dashboard" replace />
  return <Outlet />
}
