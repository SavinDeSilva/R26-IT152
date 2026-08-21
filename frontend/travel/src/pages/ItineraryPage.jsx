/**
 * ItineraryPage.jsx — the Itinerary screen in the Travel app.
 *
 * Wizard order: Attractions → Budget → Stay → THIS PAGE → Discover → Export
 *
 * What this page does:
 *   - shows the day-by-day plan
 *   - lets user pick start time (or Auto by mood)
 *   - asks the server to generate / rebuild the plan
 *
 * Other files in the chain:
 *   client.js              → sends the API request
 *   routes/itinerary.py    → server URL handler
 *   trip_plan_service.py   → splits places by day + hotels
 *   ai_service.py          → makes the clock times
 *   generated_itinerary.py → saves the plan in the database
 */
import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { itineraryApi } from '../api/client';
import { useTrip } from '../context/TripContext';

// DAY_START_OPTIONS = list of choices for the dropdown
// value '' means Auto → server averages the trip moods for start time
const DAY_START_OPTIONS = [
  { value: '', label: 'Auto (by mood)' },
  { value: '06:30 AM', label: '06:30 AM — early start' },
  { value: '07:30 AM', label: '07:30 AM' },
  { value: '08:30 AM', label: '08:30 AM' },
  { value: '09:00 AM', label: '09:00 AM' },
  { value: '10:00 AM', label: '10:00 AM — relaxed' },
  { value: '11:00 AM', label: '11:00 AM' },
];

export default function ItineraryPage() {
  const navigate = useNavigate();
  // trip = current trip object from TripContext (shared memory in the browser)
  const { trip, updateTrip } = useTrip();
  const [loading, setLoading] = useState(false); // true while waiting for API
  const [error, setError] = useState('');        // error message text
  const [data, setData] = useState(null);        // itinerary JSON from server
  const [dayStart, setDayStart] = useState(trip.preferredDayStart || '');
  const loadedTripRef = useRef(null);            // remembers which trip we already loaded
  // hasStay = true if user already picked hotels
  const hasStay = Boolean(trip.accommodations?.length || trip.accommodation);

  /** What it does: saves the server plan into page state + TripContext. */
  const applyPayload = (payload) => {
    setData(payload);
    updateTrip({
      itinerary: payload,
      preferredDayStart: payload?.day_start || dayStart || '',
    });
    loadedTripRef.current = trip.tripId;
  };

  /** What it does: asks the server to build / rebuild the itinerary. */
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
      setError(e.response?.data?.error || 'Failed to generate itinerary');
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
            setError(getErr.response?.data?.error || 'Failed to load itinerary');
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
            setError(e.response?.data?.error || 'Failed to generate itinerary');
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

  if (!trip.tripId || !hasStay) {
    return (
      <div className="beach-fade">
        <section className="hero">
          <h1 className="serif">Itinerary Summary</h1>
          <p>Your day-by-day schedule appears here after you choose attractions, budget, and stays.</p>
        </section>
        <div className="card" style={{ padding: 24 }}>
          <p style={{ color: 'var(--muted)', marginTop: 0 }}>
            {!trip.tripId
              ? 'Start by selecting attractions and confirming your trip.'
              : 'Pick accommodation for each destination, then come back to build the itinerary.'}
          </p>
          <button
            className="btn btn-primary"
            onClick={() => navigate(!trip.tripId ? '/attractions' : '/accommodation')}
          >
            {!trip.tripId ? 'Go to Attractions' : 'Go to Accommodation'}
          </button>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="card" style={{ padding: 48, textAlign: 'center' }}>
        <h2 className="serif">Building your itinerary...</h2>
        <p style={{ color: 'var(--muted)' }}>Scheduling your selected places with a flexible day start.</p>
      </div>
    );
  }

  if (error && !data) return <div className="error">{error}</div>;
  if (!data) return null;

  return (
    <div className="beach-fade">
      <section className="hero">
        <h1 className="serif">{data.title}</h1>
        <p>{data.summary}</p>
        <div style={{ display: 'flex', gap: 12, marginTop: 12, flexWrap: 'wrap' }}>
          <span className="badge">{trip.days} Days</span>
          <span className="badge">{data.route}</span>
          {data.day_start && <span className="badge">Starts ~ {data.day_start}</span>}
          {(trip.accommodations || []).length > 0 && (
            <span className="badge">
              Stays: {[...new Set(trip.accommodations.map((a) => a.name))].join(', ')}
            </span>
          )}
        </div>
      </section>

      <div className="card" style={{ padding: 20, marginBottom: 20 }}>
        <h3 style={{ marginTop: 0 }}>Flexible day start</h3>
        <p style={{ color: 'var(--muted)', marginTop: 0 }}>
          Schedules are not locked to 9:00 AM. Pick a start time (or leave Auto to follow your moods),
          then rebuild.
        </p>
        <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', alignItems: 'center' }}>
          <select
            value={dayStart}
            onChange={(e) => {
              setDayStart(e.target.value);
              updateTrip({ preferredDayStart: e.target.value });
            }}
            style={{ minWidth: 220, padding: '10px 12px', borderRadius: 10 }}
          >
            {DAY_START_OPTIONS.map((opt) => (
              <option key={opt.label} value={opt.value}>{opt.label}</option>
            ))}
          </select>
          <button className="btn btn-outline" type="button" onClick={() => generate(dayStart)}>
            Rebuild schedule
          </button>
        </div>
        {error && <div className="error" style={{ marginTop: 12 }}>{error}</div>}
      </div>

      <div className="card" style={{ padding: 20, marginBottom: 20 }}>
        <h3>Your Trip Summary</h3>
        <p>{data.summary}</p>
        <div className="grid-cards" style={{ marginTop: 16 }}>
          {(data.highlights || []).map((h) => (
            <div key={h} className="card" style={{ padding: 16 }}>{h}</div>
          ))}
        </div>
      </div>

      <h2 className="serif">Day-by-Day Schedule</h2>
      {(data.days || []).map((day) => (
        <div key={day.day} className="card" style={{ padding: 20, marginBottom: 16 }}>
          <h3>Day {day.day} — {day.location || day.title?.replace(/^Day \d+ — /i, '') || day.title}</h3>
          <p style={{ color: 'var(--muted)' }}>{day.location} · {day.accommodation}</p>
          {(day.activities || []).map((act) => (
            <div key={act.attraction_id || act.title} style={{ marginTop: 12, paddingLeft: 12, borderLeft: '3px solid var(--primary)' }}>
              <strong>{act.time}</strong> — {act.title}
              {act.mood_tag && <span className="badge" style={{ marginLeft: 8 }}>{act.mood_tag}</span>}
              {act.category && <em style={{ marginLeft: 8, color: 'var(--muted)' }}>{act.category}</em>}
              <div style={{ fontSize: 14, color: 'var(--muted)' }}>{act.description}</div>
            </div>
          ))}
        </div>
      ))}

      <div className="page-actions">
        <button className="btn btn-outline" onClick={() => navigate('/recommendations')}>Discover Recommendations</button>
        <button className="btn btn-primary" onClick={() => navigate('/export')}>Continue to Export</button>
      </div>
    </div>
  );
}
