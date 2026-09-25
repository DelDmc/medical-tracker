import '@testing-library/jest-dom/vitest'
import { cleanup } from '@testing-library/react'
import { afterAll, afterEach, beforeAll } from 'vitest'

import { resetRestoreState } from '../auth/restore'
import { session } from '../auth/session'
import { server } from './server'

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }))

afterEach(() => {
  cleanup()
  server.resetHandlers()
  session.reset()
  resetRestoreState()
  window.localStorage.clear()
  window.sessionStorage.clear()
})

afterAll(() => server.close())
