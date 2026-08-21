import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
  timeout: 20000,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('touristToken')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err?.response?.status === 401 && localStorage.getItem('touristToken')) {
      // Token expired / invalid — re-auth on Tour Ceylon (single login).
      // Skip hard redirect on /enter and /me so Enter.jsx can handle handoff cleanly.
      const url = err?.config?.url || ''
      const path = window.location.pathname || ''
      if (
        !url.includes('/tourists/login') &&
        !url.includes('/tourists/register') &&
        !url.includes('/tourists/google') &&
        !url.includes('/tourists/bridge-travel') &&
        !path.includes('/enter') &&
        !path.includes('/login')
      ) {
        localStorage.removeItem('touristToken')
        localStorage.removeItem('touristId')
        localStorage.removeItem('touristName')
        const travel = import.meta.env.VITE_TRAVEL_APP_URL || 'http://localhost:5180'
        window.location.href = `${travel.replace(/\/$/, '')}/login`
      }
    }
    return Promise.reject(err)
  },
)

export function saveTouristSession({ access_token, tourist }) {
  if (access_token) localStorage.setItem('touristToken', access_token)
  if (tourist?.id != null) localStorage.setItem('touristId', String(tourist.id))
  if (tourist?.name) localStorage.setItem('touristName', tourist.name)
}

export function clearTouristSession() {
  localStorage.removeItem('touristToken')
  localStorage.removeItem('touristId')
  localStorage.removeItem('touristName')
  localStorage.removeItem('activeIncidentId')
  localStorage.removeItem('activeStationName')
  try {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
  } catch {
    /* ignore */
  }
}

export default api
