import { useEffect, useRef, useState } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { authApi } from '../api/client';
import { useSiteI18n } from '@shared/i18n/react';

const GOOGLE_SCRIPT = 'https://accounts.google.com/gsi/client';

export default function LoginPage() {
  const { t } = useSiteI18n();
  const { login, register, loginWithGoogle, isAuthenticated } = useAuth();
  const [email, setEmail] = useState('test@example.com');
  const [password, setPassword] = useState('secret123');
  const [mode, setMode] = useState('login');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [googleReady, setGoogleReady] = useState(false);
  const [googleClientId, setGoogleClientId] = useState(import.meta.env.VITE_GOOGLE_CLIENT_ID || '');
  const googleBtnRef = useRef(null);
  const googleEnabled = Boolean(googleClientId);

  useEffect(() => {
    let cancelled = false;
    authApi
      .googleConfig()
      .then(({ data }) => {
        if (!cancelled && data?.client_id) setGoogleClientId(data.client_id);
      })
      .catch(() => {
        /* keep VITE_GOOGLE_CLIENT_ID fallback */
      });
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!googleClientId) return undefined;

    let cancelled = false;

    const handleCredential = async (response) => {
      if (!response?.credential) {
        setError(t('googleSignInNoCredential'));
        return;
      }
      setError('');
      setLoading(true);
      try {
        await loginWithGoogle(response.credential);
      } catch (err) {
        setError(err.response?.data?.error || t('googleSignInFailed'));
      } finally {
        setLoading(false);
      }
    };

    const renderButton = () => {
      if (cancelled || !window.google?.accounts?.id || !googleBtnRef.current) return;

      window.google.accounts.id.initialize({
        client_id: googleClientId,
        callback: handleCredential,
        auto_select: false,
        cancel_on_tap_outside: true,
      });

      const width = Math.min(
        Math.max(googleBtnRef.current.offsetWidth || 336, 240),
        400
      );

      googleBtnRef.current.innerHTML = '';
      window.google.accounts.id.renderButton(googleBtnRef.current, {
        theme: 'outline',
        size: 'medium',
        text: 'continue_with',
        shape: 'rectangular',
        width,
        logo_alignment: 'left',
        locale: 'en',
      });

      if (!cancelled) setGoogleReady(true);
    };

    const frame = requestAnimationFrame(renderButton);

    if (window.google?.accounts?.id) {
      return () => {
        cancelled = true;
        cancelAnimationFrame(frame);
      };
    }

    const existing = document.querySelector(`script[src="${GOOGLE_SCRIPT}"]`);
    if (existing) {
      existing.addEventListener('load', renderButton);
      return () => {
        cancelled = true;
        cancelAnimationFrame(frame);
        existing.removeEventListener('load', renderButton);
      };
    }

    const script = document.createElement('script');
    script.src = GOOGLE_SCRIPT;
    script.async = true;
    script.defer = true;
    script.onload = renderButton;
    script.onerror = () => {
      if (!cancelled) setError(t('googleSignInLoadFailed'));
    };
    document.head.appendChild(script);

    return () => {
      cancelled = true;
      cancelAnimationFrame(frame);
    };
  }, [googleClientId, loginWithGoogle, t]);

  if (isAuthenticated) return <Navigate to="/attractions" replace />;

  const submit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      if (mode === 'login') await login(email, password);
      else await register(email, password);
    } catch (err) {
      if (!err.response) {
        setError(t('serverUnreachable'));
      } else {
        setError(err.response?.data?.error || t('authFailed'));
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <form className="card beach-fade login-card" onSubmit={submit}>
        <div style={{ display: 'flex', justifyContent: 'center', marginBottom: 20 }}>
          <img
            src="/tour-ceylon-logo.png"
            alt="Tour Ceylon"
            className="login-logo"
          />
        </div>
        <h2 className="serif" style={{ marginTop: 0, textAlign: 'center' }}>
          {t('signInPlanTrip')}
        </h2>
        {error && <div className="error">{error}</div>}

        {googleEnabled && (
          <>
            <div
              className="google-auth-stack"
              style={{
                opacity: googleReady && !loading ? 1 : 0.65,
                pointerEvents: loading ? 'none' : 'auto',
              }}
            >
              <div className="google-auth-slot">
                <div
                  ref={googleBtnRef}
                  className="google-auth-btn"
                  aria-label={t('googleLogIn')}
                />
              </div>
            </div>
            {!googleReady && (
              <p style={{ textAlign: 'center', color: 'var(--muted)', fontSize: 13, marginTop: 0 }}>
                {t('loadingGoogleSignIn')}
              </p>
            )}
            <div className="auth-divider">
              <span />
              {t('orContinueEmail')}
              <span />
            </div>
          </>
        )}

        {!googleEnabled && (
          <div className="info" style={{ marginBottom: 14, fontSize: 13 }}>
            {t('googleSignInHint')}
          </div>
        )}

        <label style={{ display: 'block', marginBottom: 12 }}>
          {t('email')}
          <input
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            style={{
              width: '100%',
              marginTop: 6,
              padding: 10,
              borderRadius: 8,
              border: '1px solid var(--border)',
            }}
          />
        </label>
        <label style={{ display: 'block', marginBottom: 16 }}>
          {t('password')}
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={{
              width: '100%',
              marginTop: 6,
              padding: 10,
              borderRadius: 8,
              border: '1px solid var(--border)',
            }}
          />
        </label>
        <button
          className="btn btn-primary"
          disabled={loading}
          style={{ width: '100%', justifyContent: 'center' }}
        >
          {loading ? t('pleaseWait') : mode === 'login' ? t('signIn') : t('createAccount')}
        </button>
        <button
          type="button"
          className="btn btn-outline"
          style={{ width: '100%', marginTop: 10, justifyContent: 'center' }}
          onClick={() => setMode(mode === 'login' ? 'register' : 'login')}
        >
          {mode === 'login' ? t('needAccountRegister') : t('alreadyHaveAccount')}
        </button>
      </form>
    </div>
  );
}
