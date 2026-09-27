import { act, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { session } from '../auth/session'
import { renderWithProviders } from '../test/render'
import { CalendarDate, Instant } from './DateTime'
import { formatInstant } from './datetime'

function signInWithTimezone(timezone: string) {
  session.signIn('access-token', { id: 1, email: 'person@example.com', timezone })
}

describe('timezone-aware presentation', () => {
  it('TC-UX-007-01 — A fixed timestamp displays in the user\'s configured timezone', () => {
    signInWithTimezone('Europe/Warsaw')

    renderWithProviders(<Instant value="2026-07-21T04:10:00Z" />)

    // 04:10 UTC is 06:10 in Warsaw (CEST, UTC+2).
    const shown = screen.getByText('2026-07-21 06:10')
    expect(shown).toHaveAttribute('dateTime', '2026-07-21T04:10:00Z')

    // The presentation follows a change of account timezone.
    act(() => signInWithTimezone('Asia/Makassar'))
    expect(screen.getByText('2026-07-21 12:10')).toBeInTheDocument()
  })

  it('TC-UX-007-02 — A date-only value displays as stored without timezone conversion', () => {
    // Honolulu is UTC-10: routed through UTC midnight, 2026-08-15 would become the 14th.
    signInWithTimezone('Pacific/Honolulu')
    expect(Intl.DateTimeFormat().resolvedOptions().timeZone).toBe('Pacific/Honolulu')
    expect(formatInstant('2026-08-15T00:00:00Z', 'Pacific/Honolulu')).toMatch(/^2026-08-14/)

    renderWithProviders(<CalendarDate value="2026-08-15" />)

    const shown = screen.getByText('2026-08-15')
    expect(shown).toHaveAttribute('dateTime', '2026-08-15')
    expect(screen.queryByText(/2026-08-14/)).not.toBeInTheDocument()
  })
})
