import { useEffect } from 'react'
import { goToTravelApp } from '../api/sessionHandoff'
import { T } from '../theme'

/** Registration is only on Tour Ceylon — one account for both apps. */
export default function Register() {
  useEffect(() => {
    goToTravelApp('/login')
  }, [])

  return (
    <div style={{ minHeight: '100dvh', display: 'grid', placeItems: 'center', background: T.page, fontFamily: T.fontBody }}>
      <p style={{ color: T.muted, padding: 24, textAlign: 'center' }}>
        Redirecting to Tour Ceylon to create your account…
      </p>
    </div>
  )
}
