import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'

import { renderApp } from '../test/render'
import { AboutPage } from './AboutPage'

describe('non-clinical purpose page', () => {
  it('TC-PRV-003-01 — The non-clinical purpose statement is displayed', () => {
    render(<AboutPage />)

    const statement = document.getElementById('purpose-statement')!
    expect(statement).toHaveTextContent(/is an organizational tool/i)
    expect(statement).toHaveTextContent(/does not provide medical advice/i)
    expect(statement).toHaveTextContent(/diagnosis/i)
    expect(statement).toHaveTextContent(/treatment/i)
    expect(statement).toHaveTextContent(/emergency assistance/i)
  })

  it('TC-PRV-003-02 — The informational page is reachable from unauthenticated navigation', async () => {
    const user = userEvent.setup()
    renderApp('/login')

    const nav = screen.getByRole('navigation', { name: 'Primary' })
    const aboutLink = within(nav).getByRole('link', { name: 'About' })

    // Reach the link with the keyboard alone, then follow it.
    for (let presses = 0; presses < 20 && document.activeElement !== aboutLink; presses += 1) {
      await user.tab()
    }
    expect(aboutLink).toHaveFocus()
    await user.keyboard('{Enter}')

    expect(await screen.findByRole('heading', { level: 1, name: 'About Medical Tracker' }))
      .toBeInTheDocument()
    expect(screen.getByText(/is an organizational tool/i)).toBeInTheDocument()
  })
})
