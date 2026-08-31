import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { budgetApi, itineraryApi, tripApi } from '../api/client';
import { useTrip } from '../context/TripContext';
import { useSiteI18n } from '@shared/i18n/react';

export default function HistoryPage() {
  const { t } = useSiteI18n();
  const navigate = useNavigate();
  const { updateTrip } = useTrip();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [openingId, setOpeningId] = useState(null);

  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      setLoading(true);
      setError('');
      try {
        const { data } = await itineraryApi.history();
        if (!cancelled) setItems(data.history || []);
      } catch (e) {
        if (!cancelled) {
          setError(e.response?.data?.error || t('failedLoadHistory'));
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    load();
    return () => {
      cancelled = true;
    };
  }, [t]);

  const openTrip = async (tripId) => {
    setOpeningId(tripId);
    setError('');
    try {
      const [tripRes, itinRes] = await Promise.all([
        tripApi.get(tripId),
        itineraryApi.get(tripId),
      ]);
      const trip = tripRes.data.trip;
      let budgetSplit = null;
      try {
        const budgetRes = await budgetApi.get(tripId);
        budgetSplit = budgetRes.data.split || budgetRes.data.budget_split || null;
      } catch {
        /* budget optional for viewing itinerary */
      }

      const itinerary = itinRes.data.itinerary?.itinerary || itinRes.data.itinerary;
      updateTrip({
        tripId: trip.trip_id,
        selectedMoods: trip.selected_moods || [],
        days: trip.days,
        selectedAttractionIds: trip.finalized_attractions || [],
        budget: trip.budget ?? 2500,
        budgetSplit,
        accommodation: trip.accommodation || null,
        accommodations: trip.accommodations || [],
        roomType: trip.room_type || 'double_hb',
        itinerary,
        preferredDayStart: itinerary?.day_start || '',
        savedReferences: [],
      });
      navigate('/itinerary');
    } catch (e) {
      setError(e.response?.data?.error || t('couldNotOpenItinerary'));
    } finally {
      setOpeningId(null);
    }
  };

  return (
    <div className="beach-fade">
      <section className="hero">
        <h1 className="serif">{t('tripHistoryTitle')}</h1>
        <p>{t('tripHistoryDesc')}</p>
      </section>

      {error && <div className="error">{error}</div>}

      {loading ? (
        <div className="card" style={{ padding: 32, textAlign: 'center' }}>
          {t('loadingSavedItineraries')}
        </div>
      ) : items.length === 0 ? (
        <div className="card" style={{ padding: 32 }}>
          <p style={{ marginTop: 0, color: 'var(--muted)' }}>
            {t('noSavedItineraries')}
          </p>
          <button className="btn btn-primary" type="button" onClick={() => navigate('/attractions')}>
            {t('startPlanning')}
          </button>
        </div>
      ) : (
        <div style={{ display: 'grid', gap: 14 }}>
          {items.map((item) => (
            <div key={`${item.trip_id}-${item.id}`} className="card" style={{ padding: 20 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', gap: 16, flexWrap: 'wrap' }}>
                <div>
                  <h3 style={{ margin: '0 0 6px' }}>{item.title}</h3>
                  <p style={{ margin: 0, color: 'var(--muted)' }}>
                    {item.route || t('sriLankaRoute')}
                    {item.day_start ? ` · ${t('startsAround')} ${item.day_start}` : ''}
                  </p>
                  <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginTop: 10 }}>
                    <span className="badge">{item.days} {t('days')}</span>
                    {(item.selected_moods || []).map((mood) => (
                      <span key={mood} className="badge">{mood}</span>
                    ))}
                    <span className="badge">{item.status}</span>
                  </div>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8, alignItems: 'flex-end' }}>
                  <span style={{ fontSize: 13, color: 'var(--muted)' }}>
                    {item.created_at ? new Date(item.created_at).toLocaleString() : ''}
                  </span>
                  <button
                    className="btn btn-primary"
                    type="button"
                    disabled={openingId === item.trip_id}
                    onClick={() => openTrip(item.trip_id)}
                  >
                    {openingId === item.trip_id ? t('opening') : t('openItinerary')}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
