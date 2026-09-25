import { http, HttpResponse } from 'msw'
import { setupServer } from 'msw/node'

import { CATEGORIES } from './factories'

const API = 'http://api.test/api/v1'

/** Reference data every page may load; individual tests add or override handlers. */
export const defaultHandlers = [http.get(`${API}/categories/`, () => HttpResponse.json(CATEGORIES))]

/** The MSW server every test shares; `server.resetHandlers()` restores the defaults. */
export const server = setupServer(...defaultHandlers)
