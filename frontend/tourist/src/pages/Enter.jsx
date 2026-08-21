import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api, { clearTouristSession, saveTouristSession } from '../api/client'
import { applyTravelHandoff, goToTravelLogin } from '../api/sessionHandoff'
import { T } from '../theme'

/**
 * Entry from Tour Ceylon SOS button.
 * Applies shared login handoff → opens Home (no separate SOS login).
 */
export default function Enter() {
  const navigate = useNavigate()
  const [message, setMessage] = useState('Opening SOS dashboard…')

  useEffect(() => {
    let cancelled = false

    const failToTravel = (text) => {
      if (cancelled) return
      setMessage(text)
      clearTouristSession()
      try {
        localStorage.removeItem('travelHandoffToken')
      } catch {
        /* ignore */
      }
      window.setTimeout(() => goToTravelLogin(), 600)
    }

    const goHome = () => {
      if (cancelled) return
      let next = '/'
      try {
        next = localStorage.getItem('sosEnterNext') || '/'
        localStorage.removeItem('sosEnterNext')
        localStorage.removeItem('travelHandoffToken')
      } catch {
        /* ignore */
      }
      navigate(next.startsWith('/') ? next : '/', { replace: true })
    }

    const run = async () => {
      applyTravelHandoff()

      // 1) Prefer tourist handoff JWT from Tour Ceylon
      let token = localStorage.getItem('touristToken')
      if (token) {
        try {
          const { data } = await api.get('/api/tourists/me')
          if (cancelled) return
          saveTouristSession({ tourist: data.tourist })
          goHome()
          return
        } catch {
          clearTouristSession()
          token = null
        }
      }

      // 2) Re-bridge using Tour Ceylon travel token (fresh SOS session)
      const travel =
        localStorage.getItem('travelHandoffToken') ||
        localStorage.getItem('access_token')
      if (travel) {
        setMessage('Linking your Tour Ceylon login…')
        try {
          const { data } = await api.post('/api/tourists/bridge-travel', {
            travel_token: travel,
          })
          if (cancelled) return
          saveTouristSession(data)
          goHome()
          return
        } catch (err) {
          console.error(err)
          failToTravel('Could not link session — open Tour Ceylon and sign in again…')
          return
        }
      }

      failToTravel('Please sign in on Tour Ceylon first…')
    }

    run()
    return () => {
      cancelled = true
    }
  }, [navigate])

  return (
    <div
      style={{
        minHeight: '100dvh',
        display: 'grid',
        placeItems: 'center',
        padding: 24,
        background: T.page,
        fontFamily: T.fontBody,
        color: T.ink,
      }}
    >
      <div style={{ textAlign: 'center', maxWidth: 360 }}>
        <p style={{ margin: 0, fontSize: 15, fontWeight: 700, color: T.navy }}>Tourist SOS</p>
        <p style={{ margin: '10px 0 0', color: T.muted, fontSize: 14, lineHeight: 1.45 }}>{message}</p>
      </div>
    </div>
  )
}
