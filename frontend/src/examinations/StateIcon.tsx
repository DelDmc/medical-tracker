/**
 * A distinct shape per examination state, so no state is told apart by colour alone
 * (ADS-FR-043-01, ADS-UX-008-01). The `data-indicator` names the shape.
 */

export type IndicatorState =
  | 'draft'
  | 'planned'
  | 'completed'
  | 'cancelled'
  | 'missed'
  | 'overdue'
  | 'upcoming'

export const INDICATOR_SHAPES: Record<IndicatorState, string> = {
  draft: 'pencil',
  planned: 'circle',
  completed: 'check',
  cancelled: 'cross',
  missed: 'slashed-circle',
  overdue: 'triangle',
  upcoming: 'clock',
}

const PATHS: Record<string, React.ReactNode> = {
  pencil: <path d="M4 20h4L19 9l-4-4L4 16v4zM14 6l4 4" />,
  circle: <circle cx="12" cy="12" r="8" />,
  check: <path d="M5 12.5l4.5 4.5L19 7" />,
  cross: <path d="M6 6l12 12M18 6L6 18" />,
  'slashed-circle': (
    <>
      <circle cx="12" cy="12" r="8" />
      <path d="M6.5 17.5l11-11" />
    </>
  ),
  triangle: <path d="M12 3.5L21.5 20h-19zM12 10v4.5M12 17.2v.3" />,
  clock: (
    <>
      <circle cx="12" cy="12" r="8" />
      <path d="M12 7.5V12l3 2" />
    </>
  ),
}

export function StateIcon({ state, className }: { state: IndicatorState; className?: string }) {
  const shape = INDICATOR_SHAPES[state]
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.4"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      focusable="false"
      data-indicator={shape}
    >
      {PATHS[shape]}
    </svg>
  )
}
