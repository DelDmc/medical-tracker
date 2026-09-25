import { Link } from 'react-router'

export function NotFoundPage() {
  return (
    <section className="page" aria-labelledby="not-found-title">
      <h1 id="not-found-title">Page not found</h1>
      <p>
        The page you asked for does not exist. <Link to="/dashboard">Go to your dashboard</Link>
      </p>
    </section>
  )
}
