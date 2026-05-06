import { useState, useEffect } from 'react'
import { NavLink, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import './Navbar.css'

export default function Navbar() {
  const { user, isSuperuser, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [scrolled, setScrolled] = useState(false)
  const [menuOpen, setMenuOpen] = useState(false)
  const [profileOpen, setProfileOpen] = useState(false)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20)
    window.addEventListener('scroll', onScroll)
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  // Close mobile menu on route change
  useEffect(() => {
    setMenuOpen(false)
    setProfileOpen(false)
  }, [location])

  const handleLogout = async () => {
    await logout()
    navigate('/')
  }

  return (
    <nav className={`navbar ${scrolled ? 'navbar--scrolled' : ''}`}>
      <div className="navbar__inner">
        {/* Logo */}
        <NavLink to="/" className="navbar__logo">
          <span className="navbar__logo-mark">ISH</span>
          <span className="navbar__logo-text">Taiwan</span>
        </NavLink>

        {/* Desktop links */}
        <div className="navbar__links">
          <NavLink to="/checklist" className={({isActive}) => isActive ? 'navbar__link active' : 'navbar__link'}>
            Checklist
          </NavLink>
          <NavLink to="/directory" className={({isActive}) => isActive ? 'navbar__link active' : 'navbar__link'}>
            Directory
          </NavLink>
          <NavLink to="/community" className={({isActive}) => isActive ? 'navbar__link active' : 'navbar__link'}>
            Community
          </NavLink>
        </div>

        {/* Auth buttons */}
        <div className="navbar__auth">
          {user ? (
            <div className="navbar__profile">
              <button
                type="button"
                className="navbar__avatar"
                title={user.username}
                onClick={() => setProfileOpen((open) => !open)}
                aria-haspopup="menu"
                aria-expanded={profileOpen}
              >
                {user.profile?.avatar ? (
                  <img src={user.profile.avatar} alt={`${user.username}'s avatar`} />
                ) : (
                  user.username.charAt(0).toUpperCase()
                )}
              </button>
              {profileOpen && (
                <div className="navbar__profile-menu" role="menu">
                  <NavLink to="/profile" className="navbar__profile-item">Profile</NavLink>
                  {isSuperuser && (
                    <NavLink to="/admin-panel" className="navbar__profile-item">Admin Panel</NavLink>
                  )}
                  <button className="navbar__profile-item navbar__profile-signout" onClick={handleLogout}>
                    Sign out
                  </button>
                </div>
              )}
            </div>
          ) : (
            <>
              <NavLink to="/login" className="btn btn-ghost">Log in</NavLink>
              <NavLink to="/register" className="btn btn-primary">Join free</NavLink>
            </>
          )}
        </div>

        {/* Mobile hamburger */}
        <button
          className={`navbar__hamburger ${menuOpen ? 'open' : ''}`}
          onClick={() => setMenuOpen(!menuOpen)}
          aria-label="Toggle menu"
        >
          <span /><span /><span />
        </button>
      </div>

      {/* Mobile menu */}
      <div className={`navbar__mobile ${menuOpen ? 'navbar__mobile--open' : ''}`}>
        <NavLink to="/checklist" className="navbar__mobile-link">Checklist</NavLink>
        <NavLink to="/directory" className="navbar__mobile-link">Directory</NavLink>
        <NavLink to="/community" className="navbar__mobile-link">Community</NavLink>
        {user ? (
          <>
            <NavLink to="/profile" className="navbar__mobile-link">Profile</NavLink>
            {isSuperuser && (
              <NavLink to="/admin-panel" className="navbar__mobile-link">Admin Panel</NavLink>
            )}
            <button className="navbar__mobile-link navbar__mobile-logout" onClick={handleLogout}>
              Sign out
            </button>
          </>
        ) : (
          <>
            <NavLink to="/login"    className="navbar__mobile-link">Log in</NavLink>
            <NavLink to="/register" className="navbar__mobile-link">Join free</NavLink>
          </>
        )}
      </div>
    </nav>
  )
}
