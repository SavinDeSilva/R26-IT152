import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { recommendationsApi, savedRefsApi } from '../api/client';
import AttractionPhoto from '../components/AttractionPhoto';
import { useTrip } from '../context/TripContext';
import { useSiteI18n } from '@shared/i18n/react';

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
    paddingBottom: '80px',
    animation: 'fadeRise 0.55s ease both',
  },

  nav: {
    position: 'sticky',
    top: 0,
    zIndex: 100,
    backdropFilter: 'blur(20px)',
    backgroundColor: 'rgba(238, 248, 248, 0.85)',
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
    color: colors.textMuted,
    background: 'rgba(0,0,0,0.03)',
    padding: '0.2rem 0.7rem',
    borderRadius: '20px',
    letterSpacing: '0.04em',
  },

  hero: {
    position: 'relative',
    margin: '0 0 1.5rem',
    borderRadius: '20px',
    overflow: 'hidden',
    width: '100%',
    background: 'rgba(255, 255, 255, 0.38)',
    padding: '2.5rem 3rem',
    boxShadow: `0 20px 60px rgba(78, 198, 212, 0.12)`,
  },
  heroBg: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundImage: 'url("/header-lagoon.png")',
    backgroundSize: 'cover',
    backgroundPosition: 'center',
    opacity: 0.42,
  },
  heroContent: {
    position: 'relative',
    zIndex: 2,
  },
  heroBadge: {
    display: 'inline-block',
    background: colors.accent,
    padding: '0.25rem 1rem',
    borderRadius: '30px',
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
    color: '#0e4a4e',
    margin: '0 0 0.3rem 0',
    letterSpacing: '-0.01em',
    lineHeight: 1.1,
  },
  heroSubtitle: {
    fontSize: '0.95rem',
    color: '#16575c',
    maxWidth: '480px',
    lineHeight: 1.5,
  },
  heroBudget: {
    marginTop: '1rem',
    padding: '0.6rem 1.2rem',
    background: 'rgba(255,255,255,0.62)',
    backdropFilter: 'blur(10px)',
    borderRadius: '40px',
    display: 'inline-block',
    fontSize: '0.85rem',
    color: '#16575c',
    border: '1px solid rgba(14, 74, 78, 0.12)',
  },
  heroBudgetStrong: {
    fontWeight: 600,
    color: '#0e4a4e',
  },

  error: {
    background: 'rgba(185, 28, 28, 0.04)',
    backdropFilter: 'blur(10px)',
    color: colors.error,
    padding: '0.7rem 1.5rem',
    borderRadius: '14px',
    margin: '0 0 1.5rem',
    border: '1px solid rgba(185, 28, 28, 0.06)',
    fontWeight: 500,
    fontSize: '0.85rem',
  },

  sectionHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '0',
    marginBottom: '1rem',
    flexWrap: 'wrap',
    gap: '0.5rem',
  },
  sectionTitle: {
    fontSize: '1.2rem',
    fontWeight: 600,
    color: colors.text,
    letterSpacing: '-0.01em',
    margin: 0,
  },
  sectionCount: {
    fontSize: '0.8rem',
    color: colors.textMuted,
  },

  grid: {
    display: 'grid',
    gap: '1.5rem',
    padding: '0',
    marginBottom: '2rem',
    width: '100%',
  },

  card: {
    background: '#FFFFFF',
    borderRadius: '14px',
    padding: '1.2rem 1.2rem 1.4rem',
    boxShadow: '0 2px 12px rgba(0, 0, 0, 0.03)',
    border: `1px solid ${colors.border}`,
    transition: 'all 0.3s ease',
    display: 'flex',
    flexDirection: 'column',
    overflow: 'hidden',
  },
  guideCard: {
    background: '#FFFFFF',
    borderRadius: '14px',
    padding: 0,
    boxShadow: '0 2px 12px rgba(0, 0, 0, 0.03)',
    border: `1px solid ${colors.border}`,
    transition: 'all 0.3s ease',
    display: 'flex',
    flexDirection: 'column',
    overflow: 'hidden',
  },
  guideCardBody: {
    padding: '1rem 1.1rem 1.2rem',
    display: 'flex',
    flexDirection: 'column',
    flex: 1,
  },
  guideImageLink: {
    fontSize: '0.72rem',
    color: colors.primary,
    wordBreak: 'break-all',
    margin: '0 0 0.75rem',
    textDecoration: 'underline',
  },
  cardHover: {
    transform: 'translateY(-4px)',
    boxShadow: `0 16px 40px rgba(78, 198, 212, 0.06), 0 4px 16px rgba(0, 0, 0, 0.02)`,
    borderColor: colors.primary,
  },
  cardTitle: {
    fontSize: '1rem',
    fontWeight: 600,
    color: colors.text,
    margin: '0 0 0.2rem 0',
    letterSpacing: '-0.01em',
  },
  cardMeta: {
    fontSize: '0.8rem',
    color: colors.textMuted,
    marginBottom: '0.3rem',
  },
  cardAddress: {
    fontSize: '0.8rem',
    color: colors.textMuted,
    margin: '0 0 0.45rem 0',
    lineHeight: 1.5,
  },
  cardContact: {
    fontSize: '0.8rem',
    color: colors.textMuted,
    margin: '0 0 0.8rem 0',
    lineHeight: 1.5,
  },
  cardDetails: {
    display: 'grid',
    gridTemplateColumns: '4.2rem 1fr',
    columnGap: '0.45rem',
    rowGap: '0.22rem',
    margin: '0 0 0.8rem',
  },
  cardDetailLabel: {
    fontWeight: 700,
    fontSize: '0.72rem',
    color: colors.primaryDark,
    paddingTop: '0.05rem',
  },
  cardDetailValue: {
    fontSize: '0.78rem',
    color: '#0c3d40',
    lineHeight: 1.4,
    wordBreak: 'break-word',
  },
  filterPanel: {
    background: colors.glass,
    border: `1px solid ${colors.border}`,
    borderRadius: '14px',
    padding: '1rem 1.1rem',
    marginBottom: '1.25rem',
    boxShadow: '0 2px 12px rgba(0, 0, 0, 0.03)',
  },
  filterTitle: {
    fontSize: '0.95rem',
    fontWeight: 600,
    margin: '0 0 0.85rem',
    color: colors.text,
  },
  filterGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
    gap: '0.75rem',
    alignItems: 'end',
  },
  filterField: {
    display: 'flex',
    flexDirection: 'column',
    gap: '0.35rem',
    minWidth: 0,
  },
  filterLabel: {
    fontSize: '0.72rem',
    fontWeight: 600,
    color: colors.textMuted,
    letterSpacing: '0.04em',
    textTransform: 'uppercase',
  },
  filterInput: {
    width: '100%',
    padding: '0.55rem 0.75rem',
    borderRadius: '10px',
    border: `1px solid ${colors.border}`,
    fontSize: '0.85rem',
    fontFamily: 'inherit',
    color: colors.text,
    background: '#fff',
    outline: 'none',
    boxSizing: 'border-box',
  },
  filterActions: {
    display: 'flex',
    gap: '0.5rem',
    flexWrap: 'wrap',
  },
  filterButton: {
    padding: '0.55rem 1rem',
    borderRadius: '999px',
    border: 'none',
    background: `linear-gradient(135deg, ${colors.primaryDark}, ${colors.primary})`,
    color: 'white',
    fontWeight: 600,
    fontSize: '0.8rem',
    cursor: 'pointer',
    fontFamily: 'inherit',
  },
  filterButtonOutline: {
    padding: '0.55rem 1rem',
    borderRadius: '999px',
    border: `1px solid ${colors.border}`,
    background: '#fff',
    color: colors.text,
    fontWeight: 600,
    fontSize: '0.8rem',
    cursor: 'pointer',
    fontFamily: 'inherit',
  },
  guideTypeChip: {
    display: 'inline-block',
    fontSize: '0.65rem',
    fontWeight: 600,
    color: colors.primaryDark,
    background: 'rgba(182, 230, 233, 0.55)',
    padding: '0.15rem 0.55rem',
    borderRadius: '999px',
    marginBottom: '0.35rem',
  },
  cardButton: {
    marginTop: 'auto',
    padding: '0.5rem 1.2rem',
    borderRadius: '30px',
    border: 'none',
    fontSize: '0.8rem',
    fontWeight: 500,
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    fontFamily: 'inherit',
    letterSpacing: '0.01em',
    alignSelf: 'flex-start',
  },
  cardButtonPrimary: {
    background: colors.primary,
    color: 'white',
  },
  cardButtonOutline: {
    background: 'transparent',
    color: colors.primary,
    border: `1px solid ${colors.primary}`,
  },
  cardButtonDisabled: {
    opacity: 0.4,
    cursor: 'not-allowed',
  },

  footer: {
    position: 'sticky',
    bottom: '1.5rem',
    margin: '1rem 0 0',
    background: colors.primaryDark,
    backdropFilter: 'blur(24px)',
    borderRadius: '60px',
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
  footerButton: {
    background: colors.primary,
    border: 'none',
    borderRadius: '40px',
    padding: '0.5rem 1.6rem',
    color: 'white',
    fontWeight: 600,
    fontSize: '0.8rem',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    fontFamily: 'inherit',
    letterSpacing: '0.01em',
  },

  bottomTab: {
    position: 'fixed',
    bottom: 0,
    left: 0,
    right: 0,
    display: 'none',
    background: 'rgba(255,255,255,0.95)',
    backdropFilter: 'blur(20px)',
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
  bottomTabIcon: {
    fontSize: '1rem',
  },

  '@media (max-width: 768px)': {
    hero: {
      padding: '1.5rem',
      margin: '0.5rem 0.8rem 1rem',
      borderRadius: '16px',
    },
    heroTitle: {
      fontSize: '1.4rem',
    },
    heroSubtitle: {
      fontSize: '0.8rem',
    },
    grid: {
      gridTemplateColumns: '1fr',
      gap: '1rem',
      padding: '0 0.8rem',
    },
    sectionHeader: {
      padding: '0 0.8rem',
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
    footer: {
      margin: '1rem 0.8rem 0',
      borderRadius: '40px',
      padding: '0.5rem 1rem',
    },
    footerInfo: {
      fontSize: '0.7rem',
    },
    footerButton: {
      padding: '0.35rem 1rem',
      fontSize: '0.7rem',
    },
    heroBudget: {
      fontSize: '0.75rem',
      padding: '0.4rem 1rem',
    },
  },
};

function isSavedReference(saved, refType, refId) {
  return saved.some(
    (item) => item.ref_type === refType && Number(item.ref_id) === Number(refId)
  );
}

export default function RecommendationsPage() {
  const { t } = useSiteI18n();
  const navigate = useNavigate();
  const { trip, updateTrip } = useTrip();
  const [businesses, setBusinesses] = useState([]);
  const [businessMatchMode, setBusinessMatchMode] = useState('all');
  const [agencies, setAgencies] = useState([]);
  const [guides, setGuides] = useState([]);
  const [guideTotal, setGuideTotal] = useState(0);
  const [guideTypes, setGuideTypes] = useState(['National', 'Chauffeur', 'Area', 'Site']);
  const [guideLanguages, setGuideLanguages] = useState([
    'English', 'German', 'French', 'Japanese', 'Chinese', 'Russian', 'Italian', 'Spanish',
    'Hindi', 'Korean', 'Arabic', 'Dutch', 'Greek', 'Hebrew', 'Hungarian', 'Swedish', 'Tamil', 'Thai', 'Urdu', 'Mandarin',
  ]);
  const [guideName, setGuideName] = useState('');
  const [guideRegNo, setGuideRegNo] = useState('');
  const [guideType, setGuideType] = useState('');
  const [guideLanguage, setGuideLanguage] = useState('');
  const [guideLoading, setGuideLoading] = useState(false);
  const [remaining, setRemaining] = useState(null);
  const [saved, setSaved] = useState([]);
  const [error, setError] = useState('');
  const [savingKey, setSavingKey] = useState('');
  const [hoveredCard, setHoveredCard] = useState(null);

  const loadGuides = async (filters = {}) => {
    setGuideLoading(true);
    try {
      const { data } = await recommendationsApi.guides({
        name: filters.name ?? guideName,
        registration_no: filters.registration_no ?? guideRegNo,
        guide_type: filters.guide_type ?? guideType,
        language: filters.language ?? guideLanguage,
        limit: 500,
      });
      setGuides(data.guides || []);
      setGuideTotal(data.total ?? (data.guides || []).length);
      if (data.guide_types?.length) setGuideTypes(data.guide_types);
      if (data.languages?.length) setGuideLanguages(data.languages);
    } catch (e) {
      setError(e.response?.data?.error || t('failedLoadGuides'));
    } finally {
      setGuideLoading(false);
    }
  };

  useEffect(() => {
    let cancelled = false;

    const load = async () => {
      try {
        const requests = [
          recommendationsApi.businesses(trip.tripId),
          recommendationsApi.agencies(trip.tripId),
          recommendationsApi.guides({ limit: 200 }),
        ];
        if (trip.tripId) {
          requests.push(savedRefsApi.list(trip.tripId));
        }

        const [biz, ag, guideRes, refs] = await Promise.all(requests);
        if (cancelled) return;

        setBusinesses(biz.data.businesses || []);
        setBusinessMatchMode(biz.data.match_mode || 'all');
        setAgencies(ag.data.agencies || []);
        setGuides(guideRes.data.guides || []);
        setGuideTotal(guideRes.data.total ?? (guideRes.data.guides || []).length);
        if (guideRes.data.guide_types?.length) setGuideTypes(guideRes.data.guide_types);
        if (guideRes.data.languages?.length) setGuideLanguages(guideRes.data.languages);
        setRemaining(biz.data.remaining_budget ?? null);

        const serverSaved = refs?.data?.saved_references || [];
        const pending = trip.pendingSavedReferences || [];
        const merged = [...serverSaved];
        pending.forEach((item) => {
          if (!isSavedReference(merged, item.ref_type, item.ref_id)) {
            merged.push(item);
          }
        });

        // Persist any locally saved refs once a trip exists
        if (trip.tripId && pending.length) {
          for (const item of pending) {
            try {
              await savedRefsApi.save({
                trip_id: trip.tripId,
                ref_type: item.ref_type,
                ref_id: Number(item.ref_id),
              });
            } catch {
              /* keep pending item if sync fails */
            }
          }
          const refreshed = await savedRefsApi.list(trip.tripId);
          const finalSaved = refreshed.data.saved_references || [];
          setSaved(finalSaved);
          updateTrip({
            savedReferences: finalSaved,
            pendingSavedReferences: [],
            remainingBudget: biz.data.remaining_budget ?? null,
          });
        } else {
          setSaved(merged);
          updateTrip({
            savedReferences: merged,
            remainingBudget: biz.data.remaining_budget ?? null,
          });
        }
        setError('');
      } catch (e) {
        if (!cancelled) {
          setError(e.response?.data?.error || t('failedLoadRecommendations'));
        }
      }
    };

    load();
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps -- reload when trip id appears; pending sync handled inside
  }, [trip.tripId]);

  const bookmark = async (refType, refId) => {
    const key = `${refType}:${refId}`;
    if (isSavedReference(saved, refType, refId)) return;

    setSavingKey(key);
    setError('');
    try {
      if (!trip.tripId) {
        const localItem = {
          id: `local-${refType}-${refId}`,
          ref_type: refType,
          ref_id: Number(refId),
        };
        const nextPending = [...(trip.pendingSavedReferences || []), localItem];
        const nextSaved = [...saved, localItem];
        setSaved(nextSaved);
        updateTrip({
          pendingSavedReferences: nextPending,
          savedReferences: nextSaved,
        });
        return;
      }

      await savedRefsApi.save({
        trip_id: trip.tripId,
        ref_type: refType,
        ref_id: Number(refId),
      });
      const { data } = await savedRefsApi.list(trip.tripId);
      setSaved(data.saved_references);
      updateTrip({ savedReferences: data.saved_references });
    } catch (e) {
      setError(e.response?.data?.error || t('failedSaveReference'));
    } finally {
      setSavingKey('');
    }
  };

  const renderSaveButton = (refType, refId) => {
    const savedAlready = isSavedReference(saved, refType, refId);
    const key = `${refType}:${refId}`;
    const saving = savingKey === key;

    if (savedAlready) {
      return (
        <button
          style={{
            ...styles.cardButton,
            ...styles.cardButtonPrimary,
            ...styles.cardButtonDisabled,
          }}
          disabled
        >
          {t('saved')}
        </button>
      );
    }

    return (
      <button
        style={{
          ...styles.cardButton,
          ...styles.cardButtonOutline,
          ...(saving ? styles.cardButtonDisabled : {}),
        }}
        disabled={saving}
        onClick={() => bookmark(refType, refId)}
      >
        {saving ? t('savingEllipsis') : t('saveForReference')}
      </button>
    );
  };

  return (
    <div className="recs-page" style={styles.container}>
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
        @media (min-width: 769px) and (max-width: 1024px) {
          .recs-page .recs-grid {
            grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)) !important;
          }
        }
        @media (max-width: 768px) {
          .recs-page {
            padding-bottom: 5.5rem !important;
          }
          .recs-page .recs-hero {
            padding: 1.35rem 1.2rem !important;
            margin: 0.5rem 0 1rem !important;
            border-radius: 14px !important;
          }
          .recs-page .recs-hero h1 {
            font-size: 1.35rem !important;
          }
          .recs-page .recs-hero p {
            font-size: 0.84rem !important;
          }
          .recs-page .recs-section-head {
            padding: 0 !important;
            flex-direction: column;
            align-items: flex-start !important;
          }
          .recs-page .recs-grid {
            grid-template-columns: 1fr !important;
            padding: 0 !important;
            gap: 0.9rem !important;
          }
          .recs-page .recs-footer {
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
          .recs-page .recs-footer button {
            width: 100%;
          }
          .card-hover:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(78, 198, 212, 0.04);
          }
        }
      `}</style>

      <section className="recs-hero" style={styles.hero}>
        <div style={styles.heroBg} />
        <div style={styles.heroContent}>
          <span style={styles.heroBadge}>{t('smartDiscovery')}</span>
          <h1 style={styles.heroTitle}>{t('completeJourneyInsights')}</h1>
          <p style={styles.heroSubtitle}>
            {t('recommendationsHeroDesc')}
          </p>
          {remaining != null && (
            <div style={styles.heroBudget}>
              {t('remainingBudget')} <strong style={styles.heroBudgetStrong}>${remaining.toFixed(2)}</strong>
            </div>
          )}
        </div>
      </section>

      {!trip.tripId && (
        <div className="info" style={{ margin: '0 0 1rem', fontSize: '0.85rem' }}>
          {t('browseRecommendationsHint')}
        </div>
      )}

      {error && <div style={styles.error}>{error}</div>}

      <div className="recs-section-head" style={styles.sectionHeader}>
        <h2 style={styles.sectionTitle}>{t('localShops')}</h2>
        <span style={styles.sectionCount}>{businesses.length} {t('businesses')}</span>
      </div>

      {businessMatchMode === 'nearby' && (
        <div className="info" style={{ margin: '0 0 1rem', fontSize: '0.85rem' }}>
          {t('nearbyShopsHint')}
        </div>
      )}
      {businessMatchMode === 'fallback' && (
        <div className="info" style={{ margin: '0 0 1rem', fontSize: '0.85rem' }}>
          {t('fallbackShopsHint')}
        </div>
      )}

      <div className="recs-grid" style={styles.grid}>
        {businesses.length === 0 && (
          <p style={{ color: 'var(--muted)', gridColumn: '1 / -1' }}>{t('noBusinessesAvailable')}</p>
        )}
        {businesses.map((b) => {
          const isHovered = hoveredCard === `biz-${b.id}`;
          return (
            <div
              key={b.id}
              className="card-hover"
              style={{
                ...styles.card,
                ...(isHovered ? styles.cardHover : {}),
              }}
              onMouseEnter={() => setHoveredCard(`biz-${b.id}`)}
              onMouseLeave={() => setHoveredCard(null)}
            >
              <h3 style={styles.cardTitle}>{b.business_name}</h3>
              <p style={styles.cardMeta}>{b.local_authority} · {b.district}</p>
              {b.address && <p style={styles.cardAddress}>{b.address}</p>}
              {(b.telephone || b.email) && (
                <div style={styles.cardDetails}>
                  {b.telephone && (
                    <>
                      <span style={styles.cardDetailLabel}>Phone</span>
                      <span style={styles.cardDetailValue}>
                        <a href={`tel:${b.telephone}`} style={{ color: colors.primaryDark }}>
                          {b.telephone}
                        </a>
                      </span>
                    </>
                  )}
                  {b.email && (
                    <>
                      <span style={styles.cardDetailLabel}>Email</span>
                      <span style={styles.cardDetailValue}>
                        <a href={`mailto:${b.email}`} style={{ color: colors.primaryDark }}>
                          {b.email}
                        </a>
                      </span>
                    </>
                  )}
                </div>
              )}
              {renderSaveButton('business_directory', b.id)}
            </div>
          );
        })}
      </div>

      <div className="recs-section-head" style={styles.sectionHeader}>
        <h2 style={styles.sectionTitle}>{t('travelAgencies')}</h2>
        <span style={styles.sectionCount}>{agencies.length} {t('agencies')}</span>
      </div>

      <div className="recs-grid" style={styles.grid}>
        {agencies.map((a) => {
          const isHovered = hoveredCard === `agency-${a.id}`;
          return (
            <div
              key={a.id}
              className="card-hover"
              style={{
                ...styles.card,
                ...(isHovered ? styles.cardHover : {}),
              }}
              onMouseEnter={() => setHoveredCard(`agency-${a.id}`)}
              onMouseLeave={() => setHoveredCard(null)}
            >
              <h3 style={styles.cardTitle}>{a.name}</h3>
              <p style={styles.cardMeta}>{a.local_authority}</p>
              <p style={styles.cardContact}>
                {a.telephone} · {a.email}
              </p>
              {renderSaveButton('travel_agency', a.id)}
            </div>
          );
        })}
      </div>

      <div className="recs-section-head" style={styles.sectionHeader}>
        <h2 style={styles.sectionTitle}>{t('tourGuides')}</h2>
        <span style={styles.sectionCount}>
          {guideLoading ? t('loading') : `${guides.length} ${t('guidesShown')} · ${guideTotal} ${t('guidesTotal')}`}
        </span>
      </div>

      <div style={styles.filterPanel}>
        <h3 style={styles.filterTitle}>{t('searchTourGuide')}</h3>
        <div style={styles.filterGrid}>
          <label style={styles.filterField}>
            <span style={styles.filterLabel}>{t('guideNameLabel')}</span>
            <input
              style={styles.filterInput}
              value={guideName}
              onChange={(e) => setGuideName(e.target.value)}
              placeholder={t('search')}
              onKeyDown={(e) => {
                if (e.key === 'Enter') loadGuides();
              }}
            />
          </label>
          <label style={styles.filterField}>
            <span style={styles.filterLabel}>{t('registrationNoLabel')}</span>
            <input
              style={styles.filterInput}
              value={guideRegNo}
              onChange={(e) => setGuideRegNo(e.target.value)}
              placeholder={t('search')}
              onKeyDown={(e) => {
                if (e.key === 'Enter') loadGuides();
              }}
            />
          </label>
          <label style={styles.filterField}>
            <span style={styles.filterLabel}>{t('guideTypeLabel')}</span>
            <select
              style={styles.filterInput}
              value={guideType}
              onChange={(e) => {
                const value = e.target.value;
                setGuideType(value);
                loadGuides({ guide_type: value });
              }}
            >
              <option value="">{t('allTypes')}</option>
              {guideTypes.map((type) => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>
          </label>
          <label style={styles.filterField}>
            <span style={styles.filterLabel}>{t('languageLabel')}</span>
            <select
              style={styles.filterInput}
              value={guideLanguage}
              onChange={(e) => {
                const value = e.target.value;
                setGuideLanguage(value);
                loadGuides({ language: value });
              }}
            >
              <option value="">{t('allLanguages')}</option>
              {guideLanguages.map((lang) => (
                <option key={lang} value={lang}>{lang}</option>
              ))}
            </select>
          </label>
          <div style={styles.filterActions}>
            <button type="button" style={styles.filterButton} onClick={() => loadGuides()}>
              {t('search')}
            </button>
            <button
              type="button"
              style={styles.filterButtonOutline}
              onClick={() => {
                setGuideName('');
                setGuideRegNo('');
                setGuideType('');
                setGuideLanguage('');
                loadGuides({
                  name: '',
                  registration_no: '',
                  guide_type: '',
                  language: '',
                });
              }}
            >
              {t('clear')}
            </button>
          </div>
        </div>
      </div>

      <div className="recs-grid" style={styles.grid}>
        {guides.length === 0 && !guideLoading ? (
          <div style={{ ...styles.card, gridColumn: '1 / -1' }}>
            <p style={{ margin: 0, color: colors.textMuted, fontSize: '0.9rem' }}>
              {t('noGuidesMatch')}
            </p>
          </div>
        ) : (
          guides.map((g) => {
            const isHovered = hoveredCard === `guide-${g.id}`;
            const imageSrc = g.image_url || g.image || null;
            return (
              <div
                key={g.id}
                className="card-hover"
                style={{
                  ...styles.guideCard,
                  ...(isHovered ? styles.cardHover : {}),
                }}
                onMouseEnter={() => setHoveredCard(`guide-${g.id}`)}
                onMouseLeave={() => setHoveredCard(null)}
              >
                <AttractionPhoto
                  src={imageSrc}
                  name={g.name}
                  gradient={`linear-gradient(135deg, ${colors.primaryDark}, ${colors.primary})`}
                  height={140}
                />
                <div style={styles.guideCardBody}>
                  {g.guide_type && <span style={styles.guideTypeChip}>{g.guide_type}</span>}
                  <h3 style={styles.cardTitle}>{g.name}</h3>
                  <p style={styles.cardMeta}>
                    {t('regLabel')} {g.registration_no || '—'}
                    {g.languages ? ` · ${g.languages}` : ''}
                  </p>
                  <p style={styles.cardAddress}>{g.address || t('addressNotListed')}</p>
                  <p style={styles.cardContact}>
                    {[g.tel, g.email].filter(Boolean).join(' · ') || t('noContactListed')}
                  </p>
                  {imageSrc && (
                    <a
                      href={imageSrc}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={styles.guideImageLink}
                      onClick={(e) => e.stopPropagation()}
                    >
                      {imageSrc}
                    </a>
                  )}
                  {renderSaveButton('tourist_guide', g.id)}
                </div>
              </div>
            );
          })
        )}
      </div>

      <div className="recs-footer" style={styles.footer}>
        <div style={styles.footerInfo}>
          <span style={styles.footerHighlight}>{saved.length}</span> {t('itemsSavedForReference')}
        </div>
        <button style={styles.footerButton} onClick={() => navigate('/export')}>
          {t('updateItineraryExport')}
        </button>
      </div>

      <div style={styles.bottomTab}>
        <button style={{ ...styles.bottomTabItem, ...styles.bottomTabActive }}>
          <span style={styles.bottomTabIcon}>◆</span>
          {t('tabDiscover')}
        </button>
        <button style={styles.bottomTabItem}>
          <span style={styles.bottomTabIcon}>◇</span>
          {t('tabMap')}
        </button>
        <button style={styles.bottomTabItem}>
          <span style={styles.bottomTabIcon}>◈</span>
          {t('tabItinerary')}
        </button>
        <button style={styles.bottomTabItem}>
          <span style={styles.bottomTabIcon}>○</span>
          {t('tabProfile')}
        </button>
      </div>
    </div>
  );
}