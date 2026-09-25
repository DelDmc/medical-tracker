import { Link } from 'react-router'

export function HomePage() {
  return (
    <section className="page" aria-labelledby="home-title">
      <h1 id="home-title">Medical Tracker</h1>
      <div className="card">
        <p>Keep your medical appointments and examination history in one place.</p>
        <p>
          <Link to="/about">Read what this application is for</Link>
        </p>
      </div>
    </section>
  )
}
