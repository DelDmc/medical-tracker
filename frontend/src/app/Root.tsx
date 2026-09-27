import { AuthProvider } from '../auth/AuthContext'
import { Layout } from './Layout'

/** The root route: providers that need the router, around the page frame. */
export function Root() {
  return (
    <AuthProvider>
      <Layout />
    </AuthProvider>
  )
}
