import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import { AuthProvider } from './context/AuthContext';
import { TripProvider } from './context/TripContext';
import './styles/global.css';
import { getSiteLanguage } from '@shared/i18n';

document.documentElement.lang = 'en';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <AuthProvider>
        <TripProvider>
          <App />
        </TripProvider>
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>
);
