import { useEffect } from 'react';
import AttractionPhoto from './AttractionPhoto';

const colors = {
  primary: '#4EC6D4',
  primaryDark: '#1E6E6F',
  text: '#1E6E6F',
  textMuted: '#4a8586',
  border: 'rgba(30, 110, 111, 0.14)',
  white: '#FFFFFF',
};

export default function AttractionDetailModal({
  attraction,
  gradient,
  selected = false,
  selectDisabled = false,
  onClose,
  onToggleSelect,
}) {
  useEffect(() => {
    const onKey = (e) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [onClose]);

  if (!attraction) return null;

  return (
    <div
      className="tc-modal-card tc-modal-card--anchored"
      role="dialog"
      aria-modal="true"
      aria-labelledby="attraction-modal-title"
      onClick={(e) => e.stopPropagation()}
    >
      <button
        type="button"
        className="tc-modal-close"
        aria-label="Close"
        onClick={onClose}
      >
        ×
      </button>

      <AttractionPhoto
        src={attraction.image}
        name={attraction.attraction_name}
        gradient={gradient}
        height={180}
      >
        <div
          style={{
            position: 'absolute',
            inset: 0,
            background: 'linear-gradient(180deg, rgba(0,0,0,0) 40%, rgba(0,0,0,0.35) 100%)',
            pointerEvents: 'none',
          }}
        />
        <span
          style={{
            position: 'absolute',
            top: '14px',
            left: '14px',
            background: 'rgba(0, 0, 0, 0.5)',
            padding: '0.25rem 0.75rem',
            borderRadius: '999px',
            fontSize: '0.62rem',
            fontWeight: 600,
            color: 'white',
            letterSpacing: '0.05em',
            textTransform: 'uppercase',
            zIndex: 2,
          }}
        >
          {attraction.mood_tag}
        </span>
      </AttractionPhoto>

      <div style={{ padding: '1rem 1.1rem 1.15rem' }}>
        <h2
          id="attraction-modal-title"
          style={{
            margin: '0 0 0.35rem',
            fontSize: '1.05rem',
            fontWeight: 700,
            color: colors.text,
            letterSpacing: '-0.02em',
            lineHeight: 1.3,
          }}
        >
          {attraction.attraction_name}
        </h2>
        <div
          style={{
            fontSize: '0.78rem',
            color: colors.textMuted,
            marginBottom: '0.85rem',
          }}
        >
          {attraction.destination} · {attraction.category}
        </div>
        <p
          style={{
            margin: 0,
            fontSize: '0.86rem',
            lineHeight: 1.6,
            color: colors.textMuted,
            whiteSpace: 'pre-wrap',
          }}
        >
          {attraction.details || 'No description available.'}
        </p>

        {!selectDisabled && (
          <button
            type="button"
            onClick={onToggleSelect}
            style={{
              marginTop: '1rem',
              width: '100%',
              padding: '0.7rem 1rem',
              borderRadius: '12px',
              border: selected ? `2px solid ${colors.primary}` : `1px solid ${colors.border}`,
              background: selected ? colors.primary : colors.white,
              color: selected ? colors.white : colors.text,
              fontSize: '0.84rem',
              fontWeight: 600,
              cursor: 'pointer',
              fontFamily: 'inherit',
              transition: 'background 0.2s ease, color 0.2s ease',
            }}
          >
            {selected ? 'Remove from trip' : 'Add to trip'}
          </button>
        )}
      </div>
    </div>
  );
}
