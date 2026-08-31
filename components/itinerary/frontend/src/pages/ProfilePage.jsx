import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import CompletedProfileCard from '@shared/CompletedProfileCard';
import { ensureSosSession, saveLinkedTouristSession, sosTouristApi } from '../api/sosClient';
import { useSiteI18n } from '@shared/i18n/react';
import { btnPrimary, btnSecondary, cardStyle, fieldStyle, labelStyle, T } from '../theme/sosProfile';

function editableValue(value) {
  const raw = String(value || '').trim();
  if (!raw || /^(pending|unknown|emergency contact)$/i.test(raw)) return '';
  return raw;
}

function touristToForm(tourist) {
  const ec = tourist.emergency_contact || {};
  const phone = editableValue(tourist.phone);
  const nationality = editableValue(tourist.nationality);
  const passport = editableValue(tourist.passport_or_nic);
  const emergencyName = editableValue(ec.name);
  const emergencyPhone = editableValue(ec.phone);
  return {
    name: tourist.name || '',
    email: tourist.email || '',
    phone,
    nationality,
    passport_or_nic: passport,
    trip_start: tourist.trip_start || '',
    trip_end: tourist.trip_end || '',
    hotel_name: tourist.hotel_name || '',
    hotel_contact: tourist.hotel_contact || '',
    emergency_name: emergencyName,
    emergency_phone: emergencyPhone,
    emergency_email: editableValue(ec.email),
    emergency_relationship: ec.relationship || '',
    emergency_contact: {
      name: emergencyName,
      phone: emergencyPhone,
      email: editableValue(ec.email),
      relationship: ec.relationship || '',
    },
    auth_provider: tourist.auth_provider,
    photo_url: tourist.photo_url || tourist.photo_path || '',
    secure_tourist_id: tourist.secure_tourist_id || '',
    profile_completed: Boolean(tourist.profile_completed),
    profile_completed_at: tourist.profile_completed_at || '',
    needs_complete: !passport || !nationality || !emergencyName || !emergencyPhone,
  };
}

function appendProfileFields(fd, form, password, photo, documentPhoto) {
  [
    'name',
    'phone',
    'nationality',
    'passport_or_nic',
    'trip_start',
    'trip_end',
    'hotel_name',
    'hotel_contact',
    'emergency_name',
    'emergency_phone',
    'emergency_email',
    'emergency_relationship',
  ].forEach((k) => {
    if (form[k] != null) fd.append(k, form[k]);
  });
  if (password) fd.append('password', password);
  if (photo) fd.append('photo', photo);
  if (documentPhoto) fd.append('document_photo', documentPhoto);
}

/**
 * Same visitor profile as Tourist SOS (frontend-tourist Profile).
 * Linked to the Tour Ceylon login — one account, one profile.
 * The form stays editable until the tourist generates a completed profile card.
 */
export default function ProfilePage() {
  const { language, t } = useSiteI18n();
  const [form, setForm] = useState(null);
  const [password, setPassword] = useState('');
  const [photo, setPhoto] = useState(null);
  const [documentPhoto, setDocumentPhoto] = useState(null);
  const [error, setError] = useState('');
  const [ok, setOk] = useState('');
  const [saving, setSaving] = useState(false);
  const [completing, setCompleting] = useState(false);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);

  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      try {
        if (!localStorage.getItem('touristToken')) {
          await ensureSosSession();
        }
        if (!localStorage.getItem('touristToken')) {
          if (!cancelled) {
            setError(t('signInFirstProfile'));
            setLoading(false);
          }
          return;
        }
        const { data } = await sosTouristApi.me();
        if (!cancelled) setForm(touristToForm(data.tourist));
      } catch (err) {
        if (!cancelled) setError(err?.response?.data?.error || t('couldNotLoadProfile'));
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    load();
    return () => {
      cancelled = true;
    };
    // Reload only when the page language changes — not on every render.
  }, [language, t]);

  const onChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const onSave = async (e) => {
    e.preventDefault();
    setError('');
    setOk('');
    setSaving(true);
    try {
      const fd = new FormData();
      appendProfileFields(fd, form, password, photo, documentPhoto);
      const { data } = await sosTouristApi.updateMe(fd);
      saveLinkedTouristSession({ tourist: data.tourist });
      setPassword('');
      setPhoto(null);
      setDocumentPhoto(null);
      setOk(t('profileSaved'));
      setForm(touristToForm(data.tourist));
      if (data.tourist?.profile_completed) setEditing(false);
    } catch (err) {
      setError(err?.response?.data?.error || t('saveFailed'));
    } finally {
      setSaving(false);
    }
  };

  const onGenerate = async () => {
    setError('');
    setOk('');
    setCompleting(true);
    try {
      const fd = new FormData();
      appendProfileFields(fd, form, password, photo, documentPhoto);
      const { data } = await sosTouristApi.completeMe(fd);
      saveLinkedTouristSession({ tourist: data.tourist });
      setPassword('');
      setPhoto(null);
      setDocumentPhoto(null);
      setOk(t('profileCompleted'));
      setForm(touristToForm(data.tourist));
    } catch (err) {
      const missing = err?.response?.data?.missing;
      setError(
        (Array.isArray(missing) && missing.length ? missing.join(' ') : null) ||
          err?.response?.data?.error ||
          t('completeProfileMissing'),
      );
    } finally {
      setCompleting(false);
    }
  };

  if (loading || !form) {
    return (
      <div style={{ width: 'min(100%, 560px)', margin: '0 auto', fontFamily: T.fontBody }}>
        {error ? (
          <div style={{ ...cardStyle, padding: 16 }}>
            <h2 style={{ marginTop: 0, fontFamily: T.fontDisplay, color: T.navy }}>{t('profile')}</h2>
            <p style={{ color: T.danger, background: T.dangerSoft, borderRadius: 8, padding: '10px 12px', fontSize: 14 }}>
              {error}
            </p>
            <Link className="btn btn-outline" to="/attractions">
              {t('back')}
            </Link>
          </div>
        ) : (
          <p style={{ padding: 32, textAlign: 'center', color: T.muted }}>{t('loadingProfile')}</p>
        )}
      </div>
    );
  }

  if (form.profile_completed && !editing) {
    return (
      <div style={{ width: 'min(100%, 560px)', margin: '0 auto', fontFamily: T.fontBody, paddingBottom: 24 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 12, marginBottom: 16 }}>
          <div>
            <h1 style={{ margin: '0 0 6px', fontFamily: T.fontDisplay, fontSize: 24, fontWeight: 800, color: T.navy }}>
              {t('yourProfile')}
            </h1>
            <p style={{ margin: 0, color: T.muted, fontSize: 14 }}>{t('profileCompleted')}</p>
          </div>
          <div style={{ display: 'flex', gap: 8, flexShrink: 0 }}>
            <button type="button" className="btn btn-outline" onClick={() => setEditing(true)}>
              {t('editProfile')}
            </button>
            <Link className="btn btn-outline" to="/attractions">
              {t('back')}
            </Link>
          </div>
        </div>
        {error && (
          <p style={{ color: T.danger, background: T.dangerSoft, borderRadius: 8, padding: '10px 12px', fontSize: 14 }}>
            {error}
          </p>
        )}
        {ok && (
          <p style={{ color: T.success, background: T.successSoft, borderRadius: 8, padding: '10px 12px', fontSize: 14 }}>
            {ok}
          </p>
        )}
        <CompletedProfileCard tourist={form} t={t} onEdit={() => setEditing(true)} />
      </div>
    );
  }

  return (
    <div style={{ width: 'min(100%, 480px)', margin: '0 auto', fontFamily: T.fontBody, paddingBottom: 120 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 12, marginBottom: 8 }}>
        <div>
          <h1 style={{ margin: '0 0 6px', fontFamily: T.fontDisplay, fontSize: 24, fontWeight: 800, color: T.navy }}>
            {t('yourProfile')}
          </h1>
          <p style={{ margin: '0 0 14px', color: T.muted, fontSize: 14 }}>
            {t('editProfileDesc')} {form.email || t('googleAccount')}
            {form.auth_provider ? ` · ${form.auth_provider}` : ''}
          </p>
        </div>
        <div style={{ display: 'flex', gap: 8, flexShrink: 0 }}>
          {form.profile_completed && (
            <button type="button" className="btn btn-outline" onClick={() => setEditing(false)}>
              {t('cancelEdit')}
            </button>
          )}
          <Link className="btn btn-outline" to="/attractions">
            {t('back')}
          </Link>
        </div>
      </div>

      {form.needs_complete && (
        <p
          style={{
            margin: '0 0 14px',
            padding: '12px 14px',
            borderRadius: 10,
            background: '#FFF8E1',
            color: '#F57F17',
            fontSize: 13.5,
            fontWeight: 600,
          }}
        >
          {t('completePassportHint')}
        </p>
      )}

      <form onSubmit={onSave} style={{ ...cardStyle, padding: '16px 16px' }}>
        <label style={labelStyle}>
          {t('fullName')}
          <input
            style={fieldStyle}
            name="name"
            value={form.name}
            onChange={onChange}
            autoComplete="name"
            required
          />
        </label>
        <label style={labelStyle}>
          {t('phone')}
          <input
            style={fieldStyle}
            name="phone"
            value={form.phone}
            onChange={onChange}
            placeholder={t('phone')}
            autoComplete="tel"
            required
          />
        </label>
        <label style={labelStyle}>
          {t('nationality')}
          <input
            style={fieldStyle}
            name="nationality"
            value={form.nationality}
            onChange={onChange}
            placeholder={t('nationality')}
            autoComplete="country-name"
            required
          />
        </label>
        <label style={labelStyle}>
          {t('passportNic')}
          <input
            style={fieldStyle}
            name="passport_or_nic"
            value={form.passport_or_nic}
            onChange={onChange}
            placeholder={t('passportNic')}
            autoComplete="off"
            required
          />
        </label>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
          <label style={labelStyle}>
            {t('tripStart')}
            <input
              style={fieldStyle}
              type="date"
              name="trip_start"
              value={form.trip_start || ''}
              onChange={onChange}
            />
          </label>
          <label style={labelStyle}>
            {t('tripEnd')}
            <input
              style={fieldStyle}
              type="date"
              name="trip_end"
              value={form.trip_end || ''}
              onChange={onChange}
            />
          </label>
        </div>
        <label style={labelStyle}>
          {t('hotelName')}
          <input style={fieldStyle} name="hotel_name" value={form.hotel_name} onChange={onChange} />
        </label>
        <label style={labelStyle}>
          {t('hotelContact')}
          <input style={fieldStyle} name="hotel_contact" value={form.hotel_contact} onChange={onChange} />
        </label>

        <p
          style={{
            margin: '8px 0 6px',
            fontSize: 12,
            fontWeight: 700,
            color: T.muted,
            textTransform: 'uppercase',
          }}
        >
          {t('emergencyContact')}
        </p>
        <label style={labelStyle}>
          {t('emergencyName')}
          <input
            style={fieldStyle}
            name="emergency_name"
            value={form.emergency_name}
            onChange={onChange}
            required
          />
        </label>
        <label style={labelStyle}>
          {t('emergencyPhone')}
          <input
            style={fieldStyle}
            name="emergency_phone"
            value={form.emergency_phone}
            onChange={onChange}
            required
          />
        </label>
        <label style={labelStyle}>
          {t('emergencyEmail')}
          <input
            style={fieldStyle}
            type="email"
            name="emergency_email"
            value={form.emergency_email}
            onChange={onChange}
          />
        </label>
        <label style={labelStyle}>
          {t('emergencyRelationship')}
          <input
            style={fieldStyle}
            name="emergency_relationship"
            value={form.emergency_relationship}
            onChange={onChange}
          />
        </label>

        <label style={labelStyle}>
          {t('newPassword')}
          <input
            style={fieldStyle}
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            minLength={6}
            autoComplete="new-password"
          />
        </label>
        <label style={labelStyle}>
          {t('updatePhoto')}
          <input
            type="file"
            accept="image/*"
            onChange={(e) => setPhoto(e.target.files?.[0] || null)}
            style={{ fontSize: 13 }}
          />
        </label>
        <label style={labelStyle}>
          {t('updateDocument')}
          <input
            type="file"
            accept="image/*"
            onChange={(e) => setDocumentPhoto(e.target.files?.[0] || null)}
            style={{ fontSize: 13 }}
          />
        </label>

        {error && (
          <p
            style={{
              color: T.danger,
              background: T.dangerSoft,
              borderRadius: 8,
              padding: '10px 12px',
              fontSize: 14,
            }}
          >
            {error}
          </p>
        )}
        {ok && (
          <p
            style={{
              color: T.success,
              background: T.successSoft,
              borderRadius: 8,
              padding: '10px 12px',
              fontSize: 14,
            }}
          >
            {ok}
          </p>
        )}

        <div
          style={{
            position: 'sticky',
            bottom: 16,
            zIndex: 6,
            marginTop: 8,
            paddingTop: 8,
            background: T.surface,
          }}
        >
          <button
            type="submit"
            disabled={saving || completing}
            style={{ ...btnPrimary, width: '100%', opacity: saving ? 0.7 : 1 }}
          >
            {saving ? t('savingEllipsis') : form.profile_completed ? t('saveChanges') : t('saveProfile')}
          </button>
          {!form.profile_completed && (
            <button
              type="button"
              disabled={saving || completing}
              onClick={onGenerate}
              style={{ ...btnSecondary, width: '100%', marginTop: 10, opacity: completing ? 0.7 : 1 }}
            >
              {completing ? t('generatingProfile') : t('generateCompletedProfile')}
            </button>
          )}
        </div>
      </form>
    </div>
  );
}
