import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Activity, Clock3, LogOut, RefreshCw, Siren } from 'lucide-react'
import api from '../api/client'
import IncidentCard from '../components/IncidentCard'
import StatsCharts from '../components/StatsCharts'
import { LivePulseDot, RadarDisplay, ensureMotionStyles } from '../components/AmbientBackground'
import PoliceBadge from '../components/PoliceBadge'
import { btnPrimary, panel, T } from '../theme'

const POLL_MS = 7000

function playAlert() {
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)()
    const osc = ctx.createOscillator()
    const gain = ctx.createGain()
    osc.type = 'sine'
    osc.frequency.value = 880
    gain.gain.value = 0.08
    osc.connect(gain)
    gain.connect(ctx.destination)
    osc.start()
    setTimeout(() => {
      osc.stop()
      ctx.close()
    }, 220)
  } catch {
    /* ignore */
  }
}

export default function Dashboard() {
  const navigate = useNavigate()
  const officer = useMemo(() => {
    try {
      return JSON.parse(localStorage.getItem('policeOfficer') || 'null')
    } catch {
      return null
    }
  }, [])

  const [incidents, setIncidents] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showClosed, setShowClosed] = useState(false)
  const [lastRefresh, setLastRefresh] = useState(new Date())
  const knownIds = useRef(new Set())
  const primed = useRef(false)

  const logout = () => {
    localStorage.removeItem('policeToken')
    localStorage.removeItem('policeOfficer')
    navigate('/login', { replace: true })
  }

  const fetchQueue = useCallback(async () => {
    try {
      const params = showClosed ? { active: '0' } : { active: '1' }
      const [{ data }, statsRes] = await Promise.all([
        api.get('/api/incidents', { params }),
        api.get('/api/incidents/stats'),
      ])
      const list = data.incidents || []

      if (primed.current) {
        const freshOpen = list.filter((i) => i.status === 'open' && !knownIds.current.has(i.id))
        if (freshOpen.length) playAlert()
      }
      list.forEach((i) => knownIds.current.add(i.id))
      primed.current = true

      setIncidents(list)
      setStats(statsRes.data)
      setError('')
      setLastRefresh(new Date())
    } catch (err) {
      setError(err?.response?.data?.error || 'Failed to load incidents')
    } finally {
      setLoading(false)
    }
  }, [showClosed])

  useEffect(() => {
    ensureMotionStyles()
    fetchQueue()
    const id = setInterval(fetchQueue, POLL_MS)
    return () => clearInterval(id)
  }, [fetchQueue])

  const openIncidents = incidents.filter((i) => i.status !== 'closed')
  const topNew = openIncidents.find((i) => i.status === 'open')
  const openCount = openIncidents.filter((i) => i.status === 'open').length
  const acknowledgedCount = openIncidents.filter((i) => i.status === 'acknowledged').length
  const dispatchedCount = openIncidents.filter((i) => i.status === 'dispatched').length

  const summary = [
    { label: 'Open', value: openCount, icon: Siren, color: T.danger, bg: T.dangerSoft },
    { label: 'Acknowledged', value: acknowledgedCount, icon: Clock3, color: '#F57F17', bg: '#FFF8E1' },
    { label: 'Dispatched', value: dispatchedCount, icon: Activity, color: '#1565C0', bg: '#E3F2FD' },
    { label: 'Active total', value: openIncidents.length, icon: Activity, color: T.navy, bg: T.navySoft },
  ]

  return (
    <div style={{ maxWidth: 1180, margin: '0 auto', padding: '24px 20px 48px', fontFamily: T.fontBody, animation: 'sos-fade-up 0.45s ease-out' }}>
      <header
        style={{
          position: 'relative',
          overflow: 'hidden',
          borderRadius: 16,
          padding: '22px 22px',
          marginBottom: 16,
          background: `linear-gradient(135deg, ${T.navy} 0%, ${T.navyMid} 55%, #1A8A8F 100%)`,
          color: T.white,
          boxShadow: '0 16px 40px rgba(11, 42, 74, 0.22)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          gap: 16,
          flexWrap: 'wrap',
        }}
      >
        <div style={{ position: 'absolute', right: '-6%', top: '-70%', width: 280, height: 280, opacity: 0.5, pointerEvents: 'none' }}>
          <RadarDisplay
            sweepColor="rgba(180, 255, 250, 0.5)"
            ringColor="rgba(255,255,255,0.2)"
            centerColor="rgba(255,255,255,0.9)"
            duration={4}
          />
        </div>
        <div style={{ position: 'relative', display: 'flex', alignItems: 'center', gap: 14, flexWrap: 'wrap' }}>
          <div
            style={{
              width: 56,
              height: 56,
              borderRadius: 12,
              background: '#fff',
              display: 'grid',
              placeItems: 'center',
              boxShadow: '0 4px 14px rgba(0,0,0,0.18)',
              flexShrink: 0,
            }}
          >
            <PoliceBadge size={48} />
          </div>
          <div>
            <p style={{ margin: 0, fontSize: 12, fontWeight: 600, opacity: 0.8, letterSpacing: '0.04em', textTransform: 'uppercase' }}>
              Sri Lanka Police
            </p>
            <h1 style={{ margin: '2px 0 0', fontFamily: T.fontDisplay, fontSize: 'clamp(1.4rem, 3vw, 1.8rem)', fontWeight: 800, letterSpacing: '-0.02em' }}>
              Incident queue
            </h1>
            <p style={{ margin: '4px 0 0', fontSize: 13.5, opacity: 0.85, display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
              <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
                <LivePulseDot color="#6EE7B7" size={7} />
                Live
              </span>
              <span aria-hidden>·</span>
              <span>{officer?.name} · {officer?.station?.display_name || `Station #${officer?.station_id}`}</span>
            </p>
          </div>
        </div>
        <button
          type="button"
          onClick={logout}
          style={{ position: 'relative', display: 'inline-flex', alignItems: 'center', gap: 8, border: '1px solid rgba(255,255,255,0.25)', background: 'rgba(255,255,255,0.1)', color: '#fff', borderRadius: T.radiusSm, padding: '10px 14px', fontWeight: 600, cursor: 'pointer', fontFamily: T.fontBody }}
        >
          <LogOut size={16} strokeWidth={2} />
          Sign out
        </button>
      </header>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: 10, marginBottom: 16 }}>
        {summary.map(({ label, value, icon: Icon, color, bg }) => (
          <div key={label} style={{ ...panel, padding: '14px 14px', display: 'flex', alignItems: 'center', gap: 12 }}>
            <div style={{ width: 36, height: 36, borderRadius: 10, background: bg, color, display: 'grid', placeItems: 'center', flexShrink: 0 }}>
              <Icon size={16} strokeWidth={2} />
            </div>
            <div>
              <p style={{ margin: 0, fontSize: 11, color: T.muted, fontWeight: 600 }}>{label}</p>
              <p style={{ margin: '2px 0 0', fontSize: 22, fontWeight: 800, color: T.ink, fontFamily: T.fontMono, lineHeight: 1 }}>{value}</p>
            </div>
          </div>
        ))}
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 16, flexWrap: 'wrap', marginBottom: 16 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16, flexWrap: 'wrap' }}>
          <label style={{ display: 'flex', gap: 8, alignItems: 'center', color: T.ink, fontSize: 14, background: T.surface, border: `1px solid ${T.line}`, borderRadius: 8, padding: '8px 12px' }}>
            <input type="checkbox" checked={showClosed} onChange={(e) => setShowClosed(e.target.checked)} />
            Show closed
            <span style={{ color: T.muted, fontSize: 12 }}>({incidents.filter((i) => i.status === 'closed').length})</span>
          </label>
          <span style={{ fontSize: 12.5, color: T.muted, fontFamily: T.fontMono }}>
            Updated {lastRefresh.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
          </span>
        </div>
        <button
          type="button"
          onClick={fetchQueue}
          disabled={loading}
          style={{ ...btnPrimary, opacity: loading ? 0.7 : 1, cursor: loading ? 'wait' : 'pointer' }}
        >
          <RefreshCw size={16} strokeWidth={2} />
          {loading ? 'Loading…' : 'Refresh'}
        </button>
      </div>

      {error && (
        <p style={{ background: T.dangerSoft, color: T.danger, borderRadius: 8, padding: '12px 14px', marginBottom: 16 }}>{error}</p>
      )}

      <section style={{ marginBottom: 28 }}>
        <h2 style={{ margin: '0 0 12px', fontSize: 16, color: T.ink, fontWeight: 700 }}>
          Active <span style={{ color: T.muted, fontWeight: 500 }}>({openIncidents.length})</span>
        </h2>

        {loading && incidents.length === 0 && (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: 12, marginBottom: 12 }}>
            {[1, 2, 3].map((i) => (
              <div key={i} style={{ ...panel, height: 130, background: T.lineSoft }} />
            ))}
          </div>
        )}
        {!loading && incidents.length === 0 && (
          <div style={{ ...panel, padding: 32, textAlign: 'center', color: T.muted, borderStyle: 'dashed', marginBottom: 12 }}>
            No incidents for this station.
          </div>
        )}

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: 12 }}>
          {incidents.map((inc) => (
            <IncidentCard key={inc.id} incident={inc} isTop={topNew && inc.id === topNew.id} />
          ))}
        </div>
      </section>

      <section>
        <h2 style={{ margin: '0 0 12px', fontSize: 16, color: T.ink, fontWeight: 700 }}>Station analytics</h2>
        <StatsCharts stats={stats} loading={loading && !stats} />
      </section>
    </div>
  )
}
