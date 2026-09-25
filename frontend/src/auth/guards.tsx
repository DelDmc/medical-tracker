import { Navigate, Outlet, useLocation } from 'react-router'

import { useAuth } from './AuthContext'

/** Routes that need a session. Without one, the visitor is sent to log in. */
export function RequireAuth() {
  const { isAuthenticated } = useAuth()
  const location = useLocation()
  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location.pathname + location.search }} />
  }
  return <Outlet />
}

/** Login and registration: an authenticated user goes straight to the dashboard. */
export function PublicOnly() {
  const { isAuthenticated } = useAuth()
  if (isAuthenticated) return <Navigate to="/dashboard" replace />
  return <Outlet />
}
