import { Link } from 'react-router'

/** The not-found and failure states shared by the examination pages. */
export function ExaminationNotFound() {
  return (
    <section className="page" aria-labelledby="not-found-title">
      <h1 id="not-found-title">Examination not found</h1>
      <p>
        This examination does not exist or is not yours.{' '}
        <Link to="/examinations">Back to your examinations</Link>
      </p>
    </section>
  )
}

export function ExaminationLoadError({ onRetry }: { onRetry: () => void }) {
  return (
    <div className="alert alert-error" role="alert">
      <p>The examination could not be loaded.</p>
      <button className="button button-secondary" type="button" onClick={onRetry}>
        Try again
      </button>
    </div>
  )
}
