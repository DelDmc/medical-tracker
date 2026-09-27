import { useAuth } from './AuthContext'

/** The account's IANA timezone, for presenting instants (ADS-UX-007-01). */
export function useAccountTimezone(): string {
  const { user } = useAuth()
  if (user?.timezone) return user.timezone
  try {
    return Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC'
  } catch {
    return 'UTC'
  }
}
