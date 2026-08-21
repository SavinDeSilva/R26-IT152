import axios from 'axios'

/**
 * Talks to the Tourist SOS API (proxied as /sos-api in Vite).
 * Uses touristToken so Profile / SOS data stay scoped to the linked visitor account.
 */
const sosApi = axios.create({
  baseURL: import.meta.env.VITE_SOS_API_URL || '/sos-api',
  timeout: 20000,
});

sosApi.interceptors.request.use((config) => {
  const token = localStorage.getItem('touristToken');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export function saveLinkedTouristSession({ access_token, tourist }) {
  if (access_token) localStorage.setItem('touristToken', access_token);
  if (tourist?.id != null) localStorage.setItem('touristId', String(tourist.id));
  if (tourist?.name) localStorage.setItem('touristName', tourist.name);
}

export function clearLinkedTouristSession() {
  localStorage.removeItem('touristToken');
  localStorage.removeItem('touristId');
  localStorage.removeItem('touristName');
  localStorage.removeItem('activeIncidentId');
  localStorage.removeItem('activeStationName');
}

export async function linkSosAccount({ email, password, name }) {
  const { data } = await sosApi.post('/api/tourists/link-account', {
    email,
    password,
    name,
  });
  saveLinkedTouristSession(data);
  return data;
}

export async function linkSosGoogle(credential) {
  const { data } = await sosApi.post('/api/tourists/google', { credential });
  saveLinkedTouristSession(data);
  return data;
}

/** Always create a fresh SOS visitor session from the current Tour Ceylon login. */
export async function ensureSosSession() {
  const travelToken = localStorage.getItem('access_token');
  if (!travelToken) return false;

  const { data } = await sosApi.post('/api/tourists/bridge-travel', {
    travel_token: travelToken,
  });
  saveLinkedTouristSession(data);
  return true;
}

export const sosTouristApi = {
  me: () => sosApi.get('/api/tourists/me'),
  updateMe: (formData) =>
    sosApi.patch('/api/tourists/me', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  incidents: () => sosApi.get('/api/tourists/me/incidents'),
};

/**
 * Open Tourist SOS Home with the Tour Ceylon login (no separate SOS login).
 */
export async function openSosDashboard(path = '/') {
  const travelToken = localStorage.getItem('access_token');
  if (!travelToken) {
    window.alert('Please sign in on Tour Ceylon first, then open SOS.');
    return;
  }

  try {
    const ok = await ensureSosSession();
    if (!ok) {
      window.alert('Please sign in on Tour Ceylon first, then open SOS.');
      return;
    }
  } catch (err) {
    console.error(err);
    const apiError = err?.response?.data?.error;
    const code = err?.response?.data?.code;
    const status = err?.response?.status;
    if (status === 401 || code === 'session_expired') {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      clearLinkedTouristSession();
      window.alert(
        apiError ||
          'Your login expired. Please log in again, then click SOS.',
      );
      window.location.assign('/login');
      return;
    }
    window.alert(
      apiError ||
        (status
          ? `Could not open SOS (API error ${status}). Check the Tour Ceylon API on port 5002.`
          : 'Could not open SOS. Make sure the Tour Ceylon API is running on port 5002.'),
    );
    return;
  }

  const base = (import.meta.env.VITE_SOS_APP_URL || 'http://localhost:5175').replace(/\/$/, '');
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  const url = new URL(`${base}/enter`);
  const token = localStorage.getItem('touristToken');
  const touristId = localStorage.getItem('touristId');
  const touristName = localStorage.getItem('touristName');

  if (token) url.searchParams.set('handoff', token);
  url.searchParams.set('travel', travelToken);
  if (touristId) url.searchParams.set('touristId', touristId);
  if (touristName) url.searchParams.set('touristName', touristName);
  if (cleanPath && cleanPath !== '/') url.searchParams.set('next', cleanPath);

  window.location.assign(url.toString());
}

export default sosApi;
