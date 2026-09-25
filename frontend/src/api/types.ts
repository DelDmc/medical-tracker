/** Shapes defined by docs/api_contract.md. */

export type Account = {
  id: number
  email: string
  timezone: string
}

export type RegistrationRequest = {
  email: string
  password: string
  timezone: string
}
