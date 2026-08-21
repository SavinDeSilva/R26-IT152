import { useEffect, useRef, useState } from 'react'
import api from '../api/client'
import { T } from '../theme'

/**
 * Google Identity Services button.
 * Requires VITE_GOOGLE_CLIENT_ID (or server /auth/config) to be set.
 */
export default function GoogleSignIn({ onCredential, disabled }) {
  const btnRef = useRef(null)
  const [clientId, setClientId] = useState(import.meta.env.VITE_GOOGLE_CLIENT_ID || '')
  const [ready, setReady] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    let cancelled = false
    const load = async () => {
      try {
        const { data } = await api.get('/api/tourists/auth/config')
        if (!cancelled && data.google_client_id) {
          setClientId(data.google_client_id)
        }
      } catch {
        /* use env fallback */
      }
    }
    load()
    return () => {
      cancelled = true
    }
  }, [])

  useEffect(() => {
    if (!clientId || disabled) return undefined

    const init = () => {
      if (!window.google?.accounts?.id || !btnRef.current) return
      window.google.accounts.id.initialize({
        client_id: clientId,
        callback: (response) => {
          if (response?.credential) onCredential?.(response.credential)
        },
      })
      btnRef.current.innerHTML = ''
      window.google.accounts.id.renderButton(btnRef.current, {
        theme: 'outline',
        size: 'large',
        width: btnRef.current.offsetWidth || 320,
        text: 'continue_with',
        shape: 'rectangular',
      })
      setReady(true)
    }

    if (window.google?.accounts?.id) {
      init()
      return undefined
    }

    const existing = document.getElementById('google-gsi')
    if (existing) {
      existing.addEventListener('load', init)
      return () => existing.removeEventListener('load', init)
    }

    const script = document.createElement('script')
    script.id = 'google-gsi'
    script.src = 'https://accounts.google.com/gsi/client'
    script.async = true
    script.defer = true
    script.onload = init
    script.onerror = () => setError('Could not load Google Sign-In')
    document.head.appendChild(script)
    return undefined
  }, [clientId, disabled, onCredential])

  if (!clientId) {
    return (
      <p style={{ margin: '12px 0 0', fontSize: 12.5, color: T.muted, textAlign: 'center', lineHeight: 1.4 }}>
        Google login: set <span style={{ fontFamily: T.fontMono }}>GOOGLE_CLIENT_ID</span> in backend `.env`
        (and optionally <span style={{ fontFamily: T.fontMono }}>VITE_GOOGLE_CLIENT_ID</span>).
      </p>
    )
  }

  return (
    <div>
      <div ref={btnRef} style={{ width: '100%', minHeight: 44, opacity: disabled ? 0.5 : 1 }} />
      {!ready && !error && (
        <p style={{ margin: '8px 0 0', fontSize: 12, color: T.muted, textAlign: 'center' }}>Loading Google…</p>
      )}
      {error && <p style={{ margin: '8px 0 0', fontSize: 12, color: T.danger, textAlign: 'center' }}>{error}</p>}
    </div>
  )
}
