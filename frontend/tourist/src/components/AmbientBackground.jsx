import { useEffect } from 'react'

const STYLE_ID = 'sos-motion-styles'

const CSS = `
@keyframes sos-drift-a {
  0%, 100% { transform: translate(0, 0) scale(1); }
  40% { transform: translate(4%, -3%) scale(1.06); }
  70% { transform: translate(-3%, 4%) scale(0.96); }
}
@keyframes sos-drift-b {
  0%, 100% { transform: translate(0, 0) scale(1); }
  35% { transform: translate(-5%, 3%) scale(1.05); }
  65% { transform: translate(3%, -4%) scale(0.97); }
}
@keyframes sos-drift-c {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(2%, 5%); }
}
@keyframes sos-pulse-ring {
  0% { transform: scale(0.55); opacity: 0.55; }
  70% { transform: scale(1.45); opacity: 0; }
  100% { transform: scale(1.45); opacity: 0; }
}
@keyframes sos-radar-spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
@keyframes sos-radar-blip {
  0%, 100% { opacity: 0.15; transform: scale(0.7); }
  40% { opacity: 1; transform: scale(1.15); }
  70% { opacity: 0.35; transform: scale(0.9); }
}
@keyframes sos-scan {
  0% { transform: translateY(-100%); opacity: 0; }
  10% { opacity: 0.5; }
  90% { opacity: 0.5; }
  100% { transform: translateY(100vh); opacity: 0; }
}
@keyframes sos-fade-up {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes sos-live-dot {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.45; transform: scale(0.75); }
}
@media (prefers-reduced-motion: reduce) {
  .sos-orb, .sos-pulse, .sos-scan, .sos-live, .sos-radar-spin, .sos-radar-blip {
    animation: none !important;
  }
}
`

export function ensureMotionStyles() {
  if (typeof document === 'undefined') return
  if (document.getElementById(STYLE_ID)) return
  const el = document.createElement('style')
  el.id = STYLE_ID
  el.textContent = CSS
  document.head.appendChild(el)
}

/**
 * Full radar: rings + rotating sweep + blips.
 * Use inside a position:relative overflow:hidden container.
 */
export function RadarDisplay({
  size = '100%',
  sweepColor = 'rgba(255,255,255,0.45)',
  ringColor = 'rgba(255,255,255,0.22)',
  centerColor = 'rgba(255,255,255,0.85)',
  duration = 4.2,
  blips = true,
}) {
  useEffect(() => {
    ensureMotionStyles()
  }, [])

  return (
    <div
      aria-hidden
      style={{
        position: 'absolute',
        inset: 0,
        display: 'grid',
        placeItems: 'center',
        pointerEvents: 'none',
        overflow: 'hidden',
      }}
    >
      <div style={{ position: 'relative', width: size, height: size, maxWidth: '120%', maxHeight: '120%', aspectRatio: '1' }}>
        {/* concentric rings */}
        {[22, 40, 58, 76, 94].map((pct) => (
          <span
            key={pct}
            style={{
              position: 'absolute',
              left: '50%',
              top: '50%',
              width: `${pct}%`,
              height: `${pct}%`,
              marginLeft: `-${pct / 2}%`,
              marginTop: `-${pct / 2}%`,
              borderRadius: '50%',
              border: `1px solid ${ringColor}`,
              boxSizing: 'border-box',
            }}
          />
        ))}

        {/* crosshairs */}
        <span style={{ position: 'absolute', left: '50%', top: '8%', bottom: '8%', width: 1, background: ringColor, transform: 'translateX(-50%)' }} />
        <span style={{ position: 'absolute', top: '50%', left: '8%', right: '8%', height: 1, background: ringColor, transform: 'translateY(-50%)' }} />

        {/* rotating sweep */}
        <div
          className="sos-radar-spin"
          style={{
            position: 'absolute',
            inset: '3%',
            borderRadius: '50%',
            background: `conic-gradient(from 0deg, transparent 0deg, transparent 300deg, ${sweepColor} 360deg)`,
            animation: `sos-radar-spin ${duration}s linear infinite`,
            opacity: 0.85,
            maskImage: 'radial-gradient(circle, #000 62%, transparent 72%)',
            WebkitMaskImage: 'radial-gradient(circle, #000 62%, transparent 72%)',
          }}
        />

        {/* expanding pulse rings */}
        {[0, 1.1, 2.2].map((delay) => (
          <span
            key={delay}
            className="sos-pulse"
            style={{
              position: 'absolute',
              left: '50%',
              top: '50%',
              width: '42%',
              height: '42%',
              marginLeft: '-21%',
              marginTop: '-21%',
              borderRadius: '50%',
              border: `1.5px solid ${sweepColor}`,
              animation: `sos-pulse-ring 3.3s ease-out ${delay}s infinite`,
            }}
          />
        ))}

        {/* blips */}
        {blips && (
          <>
            <span className="sos-radar-blip" style={{ position: 'absolute', left: '68%', top: '32%', width: 7, height: 7, borderRadius: '50%', background: centerColor, boxShadow: `0 0 10px ${sweepColor}`, animation: 'sos-radar-blip 2.8s ease-in-out 0.2s infinite' }} />
            <span className="sos-radar-blip" style={{ position: 'absolute', left: '28%', top: '58%', width: 6, height: 6, borderRadius: '50%', background: centerColor, boxShadow: `0 0 8px ${sweepColor}`, animation: 'sos-radar-blip 3.4s ease-in-out 1.1s infinite' }} />
            <span className="sos-radar-blip" style={{ position: 'absolute', left: '62%', top: '70%', width: 5, height: 5, borderRadius: '50%', background: centerColor, boxShadow: `0 0 8px ${sweepColor}`, animation: 'sos-radar-blip 3.1s ease-in-out 1.8s infinite' }} />
          </>
        )}

        {/* center dot */}
        <span
          style={{
            position: 'absolute',
            left: '50%',
            top: '50%',
            width: 8,
            height: 8,
            marginLeft: -4,
            marginTop: -4,
            borderRadius: '50%',
            background: centerColor,
            boxShadow: `0 0 12px ${sweepColor}`,
          }}
        />
      </div>
    </div>
  )
}

/** Soft expanding rings only (legacy helper) */
export function RadarPulse({ color = 'rgba(255,255,255,0.35)' }) {
  return <RadarDisplay sweepColor={color} ringColor={color} centerColor={color} blips={false} />
}

const TOURIST_BG = '/bgi.jpg'

/** Beach SOS photo + corner radar */
export default function AmbientBackground({ variant = 'light', scan = false, radar = true }) {
  useEffect(() => {
    ensureMotionStyles()
  }, [])

  const isDark = variant === 'dark'

  return (
    <div
      aria-hidden
      style={{
        position: 'absolute',
        inset: 0,
        zIndex: 0,
        pointerEvents: 'none',
        overflow: 'hidden',
        background: isDark ? '#062E34' : '#EAF6F6',
      }}
    >
      <div
        style={{
          position: 'absolute',
          inset: 0,
          backgroundImage: `url(${TOURIST_BG})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center bottom',
          backgroundRepeat: 'no-repeat',
          opacity: isDark ? 0.35 : 0.55,
          filter: isDark ? 'brightness(0.55) saturate(0.85)' : 'none',
        }}
      />
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background: isDark
            ? 'linear-gradient(155deg, rgba(6, 46, 52, 0.88) 0%, rgba(10, 74, 82, 0.9) 48%, rgba(14, 96, 106, 0.92) 100%)'
            : `
              linear-gradient(180deg, rgba(242, 250, 250, 0.86) 0%, rgba(234, 246, 246, 0.9) 45%, rgba(227, 241, 242, 0.94) 100%),
              radial-gradient(ellipse 90% 50% at 50% 100%, rgba(232, 213, 163, 0.18), transparent 55%)
            `,
        }}
      />

      <div
        style={{
          position: 'absolute',
          inset: 0,
          backgroundImage: isDark
            ? 'linear-gradient(rgba(255,255,255,0.045) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.045) 1px, transparent 1px)'
            : 'linear-gradient(rgba(10,74,82,0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(10,74,82,0.04) 1px, transparent 1px)',
          backgroundSize: '48px 48px',
          maskImage: 'radial-gradient(ellipse 80% 70% at 50% 30%, #000 20%, transparent 75%)',
          WebkitMaskImage: 'radial-gradient(ellipse 80% 70% at 50% 30%, #000 20%, transparent 75%)',
        }}
      />

      {radar && (
        <div
          style={{
            position: 'absolute',
            width: 'min(92vw, 520px)',
            height: 'min(92vw, 520px)',
            right: isDark ? '-12%' : '-18%',
            top: isDark ? '8%' : '-8%',
            opacity: isDark ? 0.5 : 0.32,
          }}
        >
          <RadarDisplay
            sweepColor={isDark ? 'rgba(120, 230, 230, 0.55)' : 'rgba(18, 112, 122, 0.45)'}
            ringColor={isDark ? 'rgba(180, 240, 240, 0.22)' : 'rgba(10, 74, 82, 0.18)'}
            centerColor={isDark ? 'rgba(200, 255, 255, 0.9)' : 'rgba(10, 74, 82, 0.75)'}
            duration={5}
          />
        </div>
      )}

      <div
        className="sos-orb"
        style={{
          position: 'absolute',
          width: '55vmax',
          height: '55vmax',
          left: '-15%',
          top: '-20%',
          borderRadius: '50%',
          background: isDark
            ? 'radial-gradient(circle, rgba(56, 180, 190, 0.18), transparent 68%)'
            : 'radial-gradient(circle, rgba(18, 112, 122, 0.1), transparent 68%)',
          filter: 'blur(8px)',
          animation: 'sos-drift-a 18s ease-in-out infinite',
        }}
      />
      <div
        className="sos-orb"
        style={{
          position: 'absolute',
          width: '45vmax',
          height: '45vmax',
          right: '-12%',
          top: '10%',
          borderRadius: '50%',
          background: isDark
            ? 'radial-gradient(circle, rgba(14, 122, 107, 0.14), transparent 68%)'
            : 'radial-gradient(circle, rgba(14, 122, 107, 0.08), transparent 68%)',
          filter: 'blur(10px)',
          animation: 'sos-drift-b 22s ease-in-out infinite',
        }}
      />

      {scan && (
        <div
          className="sos-scan"
          style={{
            position: 'absolute',
            left: 0,
            right: 0,
            height: 120,
            background: isDark
              ? 'linear-gradient(180deg, transparent, rgba(120, 220, 220, 0.09), transparent)'
              : 'linear-gradient(180deg, transparent, rgba(10, 74, 82, 0.05), transparent)',
            animation: 'sos-scan 9s linear infinite',
          }}
        />
      )}
    </div>
  )
}

export function LivePulseDot({ color = '#0E7A6B', size = 7 }) {
  useEffect(() => {
    ensureMotionStyles()
  }, [])
  return (
    <span
      className="sos-live"
      style={{
        width: size,
        height: size,
        borderRadius: '50%',
        background: color,
        display: 'inline-block',
        animation: 'sos-live-dot 1.6s ease-in-out infinite',
      }}
    />
  )
}
