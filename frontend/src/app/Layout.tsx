import { useId, useState } from 'react'
import { Link, NavLink, Outlet } from 'react-router'

import { useAuth } from '../auth/AuthContext'

import styles from './Layout.module.css'

type NavItem = { to: string; label: string }

const PUBLIC_NAV: NavItem[] = [
  { to: '/login', label: 'Log in' },
  { to: '/register', label: 'Register' },
  { to: '/about', label: 'About' },
]

const AUTHENTICATED_NAV: NavItem[] = [
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/examinations', label: 'Examinations' },
  { to: '/account', label: 'Account' },
  { to: '/about', label: 'About' },
]

/** The page frame shared by every route: header, primary navigation, main, footer. */
export function Layout() {
  const { isAuthenticated, logOut } = useAuth()
  const [menuOpen, setMenuOpen] = useState(false)
  const navId = useId()
  const closeMenu = () => setMenuOpen(false)

  return (
    <div className={styles.app}>
      <a className="skip-link" href="#main">
        Skip to main content
      </a>
      <header className={styles.header}>
        <div className={styles.headerInner}>
          <Link
            to={isAuthenticated ? '/dashboard' : '/login'}
            className={styles.brand}
            onClick={closeMenu}
          >
            <span className={styles.brandMark} aria-hidden="true">
              +
            </span>
            Medical Tracker
          </Link>
          <button
            type="button"
            className={`button button-secondary ${styles.menuButton}`}
            aria-expanded={menuOpen}
            aria-controls={navId}
            onClick={() => setMenuOpen((open) => !open)}
          >
            Menu
          </button>
          <nav className={styles.nav} aria-label="Primary">
            <ul
              id={navId}
              className={`${styles.navList} ${menuOpen ? styles.navListOpen : ''}`}
            >
              {(isAuthenticated ? AUTHENTICATED_NAV : PUBLIC_NAV).map((item) => (
                <li key={item.to}>
                  <NavLink to={item.to} className={styles.navLink} onClick={closeMenu}>
                    {item.label}
                  </NavLink>
                </li>
              ))}
              {isAuthenticated ? (
                <li>
                  <button
                    type="button"
                    className={styles.navButton}
                    onClick={() => {
                      closeMenu()
                      void logOut()
                    }}
                  >
                    Log out
                  </button>
                </li>
              ) : null}
            </ul>
          </nav>
        </div>
      </header>
      <main id="main" className={styles.main} tabIndex={-1}>
        <Outlet />
      </main>
      <footer className={styles.footer}>
        <p>
          An organizational tool only — not medical advice. <Link to="/about">About this app</Link>
        </p>
      </footer>
    </div>
  )
}
