import { useEffect } from 'react'
import { POLICE_BG } from '../assets'

const STYLE_ID = 'police-motion-styles'

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
  10% { opacity: 0.55; }
  90% { opacity: 0.55; }
  100% { transform: translateY(100vh); opacity: 0; }
}
@keyframes sos-live-dot {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.45; transform: scale(0.75); }
}
@keyframes sos-fade-up {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}
@media (prefers-reduced-motion: reduce) {
  .sos-orb, .sos-scan, .sos-live, .sos-enter, .sos-radar-spin, .sos-radar-blip, .sos-pulse {
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
        <span style={{ position: 'absolute', left: '50%', top: '8%', bottom: '8%', width: 1, background: ringColor, transform: 'translateX(-50%)' }} />
        <span style={{ position: 'absolute', top: '50%', left: '8%', right: '8%', height: 1, background: ringColor, transform: 'translateY(-50%)' }} />
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
        {blips && (
          <>
            <span className="sos-radar-blip" style={{ position: 'absolute', left: '68%', top: '32%', width: 7, height: 7, borderRadius: '50%', background: centerColor, boxShadow: `0 0 10px ${sweepColor}`, animation: 'sos-radar-blip 2.8s ease-in-out 0.2s infinite' }} />
            <span className="sos-radar-blip" style={{ position: 'absolute', left: '28%', top: '58%', width: 6, height: 6, borderRadius: '50%', background: centerColor, boxShadow: `0 0 8px ${sweepColor}`, animation: 'sos-radar-blip 3.4s ease-in-out 1.1s infinite' }} />
            <span className="sos-radar-blip" style={{ position: 'absolute', left: '62%', top: '70%', width: 5, height: 5, borderRadius: '50%', background: centerColor, boxShadow: `0 0 8px ${sweepColor}`, animation: 'sos-radar-blip 3.1s ease-in-out 1.8s infinite' }} />
          </>
        )}
        <span style={{ position: 'absolute', left: '50%', top: '50%', width: 8, height: 8, marginLeft: -4, marginTop: -4, borderRadius: '50%', background: centerColor, boxShadow: `0 0 12px ${sweepColor}` }} />
      </div>
    </div>
  )
}

export function RadarPulse({ color = 'rgba(255,255,255,0.35)' }) {
  return <RadarDisplay sweepColor={color} ringColor={color} centerColor={color} blips={false} />
}

export default function AmbientBackground({ variant = 'light', scan = true, radar = true }) {
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
        background: isDark ? '#0B1A2E' : '#EAF6F6',
      }}
    >
      {/* Official Sri Lanka Police background graphic */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          backgroundImage: `url(${POLICE_BG})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundRepeat: 'no-repeat',
          opacity: isDark ? 0.88 : 0.42,
          filter: isDark ? 'none' : 'saturate(0.85)',
        }}
      />
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background: isDark
            ? 'linear-gradient(155deg, rgba(6, 20, 40, 0.72) 0%, rgba(10, 40, 55, 0.78) 48%, rgba(14, 50, 60, 0.85) 100%)'
            : `
              linear-gradient(180deg, rgba(242, 250, 250, 0.88) 0%, rgba(234, 246, 246, 0.92) 55%, rgba(234, 246, 246, 0.96) 100%),
              radial-gradient(ellipse 90% 55% at 0% -5%, rgba(18, 112, 122, 0.12), transparent 55%)
            `,
        }}
      />

      <div
        style={{
          position: 'absolute',
          inset: 0,
          backgroundImage: isDark
            ? 'linear-gradient(rgba(255,255,255,0.045) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.045) 1px, transparent 1px)'
            : 'linear-gradient(rgba(10,74,82,0.045) 1px, transparent 1px), linear-gradient(90deg, rgba(10,74,82,0.045) 1px, transparent 1px)',
          backgroundSize: '56px 56px',
          maskImage: 'radial-gradient(ellipse 85% 70% at 50% 20%, #000 15%, transparent 80%)',
          WebkitMaskImage: 'radial-gradient(ellipse 85% 70% at 50% 20%, #000 15%, transparent 80%)',
        }}
      />

      {radar && (
        <div
          style={{
            position: 'absolute',
            width: 'min(70vw, 560px)',
            height: 'min(70vw, 560px)',
            right: isDark ? '-8%' : '-14%',
            bottom: isDark ? '-10%' : 'auto',
            top: isDark ? 'auto' : '-12%',
            opacity: isDark ? 0.45 : 0.28,
          }}
        >
          <RadarDisplay
            sweepColor={isDark ? 'rgba(120, 230, 230, 0.55)' : 'rgba(18, 112, 122, 0.42)'}
            ringColor={isDark ? 'rgba(180, 240, 240, 0.2)' : 'rgba(10, 74, 82, 0.16)'}
            centerColor={isDark ? 'rgba(200, 255, 255, 0.9)' : 'rgba(10, 74, 82, 0.7)'}
            duration={4.6}
          />
        </div>
      )}

      <div
        className="sos-orb"
        style={{
          position: 'absolute',
          width: '50vmax',
          height: '50vmax',
          left: '-18%',
          top: '-22%',
          borderRadius: '50%',
          background: isDark
            ? 'radial-gradient(circle, rgba(56, 180, 190, 0.18), transparent 68%)'
            : 'radial-gradient(circle, rgba(18, 112, 122, 0.1), transparent 68%)',
          filter: 'blur(6px)',
          animation: 'sos-drift-a 20s ease-in-out infinite',
        }}
      />

      {scan && (
        <div
          className="sos-scan"
          style={{
            position: 'absolute',
            left: 0,
            right: 0,
            height: 140,
            background: isDark
              ? 'linear-gradient(180deg, transparent, rgba(120, 220, 220, 0.1), transparent)'
              : 'linear-gradient(180deg, transparent, rgba(10, 74, 82, 0.05), transparent)',
            animation: 'sos-scan 10s linear infinite',
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
