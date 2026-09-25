import { Navigate, type RouteObject } from 'react-router'

import { PublicOnly, RequireAuth } from '../auth/guards'
import { AboutPage } from '../pages/AboutPage'
import { DashboardPage } from '../pages/DashboardPage'
import { LoginPage } from '../pages/LoginPage'
import { NotFoundPage } from '../pages/NotFoundPage'
import { RegisterPage } from '../pages/RegisterPage'
import { Root } from './Root'

export const routes: RouteObject[] = [
  {
    element: <Root />,
    children: [
      { path: '/', element: <Navigate to="/dashboard" replace /> },
      // Reachable signed in or out (ADS-PRV-003-01).
      { path: '/about', element: <AboutPage /> },
      {
        element: <PublicOnly />,
        children: [
          { path: '/login', element: <LoginPage /> },
          { path: '/register', element: <RegisterPage /> },
        ],
      },
      {
        element: <RequireAuth />,
        children: [{ path: '/dashboard', element: <DashboardPage /> }],
      },
      { path: '*', element: <NotFoundPage /> },
    ],
  },
]
