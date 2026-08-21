import { NavLink, useLocation, useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { useTrip } from '../context/TripContext';
import { useAuth } from '../context/AuthContext';

const STEPS = [
  { path: '/attractions', label: 'Attractions', full: 'Attractions Selection' },
  { path: '/budget', label: 'Budget', full: 'Budget Allocation' },
  { path: '/accommodation', label: 'Stay', full: 'Accommodation Selection' },
  { path: '/itinerary', label: 'Itinerary', full: 'Itinerary Summary' },
  { path: '/recommendations', label: 'Discover', full: 'Recommendations Discovery' },
  { path: '/export', label: 'Export', full: 'Export Summary' },
];

export default function Layout({ children, progress = 25 }) {
  const location = useLocation();
  const navigate = useNavigate();
  const { trip, updateTrip } = useTrip();
  const { logout } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);

  const currentStepIndex = STEPS.findIndex((s) => s.path === location.pathname);
  const currentLabel =
    STEPS.find((s) => s.path === location.pathname)?.full ||
    (location.pathname === '/profile'
      ? 'Profile'
      : location.pathname === '/history'
        ? 'Trip History'
        : 'Planning');

  useEffect(() => {
    setMenuOpen(false);
  }, [location.pathname]);

  useEffect(() => {
    document.body.style.overflow = menuOpen ? 'hidden' : '';
    return () => {
      document.body.style.overflow = '';
    };
  }, [menuOpen]);

  useEffect(() => {
    const onKey = (e) => {
      if (e.key === 'Escape') setMenuOpen(false);
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, []);

  return (
    <div className="tc-shell">
      <div
        className={`tc-overlay${menuOpen ? ' is-open' : ''}`}
        onClick={() => setMenuOpen(false)}
        aria-hidden={!menuOpen}
      />

      <aside className={`tc-sidebar${menuOpen ? ' is-open' : ''}`} aria-label="Trip steps">
        <div className="tc-sidebar-head">
          <img
            src="/tour-ceylon-logo.png"
            alt="Tour Ceylon"
            className="tc-logo"
          />
          <button
            type="button"
            className="tc-icon-btn tc-sidebar-close"
            onClick={() => setMenuOpen(false)}
            aria-label="Close menu"
          >
            <span className="tc-close-icon" aria-hidden="true" />
          </button>
        </div>

        <nav className="tc-nav">
          {STEPS.map((step, index) => {
            const done = index < currentStepIndex;
            return (
              <NavLink
                key={step.path}
                to={step.path}
                className={({ isActive }) =>
                  `tc-nav-item${isActive ? ' is-active' : ''}${done ? ' is-done' : ''}`
                }
              >
                <span className="tc-nav-index">{String(index + 1).padStart(2, '0')}</span>
                <span className="tc-nav-label">{step.full}</span>
                {done && <span className="tc-nav-chip">Done</span>}
                {index === currentStepIndex && (
                  <span className="tc-nav-chip is-current">
                    {currentStepIndex + 1}/{STEPS.length}
                  </span>
                )}
              </NavLink>
            );
          })}
        </nav>

        <div className="tc-advisory">
          <div className="tc-advisory-title">Advisory</div>
          <p>
            For an n-day trip, pick attractions from 1 to n distinct locations.
            Multiple stops in the same place are fine.
          </p>
        </div>

        <NavLink
          to="/history"
          className={({ isActive }) => `tc-nav-item${isActive ? ' is-active' : ''}`}
          style={{ marginTop: 8 }}
        >
          <span className="tc-nav-index">H</span>
          <span className="tc-nav-label">Trip History</span>
        </NavLink>
      </aside>

      <div className="tc-main">
        <header className="tc-topbar">
          <div className="tc-topbar-left">
            <button
              type="button"
              className={`tc-burger${menuOpen ? ' is-open' : ''}`}
              onClick={() => setMenuOpen((o) => !o)}
              aria-label={menuOpen ? 'Close menu' : 'Open menu'}
              aria-expanded={menuOpen}
            >
              <span />
              <span />
              <span />
            </button>
            <div className="tc-breadcrumb">
              <span className="tc-breadcrumb-muted">Dashboard</span>
              <span className="tc-breadcrumb-sep" aria-hidden="true">
                /
              </span>
              <span className="tc-breadcrumb-active">{currentLabel}</span>
            </div>
          </div>

          <input
            className="tc-search"
            placeholder="Search attractions…"
            value={trip.landmarkSearch || ''}
            onChange={(e) => {
              const value = e.target.value;
              updateTrip({ landmarkSearch: value });
              if (location.pathname !== '/attractions') navigate('/attractions');
            }}
            aria-label="Search attractions"
          />

          <div className="tc-topbar-right">
            <div className="tc-progress" aria-label={`Trip progress ${progress}%`}>
              <span className="tc-progress-label">{progress}%</span>
              <div className="tc-progress-track">
                <div
                  className="tc-progress-fill"
                  style={{ width: `${Math.min(progress, 100)}%` }}
                />
              </div>
            </div>

            <NavLink
              to="/history"
              className={({ isActive }) => `tc-profile-btn${isActive ? ' is-active' : ''}`}
              title="Trip History"
            >
              History
            </NavLink>
            <NavLink
              to="/profile"
              className={({ isActive }) => `tc-profile-btn${isActive ? ' is-active' : ''}`}
              title="Profile"
            >
              Profile
            </NavLink>
            <button
              type="button"
              className="tc-logout-btn"
              onClick={() => {
                logout();
                navigate('/login', { replace: true });
              }}
            >
              Log out
            </button>
          </div>
        </header>

        <main className="tc-content">{children}</main>
      </div>
    </div>
  );
}
