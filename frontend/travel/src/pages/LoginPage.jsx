import { useEffect, useRef, useState } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const GOOGLE_SCRIPT = 'https://accounts.google.com/gsi/client';

export default function LoginPage() {
  const { login, register, loginWithGoogle, isAuthenticated } = useAuth();
  const [email, setEmail] = useState('test@example.com');
  const [password, setPassword] = useState('secret123');
  const [mode, setMode] = useState('login');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [googleReady, setGoogleReady] = useState(false);
  const [googleEnabled, setGoogleEnabled] = useState(false);
  const googleBtnRef = useRef(null);
  const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID || '';

  useEffect(() => {
    let cancelled = false;

    const setupGoogle = async () => {
      if (!googleClientId) {
        setGoogleEnabled(false);
        return;
      }
      setGoogleEnabled(true);

      const handleCredential = async (response) => {
        if (!response?.credential) {
          setError('Google Sign-In failed. No credential returned.');
          return;
        }
        setError('');
        setLoading(true);
        try {
          await loginWithGoogle(response.credential);
        } catch (err) {
          setError(err.response?.data?.error || 'Google Sign-In failed');
        } finally {
          setLoading(false);
        }
      };

      const renderButton = () => {
        if (cancelled || !window.google?.accounts?.id || !googleBtnRef.current) return;
        googleBtnRef.current.innerHTML = '';
        window.google.accounts.id.initialize({
          client_id: googleClientId,
          callback: handleCredential,
          auto_select: false,
          cancel_on_tap_outside: true,
        });
        window.google.accounts.id.renderButton(googleBtnRef.current, {
          theme: 'outline',
          size: 'large',
          text: 'continue_with',
          shape: 'pill',
          width: 340,
        });
        if (!cancelled) setGoogleReady(true);
      };

      if (window.google?.accounts?.id) {
        renderButton();
        return;
      }

      const existing = document.querySelector(`script[src="${GOOGLE_SCRIPT}"]`);
      if (existing) {
        existing.addEventListener('load', renderButton);
        return;
      }

      const script = document.createElement('script');
      script.src = GOOGLE_SCRIPT;
      script.async = true;
      script.defer = true;
      script.onload = renderButton;
      script.onerror = () => {
        if (!cancelled) setError('Could not load Google Sign-In. Check your network.');
      };
      document.head.appendChild(script);
    };

    setupGoogle();
    return () => {
      cancelled = true;
    };
  }, [googleClientId, loginWithGoogle]);

  if (isAuthenticated) return <Navigate to="/attractions" replace />;

  const submit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      if (mode === 'login') await login(email, password);
      else await register(email, password);
    } catch (err) {
      setError(err.response?.data?.error || 'Authentication failed');
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
          Sign in to plan your trip
        </h2>
        {error && <div className="error">{error}</div>}

        {googleEnabled && (
          <>
            <div
              ref={googleBtnRef}
              style={{
                display: 'flex',
                justifyContent: 'center',
                minHeight: 44,
                marginBottom: 12,
                opacity: googleReady && !loading ? 1 : 0.6,
                pointerEvents: loading ? 'none' : 'auto',
              }}
            />
            {!googleReady && (
              <p style={{ textAlign: 'center', color: 'var(--muted)', fontSize: 13, marginTop: 0 }}>
                Loading Google Sign-In…
              </p>
            )}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 10,
                margin: '8px 0 16px',
                color: 'var(--muted)',
                fontSize: 13,
              }}
            >
              <span style={{ flex: 1, height: 1, background: 'var(--border)' }} />
              or continue with email
              <span style={{ flex: 1, height: 1, background: 'var(--border)' }} />
            </div>
          </>
        )}

        {!googleEnabled && (
          <div
            className="info"
            style={{ marginBottom: 14, fontSize: 13 }}
          >
            Google Sign-In is available once you set <code>VITE_GOOGLE_CLIENT_ID</code> and{' '}
            <code>GOOGLE_CLIENT_ID</code> (same Client ID from Google Cloud Console).
          </div>
        )}

        <label style={{ display: 'block', marginBottom: 12 }}>
          Email
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
          Password
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
          {loading ? 'Please wait...' : mode === 'login' ? 'Sign In' : 'Create Account'}
        </button>
        <button
          type="button"
          className="btn btn-outline"
          style={{ width: '100%', marginTop: 10, justifyContent: 'center' }}
          onClick={() => setMode(mode === 'login' ? 'register' : 'login')}
        >
          {mode === 'login' ? 'Need an account? Register' : 'Already have an account? Sign in'}
        </button>
      </form>
    </div>
  );
}
