import { useQuery } from '@tanstack/react-query'
import { Link, useLocation } from 'react-router'

import { examinationKeys, listExaminations } from '../api/examinations'
import { ExaminationResults } from '../examinations/ExaminationResults'

export function ExaminationListPage() {
  const location = useLocation()
  const message = (location.state as { message?: string } | null)?.message
  const params = {}
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
      <ExaminationResults
        query={query}
        empty={
          <>
            <p>You have no examinations yet.</p>
            <p>
              <Link to="/examinations/new">Add your first examination</Link>
            </p>
          </>
        }
      />
    </section>
  )
}
