import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Download, MapPin, MessageCircle, Siren } from 'lucide-react'
import CallNearestHospital from '../components/CallNearestHospital'
import IncidentChat from '../components/IncidentChat'
import IncidentWorkflow from '../components/IncidentWorkflow'
import TouristNav from '../components/TouristNav'
import SOSButton from '../components/SOSButton'
import { LivePulseDot, RadarDisplay, ensureMotionStyles } from '../components/AmbientBackground'
import api from '../api/client'
import { cardStyle, statusColors, T } from '../theme'
import { SITES } from '@shared/config'

export default function Home({ activeIncidentId, onCurrentIncident, onTrigger, sending, sendingType }) {
  const [touristId, setTouristId] = useState('')
  const [stationName, setStationName] = useState('')
  const [current, setCurrent] = useState(null)
  const [recentHistory, setRecentHistory] = useState([])
  const [installHint, setInstallHint] = useState(false)
  const [deferredPrompt, setDeferredPrompt] = useState(null)

  const loadIncidents = useCallback(async () => {
    try {
      const { data } = await api.get('/api/tourists/me/incidents')
      setCurrent(data.current)
      setRecentHistory((data.history || []).slice(0, 3))
      if (data.current?.id) {
        localStorage.setItem('activeIncidentId', String(data.current.id))
        if (data.current.station?.display_name) {
          localStorage.setItem('activeStationName', data.current.station.display_name)
          setStationName(data.current.station.display_name)
        }
        onCurrentIncident?.(String(data.current.id))
      }
    } catch {
      /* ignore poll errors */
    }
  }, [onCurrentIncident])

  useEffect(() => {
    ensureMotionStyles()
    setTouristId(localStorage.getItem('touristId') || '')
    setStationName(localStorage.getItem('activeStationName') || '')
    loadIncidents()
    const poll = setInterval(loadIncidents, 7000)

    const onBip = (e) => {
      e.preventDefault()
      setDeferredPrompt(e)
      setInstallHint(true)
    }
    window.addEventListener('beforeinstallprompt', onBip)
    return () => {
      clearInterval(poll)
      window.removeEventListener('beforeinstallprompt', onBip)
    }
  }, [activeIncidentId, loadIncidents])

  const install = async () => {
    if (!deferredPrompt) return
    deferredPrompt.prompt()
    await deferredPrompt.userChoice
    setDeferredPrompt(null)
    setInstallHint(false)
  }

  const incidentId = activeIncidentId || (current?.id ? String(current.id) : null)
  const st = statusColors[current?.status || 'open'] || statusColors.open

  const tiles = [
    { icon: Siren, title: 'One-tap SOS', text: 'Six emergency types' },
    { icon: MapPin, title: 'Current location', text: 'Fresh read on SOS only' },
    { icon: MessageCircle, title: 'Station chat', text: 'Text · photo · voice' },
  ]

  return (
    <>
      <TouristNav />
      <div className="sos-enter sos-page" style={{ fontFamily: T.fontBody }}>
        <section
          style={{
            position: 'relative',
            overflow: 'hidden',
            borderRadius: 14,
            padding: '28px 24px 24px',
            marginBottom: 16,
            minHeight: 200,
            background: `linear-gradient(90deg, rgba(8, 32, 38, 0.82) 0%, rgba(10, 74, 82, 0.62) 55%, rgba(10, 74, 82, 0.38) 100%), url('/bgi.jpg') center/cover no-repeat`,
            color: T.white,
            boxShadow: '0 16px 40px rgba(10, 74, 82, 0.28)',
          }}
        >
          <div style={{ position: 'absolute', right: '-18%', top: '-35%', width: '72%', height: '160%', opacity: 0.55 }}>
            <RadarDisplay
              sweepColor="rgba(180, 255, 250, 0.55)"
              ringColor="rgba(255,255,255,0.22)"
              centerColor="rgba(255,255,255,0.95)"
              duration={3.8}
            />
          </div>
          <div style={{ position: 'relative', zIndex: 1 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 12, marginBottom: 14 }}>
              <button
                type="button"
                onClick={() => window.location.assign(`${SITES.police.replace(/\/$/, '')}/login`)}
                style={{
                  margin: 0,
                  padding: 0,
                  border: 0,
                  background: 'transparent',
                  color: 'inherit',
                  font: 'inherit',
                  fontSize: 12,
                  fontWeight: 600,
                  opacity: 0.8,
                  letterSpacing: '0.04em',
                  textTransform: 'uppercase',
                  cursor: 'pointer',
                }}
              >
                Radar desk
              </button>
              <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6, background: 'rgba(255,255,255,0.12)', padding: '5px 10px', borderRadius: 999, fontSize: 11, fontWeight: 700 }}>
                <LivePulseDot color="#6EE7B7" size={6} />
                {current ? st.label : 'Scanning'}
              </span>
            </div>
            <h1 style={{ margin: 0, fontFamily: T.fontBody, fontSize: 'clamp(1.7rem, 4vw, 2.2rem)', fontWeight: 800, lineHeight: 1.15 }}>
              Tourist SOS
            </h1>
            <p style={{ margin: '10px 0 0', fontSize: 14.5, lineHeight: 1.5, opacity: 0.88, maxWidth: '34ch' }}>
              {current
                ? `Active case #${current.id} with your nearest station.`
                : 'Tap an emergency type below. Only the nearest police station is notified.'}
            </p>
          </div>
        </section>

        <div className="sos-tiles">
          {tiles.map(({ icon: Icon, title, text }) => (
            <div key={title} style={{ ...cardStyle, padding: '16px 14px' }}>
              <div style={{ width: 36, height: 36, marginBottom: 10, borderRadius: 8, background: T.navySoft, color: T.navy, display: 'grid', placeItems: 'center' }}>
                <Icon size={16} strokeWidth={2} />
              </div>
              <p style={{ margin: 0, fontSize: 15, fontWeight: 700, color: T.ink }}>{title}</p>
              <p style={{ margin: '4px 0 0', fontSize: 13, color: T.muted, lineHeight: 1.4 }}>{text}</p>
            </div>
          ))}
        </div>

        <SOSButton
          variant="page"
          onTrigger={onTrigger}
          sending={sending}
          sendingType={sendingType}
          statusLabel={current ? st.label : 'Ready'}
        />

        {incidentId && touristId && (
          <IncidentWorkflow incidentId={incidentId} touristId={touristId} />
        )}

        <section style={{ marginBottom: 14 }} id="sos-chat">
          {incidentId && touristId ? (
            <IncidentChat
              incidentId={incidentId}
              mode="tourist"
              touristId={touristId}
              stationName={stationName || current?.station?.display_name}
            />
          ) : (
            <div style={{ ...cardStyle, padding: '18px 16px', border: `1px dashed ${T.line}`, background: T.navySoft }}>
              <p style={{ margin: 0, display: 'inline-flex', alignItems: 'center', gap: 8, fontSize: 14, fontWeight: 700, color: T.navy }}>
                <MessageCircle size={18} strokeWidth={2} />
                Station chat
              </p>
              <p style={{ margin: '8px 0 0', fontSize: 13.5, lineHeight: 1.45, color: T.muted }}>
                After you send SOS, chat with the nearest station here (text, photos, voice).
              </p>
            </div>
          )}
        </section>

        {recentHistory.length > 0 && (
          <section style={{ ...cardStyle, padding: '14px 14px', marginBottom: 14 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
              <p style={{ margin: 0, fontSize: 12, fontWeight: 700, color: T.muted, textTransform: 'uppercase' }}>Recent history</p>
              <Link to="/history" style={{ fontSize: 13, fontWeight: 700, color: T.navy, textDecoration: 'none' }}>See all</Link>
            </div>
            {recentHistory.map((i) => (
              <div key={i.id} style={{ display: 'flex', justifyContent: 'space-between', gap: 8, padding: '8px 0', borderTop: `1px solid ${T.lineSoft}`, fontSize: 13 }}>
                <span style={{ color: T.ink, fontWeight: 600 }}>#{i.id} · {i.incident_type_label || i.incident_type}</span>
                <span style={{ color: T.muted, fontFamily: T.fontMono, fontSize: 11 }}>
                  {i.triggered_at ? new Date(i.triggered_at).toLocaleDateString() : ''}
                </span>
              </div>
            ))}
          </section>
        )}

        <CallNearestHospital />

        {installHint && (
          <button
            type="button"
            onClick={install}
            style={{
              marginTop: 12, width: '100%', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: 8,
              border: `1px solid ${T.line}`, background: T.surface, color: T.navy, borderRadius: T.radiusSm,
              padding: '13px 16px', fontWeight: 600, cursor: 'pointer', fontFamily: T.fontBody, boxShadow: T.shadowSm,
            }}
          >
            <Download size={18} strokeWidth={2} />
            Install on home screen
          </button>
        )}
      </div>
    </>
  )
}
