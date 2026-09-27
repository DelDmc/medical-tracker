import react from '@vitejs/plugin-react'
import { defineConfig } from 'vitest/config'

export default defineConfig({
  plugins: [react()],
  server: {
    // Serve on "localhost" so the frontend and a local backend are same-site and the
    // SameSite=Lax authentication cookies are sent (ADS-SEC-005-04, ADS-SEC-005-08).
    host: 'localhost',
    port: 5173,
    strictPort: true,
  },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/test/setup.ts'],
    restoreMocks: true,
    passWithNoTests: true,
    env: {
      VITE_API_BASE_URL: 'http://api.test',
      // A zone west of UTC, so any date-only value routed through a UTC conversion
      // renders on the wrong day and fails the suite (IMPLEMENTATION_PLAN.md R4).
      TZ: 'Pacific/Honolulu',
    },
  },
})
