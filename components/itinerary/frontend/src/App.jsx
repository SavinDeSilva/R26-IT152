import { Navigate, Route, Routes } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import Layout from './components/Layout';
import LoginPage from './pages/LoginPage';
import HomePage from './pages/HomePage';
import AttractionsPage from './pages/AttractionsPage';
import BudgetPage from './pages/BudgetPage';
import AccommodationPage from './pages/AccommodationPage';
import ItineraryPage from './pages/ItineraryPage';
import RecommendationsPage from './pages/RecommendationsPage';
import ExportPage from './pages/ExportPage';
import ProfilePage from './pages/ProfilePage';
import HistoryPage from './pages/HistoryPage';
import SiteChrome from '@shared/SiteChrome';
import { SITES } from '@shared/config';
import { openSosDashboard } from './api/sosClient';
import PageBackground from './components/PageBackground';

import { useSiteI18n } from '@shared/i18n/react';

function ProtectedRoute({ children }) {
  const { t } = useSiteI18n();
  const { isAuthenticated, ready } = useAuth();
  if (!ready) {
    return (
      <div style={{ padding: 40, textAlign: 'center', fontFamily: 'sans-serif' }}>
        {t('checkingLogin')}
      </div>
    );
  }
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return children;
}

function TravelChrome({ active, children }) {
  const { isAuthenticated, user, logout } = useAuth();

  const onSosClick = async (e) => {
    e.preventDefault();
    if (isAuthenticated) {
      await openSosDashboard('/');
      return;
    }
    window.location.assign(SITES.sos);
  };

  const onLogout = () => {
    logout();
    window.location.assign('/login');
  };

  return (
    <div className="tc-travel-shell tc-has-page-bg">
      <PageBackground />
      <SiteChrome
        app="travel"
        active={active}
        onSosClick={onSosClick}
        isAuthenticated={isAuthenticated}
        user={user}
        onLogout={onLogout}
      >
        {children}
      </SiteChrome>
    </div>
  );
}

export default function App() {
  return (
    <Routes>
      <Route
        path="/"
        element={(
          <TravelChrome active="home">
            <HomePage />
          </TravelChrome>
        )}
      />
      <Route
        path="/login"
        element={(
          <TravelChrome active="home">
            <LoginPage />
          </TravelChrome>
        )}
      />
      <Route
        path="/*"
        element={
          <ProtectedRoute>
            <TravelChrome active="itinerary">
              <Routes>
                <Route path="/attractions" element={<Layout progress={25}><AttractionsPage /></Layout>} />
                <Route path="/budget" element={<Layout progress={45}><BudgetPage /></Layout>} />
                <Route path="/accommodation" element={<Layout progress={65}><AccommodationPage /></Layout>} />
                <Route path="/itinerary" element={<Layout progress={80}><ItineraryPage /></Layout>} />
                <Route path="/recommendations" element={<Layout progress={90}><RecommendationsPage /></Layout>} />
                <Route path="/export" element={<Layout progress={100}><ExportPage /></Layout>} />
                <Route path="/history" element={<Layout progress={100}><HistoryPage /></Layout>} />
                <Route path="/profile" element={<Layout progress={100}><ProfilePage /></Layout>} />
                <Route path="*" element={<Navigate to="/attractions" replace />} />
              </Routes>
            </TravelChrome>
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}
