/**
 * ItineraryPage.jsx — day-by-day schedule after Attractions → Budget → Stay.
 */
import { useEffect, useMemo, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { itineraryApi } from '../api/client';
import { useTrip } from '../context/TripContext';
import { useSiteI18n } from '@shared/i18n/react';

const colors = {
  primary: '#4EC6D4',
  primaryLight: '#b6E6E9',
  primaryDark: '#1E6E6F',
  seafoam: '#7AC7BD',
  accent: '#F2D9B7',
  background: '#eef8f8',
  text: '#1E6E6F',
  textMuted: '#4a8586',
  border: 'rgba(30, 110, 111, 0.14)',
  glass: '#ffffff',
  error: '#B91C1C',
  white: '#FFFFFF',
};

const fontBody = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif";

const styles = {
  container: {
    background: colors.background,
    fontFamily: fontBody,
    color: colors.text,
    padding: 0,
    width: '100%',
    maxWidth: '1400px',
    margin: '0 auto',
    minHeight: '100%',
    position: 'relative',
    animation: 'fadeRise 0.55s ease both',
    overflowX: 'hidden',
    boxSizing: 'border-box',
    paddingBottom: '5.5rem',
  },
  hero: {
    position: 'relative',
    margin: '0 0 1.25rem',
    borderRadius: '16px',
    overflow: 'hidden',
    width: '100%',
    background: 'rgba(255, 255, 255, 0.38)',
    minHeight: 0,
    display: 'flex',
    alignItems: 'center',
    padding: '1.6rem 1.35rem',
    boxShadow: '0 18px 48px rgba(30, 110, 111, 0.14)',
  },
  heroBg: {
    position: 'absolute',
    inset: 0,
    backgroundImage: 'url("/header-lagoon.png")',
    backgroundSize: 'cover',
    backgroundPosition: 'center',
    opacity: 0.42,
    pointerEvents: 'none',
  },
  heroContent: {
    position: 'relative',
    zIndex: 2,
    width: '100%',
    minWidth: 0,
  },
  heroBadge: {
    display: 'inline-block',
    background: colors.accent,
    padding: '0.28rem 0.9rem',
    borderRadius: '999px',
    fontSize: '0.65rem',
    fontWeight: 700,
    letterSpacing: '0.08em',
    textTransform: 'uppercase',
    color: colors.primaryDark,
    marginBottom: '0.7rem',
  },
  heroTitle: {
    fontSize: 'clamp(1.35rem, 4.2vw, 2.15rem)',
    fontWeight: 700,
    fontFamily: fontBody,
    color: '#0e4a4e',
    margin: '0 0 0.45rem',
    letterSpacing: '-0.02em',
    lineHeight: 1.2,
  },
  heroSubtitle: {
    fontSize: 'clamp(0.82rem, 2.6vw, 0.98rem)',
    color: '#16575c',
    maxWidth: '42rem',
    margin: '0 0 1rem',
    lineHeight: 1.55,
  },
  heroMeta: {
    display: 'flex',
    gap: '0.5rem',
    flexWrap: 'wrap',
  },
  heroChip: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '0.35rem',
    background: 'rgba(255,255,255,0.72)',
    border: '1px solid rgba(14, 74, 78, 0.14)',
    color: '#0e4a4e',
    padding: '0.32rem 0.75rem',
    borderRadius: '999px',
    fontSize: '0.75rem',
    fontWeight: 600,
    letterSpacing: '0.02em',
  },
  grid: {
    display: 'grid',
    gap: '1.25rem',
    alignItems: 'start',
    width: '100%',
  },
  sectionTitle: {
    fontSize: '1.15rem',
    fontWeight: 700,
    color: colors.text,
    letterSpacing: '-0.015em',
    margin: '0 0 0.85rem',
    fontFamily: fontBody,
  },
  dayCard: {
    background: colors.glass,
    border: `1px solid ${colors.border}`,
    borderRadius: '16px',
    boxShadow: '0 8px 28px rgba(30, 110, 111, 0.06)',
    marginBottom: '1rem',
    overflow: 'hidden',
  },
  dayHead: {
    width: '100%',
    display: 'flex',
    alignItems: 'center',
    gap: '0.9rem',
    padding: '1rem 1.15rem',
    background: 'transparent',
    border: 'none',
    cursor: 'pointer',
    textAlign: 'left',
    fontFamily: 'inherit',
    color: 'inherit',
  },
  dayIndex: {
    width: '42px',
    height: '42px',
    borderRadius: '12px',
    background: 'linear-gradient(145deg, #4EC6D4, #1E6E6F)',
    color: 'white',
    display: 'grid',
    placeItems: 'center',
    fontWeight: 800,
    fontSize: '0.82rem',
    flexShrink: 0,
    letterSpacing: '0.02em',
  },
  dayTitle: {
    margin: 0,
    fontSize: '1.02rem',
    fontWeight: 700,
    color: colors.text,
    letterSpacing: '-0.015em',
  },
  dayMeta: {
    margin: '0.15rem 0 0',
    fontSize: '0.78rem',
    color: colors.textMuted,
  },
  dayCount: {
    marginLeft: 'auto',
    fontSize: '0.7rem',
    fontWeight: 700,
    letterSpacing: '0.04em',
    textTransform: 'uppercase',
    color: colors.textMuted,
    background: 'rgba(30, 110, 111, 0.06)',
    padding: '0.28rem 0.6rem',
    borderRadius: '999px',
    whiteSpace: 'nowrap',
  },
  timeline: {
    padding: '0 1.15rem 1.15rem 1.15rem',
  },
  activity: {
    display: 'grid',
    gridTemplateColumns: '5.4rem 16px 1fr',
    gap: '0.85rem',
    alignItems: 'stretch',
  },
  activityTime: {
    fontSize: '0.78rem',
    fontWeight: 700,
    color: colors.primaryDark,
    paddingTop: '0.15rem',
    letterSpacing: '0.01em',
  },
  activityTimeInput: {
    width: '100%',
    maxWidth: '6.4rem',
    border: `1px solid ${colors.border}`,
    background: colors.white,
    color: '#0c3d40',
    borderRadius: '8px',
    padding: '0.28rem 0.3rem',
    fontSize: '0.72rem',
    fontWeight: 700,
    fontFamily: 'inherit',
    letterSpacing: '0.01em',
    boxShadow: '0 1px 4px rgba(12, 61, 64, 0.06)',
  },
  rail: {
    position: 'relative',
    display: 'flex',
    justifyContent: 'center',
  },
  railDot: {
    width: '12px',
    height: '12px',
    borderRadius: '50%',
    background: colors.primary,
    border: `2px solid ${colors.white}`,
    boxShadow: '0 0 0 3px rgba(78, 198, 212, 0.28)',
    marginTop: '0.28rem',
    zIndex: 1,
    flexShrink: 0,
  },
  railLine: {
    position: 'absolute',
    top: '16px',
    bottom: '-8px',
    width: '2px',
    background: 'linear-gradient(180deg, rgba(78, 198, 212, 0.55), rgba(30, 110, 111, 0.08))',
  },
  activityBody: {
    background: 'rgba(238, 248, 248, 0.7)',
    border: `1px solid ${colors.border}`,
    borderRadius: '12px',
    padding: '0.75rem 0.9rem 0.85rem',
    marginBottom: '0.75rem',
  },
  activityTitle: {
    margin: 0,
    fontSize: '0.92rem',
    fontWeight: 700,
    color: colors.text,
  },
  activityBadges: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '0.35rem',
    marginTop: '0.4rem',
  },
  badge: {
    display: 'inline-flex',
    alignItems: 'center',
    padding: '0.15rem 0.55rem',
    borderRadius: '999px',
    fontSize: '0.65rem',
    fontWeight: 700,
    letterSpacing: '0.03em',
    background: colors.accent,
    color: colors.primaryDark,
  },
  badgeMuted: {
    background: 'rgba(30, 110, 111, 0.08)',
    color: colors.textMuted,
  },
  badgeSlot: {
    background: 'rgba(78, 198, 212, 0.22)',
    textTransform: 'capitalize',
  },
  suggestBox: {
    margin: '0.35rem 0 0.2rem 4.2rem',
    padding: '0.7rem 0.85rem',
    borderRadius: '12px',
    border: `1px dashed ${colors.border}`,
    background: 'rgba(255,255,255,0.65)',
  },
  suggestTitle: {
    margin: '0 0 0.45rem',
    fontSize: '0.72rem',
    fontWeight: 700,
    letterSpacing: '0.06em',
    textTransform: 'uppercase',
    color: colors.textMuted,
  },
  suggestItem: {
    display: 'flex',
    flexDirection: 'column',
    gap: '0.1rem',
    marginBottom: '0.4rem',
    fontSize: '0.82rem',
  },
  suggestMeta: {
    fontSize: '0.72rem',
    color: colors.textMuted,
  },
  activityDesc: {
    margin: '0.4rem 0 0',
    fontSize: '0.8rem',
    lineHeight: 1.5,
    color: colors.textMuted,
  },
  sidebar: {
    display: 'flex',
    flexDirection: 'column',
    gap: '1rem',
  },
  panel: {
    background: colors.glass,
    border: `1px solid ${colors.border}`,
    borderRadius: '16px',
    padding: '1.15rem 1.2rem 1.25rem',
    boxShadow: '0 8px 28px rgba(30, 110, 111, 0.06)',
  },
  panelTitle: {
    margin: '0 0 0.35rem',
    fontSize: '0.95rem',
    fontWeight: 700,
    color: colors.text,
  },
  panelText: {
    margin: '0 0 0.9rem',
    fontSize: '0.8rem',
    lineHeight: 1.5,
    color: colors.textMuted,
  },
  select: {
    width: '100%',
    padding: '0.7rem 0.9rem',
    borderRadius: '12px',
    border: `1px solid ${colors.border}`,
    background: colors.white,
    color: colors.text,
    fontFamily: 'inherit',
    fontSize: '0.88rem',
    fontWeight: 600,
    outline: 'none',
    marginBottom: '0.75rem',
  },
  btnPrimary: {
    width: '100%',
    border: 'none',
    borderRadius: '999px',
    padding: '0.72rem 1.2rem',
    background: 'linear-gradient(135deg, #4EC6D4, #7AC7BD)',
    color: 'white',
    fontWeight: 700,
    fontSize: '0.85rem',
    cursor: 'pointer',
    fontFamily: 'inherit',
  },
  btnOutline: {
    border: `1px solid ${colors.border}`,
    borderRadius: '999px',
    padding: '0.72rem 1.2rem',
    background: colors.white,
    color: colors.primaryDark,
    fontWeight: 700,
    fontSize: '0.85rem',
    cursor: 'pointer',
    fontFamily: 'inherit',
  },
  statsGrid: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: '0.65rem',
  },
  statCard: {
    background: 'rgba(238, 248, 248, 0.85)',
    border: `1px solid ${colors.border}`,
    borderRadius: '12px',
    padding: '0.75rem 0.8rem',
  },
  statLabel: {
    fontSize: '0.65rem',
    fontWeight: 700,
    letterSpacing: '0.06em',
    textTransform: 'uppercase',
    color: colors.textMuted,
  },
  statValue: {
    marginTop: '0.25rem',
    fontSize: '0.95rem',
    fontWeight: 700,
    color: colors.text,
  },
  highlight: {
    padding: '0.7rem 0.8rem',
    borderRadius: '12px',
    background: 'rgba(242, 217, 183, 0.28)',
    border: `1px solid ${colors.border}`,
    fontSize: '0.8rem',
    lineHeight: 1.45,
    color: colors.text,
    marginBottom: '0.5rem',
  },
  stayItem: {
    display: 'flex',
    flexDirection: 'column',
    gap: '0.1rem',
    padding: '0.55rem 0',
    borderBottom: `1px solid ${colors.border}`,
    fontSize: '0.82rem',
  },
  error: {
    color: colors.error,
    background: '#fef2f2',
    padding: '0.7rem 0.9rem',
    borderRadius: '12px',
    margin: '0 0 0.85rem',
    fontSize: '0.82rem',
    fontWeight: 500,
  },
  emptyCard: {
    background: colors.glass,
    border: `1px solid ${colors.border}`,
    borderRadius: '16px',
    padding: '1.5rem 1.35rem',
    boxShadow: '0 8px 28px rgba(30, 110, 111, 0.06)',
  },
  footer: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: '0.85rem',
    flexWrap: 'wrap',
    marginTop: '0.5rem',
    padding: '1rem 1.15rem',
    background: colors.glass,
    border: `1px solid ${colors.border}`,
    borderRadius: '16px',
    boxShadow: '0 12px 40px rgba(15, 55, 56, 0.12)',
  },
  footerInfo: {
    fontSize: '0.82rem',
    color: colors.textMuted,
    minWidth: 0,
  },
  footerActions: {
    display: 'flex',
    gap: '0.65rem',
    flexWrap: 'wrap',
  },
  skeletonCard: {
    background: colors.glass,
    border: `1px solid ${colors.border}`,
    borderRadius: '16px',
    padding: '1.15rem',
    marginBottom: '1rem',
  },
  skeletonLine: {
    height: '12px',
    borderRadius: '8px',
    background: 'linear-gradient(90deg, rgba(30,110,111,0.08), rgba(78,198,212,0.16), rgba(30,110,111,0.08))',
    backgroundSize: '200% 100%',
    animation: 'itineraryShimmer 1.4s ease infinite',
    marginBottom: '0.65rem',
  },
};

function displayTimeToInput(label) {
  const match = String(label || '').trim().match(/^(\d{1,2}):(\d{2})\s*(AM|PM)?$/i);
  if (!match) return '';
  let hour = Number(match[1]);
  const minute = match[2];
  const meridiem = (match[3] || '').toUpperCase();
  if (meridiem === 'PM' && hour !== 12) hour += 12;
  if (meridiem === 'AM' && hour === 12) hour = 0;
  return `${String(hour).padStart(2, '0')}:${minute}`;
}

function inputTimeToDisplay(value) {
  const [hourText, minute] = String(value || '').split(':');
  if (hourText == null || minute == null) return '';
  const hour = Number(hourText);
  if (Number.isNaN(hour)) return '';
  const meridiem = hour >= 12 ? 'PM' : 'AM';
  const displayHour = hour % 12 || 12;
  return `${displayHour}:${minute} ${meridiem}`;
}

export default function ItineraryPage() {
  const { t } = useSiteI18n();
  const navigate = useNavigate();
  const { trip, updateTrip } = useTrip();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [data, setData] = useState(null);
  const [dayStart, setDayStart] = useState(trip.preferredDayStart || '');
  const [expandedDays, setExpandedDays] = useState(() => new Set());
  const loadedTripRef = useRef(null);
  const hasStay = Boolean(trip.accommodations?.length || trip.accommodation);

  const changeActivityTime = async (dayNumber, index, inputValue) => {
    const nextTime = inputTimeToDisplay(inputValue);
    if (!nextTime || !trip.tripId || !data) return;
    const previous = data;
    const nextData = {
      ...data,
      days: (data.days || []).map((day) => {
        if (day.day !== dayNumber) return day;
        return {
          ...day,
          activities: (day.activities || []).map((act, i) => (
            i === index ? { ...act, time: nextTime } : act
          )),
        };
      }),
    };
    setData(nextData);
    updateTrip({ itinerary: nextData });
    try {
      const { data: res } = await itineraryApi.updateActivityTime(trip.tripId, {
        day: dayNumber,
        index,
        time: nextTime,
      });
      const payload = res.itinerary?.itinerary || res.itinerary;
      if (payload?.days) {
        setData(payload);
        updateTrip({ itinerary: payload });
      }
    } catch (e) {
      setData(previous);
      updateTrip({ itinerary: previous });
      setError(e.response?.data?.error || t('failedSaveTime'));
    }
  };

  const applyPayload = (payload) => {
    setData(payload);
    updateTrip({
      itinerary: payload,
      preferredDayStart: payload?.day_start || dayStart || '',
    });
    loadedTripRef.current = trip.tripId;
    setExpandedDays(new Set((payload?.days || []).map((day) => day.day)));
  };

  const generate = async (preferredStart = dayStart) => {
    setLoading(true);
    setError('');
    try {
      const created = await itineraryApi.generate(trip.tripId, {
        dayStart: preferredStart || undefined,
      });
      const payload = created.data.itinerary.itinerary;
      applyPayload(payload);
    } catch (e) {
      setError(e.response?.data?.error || t('failedGenerateItinerary'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setDayStart(trip.preferredDayStart || '');
  }, [trip.preferredDayStart]);

  useEffect(() => {
    if (!trip.tripId || !hasStay) {
      setData(null);
      setLoading(false);
      setError('');
      loadedTripRef.current = null;
      return;
    }

    if (trip.itinerary && loadedTripRef.current === trip.tripId) {
      setData(trip.itinerary);
      setLoading(false);
      return;
    }

    if (trip.itinerary) {
      applyPayload(trip.itinerary);
      setLoading(false);
      return;
    }

    let cancelled = false;

    const loadItinerary = async () => {
      setLoading(true);
      setError('');
      try {
        const existing = await itineraryApi.get(trip.tripId);
        if (cancelled) return;
        applyPayload(existing.data.itinerary.itinerary);
      } catch (getErr) {
        if (getErr.response?.status !== 404) {
          if (!cancelled) {
            setError(getErr.response?.data?.error || t('failedLoadItinerary'));
            setLoading(false);
          }
          return;
        }
        try {
          const created = await itineraryApi.generate(trip.tripId, {
            dayStart: trip.preferredDayStart || undefined,
          });
          if (cancelled) return;
          applyPayload(created.data.itinerary.itinerary);
        } catch (e) {
          if (!cancelled) {
            setError(e.response?.data?.error || t('failedGenerateItinerary'));
          }
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    loadItinerary();
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [trip.tripId, trip.itinerary, trip.accommodation, trip.accommodations, hasStay]);

  const stayNames = useMemo(
    () => [...new Set((trip.accommodations || []).map((stay) => stay.name).filter(Boolean))],
    [trip.accommodations],
  );

  const activityCount = useMemo(
    () => (data?.days || []).reduce((total, day) => total + (day.activities || []).length, 0),
    [data],
  );

  const toggleDay = (dayNum) => {
    setExpandedDays((prev) => {
      const next = new Set(prev);
      if (next.has(dayNum)) next.delete(dayNum);
      else next.add(dayNum);
      return next;
    });
  };

  const pageStyle = (
    <style>{`
      @keyframes itineraryShimmer {
        0% { background-position: 200% 0; }
        100% { background-position: -200% 0; }
      }
      .itinerary-page .itinerary-select:focus {
        border-color: #4EC6D4;
        box-shadow: 0 0 0 3px rgba(78, 198, 212, 0.16);
      }
      .itinerary-page .itinerary-day-head:hover {
        background: rgba(238, 248, 248, 0.85);
      }
      .itinerary-page .itinerary-btn-primary:hover {
        filter: brightness(0.97);
        transform: translateY(-1px);
      }
      .itinerary-page .itinerary-btn-outline:hover {
        border-color: #4EC6D4;
        background: rgba(182, 230, 233, 0.35);
      }
      @media (max-width: 720px) {
        .itinerary-page .itinerary-activity {
          grid-template-columns: 4.4rem 12px 1fr !important;
          gap: 0.55rem !important;
        }
        .itinerary-page .itinerary-footer {
          flex-direction: column !important;
          align-items: stretch !important;
        }
        .itinerary-page .itinerary-footer-actions,
        .itinerary-page .itinerary-footer-actions button {
          width: 100%;
        }
        .itinerary-page .itinerary-suggest {
          margin-left: 0 !important;
        }
      }
    `}</style>
  );

  if (!trip.tripId || !hasStay) {
    return (
      <div className="itinerary-page" style={styles.container}>
        {pageStyle}
        <section className="itinerary-hero" style={styles.hero}>
          <div style={styles.heroBg} />
          <div style={styles.heroContent}>
            <span style={styles.heroBadge}>{t('stepItineraryBadge')}</span>
            <h1 style={styles.heroTitle}>{t('dayByDayPlan')}</h1>
            <p style={styles.heroSubtitle}>
              {t('itineraryEmptyDesc')}
            </p>
          </div>
        </section>
        <div style={styles.emptyCard}>
          <h2 style={{ ...styles.panelTitle, fontSize: '1.05rem' }}>{t('finishPreviousSteps')}</h2>
          <p style={styles.panelText}>
            {!trip.tripId
              ? t('selectAttractionsTripHint')
              : t('chooseAccommodationReturnHint')}
          </p>
          <button
            type="button"
            className="itinerary-btn-primary"
            style={{ ...styles.btnPrimary, width: 'auto', padding: '0.72rem 1.4rem' }}
            onClick={() => navigate(!trip.tripId ? '/attractions' : '/accommodation')}
          >
            {!trip.tripId ? t('goToAttractions') : t('goToAccommodation')}
          </button>
        </div>
      </div>
    );
  }

  if (loading && !data) {
    return (
      <div className="itinerary-page" style={styles.container}>
        {pageStyle}
        <section className="itinerary-hero" style={styles.hero}>
          <div style={styles.heroBg} />
          <div style={styles.heroContent}>
            <span style={styles.heroBadge}>{t('buildingSchedule')}</span>
            <h1 style={styles.heroTitle}>{t('preparingItinerary')}</h1>
            <p style={styles.heroSubtitle}>
              {t('itineraryBuildDesc')}
            </p>
          </div>
        </section>
        {[1, 2, 3].map((item) => (
          <div key={item} style={styles.skeletonCard}>
            <div style={{ ...styles.skeletonLine, width: '38%' }} />
            <div style={{ ...styles.skeletonLine, width: '72%' }} />
            <div style={{ ...styles.skeletonLine, width: '54%', marginBottom: 0 }} />
          </div>
        ))}
      </div>
    );
  }

  if (error && !data) {
    return (
      <div className="itinerary-page" style={styles.container}>
        {pageStyle}
        <div style={styles.error}>{error}</div>
        <button
          type="button"
          className="itinerary-btn-primary"
          style={{ ...styles.btnPrimary, width: 'auto' }}
          onClick={() => generate(dayStart)}
        >
          {t('tryAgain')}
        </button>
      </div>
    );
  }

  if (!data) return null;

  const dayLabel = (day) =>
    day.location || day.title?.replace(/^Day \d+ — /i, '') || day.title || t('sriLanka');

  return (
    <div className="itinerary-page" style={styles.container}>
      {pageStyle}

      <section className="itinerary-hero" style={styles.hero}>
        <div style={styles.heroBg} />
        <div style={styles.heroContent}>
          <span style={styles.heroBadge}>{t('stepItineraryBadge')}</span>
          <h1 style={styles.heroTitle}>{data.title}</h1>
          <p style={styles.heroSubtitle}>{data.summary}</p>
          <div style={styles.heroMeta}>
            <span style={styles.heroChip}>{trip.days} {t('days')}</span>
            {data.route && <span style={styles.heroChip}>{data.route}</span>}
            {data.day_start && <span style={styles.heroChip}>{t('startsAroundTilde')} {data.day_start}</span>}
            <span style={styles.heroChip}>{activityCount} {t('stops')}</span>
          </div>
        </div>
      </section>

      <div className="itinerary-grid" style={styles.grid}>
        <div>
          <h2 className="itinerary-section-title" style={styles.sectionTitle}>{t('dayByDaySchedule')}</h2>
          {(data.days || []).map((day) => {
            const open = expandedDays.has(day.day);
            const activities = day.activities || [];
            return (
              <article key={day.day} className="itinerary-day" style={styles.dayCard}>
                <button
                  type="button"
                  className="itinerary-day-head"
                  style={styles.dayHead}
                  onClick={() => toggleDay(day.day)}
                  aria-expanded={open}
                >
                  <span style={styles.dayIndex}>D{day.day}</span>
                  <span style={{ minWidth: 0, flex: 1 }}>
                    <h3 style={styles.dayTitle}>{dayLabel(day)}</h3>
                    <p style={styles.dayMeta}>
                      {day.location || t('sriLanka')}
                      {day.accommodation ? ` · ${day.accommodation}` : ''}
                    </p>
                  </span>
                  <span style={styles.dayCount}>
                    {activities.length} {activities.length === 1 ? t('stop') : t('stops')}
                    <span aria-hidden="true" style={{ marginLeft: 8 }}>{open ? '▾' : '▸'}</span>
                  </span>
                </button>

                {open && (
                  <div style={styles.timeline}>
                    {activities.length === 0 ? (
                      <p style={{ ...styles.panelText, margin: 0 }}>{t('noActivitiesDay')}</p>
                    ) : (
                      activities.map((act, index) => (
                        <div
                          key={act.attraction_id || `${day.day}-${act.title}-${index}`}
                          className="itinerary-activity"
                          style={styles.activity}
                        >
                          <div style={styles.activityTime}>
                            <input
                              type="time"
                              className="itinerary-time-input"
                              aria-label={t('changeStopTime')}
                              title={t('changeStopTime')}
                              value={displayTimeToInput(act.time)}
                              onClick={(e) => e.stopPropagation()}
                              onChange={(e) => changeActivityTime(day.day, index, e.target.value)}
                              style={styles.activityTimeInput}
                            />
                          </div>
                          <div style={styles.rail}>
                            <span style={styles.railDot} />
                            {index < activities.length - 1 && <span style={styles.railLine} />}
                          </div>
                          <div style={styles.activityBody}>
                            <h4 style={styles.activityTitle}>{act.title}</h4>
                            {(act.mood_tag || act.category || act.time_slot) && (
                              <div style={styles.activityBadges}>
                                {act.time_slot && (
                                  <span style={{ ...styles.badge, ...styles.badgeSlot }}>{act.time_slot}</span>
                                )}
                                {act.mood_tag && <span style={styles.badge}>{act.mood_tag}</span>}
                                {act.category && (
                                  <span style={{ ...styles.badge, ...styles.badgeMuted }}>{act.category}</span>
                                )}
                              </div>
                            )}
                            {act.description && <p style={styles.activityDesc}>{act.description}</p>}
                          </div>
                        </div>
                      ))
                    )}
                    {(day.suggestions || []).length > 0 && (
                      <div className="itinerary-suggest" style={styles.suggestBox}>
                        <p style={styles.suggestTitle}>{t('suggestedNearby')}</p>
                        {day.suggestions.map((item) => (
                          <div key={item.attraction_id || item.title} style={styles.suggestItem}>
                            <strong>{item.title}</strong>
                            <span style={styles.suggestMeta}>
                              {[item.destination, item.category, item.mood_tag].filter(Boolean).join(' · ')}
                            </span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </article>
            );
          })}
        </div>

        <aside className="itinerary-sidebar" style={styles.sidebar}>
          {error && <div style={styles.error}>{error}</div>}

          <div style={styles.panel}>
            <h3 style={styles.panelTitle}>{t('tripOverview')}</h3>
            <div className="itinerary-stats" style={styles.statsGrid}>
              <div style={styles.statCard}>
                <div style={styles.statLabel}>{t('duration')}</div>
                <div style={styles.statValue}>{trip.days || 0} {t('days')}</div>
              </div>
              <div style={styles.statCard}>
                <div style={styles.statLabel}>{t('stopsLabel')}</div>
                <div style={styles.statValue}>{activityCount}</div>
              </div>
              <div style={styles.statCard}>
                <div style={styles.statLabel}>{t('start')}</div>
                <div style={styles.statValue}>{data.day_start || t('auto')}</div>
              </div>
              <div style={styles.statCard}>
                <div style={styles.statLabel}>{t('route')}</div>
                <div style={{ ...styles.statValue, fontSize: '0.82rem', lineHeight: 1.35 }}>
                  {data.route || t('sriLanka')}
                </div>
              </div>
            </div>
          </div>

          {(data.highlights || []).length > 0 && (
            <div style={styles.panel}>
              <h3 style={styles.panelTitle}>{t('highlights')}</h3>
              {(data.highlights || []).map((item) => (
                <div key={item} style={styles.highlight}>{item}</div>
              ))}
            </div>
          )}

          {data.ml?.used && (
            <div style={styles.panel}>
              <h3 style={styles.panelTitle}>{t('scheduleModel')}</h3>
              <p style={styles.panelText}>{t('scheduleModelDesc')}</p>
              {data.ml.chosen_model && (
                <div style={styles.highlight}>
                  {t('chosenModel')}: {data.ml.chosen_model}
                </div>
              )}
              {data.ml.holdout?.macro_f1 != null && (
                <div style={styles.highlight}>
                  {t('holdoutMacroF1')}: {data.ml.holdout.macro_f1}
                </div>
              )}
              {data.ml.baseline?.macro_f1 != null && (
                <div style={styles.highlight}>
                  {t('baselineMacroF1')}: {data.ml.baseline.macro_f1}
                </div>
              )}
            </div>
          )}

          {(stayNames.length > 0 || trip.accommodation) && (
            <div style={styles.panel}>
              <h3 style={styles.panelTitle}>{t('confirmedStays')}</h3>
              {stayNames.length > 0
                ? (trip.accommodations || []).map((stay) => (
                    <div key={`${stay.destination}-${stay.name}`} style={styles.stayItem}>
                      <strong>{stay.name}</strong>
                      <span style={{ color: colors.textMuted, fontSize: '0.75rem' }}>
                        {stay.destination || t('sriLanka')}
                      </span>
                    </div>
                  ))
                : (
                    <div style={styles.stayItem}>
                      <strong>{trip.accommodation}</strong>
                    </div>
                  )}
            </div>
          )}
        </aside>
      </div>

      <div className="itinerary-footer" style={styles.footer}>
        <div style={styles.footerInfo}>
          {t('reviewPlanExport')}
        </div>
        <div className="itinerary-footer-actions" style={styles.footerActions}>
          <button
            type="button"
            className="itinerary-btn-outline"
            style={styles.btnOutline}
            onClick={() => navigate('/recommendations')}
          >
            {t('discoverRecommendations')}
          </button>
          <button
            type="button"
            className="itinerary-btn-primary"
            style={{ ...styles.btnPrimary, width: 'auto' }}
            onClick={() => navigate('/export')}
          >
            {t('continueToExport')}
          </button>
        </div>
      </div>
    </div>
  );
}
