import { useCallback, useEffect, useState } from 'react'
import { Navigate, Route, Routes, useLocation, useNavigate } from 'react-router-dom'
import Home from './pages/Home'
import Login from './pages/Login'
import Register from './pages/Register'
import Enter from './pages/Enter'
import Profile from './pages/Profile'
import History from './pages/History'
import SOSButton from './components/SOSButton'
import SOSSentOverlay from './components/SOSSentOverlay'
import AmbientBackground from './components/AmbientBackground'
import useGeolocation from './hooks/useGeolocation'
import api, { clearTouristSession, saveTouristSession } from './api/client'
import { applyTravelHandoff, goToTravelLogin } from './api/sessionHandoff'
import SiteChrome from '@shared/SiteChrome'
import { T } from './theme'
import './sos-layout.css'

function RequireAuth({ children, ready }) {
  const token = localStorage.getItem('touristToken')

  useEffect(() => {
    if (ready && !token) goToTravelLogin()
  }, [ready, token])

  if (!ready) {
    return (
      <p style={{ padding: 32, textAlign: 'center', color: T.muted, fontFamily: T.fontBody }}>
        Checking login…
      </p>
    )
  }
  if (!token) {
    return (
      <p style={{ padding: 32, textAlign: 'center', color: T.muted, fontFamily: T.fontBody }}>
        Opening Tour Ceylon login…
      </p>
    )
  }
  return children
}

export default function App() {
  const navigate = useNavigate()
  const location = useLocation()
  const { getCurrent } = useGeolocation()
  const [sending, setSending] = useState(false)
  const [sendingType, setSendingType] = useState(null)
  const [overlay, setOverlay] = useState({ visible: false, incidentId: null, type: null, station: null })
  const [touristId, setTouristId] = useState(() => localStorage.getItem('touristId'))
  const [activeIncidentId, setActiveIncidentId] = useState(() => localStorage.getItem('activeIncidentId'))
  const [sessionReady, setSessionReady] = useState(false)

  useEffect(() => {
    applyTravelHandoff()
  }, [])

  useEffect(() => {
    let cancelled = false

    // /enter owns session bootstrap — do not clear/race with it
    if (location.pathname === '/enter') {
      setSessionReady(true)
      return undefined
    }

    const validate = async () => {
      applyTravelHandoff()
      const token = localStorage.getItem('touristToken')
      if (!token) {
        if (!cancelled) {
          setTouristId(null)
          setSessionReady(true)
        }
        return
      }
      try {
        const { data } = await api.get('/api/tourists/me')
        if (cancelled) return
        saveTouristSession({ tourist: data.tourist })
        setTouristId(String(data.tourist.id))
        setActiveIncidentId(localStorage.getItem('activeIncidentId'))
      } catch {
        if (cancelled) return
        clearTouristSession()
        setTouristId(null)
        setActiveIncidentId(null)
        if (!['/login', '/register'].includes(location.pathname)) {
          goToTravelLogin()
        }
      } finally {
        if (!cancelled) setSessionReady(true)
      }
    }
    setSessionReady(false)
    validate()
    return () => {
      cancelled = true
    }
  }, [location.pathname, navigate])

  const onCurrentIncident = useCallback((id) => {
    setActiveIncidentId(id)
  }, [])

  const triggerSOS = async (type) => {
    const id = localStorage.getItem('touristId')
    const token = localStorage.getItem('touristToken')
    if (!id || !token) {
      goToTravelLogin()
      return
    }

    setOverlay({ visible: true, incidentId: null, type, station: null })
    setSending(true)
    setSendingType(type)

    if (navigator.vibrate) {
      try { navigator.vibrate([80, 40, 80]) } catch { /* ignore */ }
    }

    try {
      let coords
      try {
        coords = await getCurrent()
      } catch {
        alert('Could not get your current location. Turn on location access and try SOS again.')
        setOverlay({ visible: false, incidentId: null, type: null, station: null })
        return
      }

      const { data } = await api.post('/api/incidents', {
        tourist_id: Number(id),
        type,
        lat: coords.latitude,
        lng: coords.longitude,
        latitude: coords.latitude,
        longitude: coords.longitude,
        accuracy: coords.accuracy,
      })

      const incident = data.incident
      const incidentId = incident?.id
      const station = incident?.station || null
      setOverlay({ visible: true, incidentId, type, station })
      if (incidentId) {
        localStorage.setItem('activeIncidentId', String(incidentId))
        if (station?.display_name) {
          localStorage.setItem('activeStationName', station.display_name)
        }
        setActiveIncidentId(String(incidentId))
      }
    } catch (err) {
      console.error(err)
      const msg = err?.response?.data?.error || 'Could not reach server — retry SOS when online.'
      setOverlay({ visible: false, incidentId: null, type: null, station: null })
      if (err?.response?.status === 401 || msg === 'Tourist not found') {
        clearTouristSession()
        setTouristId(null)
        alert('Please log in again on Tour Ceylon.')
        goToTravelLogin()
        return
      }
      alert(msg)
    } finally {
      setSending(false)
      setSendingType(null)
    }
  }

  const publicPaths = ['/login', '/register', '/enter']
  const showSos = Boolean(touristId) && !publicPaths.includes(location.pathname) && sessionReady
  const isEnter = location.pathname === '/enter'

  const shell = (
    <div style={{ position: 'relative', minHeight: 'calc(100dvh - 12.5rem)', fontFamily: T.fontBody, color: T.ink, background: T.page }}>
      {!isEnter && <AmbientBackground variant="light" scan />}
      <div style={{ position: 'relative', zIndex: 1 }}>
        <Routes>
          <Route path="/enter" element={<Enter />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route
            path="/"
            element={(
              <RequireAuth ready={sessionReady}>
                <Home
                  activeIncidentId={activeIncidentId}
                  onCurrentIncident={onCurrentIncident}
                  onTrigger={triggerSOS}
                  sending={sending}
                  sendingType={sendingType}
                />
              </RequireAuth>
            )}
          />
          <Route
            path="/history"
            element={(
              <RequireAuth ready={sessionReady}>
                <History />
              </RequireAuth>
            )}
          />
          <Route
            path="/profile"
            element={(
              <RequireAuth ready={sessionReady}>
                <Profile />
              </RequireAuth>
            )}
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
      {showSos && location.pathname !== '/' && (
        <SOSButton onTrigger={triggerSOS} sending={sending} sendingType={sendingType} />
      )}
      <SOSSentOverlay
        visible={overlay.visible}
        incidentId={overlay.incidentId}
        incidentType={overlay.type}
        stationName={overlay.station?.display_name}
        onDismiss={() => {
          setOverlay({ visible: false, incidentId: null, type: null, station: null })
          requestAnimationFrame(() => {
            document.getElementById('sos-chat')?.scrollIntoView({ behavior: 'smooth', block: 'center' })
          })
        }}
      />
    </div>
  )

  if (isEnter) return shell
  return (
    <SiteChrome app="tourist" active="sos">
      {shell}
    </SiteChrome>
  )
}
