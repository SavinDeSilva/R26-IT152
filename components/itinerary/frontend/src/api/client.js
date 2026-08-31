import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  const lang = 'en';
  config.headers['X-Site-Language'] = lang;
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status;
    const url = String(error.config?.url || '');
    const isAuthRoute =
      url.includes('/auth/login') ||
      url.includes('/auth/register') ||
      url.includes('/auth/google') ||
      url.includes('/auth/link-account');
    const body = error.response?.data || {};
    const msg = String(body.msg || body.error || body.code || '').toLowerCase();
    const jwtFailure =
      !isAuthRoute &&
      (status === 401 || status === 422) &&
      (msg.includes('token') ||
        msg.includes('authorization') ||
        msg.includes('signature') ||
        msg.includes('expired') ||
        msg.includes('session_expired') ||
        msg === 'missing authorization header');

    if (jwtFailure) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      localStorage.removeItem('touristToken');
      localStorage.removeItem('touristId');
      localStorage.removeItem('touristName');
      if (window.location.pathname !== '/login') {
        window.location.assign('/login');
      }
    }
    return Promise.reject(error);
  }
);

export const authApi = {
  register: (email, password) => api.post('/auth/register', { email, password }),
  login: (email, password) => api.post('/auth/login', { email, password }),
  google: (credential) => api.post('/auth/google', { credential }),
  googleConfig: () => api.get('/auth/google/config'),
  me: () => api.get('/auth/me'),
  linkAccount: (email, password, name) =>
    api.post('/auth/link-account', { email, password, name }),
};

export const attractionsApi = {
  /** List catalog in English for fast load; mood/category labels are localized in the UI. */
  list: (moods = [], options = {}) => {
    const { lang = 'en', signal, timeout = 20000 } = options;
    const params = { lang, ...(moods.length ? { moods: moods.join(',') } : {}) };
    return api.get('/attractions', { params, timeout, signal });
  },
  get: (id, lang) => {
    const siteLang = 'en';
    return api.get(`/attractions/${id}`, { params: { lang: siteLang }, timeout: 45000 });
  },
};

export const imagesApi = {
  resolve: (url, q) => api.get('/images/resolve', { params: { url, q } }),
};

export const tripApi = {
  list: () => api.get('/trip-input'),
  create: (payload, options = {}) => api.post('/trip-input', payload, options),
  update: (tripId, payload) => api.patch(`/trip-input/${tripId}`, payload),
  get: (tripId) => api.get(`/trip-input/${tripId}`),
};

export const budgetApi = {
  split: (payload) => api.post('/budget/split', payload),
  get: (tripId) => api.get(`/budget/split/${tripId}`),
};

export const accommodationApi = {
  list: (tripId, roomType, query) =>
    api.get('/accommodation', {
      params: {
        trip_id: tripId,
        ...(roomType ? { room_type: roomType } : {}),
        ...(query ? { q: query } : {}),
      },
    }),
  search: (query, roomType) =>
    api.get('/accommodation/search', {
      params: {
        q: query,
        ...(roomType ? { room_type: roomType } : {}),
      },
    }),
};

/**
 * itineraryApi = object with functions that talk to the itinerary server URLs.
 *
 * generate(tripId, { dayStart })
 *   What it does: asks server to build the day plan.
 *   dayStart empty = Auto by mood; or pass "08:30 AM".
 *
 * get(tripId)
 *   What it does: loads the saved plan for one trip.
 *
 * history()
 *   What it does: lists old plans (History page).
 *
 * pdfUrl(tripId)
 *   What it does: returns the PDF download link (Export page).
 */
export const itineraryApi = {
  generate: (tripId, options = {}) =>
    api.post('/itinerary/generate', {
      trip_id: tripId,
      day_start: options.dayStart || options.day_start || undefined,
    }),
  get: (tripId) => api.get(`/itinerary/${tripId}`),
  updateActivityTime: (tripId, { day, index, time }) =>
    api.patch(`/itinerary/${tripId}/activities`, { day, index, time }),
  history: () => api.get('/itinerary/history'),
  pdfUrl: (tripId) => `${import.meta.env.VITE_API_URL || '/api'}/itinerary/${tripId}/pdf`,
};

export const recommendationsApi = {
  businesses: (tripId) =>
    api.get('/business-directory', { params: tripId ? { trip_id: tripId } : {} }),
  agencies: (tripId) =>
    api.get('/travel-agencies', { params: tripId ? { trip_id: tripId } : {} }),
  guides: (filters = {}) =>
    api.get('/tourist-guides', {
      params: {
        name: filters.name || undefined,
        registration_no: filters.registration_no || undefined,
        guide_type: filters.guide_type || undefined,
        language: filters.language || undefined,
        limit: filters.limit ?? 200,
        offset: filters.offset ?? 0,
      },
    }),
};

export const savedRefsApi = {
  save: (payload) => api.post('/saved-references', payload),
  list: (tripId) =>
    api.get('/saved-references', { params: tripId ? { trip_id: tripId } : {} }),
};

export const riskApi = {
  sites: () => api.get('/risk/sites'),
  itineraryCheck: (sites, date) =>
    api.post('/risk/itinerary-check', {
      sites: (sites || []).map((id) => Number(id)).filter((id) => Number.isFinite(id)),
      date: date || new Date().toISOString().slice(0, 10),
    }),
};

export default api;
