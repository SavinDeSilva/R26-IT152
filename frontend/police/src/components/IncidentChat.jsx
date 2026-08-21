import { useCallback, useEffect, useRef, useState } from 'react'
import { ImagePlus, Mic, Send, Square } from 'lucide-react'
import api from '../api/client'
import { T } from '../theme'

const POLL_MS = 4000

function mediaSrc(pathOrUrl) {
  if (!pathOrUrl) return null
  if (pathOrUrl.startsWith('http') || pathOrUrl.startsWith('/')) {
    const base = import.meta.env.VITE_API_URL || ''
    if (pathOrUrl.startsWith('/') && base) return `${base.replace(/\/$/, '')}${pathOrUrl}`
    return pathOrUrl
  }
  const base = import.meta.env.VITE_API_URL || ''
  return `${base.replace(/\/$/, '')}/uploads/${pathOrUrl}`
}

export default function IncidentChat({ incidentId, stationName }) {
  const [messages, setMessages] = useState([])
  const [text, setText] = useState('')
  const [error, setError] = useState('')
  const [sending, setSending] = useState(false)
  const [recording, setRecording] = useState(false)
  const listRef = useRef(null)
  const mediaRecorderRef = useRef(null)
  const chunksRef = useRef([])
  const sinceIdRef = useRef(0)
  const imageInputRef = useRef(null)

  const load = useCallback(async () => {
    if (!incidentId) return
    try {
      const { data } = await api.get(`/api/incidents/${incidentId}/messages`, {
        params: { since_id: sinceIdRef.current || undefined },
      })
      const batch = data.messages || []
      if (batch.length) {
        setMessages((prev) => {
          const ids = new Set(prev.map((m) => m.id))
          const merged = [...prev]
          for (const m of batch) {
            if (!ids.has(m.id)) merged.push(m)
          }
          return merged
        })
        sinceIdRef.current = Math.max(sinceIdRef.current, ...batch.map((m) => m.id))
      }
      setError('')
    } catch (err) {
      setError(err?.response?.data?.error || 'Could not load chat')
    }
  }, [incidentId])

  useEffect(() => {
    sinceIdRef.current = 0
    setMessages([])
    load()
    const t = setInterval(load, POLL_MS)
    return () => clearInterval(t)
  }, [load])

  useEffect(() => {
    if (listRef.current) listRef.current.scrollTop = listRef.current.scrollHeight
  }, [messages])

  const sendText = async (e) => {
    e?.preventDefault?.()
    const body = text.trim()
    if (!body || sending) return
    setSending(true)
    try {
      const form = new FormData()
      form.append('message_type', 'text')
      form.append('body', body)
      const { data } = await api.post(`/api/incidents/${incidentId}/messages`, form)
      setText('')
      if (data.message) {
        setMessages((prev) => (prev.some((m) => m.id === data.message.id) ? prev : [...prev, data.message]))
        sinceIdRef.current = Math.max(sinceIdRef.current, data.message.id)
      }
    } catch (err) {
      alert(err?.response?.data?.error || 'Failed to send')
    } finally {
      setSending(false)
    }
  }

  const sendMedia = async (file, messageType) => {
    if (!file || sending) return
    setSending(true)
    try {
      const form = new FormData()
      form.append('message_type', messageType)
      form.append('media', file)
      const { data } = await api.post(`/api/incidents/${incidentId}/messages`, form)
      if (data.message) {
        setMessages((prev) => (prev.some((m) => m.id === data.message.id) ? prev : [...prev, data.message]))
        sinceIdRef.current = Math.max(sinceIdRef.current, data.message.id)
      }
    } catch (err) {
      alert(err?.response?.data?.error || `Failed to send ${messageType}`)
    } finally {
      setSending(false)
    }
  }

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mime = MediaRecorder.isTypeSupported('audio/webm') ? 'audio/webm' : undefined
      const recorder = new MediaRecorder(stream, mime ? { mimeType: mime } : undefined)
      chunksRef.current = []
      recorder.ondataavailable = (ev) => {
        if (ev.data?.size) chunksRef.current.push(ev.data)
      }
      recorder.onstop = async () => {
        stream.getTracks().forEach((t) => t.stop())
        const blob = new Blob(chunksRef.current, { type: recorder.mimeType || 'audio/webm' })
        const file = new File([blob], 'voice.webm', { type: blob.type })
        await sendMedia(file, 'voice')
      }
      mediaRecorderRef.current = recorder
      recorder.start()
      setRecording(true)
    } catch {
      alert('Microphone permission is required for voice messages.')
    }
  }

  const stopRecording = () => {
    const rec = mediaRecorderRef.current
    if (rec && rec.state !== 'inactive') rec.stop()
    setRecording(false)
  }

  return (
    <div style={{
      display: 'flex', flexDirection: 'column', background: T.surface,
      border: `1px solid ${T.line}`, borderRadius: 12, overflow: 'hidden', minHeight: 360, maxHeight: 460,
    }}>
      <div style={{ padding: '12px 14px', borderBottom: `1px solid ${T.line}`, background: T.navySoft }}>
        <p style={{ margin: 0, fontSize: 13, fontWeight: 700, color: T.navy }}>Tourist chat</p>
        <p style={{ margin: '4px 0 0', fontSize: 12, color: T.muted }}>
          Private to this station{stationName ? ` (${stationName})` : ''}. Text, image, and voice.
        </p>
      </div>

      <div ref={listRef} style={{
        flex: 1, overflowY: 'auto', padding: 12, display: 'flex', flexDirection: 'column', gap: 8, background: T.page,
      }}>
        {messages.length === 0 && !error && (
          <p style={{ margin: 'auto', color: T.muted, fontSize: 13, textAlign: 'center' }}>Waiting for tourist messages…</p>
        )}
        {error && <p style={{ color: T.danger, fontSize: 13 }}>{error}</p>}
        {messages.map((m) => {
          const mine = m.sender_role === 'officer'
          return (
            <div
              key={m.id}
              style={{
                alignSelf: mine ? 'flex-end' : 'flex-start',
                maxWidth: '85%',
                background: mine ? T.navy : T.surface,
                color: mine ? T.white : T.ink,
                borderRadius: 12,
                padding: '8px 10px',
                border: mine ? 'none' : `1px solid ${T.line}`,
              }}
            >
              <p style={{ margin: '0 0 4px', fontSize: 10, opacity: 0.75, fontWeight: 600 }}>
                {m.sender_role === 'tourist' ? 'Tourist' : 'You'} · {m.message_type}
              </p>
              {m.message_type === 'image' && m.media_url && (
                <a href={mediaSrc(m.media_url)} target="_blank" rel="noreferrer">
                  <img src={mediaSrc(m.media_url)} alt="" style={{ display: 'block', maxWidth: '100%', borderRadius: 8 }} />
                </a>
              )}
              {m.message_type === 'voice' && m.media_url && (
                <audio controls src={mediaSrc(m.media_url)} style={{ width: '100%', maxWidth: 240 }} />
              )}
              {m.body && <p style={{ margin: m.message_type !== 'text' ? '6px 0 0' : 0, fontSize: 14, whiteSpace: 'pre-wrap' }}>{m.body}</p>}
            </div>
          )
        })}
      </div>

      <form onSubmit={sendText} style={{ display: 'flex', gap: 6, padding: 10, borderTop: `1px solid ${T.line}` }}>
        <input ref={imageInputRef} type="file" accept="image/*" style={{ display: 'none' }} onChange={(e) => {
          const f = e.target.files?.[0]
          e.target.value = ''
          if (f) sendMedia(f, 'image')
        }} />
        <button type="button" onClick={() => imageInputRef.current?.click()} disabled={sending || recording} style={iconBtn}>
          <ImagePlus size={18} />
        </button>
        <button
          type="button"
          onClick={recording ? stopRecording : startRecording}
          disabled={sending}
          style={{ ...iconBtn, background: recording ? T.dangerSoft : T.navySoft, color: recording ? T.danger : T.navy }}
        >
          {recording ? <Square size={16} /> : <Mic size={18} />}
        </button>
        <input
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Reply to tourist…"
          disabled={sending || recording}
          style={{
            flex: 1, border: `1px solid ${T.line}`, borderRadius: 8, padding: '10px 12px',
            fontFamily: T.fontBody, fontSize: 14, outline: 'none',
          }}
        />
        <button type="submit" disabled={sending || !text.trim()} style={{ ...iconBtn, background: T.navy, color: T.white }}>
          <Send size={16} />
        </button>
      </form>
    </div>
  )
}

const iconBtn = {
  width: 40, height: 40, border: 'none', borderRadius: 8, background: T.navySoft, color: T.navy,
  display: 'grid', placeItems: 'center', cursor: 'pointer', flexShrink: 0,
}
