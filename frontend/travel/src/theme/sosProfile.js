/** Match Tourist SOS profile look (frontend-tourist theme). */
export const T = {
  navy: '#0A4A52',
  navySoft: '#DDF2F3',
  surface: '#FFFFFF',
  ink: '#0D2C30',
  muted: '#4A6B70',
  line: '#C5DDDF',
  danger: '#C23B3B',
  dangerSoft: '#FCEAEA',
  success: '#0E7A6B',
  successSoft: '#E3F5F1',
  white: '#FFFFFF',
  shadowSm: '0 2px 10px rgba(10, 74, 82, 0.07)',
  radius: 10,
  radiusSm: 6,
  fontDisplay: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
  fontBody: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
};

export const cardStyle = {
  background: T.surface,
  color: T.ink,
  border: `1px solid ${T.line}`,
  borderRadius: T.radius,
  boxShadow: T.shadowSm,
};

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
};

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
};

export const labelStyle = {
  display: 'flex',
  flexDirection: 'column',
  gap: 6,
  marginBottom: 12,
  color: T.muted,
  fontSize: 13,
  fontWeight: 600,
  fontFamily: T.fontBody,
};
