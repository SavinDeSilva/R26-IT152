import { useState } from 'react'
import { AlertTriangle, Car, HeartPulse, Package, Siren, UserX } from 'lucide-react'
import { T } from '../theme'

export const SOS_TYPES = [
  { id: 'general', label: 'Emergency', icon: Siren, accent: '#C23B3B' },
  { id: 'medical', label: 'Medical', icon: HeartPulse, accent: '#0E7A6B' },
  { id: 'rape', label: 'Assault', icon: AlertTriangle, accent: '#6B2D3C' },
  { id: 'theft', label: 'Theft', icon: Package, accent: '#8A6A2F' },
  { id: 'accident', label: 'Accident', icon: Car, accent: '#3D5A5E' },
  { id: 'harassment', label: 'Harassment', icon: UserX, accent: '#2F4A4E' },
]

function TypeGrid({ onTrigger, disabled, sending, sendingType, pressed, setPressed }) {
  return (
    <div className="sos-types">
      {SOS_TYPES.map((t) => {
        const isSending = sending && sendingType === t.id
        const active = pressed === t.id
        const Icon = t.icon
        return (
          <button
            key={t.id}
            type="button"
            onClick={() => onTrigger(t.id)}
            disabled={disabled || sending}
            aria-label={`Trigger ${t.label} SOS`}
            onPointerDown={() => setPressed(t.id)}
            onPointerUp={() => setPressed(null)}
            onPointerLeave={() => setPressed(null)}
            style={{
              minWidth: 0,
              minHeight: 88,
              border: `1px solid ${T.line}`,
              borderTop: `3px solid ${t.accent}`,
              borderRadius: 10,
              background: active ? T.navySoft : T.white,
              color: T.navy,
              fontFamily: T.fontBody,
              fontWeight: 700,
              cursor: disabled || sending ? 'not-allowed' : 'pointer',
              opacity: disabled || (sending && !isSending) ? 0.42 : 1,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 8,
              padding: '12px 8px',
              transform: active ? 'translateY(1px)' : 'none',
              WebkitTapHighlightColor: 'transparent',
              touchAction: 'manipulation',
            }}
          >
            <Icon size={20} strokeWidth={2.1} color={t.accent} />
            <span style={{
              fontSize: 13,
              fontWeight: 700,
              lineHeight: 1.2,
              textAlign: 'center',
              color: T.ink,
            }}>
              {isSending ? 'Sending…' : t.label}
            </span>
          </button>
        )
      })}
    </div>
  )
}

export default function SOSButton({ onTrigger, disabled, sending, sendingType, variant = 'dock', statusLabel }) {
  const [pressed, setPressed] = useState(null)
  const grid = (
    <TypeGrid
      onTrigger={onTrigger}
      disabled={disabled}
      sending={sending}
      sendingType={sendingType}
      pressed={pressed}
      setPressed={setPressed}
    />
  )

  if (variant === 'page') {
    return (
      <section
        role="group"
        aria-label="Emergency SOS types"
        style={{
          background: T.surface,
          border: `1px solid ${T.line}`,
          borderRadius: 12,
          boxShadow: T.shadowSm,
          padding: '16px 16px 18px',
          marginBottom: 16,
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 12, marginBottom: 12 }}>
          <p style={{ margin: 0, fontSize: 12, fontWeight: 700, color: T.navy, letterSpacing: '0.08em', textTransform: 'uppercase' }}>
            Police response
          </p>
          {statusLabel ? (
            <span style={{
              fontSize: 11,
              fontWeight: 700,
              padding: '4px 10px',
              borderRadius: 999,
              background: statusLabel === 'Ready' ? T.navySoft : '#FFF8E6',
              color: statusLabel === 'Ready' ? T.navy : '#8A6A00',
            }}>
              {statusLabel}
            </span>
          ) : null}
        </div>
        {grid}
      </section>
    )
  }

  return (
    <div
      role="group"
      aria-label="Emergency SOS types"
      style={{
        position: 'fixed',
        left: 0,
        right: 0,
        bottom: 'max(0.9rem, env(safe-area-inset-bottom))',
        zIndex: 1000,
        display: 'flex',
        justifyContent: 'center',
        padding: '0.6rem 0',
        pointerEvents: 'none',
      }}
    >
      <div
        style={{
          pointerEvents: 'auto',
          width: 'min(1180px, calc(100% - 2rem))',
          padding: 12,
          borderRadius: 14,
          background: T.surface,
          border: `1px solid ${T.line}`,
          boxShadow: '0 10px 32px rgba(11, 42, 74, 0.14)',
        }}
      >
        {grid}
      </div>
    </div>
  )
}
