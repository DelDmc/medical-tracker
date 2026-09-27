import type { UseQueryResult } from '@tanstack/react-query'
import type { ReactNode } from 'react'

import type { Examination } from '../api/types'
import { ExaminationList } from './ExaminationItem'

/**
 * Exactly one of four mutually exclusive states (ADS-FR-020-01): loading, error,
 * empty, or the populated list.
 */
export function ExaminationResults({
  query,
  empty,
}: {
  query: UseQueryResult<Examination[]>
  empty: ReactNode
}) {
  if (query.isPending) {
    return (
      <p className="muted" role="status" data-state="loading">
        Loading examinations…
      </p>
    )
  }
  if (query.isError) {
    return (
      <div className="alert alert-error" role="alert" data-state="error">
        <p>Your examinations could not be loaded.</p>
        <button className="button button-secondary" type="button" onClick={() => query.refetch()}>
          Try again
        </button>
      </div>
    )
  }
  if (!query.data.length) {
    return (
      <div className="card" data-state="empty">
        {empty}
      </div>
    )
  }
  return (
    <div data-state="populated">
      <ExaminationList examinations={query.data} />
    </div>
  )
}
