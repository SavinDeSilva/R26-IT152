import { useState } from 'react'
import { Phone } from 'lucide-react'
import api from '../api/client'
import useGeolocation from '../hooks/useGeolocation'
import { T } from '../theme'

export default function CallNearestHospital() {
  const { getCurrent } = useGeolocation()
  const [busy, setBusy] = useState(false)
  const [hint, setHint] = useState('')

  const onCall = async () => {
    setBusy(true)
    setHint('')
    try {
      let lat
      let lng
      try {
        // Fresh current location only — never reuse cached device location
        const pos = await getCurrent()
        lat = pos.latitude
        lng = pos.longitude
      } catch {
        setHint('Could not get your current location. Enable location and try again.')
        return
      }

      const { data } = await api.get('/api/hospitals/nearest', { params: { lat, lng } })
      const number = data.dial_number
      if (!number) {
        setHint('No phone number for nearest hospital.')
        return
      }

      const name = data.hospital?.name || 'Hospital'
      const dist = data.distance_km != null ? ` · ${data.distance_km.toFixed(1)} km` : ''
      setHint(`${name}${dist}`)
      window.location.href = `tel:${number}`
    } catch (err) {
      setHint(err?.response?.data?.error || 'Could not find a nearby hospital.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div>
      <button
        type="button"
        onClick={onCall}
        disabled={busy}
        style={{
          width: '100%',
          display: 'inline-flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 8,
          border: `1px solid ${T.success}`,
          background: T.successSoft,
          color: T.success,
          borderRadius: T.radiusSm,
          padding: '14px 16px',
          fontWeight: 650,
          fontSize: 15,
          cursor: busy ? 'wait' : 'pointer',
          opacity: busy ? 0.7 : 1,
          fontFamily: T.fontBody,
        }}
      >
        <Phone size={18} strokeWidth={2} />
        {busy ? 'Finding hospital…' : 'Call nearest hospital'}
      </button>
      {hint && <p style={{ margin: '10px 0 0', fontSize: 13.5, color: T.success, lineHeight: 1.4 }}>{hint}</p>}
    </div>
  )
}
