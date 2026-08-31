import { NavLink, useLocation, useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { useTrip } from '../context/TripContext';
import { useSiteI18n } from '@shared/i18n/react';

const STEPS = [
  { path: '/attractions', labelKey: 'step_attractions', fullKey: 'step_attractions_full' },
  { path: '/budget', labelKey: 'step_budget', fullKey: 'step_budget_full' },
  { path: '/accommodation', labelKey: 'step_stay', fullKey: 'step_stay_full' },
  { path: '/itinerary', labelKey: 'step_itinerary', fullKey: 'step_itinerary_full' },
  { path: '/recommendations', labelKey: 'step_discover', fullKey: 'step_discover_full' },
  { path: '/export', labelKey: 'step_export', fullKey: 'step_export_full' },
];

export default function Layout({ children, progress = 25 }) {
  const location = useLocation();
  const navigate = useNavigate();
  const { trip, updateTrip } = useTrip();
  const { t } = useSiteI18n();
  const [menuOpen, setMenuOpen] = useState(false);

  const currentStepIndex = STEPS.findIndex((s) => s.path === location.pathname);
  const currentStep = STEPS.find((s) => s.path === location.pathname);
  const currentLabel =
    (currentStep && t(currentStep.fullKey)) ||
    (location.pathname === '/profile'
      ? t('profile')
      : location.pathname === '/history'
        ? t('tripHistory')
        : t('planning'));

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
    <div className="tc-shell tc-has-page-bg">
      <div
        className={`tc-overlay${menuOpen ? ' is-open' : ''}`}
        onClick={() => setMenuOpen(false)}
        aria-hidden={!menuOpen}
      />

      <aside className={`tc-sidebar${menuOpen ? ' is-open' : ''}`} aria-label={t('tripSteps')}>
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
            aria-label={t('closeMenu')}
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
                <span className="tc-nav-label">{t(step.fullKey)}</span>
                {done && <span className="tc-nav-chip">{t('done')}</span>}
                {index === currentStepIndex && (
                  <span className="tc-nav-chip is-current">
                    {currentStepIndex + 1}/{STEPS.length}
                  </span>
                )}
              </NavLink>
            );
          })}
        </nav>

        <NavLink
          to="/history"
          className={({ isActive }) => `tc-nav-item${isActive ? ' is-active' : ''}`}
          style={{ marginTop: 8 }}
        >
          <span className="tc-nav-index">H</span>
          <span className="tc-nav-label">{t('tripHistory')}</span>
        </NavLink>
      </aside>

      <div className="tc-main">
        <header className="tc-topbar">
          <div className="tc-topbar-left">
            <button
              type="button"
              className={`tc-burger${menuOpen ? ' is-open' : ''}`}
              onClick={() => setMenuOpen((o) => !o)}
              aria-label={menuOpen ? t('closeMenu') : t('openMenu')}
              aria-expanded={menuOpen}
            >
              <span />
              <span />
              <span />
            </button>
            <div className="tc-breadcrumb">
              <span className="tc-breadcrumb-muted">{t('dashboard')}</span>
              <span className="tc-breadcrumb-sep" aria-hidden="true">
                /
              </span>
              <span className="tc-breadcrumb-active">{currentLabel}</span>
            </div>
          </div>

          <input
            className="tc-search"
            type="search"
            placeholder={t('searchAttractions')}
            value={trip.landmarkSearch || ''}
            onChange={(e) => {
              const value = e.target.value;
              updateTrip({ landmarkSearch: value });
              if (location.pathname !== '/attractions') navigate('/attractions');
            }}
            onKeyDown={(e) => {
              if (e.key !== 'Enter') return;
              e.preventDefault();
              if (location.pathname !== '/attractions') navigate('/attractions');
            }}
            aria-label={t('searchAttractions')}
            autoComplete="off"
          />

          <div className="tc-topbar-right">
            <div className="tc-progress" aria-label={`${t('tripProgress')} ${progress}%`}>
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
              title={t('tripHistory')}
            >
              {t('history')}
            </NavLink>
          </div>
        </header>

        <main className="tc-content">{children}</main>
      </div>
    </div>
  );
}
