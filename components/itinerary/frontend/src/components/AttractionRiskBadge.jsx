import { useSiteI18n } from '@shared/i18n/react';

const colors = {
  textMuted: '#4a8586',
};

function riskColor(level) {
  if (level === 'High') return '#dc2626';
  if (level === 'Medium') return '#d97706';
  return '#15803d';
}

export default function AttractionRiskBadge({ risk, checking = false, compact = false, overlay = false }) {
  const { t } = useSiteI18n();

  if (!risk && checking) {
    if (overlay) return null;
    return (
      <div style={{ marginTop: compact ? 0 : '0.45rem', fontSize: '0.68rem', color: colors.textMuted, fontWeight: 600 }}>
        {t('checkingCrowdRisk')}
      </div>
    );
  }
  if (!risk) return null;

  const color = riskColor(risk.risk_level);
  const crowd = Math.round((risk.crowd_score || 0) * 100);

  if (overlay) {
    return (
      <span
        style={{
          position: 'absolute',
          left: '12px',
          bottom: '10px',
          zIndex: 2,
          pointerEvents: 'none',
          fontSize: '0.62rem',
          fontWeight: 700,
          letterSpacing: '0.04em',
          textTransform: 'uppercase',
          color: '#fff',
          background: color,
          borderRadius: '999px',
          padding: '0.18rem 0.55rem',
        }}
      >
        {risk.risk_level} · {crowd}%
      </span>
    );
  }

  return (
    <div
      style={{
        display: 'flex',
        flexWrap: 'wrap',
        gap: '0.35rem',
        alignItems: 'center',
        marginTop: compact ? 0 : '0.5rem',
      }}
    >
      <span
        style={{
          fontSize: '0.62rem',
          fontWeight: 700,
          letterSpacing: '0.04em',
          textTransform: 'uppercase',
          color: '#fff',
          background: color,
          borderRadius: '999px',
          padding: '0.18rem 0.55rem',
        }}
      >
        {risk.risk_level} {t('risk')}
      </span>
      <span style={{ fontSize: '0.68rem', color: colors.textMuted, fontWeight: 600 }}>
        {crowd}% {t('crowded')}
      </span>
      <span
        style={{
          fontSize: '0.68rem',
          fontWeight: 600,
          color: risk.recommended ? '#15803d' : '#b45309',
        }}
      >
        {risk.recommended ? t('goodToVisit') : t('considerAlternative')}
      </span>
    </div>
  );
}
