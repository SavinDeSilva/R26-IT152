import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { accommodationApi, tripApi } from '../api/client';
import AttractionPhoto from '../components/AttractionPhoto';
import { useTrip } from '../context/TripContext';

const colors = {
  primary: '#4EC6D4',
  primaryLight: '#b6E6E9',
  primaryDark: '#1E6E6F',
  primaryMid: '#7AC7BD',
  seafoam: '#7AC7BD',
  deepest: '#1E6E6F',
  accent: '#F2D9B7',
  background: '#eef8f8',
  text: '#1E6E6F',
  textMuted: '#4a8586',
  border: 'rgba(30, 110, 111, 0.14)',
  glass: '#ffffff',
  error: '#B91C1C',
  success: '#7AC7BD',
  white: '#FFFFFF',
};

const fontBody = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif";

// Professional design system
const styles = {
  container: {
    background: colors.background,
    fontFamily: fontBody,
    color: colors.text,
    padding: '0',
    width: '100%',
    maxWidth: '1200px',
    margin: '0 auto',
    minHeight: '100vh',
    position: 'relative',
    animation: 'fadeRise 0.55s ease both',
  },

  nav: {
    position: 'sticky',
    top: 0,
    zIndex: 100,
    backgroundColor: colors.glass,
    borderBottom: `1px solid ${colors.border}`,
    padding: '0.8rem 2rem',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  navBrand: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.75rem',
    fontWeight: 600,
    fontSize: '1.1rem',
    letterSpacing: '0.01em',
  },
  navBrandIcon: {
    width: '32px',
    height: '32px',
    background: colors.primaryDark,
    borderRadius: '8px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: 'white',
    fontSize: '0.8rem',
    fontWeight: 700,
  },
  navBadge: {
    fontSize: '0.65rem',
    fontWeight: 500,
    color: colors.deepest,
    background: colors.accent,
    padding: '0.2rem 0.7rem',
    borderRadius: '8px',
    letterSpacing: '0.04em',
  },

  hero: {
    position: 'relative',
    margin: '0 0 1.5rem',
    borderRadius: '8px',
    overflow: 'hidden',
    width: '100%',
    background: `linear-gradient(135deg, rgba(30, 110, 111, 0.88) 0%, rgba(78, 198, 212, 0.65) 100%)`,
    minHeight: '260px',
    display: 'flex',
    alignItems: 'center',
    padding: '2.5rem 3rem',
    boxShadow: `0 20px 60px rgba(78, 198, 212, 0.12)`,
  },
  heroBg: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundImage: 'url("https://images.unsplash.com/photo-1519046904884-53103b34b206?w=1400&q=80")',
    backgroundSize: 'cover',
    backgroundPosition: 'center',
    opacity: 0.15,
  },
  heroContent: {
    position: 'relative',
    zIndex: 2,
    width: '100%',
  },
  heroBadge: {
    display: 'inline-block',
    background: colors.accent,
    padding: '0.25rem 1rem',
    borderRadius: '8px',
    fontSize: '0.65rem',
    fontWeight: 600,
    letterSpacing: '0.08em',
    textTransform: 'uppercase',
    color: colors.primaryDark,
    border: '1px solid rgba(30, 110, 111, 0.08)',
    marginBottom: '0.5rem',
  },
  heroTitle: {
    fontSize: '2rem',
    fontWeight: 700,
    fontFamily: fontBody,
    color: 'white',
    margin: '0 0 0.3rem 0',
    letterSpacing: '-0.01em',
    lineHeight: 1.1,
  },
  heroSubtitle: {
    fontSize: '0.95rem',
    color: 'rgba(255,255,255,0.7)',
    maxWidth: '460px',
    marginBottom: '1.5rem',
    lineHeight: 1.5,
  },
  searchBar: {
    display: 'flex',
    gap: '0.5rem',
    background: 'rgba(255,255,255,0.12)',
    borderRadius: '8px',
    padding: '0.3rem',
    maxWidth: '440px',
    border: '1px solid rgba(255,255,255,0.04)',
  },
  searchInput: {
    flex: 1,
    background: 'transparent',
    border: 'none',
    padding: '0.6rem 1.2rem',
    fontSize: '0.85rem',
    color: 'white',
    outline: 'none',
    fontFamily: 'inherit',
  },
  searchButton: {
    background: colors.primary,
    border: 'none',
    borderRadius: '8px',
    padding: '0.5rem 1.4rem',
    color: 'white',
    fontWeight: 500,
    fontSize: '0.8rem',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    fontFamily: 'inherit',
  },

  statsBar: {
    display: 'flex',
    flexWrap: 'wrap',
    alignItems: 'center',
    gap: '0.5rem 1.5rem',
    background: colors.glass,
    borderRadius: '8px',
    padding: '0.6rem 1.8rem',
    margin: '0 0 1.5rem',
    border: `1px solid ${colors.border}`,
    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.02)',
  },
  statItem: {
    fontSize: '0.8rem',
    color: colors.textMuted,
    display: 'flex',
    alignItems: 'center',
    gap: '0.3rem',
  },
  statHighlight: {
    fontWeight: 600,
    color: colors.text,
  },

  roomTypeBar: {
    display: 'flex',
    flexWrap: 'wrap',
    alignItems: 'center',
    gap: '0.75rem',
    background: colors.glass,
    borderRadius: '8px',
    padding: '0.75rem 1.8rem',
    margin: '0 0 1rem',
    border: `1px solid ${colors.border}`,
  },
  roomTypeLabel: {
    fontSize: '0.8rem',
    fontWeight: 600,
    color: colors.text,
  },
  roomTypeHint: {
    fontSize: '0.72rem',
    color: colors.textMuted,
    flex: '1 1 180px',
  },
  roomTypeOptions: {
    display: 'flex',
    gap: '0.45rem',
    flexWrap: 'wrap',
  },
  roomTypeButton: {
    border: `1px solid ${colors.border}`,
    background: colors.white,
    color: colors.text,
    borderRadius: '8px',
    padding: '0.35rem 0.9rem',
    fontSize: '0.75rem',
    fontWeight: 600,
    cursor: 'pointer',
    fontFamily: 'inherit',
  },
  roomTypeButtonActive: {
    background: colors.primaryDark,
    borderColor: colors.primaryDark,
    color: colors.white,
  },

  error: {
    background: 'rgba(185, 28, 28, 0.04)',
    color: colors.error,
    padding: '0.7rem 1.5rem',
    borderRadius: '14px',
    margin: '0 0 1.5rem',
    border: '1px solid rgba(185, 28, 28, 0.06)',
    fontWeight: 500,
    fontSize: '0.85rem',
  },

  section: {
    padding: '0 0 1rem',
  },
  sectionHeader: {
    display: 'flex',
    alignItems: 'baseline',
    justifyContent: 'space-between',
    marginBottom: '0.5rem',
    flexWrap: 'wrap',
    gap: '0.5rem',
  },
  sectionTitle: {
    fontSize: '1.2rem',
    fontWeight: 600,
    fontFamily: fontBody,
    color: colors.text,
    letterSpacing: '-0.01em',
    margin: 0,
  },
  sectionSub: {
    fontSize: '0.75rem',
    color: colors.textMuted,
  },

  grid: {
    display: 'grid',
    gap: '1.5rem',
    marginTop: '0.5rem',
    width: '100%',
  },

  card: {
    background: '#FFFFFF',
    borderRadius: '14px',
    overflow: 'hidden',
    boxShadow: '0 2px 12px rgba(0, 0, 0, 0.03)',
    transition: 'all 0.3s ease',
    cursor: 'pointer',
    border: `1px solid ${colors.border}`,
    display: 'flex',
    flexDirection: 'column',
  },
  cardHover: {
    transform: 'translateY(-4px)',
    boxShadow: `0 16px 40px rgba(78, 198, 212, 0.06), 0 4px 16px rgba(0, 0, 0, 0.02)`,
    borderColor: colors.primary,
  },
  cardImageOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: 'linear-gradient(180deg, rgba(0,0,0,0) 40%, rgba(0,0,0,0.15) 100%)',
  },
  cardTags: {
    position: 'absolute',
    top: '12px',
    left: '12px',
    display: 'flex',
    gap: '0.4rem',
    flexWrap: 'wrap',
  },
  cardTag: {
    background: 'rgba(0, 0, 0, 0.45)',
    padding: '0.15rem 0.7rem',
    borderRadius: '8px',
    fontSize: '0.55rem',
    fontWeight: 500,
    color: 'white',
    letterSpacing: '0.04em',
    textTransform: 'uppercase',
  },
  cardBody: {
    padding: '1rem 1.2rem 1.2rem',
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
  },
  cardTitle: {
    fontSize: '1rem',
    fontWeight: 600,
    color: colors.text,
    margin: '0 0 0.15rem 0',
    letterSpacing: '-0.01em',
  },
  cardLocation: {
    fontSize: '0.75rem',
    color: colors.textMuted,
    marginBottom: '0.4rem',
  },
  cardRating: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.3rem',
    fontSize: '0.75rem',
    color: colors.textMuted,
    marginBottom: '0.5rem',
  },
  cardPrice: {
    marginTop: 'auto',
    background: colors.primary,
    padding: '0.25rem 0.8rem',
    borderRadius: '8px',
    display: 'inline-block',
    fontSize: '0.8rem',
    fontWeight: 600,
    color: 'white',
    alignSelf: 'flex-start',
    letterSpacing: '-0.01em',
  },
  cardPriceGreen: {
    background: colors.primaryDark,
  },
  cardSelected: {
    border: `2px solid ${colors.primary}`,
    boxShadow: `0 0 0 3px rgba(78, 198, 212, 0.06), 0 8px 24px rgba(78, 198, 212, 0.04)`,
  },
  cardSelectedBadge: {
    marginTop: '0.5rem',
    fontSize: '0.65rem',
    fontWeight: 600,
    color: colors.primary,
    display: 'flex',
    alignItems: 'center',
    gap: '0.3rem',
  },

  emptyCard: {
    background: '#ffffff',
    borderRadius: '10px',
    padding: '2rem',
    textAlign: 'center',
    border: `1px dashed ${colors.border}`,
    color: colors.textMuted,
  },
  emptyCardTitle: {
    fontWeight: 600,
    color: colors.text,
  },

  footer: {
    position: 'sticky',
    bottom: '1.5rem',
    margin: '2rem 0 0',
    background: colors.primaryDark,
    borderRadius: '10px',
    padding: '0.7rem 1.5rem',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    flexWrap: 'wrap',
    gap: '0.8rem',
    border: `1px solid rgba(255,255,255,0.04)`,
    boxShadow: '0 20px 60px rgba(0, 0, 0, 0.08)',
  },
  footerInfo: {
    color: 'rgba(255,255,255,0.8)',
    fontSize: '0.8rem',
  },
  footerHighlight: {
    fontWeight: 600,
    color: 'white',
  },
  footerDays: {
    display: 'flex',
    gap: '0.3rem',
    flexWrap: 'wrap',
    marginTop: '0.2rem',
  },
  footerDayPill: {
    background: 'rgba(255,255,255,0.05)',
    padding: '0.1rem 0.6rem',
    borderRadius: '8px',
    fontSize: '0.6rem',
    color: 'rgba(255,255,255,0.5)',
  },
  footerButton: {
    background: colors.primary,
    border: 'none',
    borderRadius: '8px',
    padding: '0.5rem 1.6rem',
    color: 'white',
    fontWeight: 600,
    fontSize: '0.8rem',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    fontFamily: 'inherit',
    letterSpacing: '0.01em',
  },
  footerButtonDisabled: {
    opacity: 0.3,
    cursor: 'not-allowed',
  },

  skeletonGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))',
    gap: '1.5rem',
  },
  skeletonCard: {
    background: 'white',
    borderRadius: '14px',
    overflow: 'hidden',
    border: `1px solid ${colors.border}`,
  },
  skeletonImage: {
    height: '140px',
    background: 'linear-gradient(90deg, #b6E6E9 25%, #F2D9B7 50%, #b6E6E9 75%)',
    backgroundSize: '200% 100%',
    animation: 'skeleton-loading 1.5s ease-in-out infinite',
  },
  skeletonBody: {
    padding: '1.2rem',
    display: 'flex',
    flexDirection: 'column',
    gap: '0.5rem',
  },
  skeletonLine: {
    height: '12px',
    background: 'linear-gradient(90deg, #b6E6E9 25%, #F2D9B7 50%, #b6E6E9 75%)',
    backgroundSize: '200% 100%',
    animation: 'skeleton-loading 1.5s ease-in-out infinite',
    borderRadius: '6px',
  },
  skeletonLineShort: {
    width: '60%',
  },
  skeletonLineMedium: {
    width: '40%',
  },

  bottomTab: {
    position: 'fixed',
    bottom: 0,
    left: 0,
    right: 0,
    display: 'none',
    background: colors.glass,
    borderTop: `1px solid ${colors.border}`,
    padding: '0.4rem 0',
    justifyContent: 'space-around',
    zIndex: 50,
  },
  bottomTabItem: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '0.15rem',
    fontSize: '0.5rem',
    color: colors.textMuted,
    fontWeight: 500,
    border: 'none',
    background: 'none',
    cursor: 'pointer',
    fontFamily: 'inherit',
    textTransform: 'uppercase',
    letterSpacing: '0.04em',
  },
  bottomTabActive: {
    color: colors.primary,
  },

  '@media (max-width: 768px)': {
    hero: {
      padding: '1.5rem',
      minHeight: '180px',
      margin: '0.5rem 0.8rem 1rem',
      borderRadius: '16px',
    },
    heroTitle: {
      fontSize: '1.4rem',
    },
    heroSubtitle: {
      fontSize: '0.8rem',
    },
    searchBar: {
      maxWidth: '100%',
    },
    statsBar: {
      padding: '0.4rem 1rem',
      margin: '0 0.8rem 1rem',
      borderRadius: '8px',
      gap: '0.3rem 1rem',
    },
    statItem: {
      fontSize: '0.7rem',
    },
    section: {
      padding: '0 0.8rem 0.5rem',
    },
    grid: {
      gridTemplateColumns: '1fr',
      gap: '1rem',
    },
    footer: {
      margin: '1rem 0.8rem 0',
      borderRadius: '8px',
      padding: '0.5rem 1rem',
    },
    footerInfo: {
      fontSize: '0.7rem',
    },
    footerButton: {
      padding: '0.35rem 1rem',
      fontSize: '0.7rem',
    },
    nav: {
      padding: '0.5rem 1rem',
    },
    navBrand: {
      fontSize: '0.9rem',
    },
    bottomTab: {
      display: 'flex',
    },
    container: {
      paddingBottom: '70px',
    },
  },

  '@media (min-width: 769px) and (max-width: 1024px)': {
    grid: {
      gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))',
    },
  },
};

const skeletonKeyframes = `
  @keyframes skeleton-loading {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
  }
`;

export default function AccommodationPage() {
  const navigate = useNavigate();
  const { trip, updateTrip } = useTrip();
  const [stops, setStops] = useState([]);
  const [dayPlan, setDayPlan] = useState([]);
  const [rules, setRules] = useState(null);
  const [filters, setFilters] = useState(null);
  const [picks, setPicks] = useState({});
  const [roomType, setRoomType] = useState(trip.roomType || 'double');
  const [roomTypes, setRoomTypes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [hoveredCard, setHoveredCard] = useState(null);

  useEffect(() => {
    const styleEl = document.createElement('style');
    styleEl.textContent = skeletonKeyframes;
    document.head.appendChild(styleEl);
    return () => styleEl.remove();
  }, []);

  const loadAccommodations = async (selectedRoomType = roomType) => {
    if (!trip.tripId) {
      setStops([]);
      setDayPlan([]);
      setRules(null);
      setFilters(null);
      setPicks({});
      setLoading(false);
      setError('');
      return;
    }
    setLoading(true);
    try {
      const { data } = await accommodationApi.list(trip.tripId, selectedRoomType);
      const loadedStops = data.stops_by_destination || [];
      setStops(loadedStops);
      setDayPlan(data.day_plan || []);
      setRules(data.rules);
      setFilters(data.filters);
      if (data.filters?.room_types?.length) {
        setRoomTypes(data.filters.room_types);
      }
      if (data.filters?.room_type) {
        setRoomType(data.filters.room_type);
      }
      const destNames = loadedStops.map((s) => s.destination);
      const availableIds = new Set(
        loadedStops.flatMap((s) => (s.hotels || []).map((h) => h.id))
      );
      const initial = {};
      (trip.accommodations || []).forEach((a) => {
        if (
          a.destination &&
          a.accommodation_id &&
          destNames.includes(a.destination) &&
          availableIds.has(a.accommodation_id)
        ) {
          initial[a.destination] = a.accommodation_id;
        }
      });
      setPicks(initial);
      setError('');
    } catch (e) {
      setError(e.response?.data?.error || 'Failed to load accommodations');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAccommodations(trip.roomType || 'double');
  }, [trip.tripId, trip.accommodations]);

  const changeRoomType = async (nextType) => {
    if (!trip.tripId || nextType === roomType) return;
    const previous = roomType;
    setRoomType(nextType);
    setError('');
    try {
      await tripApi.update(trip.tripId, { room_type: nextType });
      updateTrip({ roomType: nextType, itinerary: null });
      await loadAccommodations(nextType);
    } catch (e) {
      setError(e.response?.data?.error || 'Failed to update room type');
      setRoomType(previous);
    }
  };

  const requiredDestinations = useMemo(() => stops.map((s) => s.destination), [stops]);
  const allPicked = requiredDestinations.length > 0 && requiredDestinations.every((d) => picks[d]);
  const pickCount = Object.values(picks).filter(Boolean).length;
  const allDestinationsHaveHotels = stops.every((s) => s.hotels.length > 0);

  const selectHotel = (destination, hotelId) => {
    setPicks((prev) => ({ ...prev, [destination]: hotelId }));
    setError('');
  };

  const continueFlow = async () => {
    if (!allDestinationsHaveHotels) {
      setError('Some destinations have no hotels within your budget. Increase accommodation budget or change places.');
      return;
    }
    if (!allPicked) {
      setError(`Choose one hotel per destination (${pickCount}/${requiredDestinations.length} selected).`);
      return;
    }
    try {
      const { data } = await tripApi.update(trip.tripId, { accommodations_by_destination: picks });
      updateTrip({
        accommodations: data.accommodations,
        accommodation: data.trip?.accommodation,
        roomType: data.trip?.room_type || roomType,
        itinerary: null,
      });
      navigate('/itinerary');
    } catch (e) {
      setError(e.response?.data?.error || 'Failed to save hotels');
    }
  };

  const SkeletonLoader = () => (
    <div style={styles.skeletonGrid}>
      {[1, 2, 3, 4].map((i) => (
        <div key={i} style={styles.skeletonCard}>
          <div style={styles.skeletonImage} />
          <div style={styles.skeletonBody}>
            <div style={{ ...styles.skeletonLine, ...styles.skeletonLineShort }} />
            <div style={styles.skeletonLine} />
            <div style={{ ...styles.skeletonLine, ...styles.skeletonLineMedium }} />
            <div style={{ ...styles.skeletonLine, width: '30%' }} />
          </div>
        </div>
      ))}
    </div>
  );

  const getCardGradient = (index) => {
    const gradients = [
      `linear-gradient(135deg, ${colors.primaryDark}, ${colors.primary})`,
      `linear-gradient(135deg, ${colors.primary}, ${colors.primaryLight})`,
      `linear-gradient(135deg, ${colors.primaryDark}, ${colors.primaryLight})`,
      `linear-gradient(135deg, ${colors.primaryLight}, ${colors.primary})`,
    ];
    return gradients[index % gradients.length];
  };

  return (
    <div className="accom-page" style={styles.container}>
      <style>{`
        @keyframes fadeRise { from { opacity:0; transform:translateY(12px);} to { opacity:1; transform:translateY(0);} }
        * { box-sizing: border-box; }
        body { margin: 0; background: ${colors.background}; }
        button { cursor: pointer; }
        button:disabled { cursor: not-allowed; }
        .card-hover:hover {
          transform: translateY(-3px);
          box-shadow: 0 16px 40px rgba(78, 198, 212, 0.06), 0 4px 16px rgba(0, 0, 0, 0.02);
          border-color: ${colors.primary};
        }
        .search-pill:focus {
          border-color: ${colors.primary};
          box-shadow: 0 0 0 2px rgba(78, 198, 212, 0.06);
        }
        @media (min-width: 769px) and (max-width: 1024px) {
          .accom-page .accom-grid {
            grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)) !important;
          }
        }
        @media (max-width: 768px) {
          .accom-page {
            padding-bottom: 5.5rem !important;
          }
          .accom-page .accom-hero {
            padding: 1.35rem 1.2rem !important;
            min-height: 0 !important;
            margin: 0.5rem 0 1rem !important;
            border-radius: 14px !important;
          }
          .accom-page .accom-hero h1 {
            font-size: 1.35rem !important;
          }
          .accom-page .accom-hero p {
            font-size: 0.84rem !important;
            margin-bottom: 1rem !important;
          }
          .accom-page .accom-search {
            max-width: 100% !important;
            flex-wrap: wrap;
          }
          .accom-page .accom-stats {
            margin: 0 0 1rem !important;
            padding: 0.65rem 1rem !important;
            gap: 0.45rem 1rem !important;
          }
          .accom-page .accom-section {
            padding: 0 0 0.5rem !important;
          }
          .accom-page .accom-section-head {
            flex-direction: column;
            align-items: flex-start !important;
            gap: 0.35rem;
          }
          .accom-page .accom-grid {
            grid-template-columns: 1fr !important;
            gap: 0.9rem !important;
          }
          .accom-page .accom-footer {
            position: fixed !important;
            left: 0.75rem;
            right: 0.75rem;
            bottom: 0.75rem;
            margin: 0 !important;
            z-index: 70;
            flex-direction: column;
            align-items: stretch !important;
            border-radius: 14px !important;
            padding: 0.85rem 1rem !important;
          }
          .accom-page .accom-footer button {
            width: 100%;
          }
          .card-hover:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(78, 198, 212, 0.04);
          }
        }
      `}</style>

      <section className="accom-hero" style={styles.hero}>
        <div style={styles.heroBg} />
        <div style={styles.heroContent}>
          <span style={styles.heroBadge}>Sri Lanka · Accommodation</span>
          <h1 style={styles.heroTitle}>Find your perfect stay</h1>
          <p style={styles.heroSubtitle}>Curated boutique hotels, jungle retreats, and coastal escapes across the island.</p>
          <div className="accom-search" style={styles.searchBar}>
            <input type="text" placeholder="Search destinations..." style={styles.searchInput} />
            <button style={styles.searchButton}>Search</button>
          </div>
        </div>
      </section>

      {(rules || filters) && (
        <div className="accom-stats" style={styles.statsBar}>
          {filters && (
            <>
              <span style={styles.statItem}>
                Total budget <span style={styles.statHighlight}>${Number(trip.budget || filters.accommodation_budget_usd || 0).toLocaleString()}</span>
              </span>
              <span style={styles.statItem}>
                Stay budget <span style={styles.statHighlight}>${filters.accommodation_budget_usd}</span>
              </span>
              <span style={styles.statItem}>
                Per night <span style={styles.statHighlight}>${filters.per_night_usd}</span>
              </span>
              <span style={styles.statItem}>
                ≈ <span style={styles.statHighlight}>{Math.round(filters.per_night_lkr).toLocaleString()}</span> LKR
              </span>
            </>
          )}
          {trip.days && (
            <span style={styles.statItem}>Days <span style={styles.statHighlight}>{trip.days}</span></span>
          )}
          {rules?.max_hotels && (
            <span style={styles.statItem}>Max <span style={styles.statHighlight}>{rules.max_hotels}</span> hotels</span>
          )}
          <span style={{ ...styles.statItem, marginLeft: 'auto', color: colors.primary }}>
            {pickCount}/{requiredDestinations.length} selected
          </span>
        </div>
      )}

      {(roomTypes.length > 0 || filters?.room_type) && (
        <div style={styles.roomTypeBar}>
          <span style={styles.roomTypeLabel}>Room type</span>
          <div style={styles.roomTypeOptions}>
            {(roomTypes.length ? roomTypes : [
              { id: 'single', label: 'Single', hint: 'Rate A' },
              { id: 'double', label: 'Double', hint: '(A+B)/2' },
              { id: 'family', label: 'Family', hint: 'Rate B' },
            ]).map((option) => {
              const active = roomType === option.id;
              return (
                <button
                  key={option.id}
                  type="button"
                  style={{
                    ...styles.roomTypeButton,
                    ...(active ? styles.roomTypeButtonActive : {}),
                  }}
                  onClick={() => changeRoomType(option.id)}
                >
                  {option.label} · {option.short || option.hint}
                </button>
              );
            })}
          </div>
          <span style={styles.roomTypeHint}>
            From each hotel range A–B: Single uses A, Double uses (A+B)/2, Family uses B. Higher room types may show fewer hotels within budget.
          </span>
        </div>
      )}

      {!trip.tripId && (
        <div style={styles.error}>
          Confirm attractions and budget first, then pick stays for each destination.
          <div style={{ marginTop: 12 }}>
            <button style={styles.searchButton} onClick={() => navigate('/attractions')}>
              Go to Attractions
            </button>
          </div>
        </div>
      )}
      {error && <div style={styles.error}>{error}</div>}

      <div className="accom-section" style={styles.section}>
        {loading ? (
          <SkeletonLoader />
        ) : (
          stops.map((stop, idx) => (
            <div key={stop.destination} style={{ marginBottom: '2rem' }}>
              <div className="accom-section-head" style={styles.sectionHeader}>
                <h2 style={styles.sectionTitle}>{stop.destination}</h2>
                <span style={styles.sectionSub}>
                  Day {stop.days.join(', ')} · {stop.attractions.map(a => a.attraction_name).join(', ')}
                </span>
              </div>
              <div className="accom-grid" style={styles.grid}>
                {stop.hotels.length === 0 ? (
                  <div style={styles.emptyCard}>
                    <p style={styles.emptyCardTitle}>No hotels available</p>
                    <p style={{ fontSize: '0.8rem', color: colors.textMuted, marginTop: '0.3rem' }}>
                      Try increasing your budget or adjusting your itinerary.
                    </p>
                  </div>
                ) : (
                  stop.hotels.map((h, hIdx) => {
                    const active = picks[stop.destination] === h.id;
                    const isHovered = hoveredCard === `${stop.destination}-${h.id}`;
                    return (
                      <div
                        key={h.id}
                        className="card-hover"
                        style={{
                          ...styles.card,
                          ...(active ? styles.cardSelected : {}),
                          ...(isHovered && !active ? styles.cardHover : {}),
                        }}
                        onMouseEnter={() => setHoveredCard(`${stop.destination}-${h.id}`)}
                        onMouseLeave={() => setHoveredCard(null)}
                        onClick={() => selectHotel(stop.destination, h.id)}
                      >
                        <AttractionPhoto
                          src={h.image}
                          name={h.name}
                          gradient={getCardGradient(hIdx)}
                          height={140}
                        >
                          <div style={styles.cardImageOverlay} />
                          <div style={styles.cardTags}>
                            <span style={styles.cardTag}>{h.category || 'Stay'}</span>
                            {active && <span style={{ ...styles.cardTag, background: colors.primary }}>Selected</span>}
                          </div>
                        </AttractionPhoto>
                        <div style={styles.cardBody}>
                          <h3 style={styles.cardTitle}>{h.name}</h3>
                          <div style={styles.cardLocation}>{h.local_authority}</div>
                          <div style={{ ...styles.cardPrice, ...(active ? styles.cardPriceGreen : {}) }}>
                            {h.price_range_display || h.price_range || 'Price on request'}
                          </div>
                          {h.price_range_base && (
                            <div style={{ fontSize: '0.68rem', color: colors.textMuted, marginTop: '0.25rem' }}>
                              Hotel range {h.price_range_base} (approx.)
                            </div>
                          )}
                          {active && (
                            <div style={styles.cardSelectedBadge}>
                              Your choice
                            </div>
                          )}
                        </div>
                      </div>
                    );
                  })
                )}
              </div>
            </div>
          ))
        )}
      </div>

      <div className="accom-footer" style={styles.footer}>
        <div style={styles.footerInfo}>
          <span style={styles.footerHighlight}>{pickCount}</span>/{requiredDestinations.length} destinations · 
          <span style={{ marginLeft: '0.3rem' }}>{allPicked ? 'All selected' : 'In progress'}</span>
          {dayPlan.length > 0 && (
            <div style={styles.footerDays}>
              {dayPlan.map((d) => (
                <span key={d.day} style={styles.footerDayPill}>
                  Day {d.day}: {d.destination}
                </span>
              ))}
            </div>
          )}
        </div>
        <button
          style={{
            ...styles.footerButton,
            ...((!allPicked || !allDestinationsHaveHotels) ? styles.footerButtonDisabled : {}),
          }}
          onClick={continueFlow}
          disabled={!allPicked || !allDestinationsHaveHotels}
        >
          Continue to Itinerary
        </button>
      </div>
    </div>
  );
}