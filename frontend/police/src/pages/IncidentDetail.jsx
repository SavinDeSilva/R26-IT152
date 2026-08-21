import { useCallback, useEffect, useMemo, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { ArrowLeft, FileDown } from 'lucide-react'
import api from '../api/client'
import LiveMap from '../components/LiveMap'
import IncidentChat from '../components/IncidentChat'
import ResponseClock from '../components/ResponseClock'
import { ensureMotionStyles } from '../components/AmbientBackground'
import PoliceBadge from '../components/PoliceBadge'
import { btnPrimary, panel, statusColors, typeColors, T } from '../theme'

const POLL_MS = 8000

function haversineKm(lat1, lon1, lat2, lon2) {
  const toRad = (d) => (d * Math.PI) / 180
  const r = 6371
  const dLat = toRad(lat2 - lat1)
  const dLon = toRad(lon2 - lon1)
  const a = Math.sin(dLat / 2) ** 2 + Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLon / 2) ** 2
  return 2 * r * Math.asin(Math.sqrt(a))
}

function fmt(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleString()
}

export default function IncidentDetail() {
  const { id } = useParams()
  const [incident, setIncident] = useState(null)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState('')
  const [loading, setLoading] = useState(true)

  const load = useCallback(async () => {
    try {
      const { data } = await api.get(`/api/incidents/${id}`)
      setIncident(data.incident)
      setError('')
    } catch (err) {
      setError(err?.response?.data?.error || 'Failed to load incident')
    } finally {
      setLoading(false)
    }
  }, [id])

  useEffect(() => {
    ensureMotionStyles()
    load()
    const t = setInterval(load, POLL_MS)
    return () => clearInterval(t)
  }, [load])

  const live = useMemo(() => {
    if (!incident) return { lat: null, lng: null }
    const ping = incident.latest_ping || (incident.pings || []).slice(-1)[0]
    return {
      lat: ping?.latitude ?? incident.initial_lat,
      lng: ping?.longitude ?? incident.initial_lng,
    }
  }, [incident])

  const distanceKm = useMemo(() => {
    if (!incident?.station || live.lat == null) return incident?.distance_to_station_km
    const { latitude: slat, longitude: slng } = incident.station
    if (slat == null || slng == null) return incident.distance_to_station_km
    return haversineKm(live.lat, live.lng, slat, slng)
  }, [incident, live])

  const transition = async (action) => {
    setBusy(action)
    try {
      const { data } = await api.patch(`/api/incidents/${id}/${action}`)
      setIncident(data.incident)
    } catch (err) {
      alert(err?.response?.data?.error || `Failed to ${action}`)
    } finally {
      setBusy('')
    }
  }

  const downloadPdf = async () => {
    try {
      const res = await api.get(`/api/incidents/${id}/report.pdf`, { responseType: 'blob' })
      const url = URL.createObjectURL(res.data)
      const a = document.createElement('a')
      a.href = url
      a.download = `incident_${id}_report.pdf`
      a.click()
      URL.revokeObjectURL(url)
    } catch (err) {
      alert(err?.response?.data?.error || 'PDF export failed')
    }
  }

  if (loading) return <p style={{ padding: 32, color: T.muted, fontFamily: T.fontBody }}>Loading incident…</p>
  if (error && !incident) return <p style={{ padding: 32, color: T.danger, fontFamily: T.fontBody }}>{error}</p>
  if (!incident) return <p style={{ padding: 32, color: T.muted, fontFamily: T.fontBody }}>Incident not found.</p>

  const tourist = incident.tourist || {}
  const status = incident.status
  const st = statusColors[status] || statusColors.open
  const ty = typeColors[incident.incident_type || 'general'] || typeColors.general
  const sidePanel = { ...panel, padding: '16px 16px', marginBottom: 12 }

  const wfBtn = (enabled, action, label) => (
    <button
      type="button"
      disabled={!enabled || busy}
      onClick={() => transition(action)}
      style={{
        ...btnPrimary,
        width: '100%',
        padding: '13px',
        background: !enabled || busy ? T.lineSoft : T.navy,
        color: !enabled || busy ? T.muted : T.white,
        boxShadow: !enabled || busy ? 'none' : btnPrimary.boxShadow,
        cursor: !enabled || busy ? 'not-allowed' : 'pointer',
      }}
    >
      {busy === action ? '…' : label}
    </button>
  )

  return (
    <div style={{ maxWidth: 1180, margin: '0 auto', padding: '22px 18px 44px', fontFamily: T.fontBody, animation: 'sos-fade-up 0.45s ease-out' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 14, color: T.muted, fontSize: 14 }}>
        <Link to="/" style={{ display: 'inline-flex', alignItems: 'center', gap: 6, color: T.navy, fontWeight: 600, textDecoration: 'none' }}>
          <ArrowLeft size={16} strokeWidth={2} /> Queue
        </Link>
        <span style={{ fontFamily: T.fontMono }}>Incident #{incident.id}</span>
      </div>

      <header style={{
        display: 'flex', justifyContent: 'space-between', gap: 16, alignItems: 'flex-start', flexWrap: 'wrap',
        padding: '18px 20px', marginBottom: 14, borderRadius: 16,
        background: `linear-gradient(135deg, ${T.navy} 0%, ${T.navyMid} 100%)`, color: T.white,
        boxShadow: '0 14px 36px rgba(11, 42, 74, 0.2)',
      }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: 12 }}>
          <div style={{ width: 44, height: 44, borderRadius: 10, background: '#fff', display: 'grid', placeItems: 'center', flexShrink: 0 }}>
            <PoliceBadge size={36} />
          </div>
          <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap', marginBottom: 6 }}>
            <h1 style={{ margin: 0, fontFamily: T.fontDisplay, fontSize: 'clamp(1.4rem, 3vw, 1.75rem)', fontWeight: 800, letterSpacing: '-0.02em' }}>
              {tourist.name || `Tourist #${incident.tourist_id}`}
            </h1>
            <span style={{ fontSize: 11, fontWeight: 700, padding: '3px 8px', borderRadius: 6, background: 'rgba(255,255,255,0.16)', color: '#fff' }}>{st.label}</span>
            <span style={{ fontSize: 11, fontWeight: 700, padding: '3px 8px', borderRadius: 6, background: ty.bg, color: ty.color }}>
              {incident.incident_type_label || incident.incident_type || 'General'}
            </span>
          </div>
          <p style={{ margin: 0, opacity: 0.85 }}>{tourist.nationality || '—'}</p>
          </div>
        </div>
        <ResponseClock startedAt={incident.triggered_at} endedAt={incident.closed_at} label={incident.closed_at ? 'Total response' : 'Time since SOS'} />
      </header>

      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1.4fr) minmax(280px, 1fr)', gap: 14 }}>
        <section>
          <div style={{ ...panel, overflow: 'hidden', padding: 0 }}>
            <LiveMap latitude={live.lat} longitude={live.lng} stationLat={incident.station?.latitude} stationLng={incident.station?.longitude} height={400} />
          </div>
          <p style={{ margin: '10px 0 0', color: T.muted, fontSize: 14 }}>
            Distance from station:{' '}
            <strong style={{ color: T.navy }}>{distanceKm != null ? `${Number(distanceKm).toFixed(2)} km` : '—'}</strong>
            {' · '}Location captured once at SOS (not live-tracked)
          </p>

          <div style={{ marginTop: 14 }}>
            <IncidentChat
              incidentId={incident.id}
              stationName={incident.station?.display_name}
            />
          </div>
        </section>

        <aside>
          <div style={sidePanel}>
            <h2 style={{ margin: '0 0 10px', fontSize: 13, color: T.muted, fontWeight: 700 }}>Tourist</h2>
            <dl style={{ margin: 0 }}>
              {[
                ['Phone', tourist.phone || '—'],
                ['Passport/NIC', tourist.passport_or_nic || '—'],
                ['Hotel', tourist.hotel_name || '—'],
                ['Emergency contact', tourist.emergency_contact ? `${tourist.emergency_contact.name} (${tourist.emergency_contact.phone || 'no phone'})` : '—'],
              ].map(([k, v]) => (
                <div key={k} style={{ display: 'grid', gridTemplateColumns: '110px 1fr', gap: 6, marginBottom: 8, fontSize: 14 }}>
                  <dt style={{ color: T.muted, margin: 0 }}>{k}</dt>
                  <dd style={{ margin: 0, color: T.ink, wordBreak: 'break-word' }}>{v}</dd>
                </div>
              ))}
            </dl>
          </div>

          <div style={sidePanel}>
            <h2 style={{ margin: '0 0 10px', fontSize: 13, color: T.muted, fontWeight: 700 }}>Notifications</h2>
            <ul style={{ listStyle: 'none', margin: 0, padding: 0, display: 'flex', flexDirection: 'column', gap: 6 }}>
              <li style={{ fontSize: 13.5, padding: '8px 10px', borderRadius: 8, background: incident.station_notified_at ? T.successSoft : T.lineSoft, color: incident.station_notified_at ? T.success : T.muted, fontWeight: incident.station_notified_at ? 600 : 400 }}>
                This station only {incident.station_notified_at ? '✓' : '—'}
              </li>
              <li style={{ fontSize: 13.5, padding: '8px 10px', borderRadius: 8, background: incident.contact_notified_at ? T.successSoft : T.lineSoft, color: incident.contact_notified_at ? T.success : T.muted, fontWeight: incident.contact_notified_at ? 600 : 400 }}>
                Emergency contact {incident.contact_notified_at ? '✓' : '—'}
              </li>
              <li style={{ fontSize: 13.5, padding: '8px 10px', borderRadius: 8, background: incident.hotel_notified_at ? T.successSoft : T.lineSoft, color: incident.hotel_notified_at ? T.success : T.muted, fontWeight: incident.hotel_notified_at ? 600 : 400 }}>
                Hotel {incident.hotel_notified_at ? '✓' : '—'}
              </li>
            </ul>
            <p style={{ margin: '10px 0 0', fontSize: 12, color: T.muted }}>
              Only the nearest station is notified. Other stations never see this incident. Hospitals are dial-only by the tourist.
            </p>
          </div>

          <div style={sidePanel}>
            <h2 style={{ margin: '0 0 10px', fontSize: 13, color: T.muted, fontWeight: 700 }}>Workflow</h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {wfBtn(status === 'open', 'acknowledge', '1. Acknowledge')}
              {wfBtn(status === 'acknowledged', 'dispatch', '2. Dispatched')}
              {wfBtn(status === 'dispatched' || status === 'acknowledged', 'close', '3. Closed')}
            </div>
            <dl style={{ margin: '12px 0 0' }}>
              {[
                ['Triggered', fmt(incident.triggered_at)],
                ['Acknowledged', fmt(incident.acknowledged_at)],
                ['Dispatched', fmt(incident.dispatched_at)],
                ['Closed', fmt(incident.closed_at)],
              ].map(([k, v]) => (
                <div key={k} style={{ display: 'grid', gridTemplateColumns: '110px 1fr', gap: 6, marginBottom: 6, fontSize: 13.5 }}>
                  <dt style={{ color: T.muted, margin: 0 }}>{k}</dt>
                  <dd style={{ margin: 0, color: T.ink }}>{v}</dd>
                </div>
              ))}
            </dl>
            {status === 'closed' && (
              <button
                type="button"
                onClick={downloadPdf}
                style={{ marginTop: 12, width: '100%', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: 8, border: `1px solid ${T.navy}`, background: T.surface, color: T.navy, borderRadius: T.radiusSm, padding: '12px', fontWeight: 700, cursor: 'pointer', fontFamily: T.fontBody }}
              >
                <FileDown size={16} strokeWidth={2} />
                Download PDF report
              </button>
            )}
          </div>
        </aside>
      </div>
    </div>
  )
}
