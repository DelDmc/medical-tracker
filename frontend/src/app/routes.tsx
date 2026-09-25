import { Navigate, type RouteObject } from 'react-router'

import { PublicOnly, RequireAuth } from '../auth/guards'
import { AboutPage } from '../pages/AboutPage'
import { AccountPage } from '../pages/AccountPage'
import { DashboardPage } from '../pages/DashboardPage'
import { ExaminationListPage } from '../pages/ExaminationListPage'
import { LoginPage } from '../pages/LoginPage'
import { NewExaminationPage } from '../pages/NewExaminationPage'
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
        children: [
          { path: '/dashboard', element: <DashboardPage /> },
          { path: '/account', element: <AccountPage /> },
          { path: '/examinations', element: <ExaminationListPage /> },
          { path: '/examinations/new', element: <NewExaminationPage /> },
        ],
      },
      { path: '*', element: <NotFoundPage /> },
    ],
  },
]
