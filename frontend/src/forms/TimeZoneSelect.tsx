import { supportedTimeZones } from '../lib/timezones'
import type { ControlProps } from './FormField'

type TimeZoneSelectProps = ControlProps & {
  value: string
  onChange: (value: string) => void
}

/** The required timezone selection control (ADS-UX-004-01). */
export function TimeZoneSelect({ value, onChange, ...control }: TimeZoneSelectProps) {
  const zones = supportedTimeZones()
  // Keep a stored value visible even if this browser does not list it.
  const options = value && !zones.includes(value) ? [value, ...zones] : zones
  return (
    <select
      {...control}
      className="input"
      value={value}
      onChange={(event) => onChange(event.target.value)}
    >
      <option value="">Select a timezone</option>
      {options.map((zone) => (
        <option key={zone} value={zone}>
          {zone.replaceAll('_', ' ')}
        </option>
      ))}
    </select>
  )
}
