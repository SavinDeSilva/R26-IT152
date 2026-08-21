import { useCallback, useEffect, useState } from 'react'
import { Check } from 'lucide-react'
import api from '../api/client'
import { cardStyle, statusColors, T } from '../theme'

const POLL_MS = 5000

const STEPS = [
  { key: 'open', label: '1. SOS sent', doneStatuses: ['open', 'acknowledged', 'dispatched', 'closed'], timeField: 'triggered_at' },
  { key: 'acknowledged', label: '2. Acknowledged', doneStatuses: ['acknowledged', 'dispatched', 'closed'], timeField: 'acknowledged_at' },
  { key: 'dispatched', label: '3. Dispatched', doneStatuses: ['dispatched', 'closed'], timeField: 'dispatched_at' },
  { key: 'closed', label: '4. Closed', doneStatuses: ['closed'], timeField: 'closed_at' },
]

function fmt(iso) {
  if (!iso) return null
  return new Date(iso).toLocaleString()
}

export default function IncidentWorkflow({ incidentId, touristId }) {
  const [incident, setIncident] = useState(null)
  const [error, setError] = useState('')

  const load = useCallback(async () => {
    if (!incidentId || !touristId) return
    try {
      const { data } = await api.get(`/api/incidents/${incidentId}/status`, {
        params: { tourist_id: touristId },
      })
      setIncident(data.incident)
      setError('')
      if (data.incident?.station?.display_name) {
        localStorage.setItem('activeStationName', data.incident.station.display_name)
      }
    } catch (err) {
      setError(err?.response?.data?.error || 'Could not load status')
    }
  }, [incidentId, touristId])

  useEffect(() => {
    load()
    const t = setInterval(load, POLL_MS)
    return () => clearInterval(t)
  }, [load])

  if (!incidentId) return null

  const status = incident?.status || 'open'
  const st = statusColors[status] || statusColors.open
  const currentIndex = STEPS.findIndex((s) => s.key === status)

  return (
    <section style={{ ...cardStyle, padding: '16px 16px', marginBottom: 14 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 10, marginBottom: 12 }}>
        <div>
          <p style={{ margin: 0, fontSize: 12, fontWeight: 700, color: T.muted, letterSpacing: '0.04em', textTransform: 'uppercase' }}>
            Case status
          </p>
          <p style={{ margin: '4px 0 0', fontSize: 14, color: T.ink, fontWeight: 650 }}>
            {incident?.station?.display_name || 'Nearest station'}
          </p>
        </div>
        <span style={{
          fontSize: 11, fontWeight: 700, padding: '4px 8px', borderRadius: 6,
          background: st.bg, color: st.color, flexShrink: 0,
        }}>
          {st.label}
        </span>
      </div>

      {error && <p style={{ margin: '0 0 10px', color: T.danger, fontSize: 13 }}>{error}</p>}

      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        {STEPS.map((step, i) => {
          const done = step.doneStatuses.includes(status)
          const active = step.key === status
          const time = incident ? fmt(incident[step.timeField]) : null
          return (
            <div
              key={step.key}
              style={{
                display: 'flex',
                gap: 10,
                alignItems: 'flex-start',
                padding: '10px 12px',
                borderRadius: 10,
                background: active ? st.bg : done ? T.navySoft : T.lineSoft,
                border: active ? `1px solid ${st.bar}` : '1px solid transparent',
              }}
            >
              <span style={{
                width: 24, height: 24, borderRadius: 999, flexShrink: 0,
                display: 'grid', placeItems: 'center',
                background: done ? (active ? st.bar : T.navy) : T.line,
                color: done ? T.white : T.muted,
                fontSize: 12, fontWeight: 700,
              }}>
                {done && i < currentIndex ? <Check size={14} strokeWidth={3} /> : i + 1}
              </span>
              <div style={{ flex: 1, minWidth: 0 }}>
                <p style={{
                  margin: 0, fontSize: 14, fontWeight: active || done ? 700 : 500,
                  color: done || active ? T.ink : T.muted,
                }}>
                  {step.label}
                </p>
                <p style={{ margin: '3px 0 0', fontSize: 12, color: T.muted, fontFamily: T.fontMono }}>
                  {time || (done ? '—' : 'Waiting…')}
                </p>
              </div>
            </div>
          )
        })}
      </div>

      <p style={{ margin: '12px 0 0', fontSize: 12.5, color: T.muted, lineHeight: 1.4 }}>
        Updates automatically when police acknowledge, dispatch, or close your case.
      </p>
    </section>
  )
}
