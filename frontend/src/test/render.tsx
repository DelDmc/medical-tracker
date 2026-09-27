import { render } from '@testing-library/react'
import type { ReactNode } from 'react'
import { createMemoryRouter, MemoryRouter, RouterProvider } from 'react-router'

import { AppProviders, createQueryClient } from '../app/AppProviders'
import { routes } from '../app/routes'
import { AuthProvider } from '../auth/AuthContext'

/** Render the whole application at `path`, as a browser would load it. */
export function renderApp(path = '/') {
  const router = createMemoryRouter(routes, { initialEntries: [path] })
  const queryClient = createQueryClient()
  const utils = render(
    <AppProviders queryClient={queryClient}>
      <RouterProvider router={router} />
    </AppProviders>,
  )
  return { ...utils, router, queryClient }
}

/** Render one component with the application's providers around it. */
export function renderWithProviders(ui: ReactNode) {
  return render(
    <AppProviders queryClient={createQueryClient()}>
      <MemoryRouter>
        <AuthProvider>{ui}</AuthProvider>
      </MemoryRouter>
    </AppProviders>,
  )
}
