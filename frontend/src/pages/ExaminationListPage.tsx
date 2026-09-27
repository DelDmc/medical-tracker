import { useQuery } from '@tanstack/react-query'
import { Link, useLocation, useSearchParams } from 'react-router'

import { examinationKeys, listExaminations, type ExaminationListParams } from '../api/examinations'
import { ExaminationFilters, FILTER_KEYS } from '../examinations/ExaminationFilters'
import { ExaminationResults } from '../examinations/ExaminationResults'
import { VIEWS, ViewSwitcher, type ExaminationView } from '../examinations/ViewSwitcher'

function viewFrom(searchParams: URLSearchParams): ExaminationView {
  const value = searchParams.get('time_state') ?? ''
  return VIEWS.some((view) => view.value === value) ? (value as ExaminationView) : ''
}

function paramsFrom(searchParams: URLSearchParams): ExaminationListParams {
  const params: ExaminationListParams = {}
  for (const key of FILTER_KEYS) {
    const value = searchParams.get(key)
    if (value) params[key] = value
  }
  const view = viewFrom(searchParams)
  if (view) params.time_state = view
  return params
}

export function ExaminationListPage() {
  const location = useLocation()
  const message = (location.state as { message?: string } | null)?.message
  const [searchParams, setSearchParams] = useSearchParams()
  const params = paramsFrom(searchParams)
  const view = viewFrom(searchParams)
  const filtered = FILTER_KEYS.some((key) => params[key])
  const query = useQuery({
    queryKey: examinationKeys.list(params),
    queryFn: () => listExaminations(params),
  })

  return (
    <section className="page" aria-labelledby="examinations-title">
      <div className="page-header">
        <h1 id="examinations-title">Examinations</h1>
        <Link className="button button-primary" to="/examinations/new">
          Add examination
        </Link>
      </div>
      {message ? (
        <div className="alert alert-success" role="status">
          <p>{message}</p>
        </div>
      ) : null}
      <ViewSwitcher current={view} searchParams={searchParams} />
      <ExaminationFilters searchParams={searchParams} setSearchParams={setSearchParams} />
      <ExaminationResults
        query={query}
        empty={
          filtered ? (
            <p>No examinations match these filters.</p>
          ) : view ? (
            <p>{VIEWS.find((candidate) => candidate.value === view)?.empty}</p>
          ) : (
            <>
              <p>You have no examinations yet.</p>
              <p>
                <Link to="/examinations/new">Add your first examination</Link>
              </p>
            </>
          )
        }
      />
    </section>
  )
}
