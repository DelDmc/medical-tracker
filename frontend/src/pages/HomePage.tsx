import { Link } from 'react-router'

export function HomePage() {
  return (
    <section className="page" aria-labelledby="home-title">
      <h1 id="home-title">Medical Tracker</h1>
      <div className="card">
        <p>Keep your medical appointments and examination history in one place.</p>
        <p className="button-row">
          <Link className="button button-primary" to="/register">
            Create an account
          </Link>
          <Link className="button button-secondary" to="/about">
            About this app
          </Link>
        </p>
      </div>
    </section>
  )
}
