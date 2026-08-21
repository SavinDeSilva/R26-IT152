import { useEffect, useState } from 'react'
import { T } from '../theme'

function formatDuration(ms) {
  const totalSec = Math.max(0, Math.floor(ms / 1000))
  const h = Math.floor(totalSec / 3600)
  const m = Math.floor((totalSec % 3600) / 60)
  const s = totalSec % 60
  if (h > 0) return `${h}h ${String(m).padStart(2, '0')}m ${String(s).padStart(2, '0')}s`
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
}

export default function ResponseClock({ startedAt, endedAt, label = 'Elapsed' }) {
  const [now, setNow] = useState(Date.now())

  useEffect(() => {
    if (endedAt) return undefined
    const id = setInterval(() => setNow(Date.now()), 1000)
    return () => clearInterval(id)
  }, [endedAt])

  if (!startedAt) return null
  const start = new Date(startedAt).getTime()
  const end = endedAt ? new Date(endedAt).getTime() : now

  return (
    <div
      style={{
        display: 'inline-flex',
        flexDirection: 'column',
        gap: 4,
        background: endedAt ? T.muted : T.navy,
        color: T.white,
        padding: '12px 14px',
        borderRadius: 10,
        minWidth: 130,
        fontFamily: T.fontBody,
      }}
    >
      <span style={{ fontSize: 11, opacity: 0.85 }}>{label}</span>
      <span style={{ fontSize: 20, fontWeight: 700, fontVariantNumeric: 'tabular-nums', fontFamily: T.fontMono }}>
        {formatDuration(end - start)}
      </span>
    </div>
  )
}
