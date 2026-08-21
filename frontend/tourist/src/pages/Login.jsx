import { useEffect } from 'react'
import { goToTravelLogin } from '../api/sessionHandoff'
import { T } from '../theme'

/** Single login: Tour Ceylon only. */
export default function Login() {
  useEffect(() => {
    goToTravelLogin()
  }, [])

  return (
    <div style={{ minHeight: '100dvh', display: 'grid', placeItems: 'center', background: T.page, fontFamily: T.fontBody }}>
      <p style={{ color: T.muted, padding: 24, textAlign: 'center' }}>
        Opening Tour Ceylon login…
      </p>
    </div>
  )
}
