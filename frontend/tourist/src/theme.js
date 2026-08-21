/** Tourist SOS — beach teal × detective casefile */
export const T = {
  navy: '#0A4A52',       // deep lagoon (primary)
  navyMid: '#12707A',    // mid teal
  navySoft: '#DDF2F3',   // seafoam wash
  surface: '#FFFFFF',
  page: '#EAF6F6',
  ink: '#0D2C30',
  muted: '#4A6B70',
  line: '#C5DDDF',
  lineSoft: '#E7F3F4',
  danger: '#C23B3B',
  dangerSoft: '#FCEAEA',
  success: '#0E7A6B',
  successSoft: '#E3F5F1',
  sand: '#E8D5A3',
  white: '#FFFFFF',
  shadow: '0 8px 28px rgba(10, 74, 82, 0.10)',
  shadowSm: '0 2px 10px rgba(10, 74, 82, 0.07)',
  radius: 10,
  radiusSm: 6,
  fontDisplay: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
  fontBody: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
  fontMono: 'Consolas, "Courier New", monospace',
}

export const typeColors = {
  general: { bg: '#C23B3B', color: '#FFFFFF' },
  medical: { bg: '#0E7A6B', color: '#FFFFFF' },
  rape: { bg: '#6B2D3C', color: '#FFFFFF' },
  theft: { bg: '#8A6A2F', color: '#FFFFFF' },
  accident: { bg: '#3D5A5E', color: '#FFFFFF' },
  harassment: { bg: '#2F4A4E', color: '#FFFFFF' },
}

export const statusColors = {
  open: { bar: '#C23B3B', bg: '#FCEAEA', color: '#A32E2E', label: 'Open' },
  acknowledged: { bar: '#D4A017', bg: '#FFF8E6', color: '#8A6A00', label: 'Acknowledged' },
  dispatched: { bar: '#12707A', bg: '#DDF2F3', color: '#0A4A52', label: 'Dispatched' },
  closed: { bar: '#0E7A6B', bg: '#E3F5F1', color: '#0E7A6B', label: 'Closed' },
}

export const shellBg = T.page

export const cardStyle = {
  background: T.surface,
  color: T.ink,
  border: `1px solid ${T.line}`,
  borderRadius: T.radius,
  boxShadow: T.shadowSm,
}

export const btnPrimary = {
  display: 'inline-flex',
  alignItems: 'center',
  justifyContent: 'center',
  gap: 8,
  border: 'none',
  borderRadius: T.radiusSm,
  padding: '13px 18px',
  background: T.navy,
  color: T.white,
  fontWeight: 650,
  fontFamily: T.fontBody,
  fontSize: 15,
  cursor: 'pointer',
  boxShadow: T.shadowSm,
}

export const fieldStyle = {
  width: '100%',
  boxSizing: 'border-box',
  border: `1px solid ${T.line}`,
  background: T.surface,
  color: T.ink,
  borderRadius: T.radiusSm,
  padding: '12px 14px',
  fontSize: 15,
  fontFamily: T.fontBody,
  outline: 'none',
}

export const labelStyle = {
  display: 'flex',
  flexDirection: 'column',
  gap: 6,
  marginBottom: 12,
  color: T.muted,
  fontSize: 13,
  fontWeight: 600,
  fontFamily: T.fontBody,
}
