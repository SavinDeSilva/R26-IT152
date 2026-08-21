import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../api/client'
import TouristNav from '../components/TouristNav'
import { cardStyle, statusColors, typeColors, T } from '../theme'

function fmt(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleString()
}

function IncidentRow({ incident }) {
  const st = statusColors[incident.status] || statusColors.open
  const ty = typeColors[incident.incident_type || 'general'] || typeColors.general
  return (
    <div style={{ ...cardStyle, padding: '14px 14px', marginBottom: 10 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 8, alignItems: 'flex-start' }}>
        <div>
          <p style={{ margin: 0, fontFamily: T.fontMono, fontSize: 12, color: T.muted }}>#{incident.id}</p>
          <p style={{ margin: '4px 0 0', fontWeight: 700, color: T.ink }}>
            {incident.incident_type_label || incident.incident_type || 'General'}
          </p>
          <p style={{ margin: '4px 0 0', fontSize: 13, color: T.muted }}>
            {incident.station?.display_name || 'Station'}
          </p>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 4, alignItems: 'flex-end' }}>
          <span style={{ fontSize: 11, fontWeight: 700, padding: '3px 8px', borderRadius: 6, background: st.bg, color: st.color }}>{st.label}</span>
          <span style={{ fontSize: 11, fontWeight: 700, padding: '3px 8px', borderRadius: 6, background: ty.bg, color: ty.color }}>
            {incident.incident_type || 'general'}
          </span>
        </div>
      </div>
      <p style={{ margin: '10px 0 0', fontSize: 12.5, color: T.muted, fontFamily: T.fontMono }}>{fmt(incident.triggered_at)}</p>
      {incident.status !== 'closed' && (
        <Link to="/" style={{ display: 'inline-block', marginTop: 10, fontSize: 13, fontWeight: 700, color: T.navy, textDecoration: 'none' }}>
          Open on SOS home →
        </Link>
      )}
    </div>
  )
}

export default function History() {
  const [current, setCurrent] = useState(null)
  const [active, setActive] = useState([])
  const [history, setHistory] = useState([])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  const load = useCallback(async () => {
    try {
      const { data } = await api.get('/api/tourists/me/incidents')
      setCurrent(data.current)
      setActive(data.active || [])
      setHistory(data.history || [])
      if (data.current?.id) {
        localStorage.setItem('activeIncidentId', String(data.current.id))
        if (data.current.station?.display_name) {
          localStorage.setItem('activeStationName', data.current.station.display_name)
        }
      }
      setError('')
    } catch (err) {
      setError(err?.response?.data?.error || 'Could not load history')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    load()
    const t = setInterval(load, 8000)
    return () => clearInterval(t)
  }, [load])

  return (
    <>
      <TouristNav />
      <div className="sos-page" style={{ fontFamily: T.fontBody, paddingBottom: '7rem' }}>
        <h1 style={{ margin: '0 0 6px', fontFamily: T.fontBody, fontSize: 24, fontWeight: 800, color: T.navy }}>SOS records</h1>
        <p style={{ margin: '0 0 16px', color: T.muted, fontSize: 14 }}>Current open cases and your past history</p>

        {loading && <p style={{ color: T.muted }}>Loading…</p>}
        {error && <p style={{ color: T.danger }}>{error}</p>}

        {!loading && (
          <>
            <p style={{ margin: '0 0 8px', fontSize: 12, fontWeight: 700, color: T.muted, textTransform: 'uppercase' }}>Current</p>
            {current ? (
              <IncidentRow incident={current} />
            ) : (
              <p style={{ ...cardStyle, padding: '14px', marginBottom: 16, color: T.muted, fontSize: 14 }}>No open SOS right now.</p>
            )}

            {active.length > 1 && (
              <>
                <p style={{ margin: '8px 0', fontSize: 12, fontWeight: 700, color: T.muted, textTransform: 'uppercase' }}>Other active</p>
                {active.slice(1).map((i) => <IncidentRow key={i.id} incident={i} />)}
              </>
            )}

            <p style={{ margin: '16px 0 8px', fontSize: 12, fontWeight: 700, color: T.muted, textTransform: 'uppercase' }}>History</p>
            {history.length === 0 ? (
              <p style={{ ...cardStyle, padding: '14px', color: T.muted, fontSize: 14 }}>No closed incidents yet.</p>
            ) : (
              history.map((i) => <IncidentRow key={i.id} incident={i} />)
            )}
          </>
        )}
      </div>
    </>
  )
}
