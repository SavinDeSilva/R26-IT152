import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { authApi } from '../api/client';
import sosApi, {
  clearLinkedTouristSession,
  linkSosAccount,
  linkSosGoogle,
  saveLinkedTouristSession,
} from '../api/sosClient';
import { clearTravelSessionCookie, hydrateTravelSessionFromCookie, writeTravelSessionCookie } from '@shared/travelSession';

const AuthContext = createContext(null);

function persistAuth(data) {
  localStorage.setItem('access_token', data.access_token);
  localStorage.setItem('user', JSON.stringify(data.user));
  writeTravelSessionCookie(data.access_token, data.user);
}

function clearAuthStorage() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('user');
  clearLinkedTouristSession();
  clearTravelSessionCookie();
}

/** Return true if JWT `exp` is in the past (or token unreadable). */
function isJwtExpired(token) {
  if (!token) return true;
  try {
    const payload = JSON.parse(atob(token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')));
    if (!payload?.exp) return false;
    // small clock skew allowance
    return payload.exp * 1000 < Date.now() - 5000;
  } catch {
    return true;
  }
}

async function syncSosSession(data, { email, password, credential } = {}) {
  try {
    if (credential) {
      await linkSosGoogle(credential);
      return;
    }
    if (email && password) {
      await linkSosAccount({
        email,
        password,
        name: data?.user?.name || undefined,
      });
    }
  } catch (err) {
    console.warn('Could not link Tourist SOS session', err?.response?.data || err);
  }
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    hydrateTravelSessionFromCookie();
    const saved = localStorage.getItem('user');
    return saved ? JSON.parse(saved) : null;
  });
  const [token, setToken] = useState(() => {
    hydrateTravelSessionFromCookie();
    return localStorage.getItem('access_token');
  });
  const [ready, setReady] = useState(false);

  const logout = useCallback(() => {
    clearAuthStorage();
    setToken(null);
    setUser(null);
  }, []);

  // Drop stale tokens on load (fixes "logged in" UI with expired JWT)
  useEffect(() => {
    let cancelled = false;

    async function validate() {
      const stored = localStorage.getItem('access_token');
      if (!stored) {
        if (!cancelled) {
          setToken(null);
          setUser(null);
          setReady(true);
        }
        return;
      }

      if (isJwtExpired(stored)) {
        clearAuthStorage();
        if (!cancelled) {
          setToken(null);
          setUser(null);
          setReady(true);
        }
        return;
      }

      try {
        const { data } = await authApi.me();
        if (cancelled) return;
        if (data?.user) {
          setUser(data.user);
          localStorage.setItem('user', JSON.stringify(data.user));
          writeTravelSessionCookie(stored, data.user);
          setToken(stored);
        } else {
          clearAuthStorage();
          setToken(null);
          setUser(null);
        }
      } catch {
        clearAuthStorage();
        if (!cancelled) {
          setToken(null);
          setUser(null);
        }
      } finally {
        if (!cancelled) setReady(true);
      }
    }

    validate();
    return () => {
      cancelled = true;
    };
  }, []);

  const applyAuth = useCallback(async (data, syncOpts) => {
    persistAuth(data);
    setToken(data.access_token);
    setUser(data.user);
    await syncSosSession(data, syncOpts);
    return data;
  }, []);

  const login = useCallback(async (email, password) => {
    try {
      const { data } = await authApi.login(email, password);
      return applyAuth(data, { email, password });
    } catch (err) {
      try {
        const { data: sos } = await sosApi.post('/api/tourists/login', { email, password });
        saveLinkedTouristSession(sos);
        const { data } = await authApi.linkAccount(email, password, sos?.tourist?.name);
        persistAuth(data);
        setToken(data.access_token);
        setUser(data.user);
        return data;
      } catch {
        throw err;
      }
    }
  }, [applyAuth]);

  const register = useCallback(async (email, password) => {
    const { data } = await authApi.register(email, password);
    return applyAuth(data, { email, password });
  }, [applyAuth]);

  const loginWithGoogle = useCallback(async (credential) => {
    const { data } = await authApi.google(credential);
    return applyAuth(data, { credential });
  }, [applyAuth]);

  const value = useMemo(
    () => ({
      user,
      token,
      ready,
      isAuthenticated: !!token && !isJwtExpired(token),
      touristLinked: !!localStorage.getItem('touristToken'),
      login,
      register,
      loginWithGoogle,
      logout,
    }),
    [user, token, ready, login, register, loginWithGoogle, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
