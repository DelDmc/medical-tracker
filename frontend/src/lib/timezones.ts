/**
 * Timezone choices for the account forms (assumption A7). The list comes from the
 * browser's IANA database; the backend remains authoritative and rejects anything it
 * does not support with a `timezone` field error.
 */

const FALLBACK_TIME_ZONES = [
  'UTC',
  'Africa/Cairo',
  'Africa/Johannesburg',
  'America/Chicago',
  'America/Denver',
  'America/Los_Angeles',
  'America/New_York',
  'America/Sao_Paulo',
  'Asia/Dubai',
  'Asia/Kolkata',
  'Asia/Makassar',
  'Asia/Shanghai',
  'Asia/Tokyo',
  'Australia/Sydney',
  'Europe/Berlin',
  'Europe/London',
  'Europe/Paris',
  'Europe/Warsaw',
  'Pacific/Auckland',
  'Pacific/Honolulu',
]

let cached: string[] | null = null

export function supportedTimeZones(): string[] {
  if (cached) return cached
  let zones: string[]
  try {
    const intl = Intl as unknown as { supportedValuesOf?: (key: string) => string[] }
    zones = intl.supportedValuesOf?.('timeZone') ?? []
  } catch {
    zones = []
  }
  if (!zones.length) zones = FALLBACK_TIME_ZONES
  cached = Array.from(new Set(['UTC', ...zones])).sort()
  return cached
}

/** The browser's own timezone, when it is one of the offered choices. */
export function detectedTimeZone(): string {
  try {
    const zone = Intl.DateTimeFormat().resolvedOptions().timeZone
    return zone && supportedTimeZones().includes(zone) ? zone : ''
  } catch {
    return ''
  }
}
