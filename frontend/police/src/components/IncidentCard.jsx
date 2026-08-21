import { Link } from 'react-router-dom'
import { useState } from 'react'
import { panel, statusColors, typeColors, T } from '../theme'

export default function IncidentCard({ incident, isTop }) {
  const [hovered, setHovered] = useState(false)
  const tourist = incident.tourist || {}
  const ping = incident.latest_ping
  const ageMin = incident.triggered_at
    ? Math.max(0, Math.round((Date.now() - new Date(incident.triggered_at).getTime()) / 60000))
    : null
  const typeKey = incident.incident_type || incident.type || 'general'
  const typeLabel = incident.incident_type_label || typeKey
  const st = statusColors[incident.status] || statusColors.open
  const ty = typeColors[typeKey] || typeColors.general

  return (
    <Link
      to={`/incidents/${incident.id}`}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        display: 'block',
        textDecoration: 'none',
        ...panel,
        background: isTop ? T.dangerSoft : T.surface,
        borderLeft: `4px solid ${st.bar}`,
        padding: '15px 16px',
        color: T.ink,
        transform: hovered ? 'translateY(-2px)' : 'none',
        boxShadow: hovered ? T.shadow : panel.boxShadow,
        transition: 'transform 150ms ease, box-shadow 150ms ease',
        fontFamily: T.fontBody,
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
        <span style={{ fontSize: 11, fontWeight: 700, padding: '3px 8px', borderRadius: 6, background: st.bg, color: st.color }}>
          {st.label}
        </span>
        <span style={{ color: T.muted, fontSize: 12, fontFamily: T.fontMono }}>#{incident.id}</span>
      </div>
      <span style={{ display: 'inline-block', margin: '0 0 8px', fontSize: 11, fontWeight: 700, padding: '3px 8px', borderRadius: 6, background: ty.bg, color: ty.color }}>
        {typeLabel}
      </span>
      <h3 style={{ margin: '0 0 4px', fontSize: 16, fontWeight: 700 }}>{tourist.name || `Tourist #${incident.tourist_id}`}</h3>
      <p style={{ margin: 0, color: T.muted, fontSize: 13 }}>
        {tourist.nationality || '—'} · {ageMin != null ? `${ageMin} min ago` : '—'}
      </p>
      <p style={{ margin: '4px 0 0', color: T.muted, fontSize: 12, fontFamily: T.fontMono }}>
        {ping
          ? `${ping.latitude.toFixed(5)}, ${ping.longitude.toFixed(5)}`
          : `${incident.initial_lat?.toFixed(5)}, ${incident.initial_lng?.toFixed(5)}`}
      </p>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginTop: 10 }}>
        {incident.contact_notified_at && (
          <span style={{ fontSize: 11, background: T.successSoft, color: T.success, padding: '3px 8px', borderRadius: 6, fontWeight: 600 }}>Contact ✓</span>
        )}
        {incident.hotel_notified_at && (
          <span style={{ fontSize: 11, background: T.successSoft, color: T.success, padding: '3px 8px', borderRadius: 6, fontWeight: 600 }}>Hotel ✓</span>
        )}
      </div>
    </Link>
  )
}
