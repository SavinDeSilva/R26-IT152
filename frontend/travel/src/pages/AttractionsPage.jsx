import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { attractionsApi, tripApi } from '../api/client';
import AttractionPhoto from '../components/AttractionPhoto';
import AttractionDetailModal from '../components/AttractionDetailModal';
import { useTrip } from '../context/TripContext';

// MOOD_OPTIONS = list of mood names shown as pills on this page.
// Must match backend ai_service.MOOD_START_HOURS (same spelling).
// Saved on the trip → later used for "Auto (by mood)" start time on Itinerary.
const MOOD_OPTIONS = ['Adventure', 'Authentic', 'Curious', 'Excited', 'Explore', 'Happy', 'Healing', 'Peaceful', 'Relaxed', 'Spiritual'];
/** Preferred order for attractions.xlsx Category values */
const CATEGORY_ORDER = ['Wild', 'Scenic', 'Pristine', 'Heritage', 'Essence', 'Thrills'];
const DESCRIPTION_PREVIEW_LEN = 120;

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
    maxWidth: '100%',
    minWidth: 0,
    margin: '0 auto',
    minHeight: '100%',
    position: 'relative',
    animation: 'fadeRise 0.55s ease both',
    overflowX: 'hidden',
    boxSizing: 'border-box',
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
    margin: '0 0 1rem',
    borderRadius: '14px',
    overflow: 'hidden',
    width: '100%',
    maxWidth: '100%',
    boxSizing: 'border-box',
    background: `linear-gradient(125deg, rgba(30, 110, 111, 0.94) 0%, rgba(78, 198, 212, 0.72) 55%, rgba(122, 199, 189, 0.65) 100%)`,
    minHeight: 0,
    display: 'flex',
    alignItems: 'center',
    padding: '1.15rem 1rem',
    boxShadow: '0 18px 48px rgba(30, 110, 111, 0.14)',
  },
  heroBg: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundImage: 'url("https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=1400&q=80")',
    backgroundSize: 'cover',
    backgroundPosition: 'center',
    opacity: 0.18,
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
    marginBottom: '0.65rem',
  },
  heroTitle: {
    fontSize: 'clamp(1.25rem, 4.5vw, 2.15rem)',
    fontWeight: 700,
    fontFamily: fontBody,
    color: 'white',
    margin: '0 0 0.4rem 0',
    letterSpacing: '-0.02em',
    lineHeight: 1.2,
  },
  heroSubtitle: {
    fontSize: 'clamp(0.8rem, 2.8vw, 0.95rem)',
    color: 'rgba(255,255,255,0.82)',
    maxWidth: '100%',
    marginBottom: '1rem',
    lineHeight: 1.5,
  },
  heroControls: {
    display: 'flex',
    gap: '0.65rem',
    alignItems: 'center',
    flexWrap: 'wrap',
  },
  heroInput: {
    background: 'rgba(255,255,255,0.16)',
    border: '1px solid rgba(255,255,255,0.28)',
    borderRadius: '10px',
    padding: '0.45rem 0.9rem',
    fontSize: '0.9rem',
    color: 'white',
    width: '72px',
    fontFamily: 'inherit',
    outline: 'none',
    fontWeight: 600,
  },
  heroInputLabel: {
    color: 'rgba(255,255,255,0.85)',
    fontSize: '0.82rem',
    display: 'flex',
    alignItems: 'center',
    gap: '0.55rem',
    background: 'rgba(0,0,0,0.12)',
    padding: '0.35rem 0.55rem 0.35rem 0.9rem',
    borderRadius: '12px',
    flexWrap: 'wrap',
    maxWidth: '100%',
  },

  mainGrid: {
    display: 'grid',
    gap: '1.5rem',
    alignItems: 'start',
    width: '100%',
    minWidth: 0,
  },

  filters: {
    marginBottom: '1.5rem',
    position: 'relative',
    zIndex: 5,
    width: '100%',
    minWidth: 0,
    maxWidth: '100%',
  },
  filterLabel: {
    fontSize: '0.75rem',
    fontWeight: 600,
    color: colors.textMuted,
    letterSpacing: '0.06em',
    textTransform: 'uppercase',
    marginBottom: '0.75rem',
  },
  pillRow: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '0.45rem',
    marginBottom: '1rem',
    width: '100%',
    minWidth: 0,
    maxWidth: '100%',
  },
  pill: {
    background: 'white',
    border: `1px solid ${colors.border}`,
    padding: '0.35rem 0.85rem',
    borderRadius: '999px',
    fontSize: '0.75rem',
    fontWeight: 500,
    color: colors.textMuted,
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    fontFamily: 'inherit',
    letterSpacing: '0.01em',
  },
  pillActive: {
    background: colors.primaryDark,
    color: 'white',
    borderColor: colors.primaryDark,
    boxShadow: '0 6px 16px rgba(30, 110, 111, 0.18)',
  },
  searchInput: {
    width: '100%',
    maxWidth: '100%',
    boxSizing: 'border-box',
    padding: '0.7rem 1.1rem',
    borderRadius: '12px',
    border: `1px solid ${colors.border}`,
    fontSize: '0.88rem',
    background: 'white',
    outline: 'none',
    fontFamily: 'inherit',
    transition: 'border-color 0.2s ease, box-shadow 0.2s ease',
    marginBottom: '1rem',
    color: colors.text,
    position: 'relative',
    zIndex: 5,
    pointerEvents: 'auto',
  },

  cardsGrid: {
    display: 'grid',
    gridTemplateColumns: '1fr',
    gap: '0.9rem',
    marginTop: '0.5rem',
    width: '100%',
    minWidth: 0,
  },

  card: {
    background: '#FFFFFF',
    borderRadius: '16px',
    overflow: 'hidden',
    boxShadow: '0 4px 18px rgba(30, 110, 111, 0.05)',
    transition: 'transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease',
    border: `1px solid ${colors.border}`,
    display: 'flex',
    flexDirection: 'column',
    position: 'relative',
    cursor: 'pointer',
  },
  cardImage: {
    height: '160px',
    background: `linear-gradient(135deg, ${colors.primaryDark}, ${colors.primary})`,
    position: 'relative',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  cardImageOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: 'linear-gradient(180deg, rgba(0,0,0,0) 40%, rgba(0,0,0,0.28) 100%)',
    pointerEvents: 'none',
  },
  cardTag: {
    position: 'absolute',
    top: '12px',
    left: '12px',
    background: 'rgba(0, 0, 0, 0.5)',
    padding: '0.2rem 0.7rem',
    borderRadius: '999px',
    fontSize: '0.58rem',
    fontWeight: 600,
    color: 'white',
    letterSpacing: '0.05em',
    textTransform: 'uppercase',
    pointerEvents: 'none',
    zIndex: 2,
  },
  cardCheckbox: {
    position: 'absolute',
    top: '12px',
    right: '12px',
    width: '24px',
    height: '24px',
    borderRadius: '8px',
    border: '2px solid rgba(255,255,255,0.9)',
    background: 'rgba(255,255,255,0.22)',
    cursor: 'pointer',
    appearance: 'none',
    WebkitAppearance: 'none',
    transition: 'all 0.2s ease',
    zIndex: 3,
    margin: 0,
    display: 'grid',
    placeItems: 'center',
    padding: 0,
  },
  cardCheckboxChecked: {
    background: colors.primary,
    borderColor: colors.primary,
  },
  cardCheckboxMark: {
    color: 'white',
    fontSize: '0.78rem',
    fontWeight: 700,
    lineHeight: 1,
    pointerEvents: 'none',
  },
  cardBody: {
    padding: '1rem 1.1rem 1.15rem',
    flex: 1,
  },
  cardTitle: {
    fontSize: '0.98rem',
    fontWeight: 600,
    color: colors.text,
    margin: '0 0 0.2rem 0',
    letterSpacing: '-0.01em',
  },
  cardMeta: {
    fontSize: '0.74rem',
    color: colors.textMuted,
    marginBottom: '0.45rem',
  },
  cardDescription: {
    fontSize: '0.8rem',
    color: colors.textMuted,
    lineHeight: 1.5,
    margin: 0,
  },
  cardMoreBtn: {
    background: 'none',
    border: 'none',
    padding: 0,
    margin: 0,
    color: colors.primaryDark,
    fontWeight: 600,
    fontSize: 'inherit',
    fontFamily: 'inherit',
    cursor: 'pointer',
    textDecoration: 'underline',
    textUnderlineOffset: '2px',
  },
  cardDisabled: {
    opacity: 0.45,
    cursor: 'not-allowed',
  },

  sidebar: {
    alignSelf: 'start',
    width: '100%',
  },
  sidebarCard: {
    background: colors.glass,
    borderRadius: '16px',
    padding: '1.25rem',
    border: `1px solid ${colors.border}`,
    boxShadow: '0 8px 28px rgba(30, 110, 111, 0.06)',
  },
  sidebarHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '0.45rem',
  },
  sidebarTitle: {
    fontSize: '1rem',
    fontWeight: 600,
    fontFamily: fontBody,
    margin: 0,
    color: colors.text,
  },
  sidebarBadge: {
    fontSize: '0.68rem',
    fontWeight: 600,
    color: colors.deepest,
    background: 'rgba(182, 230, 233, 0.55)',
    padding: '0.25rem 0.65rem',
    borderRadius: '999px',
  },
  sidebarStats: {
    fontSize: '0.78rem',
    color: colors.textMuted,
    marginBottom: '0.85rem',
  },
  sidebarList: {
    listStyle: 'none',
    padding: 0,
    margin: '0 0 1rem',
    maxHeight: '280px',
    overflowY: 'auto',
  },
  sidebarItem: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    gap: '0.5rem',
    padding: '0.55rem 0',
    borderBottom: `1px solid ${colors.border}`,
    fontSize: '0.82rem',
  },
  sidebarItemName: {
    fontWeight: 600,
    color: colors.text,
  },
  sidebarItemDest: {
    color: colors.textMuted,
    fontWeight: 400,
  },
  sidebarButton: {
    width: '100%',
    padding: '0.85rem 1rem',
    borderRadius: '12px',
    border: 'none',
    background: `linear-gradient(135deg, ${colors.primaryDark}, ${colors.primary})`,
    color: 'white',
    fontWeight: 600,
    fontSize: '0.88rem',
    cursor: 'pointer',
    fontFamily: 'inherit',
    boxShadow: '0 10px 24px rgba(30, 110, 111, 0.2)',
    transition: 'transform 0.2s ease, opacity 0.2s ease',
  },
  sidebarButtonDisabled: {
    opacity: 0.45,
    cursor: 'not-allowed',
    boxShadow: 'none',
  },

  error: {
    background: 'rgba(185, 28, 28, 0.04)',
    color: colors.error,
    padding: '0.7rem 1.5rem',
    borderRadius: '14px',
    marginBottom: '1rem',
    border: '1px solid rgba(185, 28, 28, 0.06)',
    fontWeight: 500,
    fontSize: '0.8rem',
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
    height: '160px',
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
};

const skeletonKeyframes = `
  @keyframes skeleton-loading {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
  }
`;

export default function AttractionsPage() {
  const navigate = useNavigate();
  const { trip, updateTrip } = useTrip();
  const [days, setDays] = useState(trip.days);
  const [moods, setMoods] = useState(trip.selectedMoods.length ? trip.selectedMoods : ['Adventure']);
  const [category, setCategory] = useState('All');
  const [attractions, setAttractions] = useState([]);
  const [selectedIds, setSelectedIds] = useState(trip.selectedAttractionIds);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [expandedCard, setExpandedCard] = useState(null);
  const search = trip.landmarkSearch || '';
  const setSearch = (value) => updateTrip({ landmarkSearch: value });

  useEffect(() => {
    const styleEl = document.createElement('style');
    styleEl.textContent = skeletonKeyframes;
    document.head.appendChild(styleEl);
    return () => styleEl.remove();
  }, []);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        // Load all attractions so name search works across every mood
        const { data } = await attractionsApi.list([]);
        setAttractions(data.attractions || []);
        updateTrip({ attractions: data.attractions || [] });
      } catch (e) {
        setError(e.response?.data?.error || 'Failed to load attractions');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const toggleMood = (mood) => {
    setMoods((prev) => {
      if (prev.includes(mood)) return prev.filter((m) => m !== mood);
      if (prev.length >= 3) return prev;
      return [...prev, mood];
    });
  };

  const selectedItems = useMemo(
    () => attractions.filter((a) => selectedIds.some((id) => Number(id) === Number(a.id))),
    [attractions, selectedIds]
  );

  const uniqueLocations = useMemo(() => {
    const seen = new Set();
    selectedItems.forEach((a) => {
      if (a.destination) seen.add(a.destination);
    });
    return [...seen];
  }, [selectedItems]);

  const toggleAttraction = (id) => {
    const numericId = Number(id);
    setSelectedIds((prev) => {
      if (prev.some((x) => Number(x) === numericId)) {
        setError('');
        return prev.filter((x) => Number(x) !== numericId);
      }
      const attr = attractions.find((a) => Number(a.id) === numericId);
      if (!attr) return [...prev, numericId];

      const currentDests = new Set(
        attractions
          .filter((a) => prev.some((x) => Number(x) === Number(a.id)))
          .map((a) => a.destination)
      );
      if (!currentDests.has(attr.destination) && currentDests.size >= days) {
        setError(
          `A ${days}-day trip allows at most ${days} different location(s). ` +
          `Unselect a place from another location first, or add more days.`
        );
        return prev;
      }
      setError('');
      return [...prev, numericId];
    });
  };

  const categoryFilters = useMemo(() => {
    const unique = [
      ...new Set(
        attractions
          .map((a) => (a.category || '').trim())
          .filter(Boolean)
      ),
    ];
    const rank = (name) => {
      const i = CATEGORY_ORDER.findIndex(
        (c) => c.toLowerCase() === name.toLowerCase()
      );
      return i === -1 ? CATEGORY_ORDER.length : i;
    };
    unique.sort((a, b) => rank(a) - rank(b) || a.localeCompare(b));
    return ['All', ...unique];
  }, [attractions]);

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    const browsingCategory = category !== 'All';
    return attractions.filter((a) => {
      const cat = (a.category || '').trim();
      const name = (a.attraction_name || '').toLowerCase();
      const dest = (a.destination || '').toLowerCase();
      const details = (a.details || '').toLowerCase();
      const matchSearch =
        !q ||
        name.includes(q) ||
        dest.includes(q) ||
        details.includes(q);

      // Name search / category browse ignore mood so filters stay usable
      // (e.g. Scenic is mostly Relaxed — still show it when Scenic is selected)
      const matchMood =
        Boolean(q) ||
        browsingCategory ||
        !moods.length ||
        moods.includes(a.mood_tag);

      const matchCat =
        !browsingCategory ||
        cat.toLowerCase() === category.toLowerCase();

      return matchSearch && matchMood && matchCat;
    });
  }, [attractions, category, search, moods]);

  const canProceed =
    selectedIds.length >= 1 &&
    uniqueLocations.length >= 1 &&
    uniqueLocations.length <= days &&
    days > 0 &&
    moods.length >= 1;

  const confirm = async () => {
    setError('');
    if (!canProceed) {
      if (uniqueLocations.length > days) {
        setError(`Maximum ${days} different location(s) for a ${days}-day trip.`);
      } else {
        setError('Select at least one attraction from 1 to ' + days + ' different location(s).');
      }
      return;
    }
    try {
      const daysInt = Math.max(1, parseInt(String(days), 10) || 1);
      // Attraction moods first so they are never dropped by the max-3 cap
      const moodsFromSelection = selectedItems
        .map((a) => a.mood_tag)
        .filter(Boolean);
      const mergedMoods = [...new Set([...moodsFromSelection, ...moods])].slice(0, 3);
      if (!mergedMoods.length) {
        setError('Select at least one mood before confirming.');
        return;
      }

      const { data } = await tripApi.create({
        days: daysInt,
        selected_moods: mergedMoods,
        finalized_attractions: selectedIds.map((id) => Number(id)),
      });
      updateTrip({
        tripId: data.trip.trip_id,
        days: daysInt,
        selectedMoods: mergedMoods,
        selectedAttractionIds: selectedIds.map((id) => Number(id)),
        itinerary: null,
        accommodations: [],
        accommodation: null,
      });
      navigate('/budget');
    } catch (e) {
      const status = e.response?.status;
      const payload = e.response?.data;
      if (status === 401 || status === 422) {
        setError('Your session expired. Please log in again.');
      } else {
        setError(
          payload?.error ||
            payload?.msg ||
            e.message ||
            'Failed to save trip'
        );
      }
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
    <div className="attr-page" style={styles.container}>
      <style>{`
        @keyframes fadeRise { from { opacity:0; transform:translateY(12px);} to { opacity:1; transform:translateY(0);} }
        .attr-page {
          width: 100% !important;
          max-width: 100% !important;
          min-width: 0 !important;
          box-sizing: border-box !important;
          overflow-x: hidden !important;
          padding-bottom: 5.5rem !important;
        }
        .attr-page *,
        .attr-page *::before,
        .attr-page *::after {
          box-sizing: border-box;
        }
        .attr-page .attr-hero {
          width: 100% !important;
          max-width: 100% !important;
          min-width: 0 !important;
        }
        .attr-page .attr-grid {
          width: 100% !important;
          min-width: 0 !important;
          grid-template-columns: 1fr !important;
        }
        .attr-page .attr-grid > div {
          min-width: 0 !important;
          max-width: 100% !important;
        }
        .attr-page .attr-pills {
          display: flex !important;
          flex-wrap: wrap !important;
          gap: 0.45rem !important;
          width: 100% !important;
          max-width: 100% !important;
          min-width: 0 !important;
          overflow: visible !important;
        }
        .attr-page .attr-pills button {
          flex: 0 0 auto !important;
        }
        .attr-page .attr-cards {
          grid-template-columns: 1fr !important;
          width: 100% !important;
          min-width: 0 !important;
        }
        .attr-page .attr-itinerary {
          position: static !important;
          width: 100% !important;
        }
        .attr-page .attr-itinerary-card {
          position: fixed !important;
          left: 0.75rem !important;
          right: 0.75rem !important;
          bottom: 0.75rem !important;
          z-index: 70 !important;
          padding: 0.85rem 1rem !important;
          border-radius: 16px !important;
          box-shadow: 0 12px 40px rgba(15, 55, 56, 0.22) !important;
        }
        .attr-page .attr-itinerary-list,
        .attr-page .attr-itinerary-stats,
        .attr-page .attr-itinerary-warn {
          display: none !important;
        }
        .attr-page .card-hover:hover {
          transform: translateY(-4px);
          box-shadow: 0 18px 40px rgba(30, 110, 111, 0.1);
          border-color: ${colors.primary};
        }
        .attr-page .search-input:focus {
          border-color: ${colors.primary};
          box-shadow: 0 0 0 3px rgba(78, 198, 212, 0.14);
        }
        .attr-page .attr-confirm:not(:disabled):hover {
          transform: translateY(-1px);
        }
        .attr-page .card-hover > div:first-child {
          height: 140px !important;
        }
        @media (min-width: 640px) {
          .attr-page .attr-cards {
            grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
          }
        }
        @media (min-width: 1025px) {
          .attr-page {
            max-width: 1400px !important;
            padding-bottom: 0 !important;
          }
          .attr-page .attr-hero {
            padding: 2.25rem 2.5rem !important;
            min-height: 220px !important;
            border-radius: 18px !important;
            margin-bottom: 1.75rem !important;
          }
          .attr-page .attr-grid {
            grid-template-columns: minmax(0, 1fr) 320px !important;
            gap: 1.5rem !important;
          }
          .attr-page .attr-cards {
            grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)) !important;
            gap: 1.15rem !important;
          }
          .attr-page .attr-itinerary {
            position: sticky !important;
            top: 88px !important;
          }
          .attr-page .attr-itinerary-card {
            position: static !important;
            left: auto !important;
            right: auto !important;
            bottom: auto !important;
            box-shadow: 0 8px 28px rgba(30, 110, 111, 0.06) !important;
          }
          .attr-page .attr-itinerary-list,
          .attr-page .attr-itinerary-stats,
          .attr-page .attr-itinerary-warn {
            display: block !important;
          }
          .attr-page .attr-itinerary-list {
            max-height: 280px;
            overflow-y: auto;
          }
          .attr-page .card-hover > div:first-child {
            height: 160px !important;
          }
        }
      `}</style>

      <section className="attr-hero" style={styles.hero}>
        <div style={styles.heroBg} />
        <div style={styles.heroContent}>
          <span style={styles.heroBadge}>Curate Your Journey</span>
          <h1 style={styles.heroTitle}>Discover the Spirit of Sri Lanka</h1>
          <p style={styles.heroSubtitle}>
            Pick any number of places in the same location. For {days} days, choose attractions from 1 to {days} different locations only.
          </p>
          <div style={styles.heroControls}>
            <div style={styles.heroInputLabel}>
              <span>Trip Duration</span>
              <input
                type="number"
                min={1}
                value={days}
                onChange={(e) => setDays(Number(e.target.value))}
                style={styles.heroInput}
              />
              <span style={{ color: 'rgba(255,255,255,0.55)' }}>days</span>
            </div>
          </div>
        </div>
      </section>

      <div className="attr-grid" style={styles.mainGrid}>
        <div>
          <div style={styles.filters}>
            <div style={styles.filterLabel}>Choose your mood · max 3</div>
            <div className="attr-pills" style={styles.pillRow}>
              {MOOD_OPTIONS.map((m) => (
                <button
                  key={m}
                  type="button"
                  style={{
                    ...styles.pill,
                    ...(moods.includes(m) ? styles.pillActive : {}),
                  }}
                  onClick={() => toggleMood(m)}
                >
                  {m}
                </button>
              ))}
            </div>

            <div style={styles.filterLabel}>Filter by category</div>
            <div className="attr-pills" style={styles.pillRow}>
              {categoryFilters.map((c) => (
                <button
                  key={c}
                  type="button"
                  style={{
                    ...styles.pill,
                    ...(category === c ? styles.pillActive : {}),
                  }}
                  onClick={() => setCategory(c)}
                >
                  {c}
                </button>
              ))}
            </div>

            <input
              className="search-input"
              type="search"
              placeholder="Search landmarks..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              onInput={(e) => setSearch(e.target.value)}
              style={styles.searchInput}
              autoComplete="off"
            />
          </div>

          {error && <div style={styles.error}>{error}</div>}

          {loading ? (
            <SkeletonLoader />
          ) : filtered.length === 0 ? (
            <div style={{ ...styles.sidebarCard, padding: '1.5rem' }}>
              <p style={{ margin: 0, color: colors.textMuted, fontSize: '0.9rem' }}>
                {search.trim()
                  ? `No attractions match “${search.trim()}”. Try another name, clear search, or switch category.`
                  : 'No attractions match your mood and category filters.'}
              </p>
            </div>
          ) : (
            <div className="attr-cards" style={styles.cardsGrid}>
              {filtered.map((a, index) => {
                const selected = selectedIds.some((id) => Number(id) === Number(a.id));
                const destFull = uniqueLocations.length >= days && !uniqueLocations.includes(a.destination);
                const isDisabled = destFull && !selected;
                const isExpanded = expandedCard?.attraction.id === a.id;
                return (
                  <div
                    key={a.id}
                    className="attr-card-wrap"
                    style={{
                      position: 'relative',
                      zIndex: isExpanded ? 50 : 'auto',
                    }}
                  >
                  <div
                    className="card-hover"
                    role="button"
                    tabIndex={isDisabled ? -1 : 0}
                    aria-pressed={selected}
                    style={{
                      ...styles.card,
                      ...(isDisabled ? styles.cardDisabled : {}),
                      ...(selected ? { borderColor: colors.primary, borderWidth: '2px' } : {}),
                      ...(isExpanded ? { visibility: 'hidden' } : {}),
                    }}
                    onClick={() => !isDisabled && toggleAttraction(a.id)}
                    onKeyDown={(e) => {
                      if (isDisabled) return;
                      if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        toggleAttraction(a.id);
                      }
                    }}
                  >
                    <AttractionPhoto
                      src={a.image}
                      name={a.attraction_name}
                      gradient={getCardGradient(index)}
                      height={160}
                    >
                      <div style={styles.cardImageOverlay} />
                      <span style={styles.cardTag}>{a.mood_tag}</span>
                      <button
                        type="button"
                        aria-label={selected ? 'Deselect attraction' : 'Select attraction'}
                        disabled={isDisabled}
                        onClick={(e) => {
                          e.stopPropagation();
                          if (!isDisabled) toggleAttraction(a.id);
                        }}
                        style={{
                          ...styles.cardCheckbox,
                          ...(selected ? styles.cardCheckboxChecked : {}),
                        }}
                      >
                        {selected ? <span style={styles.cardCheckboxMark}>✓</span> : null}
                      </button>
                    </AttractionPhoto>
                    <div style={styles.cardBody}>
                      <h3 style={styles.cardTitle}>{a.attraction_name}</h3>
                      <div style={styles.cardMeta}>{a.destination} · {a.category}</div>
                      <p style={styles.cardDescription}>
                        {a.details && a.details.length > DESCRIPTION_PREVIEW_LEN
                          ? `${a.details.slice(0, DESCRIPTION_PREVIEW_LEN).trimEnd()}… `
                          : (a.details || '')}
                        {a.details && a.details.length > DESCRIPTION_PREVIEW_LEN && (
                          <button
                            type="button"
                            style={styles.cardMoreBtn}
                            onClick={(e) => {
                              e.stopPropagation();
                              setExpandedCard({ attraction: a, index });
                            }}
                          >
                            more
                          </button>
                        )}
                      </p>
                      {selected && (
                        <div style={{ marginTop: '0.4rem', fontSize: '0.65rem', color: colors.primary, fontWeight: 600 }}>
                          Selected
                        </div>
                      )}
                    </div>
                  </div>
                  {isExpanded && (
                    <AttractionDetailModal
                      attraction={a}
                      gradient={getCardGradient(index)}
                      selected={selected}
                      selectDisabled={isDisabled}
                      onClose={() => setExpandedCard(null)}
                      onToggleSelect={() => toggleAttraction(a.id)}
                    />
                  )}
                  </div>
                );
              })}
            </div>
          )}
        </div>

        <div className="attr-itinerary" style={styles.sidebar}>
          <div className="attr-itinerary-card" style={styles.sidebarCard}>
            <div className="attr-itinerary-head" style={styles.sidebarHeader}>
              <h3 style={styles.sidebarTitle}>Trip Itinerary</h3>
              <span style={styles.sidebarBadge}>{selectedIds.length} Selected</span>
            </div>
            <div className="attr-itinerary-stats" style={styles.sidebarStats}>
              Locations: {uniqueLocations.length}/{days} max · {selectedIds.length} attraction(s)
            </div>
            {!canProceed && selectedIds.length > 0 && uniqueLocations.length > days && (
              <div className="attr-itinerary-warn" style={{ ...styles.error, marginTop: '0.5rem', fontSize: '0.75rem' }}>
                Too many locations — remove places until you have at most {days}.
              </div>
            )}
            <ul className="attr-itinerary-list" style={styles.sidebarList}>
              {selectedItems.map((a) => (
                <li key={a.id} style={styles.sidebarItem}>
                  <span>
                    <span style={styles.sidebarItemName}>{a.attraction_name}</span>
                    <span style={styles.sidebarItemDest}> ({a.destination})</span>
                  </span>
                  <button
                    onClick={() => toggleAttraction(a.id)}
                    style={{
                      background: 'none',
                      border: 'none',
                      color: colors.textMuted,
                      cursor: 'pointer',
                      fontSize: '0.8rem',
                      fontFamily: 'inherit',
                      padding: '0.2rem 0.5rem',
                    }}
                  >
                    ×
                  </button>
                </li>
              ))}
            </ul>
            <button
              className="attr-confirm"
              style={{
                ...styles.sidebarButton,
                ...(!canProceed ? styles.sidebarButtonDisabled : {}),
              }}
              disabled={!canProceed}
              onClick={confirm}
            >
              Confirm & Move to Budget
            </button>
          </div>
        </div>
      </div>

      {expandedCard && (
        <div
          className="tc-modal-backdrop is-open"
          onClick={() => setExpandedCard(null)}
          aria-hidden="true"
        />
      )}
    </div>
  );
}