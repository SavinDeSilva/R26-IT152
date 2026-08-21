/** Police console — beach teal × detective casefile */
export const T = {
  navy: '#0A4A52',
  navyMid: '#12707A',
  navySoft: '#DDF2F3',
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

export const panel = {
  background: T.surface,
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
  padding: '12px 16px',
  background: T.navy,
  color: T.white,
  fontWeight: 650,
  fontFamily: T.fontBody,
  fontSize: 14,
  cursor: 'pointer',
  boxShadow: T.shadowSm,
}

export const bureauBg = T.page
