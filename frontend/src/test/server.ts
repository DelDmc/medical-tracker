import { setupServer } from 'msw/node'

/** The MSW server every test shares; tests add handlers with `server.use(...)`. */
export const server = setupServer()
