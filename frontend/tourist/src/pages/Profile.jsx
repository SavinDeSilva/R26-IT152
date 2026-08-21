import { useEffect, useState } from 'react'
import api, { saveTouristSession } from '../api/client'
import TouristNav from '../components/TouristNav'
import { btnPrimary, cardStyle, fieldStyle, labelStyle, T } from '../theme'

export default function Profile() {
  const [form, setForm] = useState(null)
  const [password, setPassword] = useState('')
  const [photo, setPhoto] = useState(null)
  const [documentPhoto, setDocumentPhoto] = useState(null)
  const [error, setError] = useState('')
  const [ok, setOk] = useState('')
  const [saving, setSaving] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const load = async () => {
      try {
        const { data } = await api.get('/api/tourists/me')
        const t = data.tourist
        const ec = t.emergency_contact || {}
        setForm({
          name: t.name || '',
          email: t.email || '',
          phone: t.phone || '',
          nationality: t.nationality || '',
          passport_or_nic: t.passport_or_nic || '',
          trip_start: t.trip_start || '',
          trip_end: t.trip_end || '',
          hotel_name: t.hotel_name || '',
          hotel_contact: t.hotel_contact || '',
          emergency_name: ec.name || '',
          emergency_phone: ec.phone || '',
          emergency_email: ec.email || '',
          emergency_relationship: ec.relationship || '',
          auth_provider: t.auth_provider,
          needs_complete: t.passport_or_nic === 'pending' || t.nationality === 'Unknown',
        })
      } catch (err) {
        setError(err?.response?.data?.error || 'Could not load profile')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  const onChange = (e) => {
    const { name, value } = e.target
    setForm((prev) => ({ ...prev, [name]: value }))
  }

  const onSave = async (e) => {
    e.preventDefault()
    setError('')
    setOk('')
    setSaving(true)
    try {
      const fd = new FormData()
      ;[
        'name', 'phone', 'nationality', 'passport_or_nic', 'trip_start', 'trip_end',
        'hotel_name', 'hotel_contact', 'emergency_name', 'emergency_phone',
        'emergency_email', 'emergency_relationship',
      ].forEach((k) => {
        if (form[k] != null) fd.append(k, form[k])
      })
      if (password) fd.append('password', password)
      if (photo) fd.append('photo', photo)
      if (documentPhoto) fd.append('document_photo', documentPhoto)

      const { data } = await api.patch('/api/tourists/me', fd)
      saveTouristSession({ tourist: data.tourist })
      setPassword('')
      setOk('Profile saved')
      setForm((prev) => ({
        ...prev,
        needs_complete: data.tourist.passport_or_nic === 'pending' || data.tourist.nationality === 'Unknown',
      }))
    } catch (err) {
      setError(err?.response?.data?.error || 'Save failed')
    } finally {
      setSaving(false)
    }
  }

  if (loading || !form) {
    return (
      <>
        <TouristNav />
        <p style={{ padding: 32, textAlign: 'center', color: T.muted }}>Loading profile…</p>
      </>
    )
  }

  return (
    <>
      <TouristNav />
      <div className="sos-page" style={{ fontFamily: T.fontBody, paddingBottom: '7rem' }}>
        <h1 style={{ margin: '0 0 6px', fontFamily: T.fontBody, fontSize: 24, fontWeight: 800, color: T.navy }}>Your profile</h1>
        <p style={{ margin: '0 0 14px', color: T.muted, fontSize: 14 }}>
          Edit your visitor details anytime. Login: {form.email || 'Google account'}
          {form.auth_provider ? ` · ${form.auth_provider}` : ''}
        </p>

        {form.needs_complete && (
          <p style={{ margin: '0 0 14px', padding: '12px 14px', borderRadius: 10, background: '#FFF8E1', color: '#F57F17', fontSize: 13.5, fontWeight: 600 }}>
            Complete your passport / nationality / emergency contact so police have accurate details.
          </p>
        )}

        <form onSubmit={onSave} style={{ ...cardStyle, padding: '16px 16px' }}>
          <label style={labelStyle}>Full name<input style={fieldStyle} name="name" value={form.name} onChange={onChange} required /></label>
          <label style={labelStyle}>Phone<input style={fieldStyle} name="phone" value={form.phone} onChange={onChange} required /></label>
          <label style={labelStyle}>Nationality<input style={fieldStyle} name="nationality" value={form.nationality} onChange={onChange} required /></label>
          <label style={labelStyle}>Passport / NIC<input style={fieldStyle} name="passport_or_nic" value={form.passport_or_nic} onChange={onChange} required /></label>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            <label style={labelStyle}>Trip start<input style={fieldStyle} type="date" name="trip_start" value={form.trip_start || ''} onChange={onChange} /></label>
            <label style={labelStyle}>Trip end<input style={fieldStyle} type="date" name="trip_end" value={form.trip_end || ''} onChange={onChange} /></label>
          </div>
          <label style={labelStyle}>Hotel name<input style={fieldStyle} name="hotel_name" value={form.hotel_name} onChange={onChange} /></label>
          <label style={labelStyle}>Hotel contact<input style={fieldStyle} name="hotel_contact" value={form.hotel_contact} onChange={onChange} /></label>

          <p style={{ margin: '8px 0 6px', fontSize: 12, fontWeight: 700, color: T.muted, textTransform: 'uppercase' }}>Emergency contact</p>
          <label style={labelStyle}>Name<input style={fieldStyle} name="emergency_name" value={form.emergency_name} onChange={onChange} required /></label>
          <label style={labelStyle}>Phone<input style={fieldStyle} name="emergency_phone" value={form.emergency_phone} onChange={onChange} required /></label>
          <label style={labelStyle}>Email<input style={fieldStyle} type="email" name="emergency_email" value={form.emergency_email} onChange={onChange} /></label>
          <label style={labelStyle}>Relationship<input style={fieldStyle} name="emergency_relationship" value={form.emergency_relationship} onChange={onChange} /></label>

          <label style={labelStyle}>New password (optional)<input style={fieldStyle} type="password" value={password} onChange={(e) => setPassword(e.target.value)} minLength={6} autoComplete="new-password" /></label>
          <label style={labelStyle}>Update photo<input type="file" accept="image/*" onChange={(e) => setPhoto(e.target.files?.[0] || null)} style={{ fontSize: 13 }} /></label>
          <label style={labelStyle}>Update document photo<input type="file" accept="image/*" onChange={(e) => setDocumentPhoto(e.target.files?.[0] || null)} style={{ fontSize: 13 }} /></label>

          {error && <p style={{ color: T.danger, background: T.dangerSoft, borderRadius: 8, padding: '10px 12px', fontSize: 14 }}>{error}</p>}
          {ok && <p style={{ color: T.success, background: T.successSoft, borderRadius: 8, padding: '10px 12px', fontSize: 14 }}>{ok}</p>}

          <button type="submit" disabled={saving} style={{ ...btnPrimary, width: '100%', marginTop: 8, opacity: saving ? 0.7 : 1 }}>
            {saving ? 'Saving…' : 'Save profile'}
          </button>
        </form>
      </div>
    </>
  )
}
