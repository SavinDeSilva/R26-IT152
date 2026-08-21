import { useState } from 'react';
import SiteChrome from '@shared/SiteChrome';
import RiskDashboard, { LIVE_DATA_NAV } from './RiskDashboard';
import './livedata.css';

export default function App() {
  const [page, setPage] = useState('home');

  const subnav = (
    <nav className="ld-subnav" aria-label="Live Data sections">
      <div className="tc-site-wrap ld-subnav-inner">
        {LIVE_DATA_NAV.map((item) => (
          <button
            key={item.key}
            type="button"
            className={`ld-subtab${page === item.key ? ' is-active' : ''}`}
            onClick={() => setPage(item.key)}
          >
            {item.label}
          </button>
        ))}
      </div>
    </nav>
  );

  return (
    <SiteChrome app="livedata" active="livedata" subnav={subnav}>
      <RiskDashboard page={page} setPage={setPage} />
    </SiteChrome>
  );
}
