import { typeColors, btnPrimary, cardStyle, T } from '../theme'

const TYPE_LABELS = {
  general: 'General',
  medical: 'Medical',
  rape: 'Rape / Assault',
  theft: 'Theft',
  accident: 'Accident',
  harassment: 'Harassment',
}

export default function SOSSentOverlay({ visible, incidentId, incidentType, stationName, onDismiss }) {
  if (!visible) return null
  const typeLabel = TYPE_LABELS[incidentType] || incidentType
  const typeStyle = typeColors[incidentType] || typeColors.general

  return (
    <div
      role="status"
      aria-live="assertive"
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 2000,
        background: 'rgba(11, 42, 74, 0.45)',
        display: 'grid',
        placeItems: 'center',
        padding: 24,
        fontFamily: T.fontBody,
      }}
    >
      <div style={{ ...cardStyle, width: 'min(100%, 380px)', padding: '28px 24px', textAlign: 'center' }}>
        <div style={{ display: 'inline-block', background: T.danger, color: T.white, fontWeight: 700, fontSize: 12, padding: '7px 12px', borderRadius: 6, marginBottom: 12 }}>
          SOS sent
        </div>
        {typeLabel && (
          <p style={{ display: 'inline-block', margin: '0 0 14px', padding: '5px 10px', borderRadius: 6, background: typeStyle.bg, color: typeStyle.color, fontWeight: 600, fontSize: 13 }}>
            {typeLabel}
          </p>
        )}
        <p style={{ margin: '0 0 10px', fontFamily: T.fontDisplay, fontSize: 22, fontWeight: 800, color: T.navy, letterSpacing: '-0.02em', lineHeight: 1.2 }}>
          Nearest station notified
        </p>
        <p style={{ margin: '0 0 14px', lineHeight: 1.5, fontSize: 15, color: T.muted }}>
          {stationName
            ? `Only ${stationName} was alerted using your current location (read once now).`
            : 'Only the nearest police station was alerted using your current location (read once now).'}
          {' '}Device location is not tracked. You can send text, photos, or voice in the chat below.
        </p>
        {incidentId != null && (
          <p style={{ margin: '0 0 20px', fontSize: 13, color: T.muted, fontFamily: T.fontMono }}>Incident #{incidentId}</p>
        )}
        <button type="button" onClick={onDismiss} style={{ ...btnPrimary, minWidth: 120 }}>
          OK
        </button>
      </div>
    </div>
  )
}
