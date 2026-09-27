import { apiRequest } from './authenticated'
import type { Dashboard } from './types'

export function getDashboard() {
  return apiRequest<Dashboard>('/dashboard/')
}

export const DASHBOARD_QUERY_KEY = ['dashboard']
