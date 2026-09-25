import { useAuth } from '../auth/AuthContext'

export function DashboardPage() {
  const { user } = useAuth()
  return (
    <section className="page" aria-labelledby="dashboard-title">
      <h1 id="dashboard-title">Dashboard</h1>
      {user ? <p className="muted">Signed in as {user.email}</p> : null}
    </section>
  )
}
