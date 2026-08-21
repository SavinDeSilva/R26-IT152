import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api/client'
import AmbientBackground from '../components/AmbientBackground'
import PoliceBadge from '../components/PoliceBadge'
import { btnPrimary, panel, T } from '../theme'

const field = {
  width: '100%',
  boxSizing: 'border-box',
  border: `1px solid ${T.line}`,
  background: T.surface,
  borderRadius: T.radiusSm,
  padding: '12px 14px',
  fontFamily: T.fontBody,
  fontSize: 15,
  outline: 'none',
  color: T.ink,
}

export default function Login() {
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const onSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const { data } = await api.post('/api/auth/login', { username, password })
      localStorage.setItem('policeToken', data.access_token)
      localStorage.setItem('policeOfficer', JSON.stringify(data.officer))
      navigate('/', { replace: true })
    } catch (err) {
      setError(err?.response?.data?.error || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div
      style={{
        position: 'relative',
        minHeight: '100dvh',
        display: 'grid',
        placeItems: 'center',
        padding: 24,
        fontFamily: T.fontBody,
        overflow: 'hidden',
      }}
    >
      <AmbientBackground variant="dark" scan />
      <form
        onSubmit={onSubmit}
        style={{
          ...panel,
          position: 'relative',
          zIndex: 1,
          width: 'min(100%, 400px)',
          padding: '32px 28px',
          animation: 'sos-fade-up 0.55s ease-out',
          boxShadow: '0 24px 60px rgba(0,0,0,0.35)',
        }}
      >
        <div style={{ marginBottom: 16, display: 'flex', alignItems: 'center', gap: 12 }}>
          <PoliceBadge size={56} />
          <span style={{ fontSize: 12, fontWeight: 700, color: T.navy, letterSpacing: '0.06em', textTransform: 'uppercase' }}>
            Sri Lanka Police
          </span>
        </div>
        <h1 style={{ margin: '0 0 6px', fontFamily: T.fontDisplay, fontSize: 26, fontWeight: 800, color: T.navy, letterSpacing: '-0.02em' }}>
          SOS Operations
        </h1>
        <p style={{ margin: '0 0 22px', color: T.muted, fontSize: 14 }}>
          Station login — each station has its own username &amp; password
        </p>

        <label style={{ display: 'flex', flexDirection: 'column', gap: 6, marginBottom: 14, fontSize: 13, color: T.muted, fontWeight: 600 }}>
          Username
          <input
            style={field}
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value.trim())}
            required
            autoComplete="username"
            spellCheck={false}
          />
        </label>
        <label style={{ display: 'flex', flexDirection: 'column', gap: 6, marginBottom: 14, fontSize: 13, color: T.muted, fontWeight: 600 }}>
          Password
          <input style={field} type="password" value={password} onChange={(e) => setPassword(e.target.value)} required autoComplete="current-password" />
        </label>

        {error && (
          <p style={{ color: T.danger, background: T.dangerSoft, borderRadius: 8, padding: '10px 12px', margin: '0 0 14px', fontSize: 14 }}>{error}</p>
        )}

        <button type="submit" disabled={loading} style={{ ...btnPrimary, width: '100%', padding: '14px 18px', opacity: loading ? 0.7 : 1, cursor: loading ? 'wait' : 'pointer' }}>
          {loading ? 'Signing in…' : 'Sign in'}
        </button>
      </form>
    </div>
  )
}
