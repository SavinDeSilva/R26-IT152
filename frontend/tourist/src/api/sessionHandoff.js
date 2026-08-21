import { saveTouristSession } from './client'

const TRAVEL_APP_URL = import.meta.env.VITE_TRAVEL_APP_URL || 'http://localhost:5180'

/**
 * Accept visitor session from Tour Ceylon (different Vite port → separate localStorage).
 * Clears handoff params from the URL after applying.
 */
export function applyTravelHandoff() {
  const params = new URLSearchParams(window.location.search)
  const handoff = params.get('handoff')
  const travel = params.get('travel')
  const touristId = params.get('touristId')
  const touristName = params.get('touristName')
  const next = params.get('next')

  if (!handoff && !travel) return false

  if (handoff) {
    saveTouristSession({
      access_token: handoff,
      tourist: {
        id: touristId || undefined,
        name: touristName || undefined,
      },
    })
  }
  if (travel) {
    try {
      localStorage.setItem('travelHandoffToken', travel)
    } catch {
      /* ignore */
    }
  }
  if (next) {
    try {
      localStorage.setItem('sosEnterNext', next)
    } catch {
      /* ignore */
    }
  }

  ;['handoff', 'travel', 'touristId', 'touristName', 'next'].forEach((k) => params.delete(k))
  const qs = params.toString()
  const path = `${window.location.pathname}${qs ? `?${qs}` : ''}${window.location.hash}`
  window.history.replaceState({}, '', path)
  return true
}

export function travelLoginUrl(path = '/login') {
  const base = TRAVEL_APP_URL.endsWith('/') ? TRAVEL_APP_URL.slice(0, -1) : TRAVEL_APP_URL
  return `${base}${path.startsWith('/') ? path : `/${path}`}`
}

export function goToTravelLogin() {
  window.location.assign(travelLoginUrl('/login'))
}

export function goToTravelApp(path = '/attractions') {
  window.location.assign(travelLoginUrl(path))
}
