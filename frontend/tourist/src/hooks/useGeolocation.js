import { useCallback, useState } from 'react'

/**
 * Fresh current location ONLY — never cached device location, never watchPosition.
 *
 * Browser options used:
 * - maximumAge: 0  → reject cached/last-known device fixes; force a new reading
 * - enableHighAccuracy: true → prefer live GPS when available
 * - no watchPosition → location is never tracked continuously
 */
export default function useGeolocation() {
  const [position, setPosition] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  const getCurrent = useCallback(() => {
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        const err = new Error('Geolocation not supported')
        setError(err)
        reject(err)
        return
      }
      setLoading(true)
      // One-shot only. Never use watchPosition / last-known device cache.
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          const data = {
            latitude: pos.coords.latitude,
            longitude: pos.coords.longitude,
            accuracy: pos.coords.accuracy,
            timestamp: pos.timestamp,
          }
          setPosition(data)
          setError(null)
          setLoading(false)
          resolve(data)
        },
        (err) => {
          setError(err)
          setLoading(false)
          reject(err)
        },
        {
          enableHighAccuracy: true,
          timeout: 20000,
          maximumAge: 0, // critical: do not reuse stored device location
        },
      )
    })
  }, [])

  return { position, error, loading, getCurrent }
}
