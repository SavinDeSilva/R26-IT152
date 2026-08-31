import { lazy, Suspense, useState } from 'react';
import SiteChrome from '@shared/SiteChrome';
import { ThemeProvider, useTheme } from '@risk/design/ThemeContext.jsx';
import { useSiteI18n } from '@shared/i18n/react';
import Home from '@risk/pages/Home.jsx';
import '@risk/index.css';
import '@risk/design/theme.css';

const Discover = lazy(() => import('@risk/pages/tourist/Discover.jsx'));
const DestinationDetail = lazy(() => import('@risk/pages/tourist/DestinationDetail.jsx'));

const NAV = [
  { key: 'home', labelKey: 'ldOverview' },
  { key: 'discover', labelKey: 'ldDiscover' },
];

function LiveDataApp() {
  const { t } = useSiteI18n();
  const [page, setPage] = useState('home');
  const [selectedSite, setSelectedSite] = useState(null);
  const { theme, toggleTheme } = useTheme();

  const go = (target) => {
    setPage(target);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const subnav = (
    <nav className="ld-subnav" aria-label={t('ldSubnavAria')}>
      <div className="tc-site-wrap ld-subnav-inner">
        {NAV.map((item) => {
          const active =
            page === item.key || (item.key === 'discover' && page === 'destinationDetail');
          return (
            <button
              key={item.key}
              type="button"
              className={`ld-subtab${active ? ' is-active' : ''}`}
              onClick={() => go(item.key)}
            >
              {t(item.labelKey)}
            </button>
          );
        })}
        <button
          type="button"
          className="ld-subtab"
          onClick={toggleTheme}
          aria-label={t('ldLightMode')}
          style={{ marginLeft: 'auto' }}
        >
          {theme === 'dark' ? t('ldLightMode') : t('ldDarkMode')}
        </button>
      </div>
    </nav>
  );

  let body = null;
  if (page === 'home') {
    body = <Home onGetStarted={() => go('discover')} />;
  } else if (page === 'discover') {
    body = (
      <Suspense fallback={<p style={{ padding: 32 }}>Loading destinations…</p>}>
        <Discover
          onSelectSite={(id, date) => {
            setSelectedSite({ id, date });
            setPage('destinationDetail');
            window.scrollTo({ top: 0, behavior: 'smooth' });
          }}
        />
      </Suspense>
    );
  } else {
    body = (
      <Suspense fallback={<p style={{ padding: 32 }}>Loading destination…</p>}>
        <DestinationDetail
          siteId={selectedSite ? selectedSite.id : null}
          date={selectedSite ? selectedSite.date : null}
          onSelectSite={(id, date) => {
            setSelectedSite({ id, date });
            window.scrollTo({ top: 0, behavior: 'smooth' });
          }}
          onBack={() => go('discover')}
        />
      </Suspense>
    );
  }

  return (
    <SiteChrome app="livedata" active="livedata" subnav={subnav}>
      <div className="ld-app-shell">{body}</div>
    </SiteChrome>
  );
}

export default function App() {
  return (
    <ThemeProvider>
      <LiveDataApp />
    </ThemeProvider>
  );
}
