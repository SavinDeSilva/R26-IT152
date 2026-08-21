import axios from 'axios'

/**
 * Links this visitor login to the Tour Ceylon travel app user account.
 * Soft-fails if travel API is offline so SOS still works alone.
 */
const travelApi = axios.create({
  baseURL: import.meta.env.VITE_TRAVEL_API_URL || 'http://127.0.0.1:5002/api',
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

export function saveTravelSession({ access_token, user }) {
  if (access_token) localStorage.setItem('access_token', access_token)
  if (user) localStorage.setItem('user', JSON.stringify(user))
}

export function clearTravelSession() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('user')
}

export async function travelLogin(email, password) {
  const { data } = await travelApi.post('/auth/login', { email, password })
  saveTravelSession(data)
  return data
}

export async function linkTravelAccount({ email, password, name }) {
  const { data } = await travelApi.post('/auth/link-account', {
    email,
    password,
    name,
  })
  saveTravelSession(data)
  return data
}

export async function linkTravelGoogle(credential) {
  const { data } = await travelApi.post('/auth/google', { credential })
  saveTravelSession(data)
  return data
}
