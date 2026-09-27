import { http, HttpResponse } from 'msw'
import { setupServer } from 'msw/node'

import { CATEGORIES } from './factories'

const API = 'http://api.test/api/v1'

export function emptyDashboard() {
  return {
    upcoming: [],
    overdue: [],
    recently_completed: [],
    status_counts: { draft: 0, planned: 0, completed: 0, cancelled: 0, missed: 0 },
    category_counts: CATEGORIES.map((category) => ({ category, count: 0 })),
    uncategorized_count: 0,
    overdue_count: 0,
  }
}

const notFound = () => HttpResponse.json({ detail: 'Not found.' }, { status: 404 })

/**
 * Responses every page may rely on — reference data, and "none configured" for an
 * examination's reminder and recurrence rule. Tests add or override handlers.
 */
export const defaultHandlers = [
  http.get(`${API}/categories/`, () => HttpResponse.json(CATEGORIES)),
  http.get(`${API}/examinations/:id/reminder/`, notFound),
  http.get(`${API}/examinations/:id/recurrence/`, notFound),
  http.get(`${API}/reminders/`, () => HttpResponse.json([])),
  http.get(`${API}/examinations/`, () => HttpResponse.json([])),
  http.get(`${API}/dashboard/`, () => HttpResponse.json(emptyDashboard())),
]

/** The MSW server every test shares; `server.resetHandlers()` restores the defaults. */
export const server = setupServer(...defaultHandlers)
