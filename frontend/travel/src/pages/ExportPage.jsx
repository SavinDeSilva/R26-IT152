import { useNavigate } from 'react-router-dom';
import { itineraryApi } from '../api/client';
import { useTrip } from '../context/TripContext';

const colors = {
  primary: '#4EC6D4',
  primaryLight: '#b6E6E9',
  primaryDark: '#1E6E6F',
  primaryMid: '#7AC7BD',
  primarySoft: '#7AC7BD',
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

  heroCard: {
    padding: '2rem',
    display: 'grid',
    gap: '1.5rem',
    alignItems: 'center',
    background: `linear-gradient(135deg, rgba(30, 110, 111, 0.88) 0%, rgba(78, 198, 212, 0.65) 100%)`,
    borderRadius: '16px',
    margin: '0 0 1.5rem',
    boxShadow: `0 20px 60px rgba(30, 110, 111, 0.12)`,
    position: 'relative',
    overflow: 'hidden',
    width: '100%',
    maxWidth: '100%',
    boxSizing: 'border-box',
  },
  heroBg: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundImage: 'url("https://images.unsplash.com/photo-1559827260-dc66d52bef19?w=1400&q=80")',
    backgroundSize: 'cover',
    backgroundPosition: 'center',
    opacity: 0.12,
  },
  heroContent: {
    position: 'relative',
    zIndex: 2,
  },
  heroTitle: {
    fontSize: '1.8rem',
    fontWeight: 700,
    color: 'white',
    margin: '0 0 0.3rem 0',
    letterSpacing: '-0.01em',
    lineHeight: 1.1,
    fontFamily: fontBody,
  },
  heroText: {
    color: 'rgba(255,255,255,0.7)',
    margin: '0 0 1rem 0',
    fontSize: '0.95rem',
    lineHeight: 1.5,
  },
  heroActions: {
    display: 'flex',
    gap: '0.75rem',
    flexWrap: 'wrap',
  },
  btnPrimary: {
    padding: '0.6rem 1.6rem',
    borderRadius: '40px',
    border: 'none',
    background: colors.accent,
    color: colors.primaryDark,
    fontWeight: 600,
    fontSize: '0.85rem',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    fontFamily: 'inherit',
    letterSpacing: '0.01em',
  },
  btnOutline: {
    padding: '0.6rem 1.6rem',
    borderRadius: '40px',
    border: '1px solid rgba(255,255,255,0.2)',
    background: 'transparent',
    color: 'white',
    fontWeight: 500,
    fontSize: '0.85rem',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    fontFamily: 'inherit',
    letterSpacing: '0.01em',
  },
  heroImage: {
    position: 'relative',
    zIndex: 2,
    height: '180px',
    borderRadius: '12px',
    backgroundImage: 'url("https://images.unsplash.com/photo-1559827260-dc66d52bef19?w=1400&q=80")',
    backgroundSize: 'cover',
    backgroundPosition: 'center',
    border: '1px solid rgba(255,255,255,0.04)',
  },

  mainGrid: {
    display: 'grid',
    gap: '2rem',
    padding: '0 0 2rem',
    width: '100%',
  },

  sectionHeader: {
    marginBottom: '1rem',
  },
  sectionTitle: {
    fontSize: '1.2rem',
    fontWeight: 600,
    color: colors.text,
    letterSpacing: '-0.01em',
    margin: 0,
    fontFamily: fontBody,
  },

  gridCards: {
    display: 'grid',
    gap: '1.5rem',
    width: '100%',
  },

  card: {
    background: colors.white,
    borderRadius: '14px',
    padding: '1.2rem 1.2rem 1.4rem',
    boxShadow: '0 2px 12px rgba(0, 0, 0, 0.03)',
    border: `1px solid ${colors.border}`,
    transition: 'all 0.3s ease',
  },
  cardTitle: {
    fontSize: '1rem',
    fontWeight: 600,
    color: colors.text,
    margin: '0 0 0.3rem 0',
    letterSpacing: '-0.01em',
    fontFamily: fontBody,
  },
  cardText: {
    fontSize: '0.85rem',
    color: colors.textMuted,
    margin: '0 0 1rem 0',
    lineHeight: 1.5,
  },
  cardBtn: {
    padding: '0.4rem 1.2rem',
    borderRadius: '30px',
    border: `1px solid ${colors.primary}`,
    background: 'transparent',
    color: colors.primary,
    fontWeight: 500,
    fontSize: '0.8rem',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    fontFamily: 'inherit',
  },

  sidebar: {
    alignSelf: 'start',
    width: '100%',
  },
  sidebarCard: {
    background: colors.glass,
    backdropFilter: 'blur(20px)',
    borderRadius: '16px',
    padding: '1.5rem',
    border: `1px solid ${colors.border}`,
    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.02)',
  },
  sidebarTitle: {
    fontSize: '1rem',
    fontWeight: 600,
    margin: '0 0 0.5rem 0',
    color: colors.text,
    fontFamily: fontBody,
  },
  statsGrid: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: '0.75rem',
    marginTop: '1rem',
  },
  statCard: {
    background: 'rgba(30, 110, 111, 0.02)',
    borderRadius: '10px',
    padding: '0.75rem',
    border: `1px solid ${colors.border}`,
  },
  statLabel: {
    fontSize: '0.65rem',
    fontWeight: 500,
    color: colors.textMuted,
    letterSpacing: '0.04em',
    textTransform: 'uppercase',
  },
  statValue: {
    fontSize: '1rem',
    fontWeight: 600,
    color: colors.text,
    marginTop: '0.1rem',
  },
  badge: {
    display: 'inline-block',
    padding: '0.15rem 0.6rem',
    borderRadius: '20px',
    fontSize: '0.65rem',
    fontWeight: 500,
    background: colors.primaryMid,
    color: 'white',
    letterSpacing: '0.04em',
  },
  progressSection: {
    marginTop: '1rem',
    paddingTop: '1rem',
    borderTop: `1px solid ${colors.border}`,
  },
  progressRow: {
    display: 'flex',
    justifyContent: 'space-between',
    fontSize: '0.8rem',
    color: colors.textMuted,
  },
  progressValue: {
    fontWeight: 600,
    color: colors.text,
  },
  progressBar: {
    height: '6px',
    background: colors.border,
    borderRadius: '999px',
    marginTop: '0.5rem',
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    background: colors.primaryMid,
    borderRadius: '999px',
    transition: 'width 0.3s ease',
  },
  detailList: {
    marginTop: '1rem',
    paddingLeft: '1.2rem',
    lineHeight: 2,
    fontSize: '0.85rem',
    color: colors.textMuted,
  },
  detailItem: {
    marginBottom: '0.2rem',
  },
  detailStrong: {
    fontWeight: 500,
    color: colors.text,
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
  error: {
    background: 'rgba(185, 28, 28, 0.04)',
    color: colors.error,
    padding: '0.9rem 1.2rem',
    borderRadius: '10px',
    margin: '0 0 1rem',
    border: '1px solid rgba(185, 28, 28, 0.08)',
    fontSize: '0.85rem',
  },

  '@media (max-width: 1024px)': {
    mainGrid: {
      gridTemplateColumns: '1fr',
    },
    sidebar: {
      position: 'static',
    },
  },
  '@media (max-width: 768px)': {
    heroCard: {
      padding: '1.5rem',
      margin: '0.5rem 0.8rem 1rem',
      borderRadius: '16px',
      gridTemplateColumns: '1fr',
      gap: '1rem',
    },
    heroTitle: {
      fontSize: '1.4rem',
    },
    heroImage: {
      height: '120px',
    },
    mainGrid: {
      padding: '0 0.8rem 1rem',
      gap: '1.5rem',
    },
    gridCards: {
      gridTemplateColumns: '1fr',
      gap: '1rem',
    },
    bottomTab: {
      display: 'flex',
    },
    container: {
      paddingBottom: '70px',
    },
    statsGrid: {
      gridTemplateColumns: '1fr 1fr',
    },
    heroActions: {
      flexDirection: 'column',
    },
    btnPrimary: {
      width: '100%',
      textAlign: 'center',
    },
    btnOutline: {
      width: '100%',
      textAlign: 'center',
    },
  },
};

export default function ExportPage() {
  const navigate = useNavigate();
  const { trip } = useTrip();

  const downloadPdf = async () => {
    if (!trip.tripId) return;
    const token = localStorage.getItem('access_token');
    const url = itineraryApi.pdfUrl(trip.tripId);
    const res = await fetch(url, { headers: { Authorization: `Bearer ${token}` } });
    if (!res.ok) {
      let message = 'PDF export failed. Please try again.';
      try {
        const data = await res.json();
        message = data.error || message;
      } catch {
        /* ignore */
      }
      window.alert(message);
      return;
    }
    const blob = await res.blob();
    const header = await blob.slice(0, 4).text();
    if (!header.startsWith('%PDF')) {
      window.alert('PDF export failed — server did not return a valid PDF.');
      return;
    }
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `itinerary-${trip.tripId?.slice(0, 8)}.pdf`;
    link.click();
  };

  return (
    <div className="export-page" style={styles.container}>
      <style>{`
        @keyframes fadeRise { from { opacity:0; transform:translateY(12px);} to { opacity:1; transform:translateY(0);} }
        * { box-sizing: border-box; }
        body { margin: 0; background: ${colors.background}; }
        button { cursor: pointer; }
        button:disabled { cursor: not-allowed; }
        .btn-primary:hover {
          background: ${colors.primaryLight};
          transform: translateY(-2px);
          box-shadow: 0 8px 24px rgba(30, 110, 111, 0.15);
        }
        .btn-outline:hover {
          background: rgba(255,255,255,0.05);
          border-color: rgba(255,255,255,0.3);
        }
        .card-btn:hover {
          background: ${colors.primary};
          color: white;
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(30, 110, 111, 0.12);
        }
        .card-hover:hover {
          transform: translateY(-3px);
          box-shadow: 0 16px 40px rgba(30, 110, 111, 0.06), 0 4px 16px rgba(0, 0, 0, 0.02);
          border-color: ${colors.primary};
        }
        @media (max-width: 1024px) {
          .export-page .export-grid {
            grid-template-columns: 1fr !important;
          }
          .export-page .export-sidebar {
            position: static !important;
          }
        }
        @media (max-width: 768px) {
          .export-page .export-hero {
            padding: 1.35rem 1.2rem !important;
            margin: 0.5rem 0 1rem !important;
            border-radius: 14px !important;
            grid-template-columns: 1fr !important;
            gap: 1rem !important;
          }
          .export-page .export-hero h1 {
            font-size: 1.35rem !important;
          }
          .export-page .export-hero-image {
            height: 120px !important;
          }
          .export-page .export-hero-actions {
            flex-direction: column !important;
          }
          .export-page .export-hero-actions button {
            width: 100%;
            text-align: center;
            justify-content: center;
          }
          .export-page .export-grid {
            padding: 0 0 1rem !important;
            gap: 1.25rem !important;
          }
          .export-page .export-cards {
            grid-template-columns: 1fr !important;
            gap: 0.9rem !important;
          }
          .export-page .export-stats {
            grid-template-columns: 1fr 1fr !important;
          }
          .card-hover:hover {
            transform: translateY(-2px);
          }
        }
        @media (max-width: 480px) {
          .export-page .export-stats {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>

      <div className="export-hero" style={styles.heroCard}>
        <div style={styles.heroBg} />
        <div style={styles.heroContent}>
          <h1 style={styles.heroTitle}>Your Sri Lankan Adventure is Ready</h1>
          <p style={styles.heroText}>Download your master itinerary or share with co-travelers.</p>
          <div className="export-hero-actions" style={styles.heroActions}>
            <button
              className="btn-primary"
              style={styles.btnPrimary}
              onClick={downloadPdf}
              disabled={!trip.tripId}
            >
              Download PDF Itinerary
            </button>
            <button className="btn-outline" style={styles.btnOutline}>
              Share with Travelers
            </button>
          </div>
        </div>
        <div className="export-hero-image" style={styles.heroImage} />
      </div>

      {!trip.tripId && (
        <div style={styles.error}>
          Complete your trip plan first, then export your itinerary.
          <div style={{ marginTop: 12 }}>
            <button style={styles.btnPrimary} onClick={() => navigate('/attractions')}>
              Go to Attractions
            </button>
          </div>
        </div>
      )}

      <div className="export-grid" style={styles.mainGrid}>
        <div>
          <div style={styles.sectionHeader}>
            <h2 style={styles.sectionTitle}>Your Master Itinerary</h2>
          </div>
          <div className="export-cards" style={styles.gridCards}>
            <div className="card-hover" style={styles.card}>
              <h3 style={styles.cardTitle}>Standard PDF</h3>
              <p style={styles.cardText}>Full day-by-day schedule with highlights and tips.</p>
              <button className="card-btn" style={styles.cardBtn} onClick={downloadPdf}>
                Download
              </button>
            </div>
            <div className="card-hover" style={styles.card}>
              <h3 style={styles.cardTitle}>Digital Summary</h3>
              <p style={styles.cardText}>Review your completed plan in the app.</p>
              <button className="card-btn" style={styles.cardBtn} onClick={() => navigate('/itinerary')}>
                View Itinerary
              </button>
            </div>
          </div>
        </div>

        <div className="export-sidebar" style={styles.sidebar}>
          <div style={styles.sidebarCard}>
            <h3 style={styles.sidebarTitle}>Trip Overview</h3>
            <div className="export-stats" style={styles.statsGrid}>
              <div style={styles.statCard}>
                <div style={styles.statLabel}>Duration</div>
                <div style={styles.statValue}>{trip.days || 0} Days</div>
              </div>
              <div style={styles.statCard}>
                <div style={styles.statLabel}>Budget</div>
                <div style={styles.statValue}>${trip.budget || 0}</div>
              </div>
              <div style={styles.statCard}>
                <div style={styles.statLabel}>Places</div>
                <div style={styles.statValue}>{trip.selectedAttractionIds?.length || 0}</div>
              </div>
              <div style={styles.statCard}>
                <div style={styles.statLabel}>Status</div>
                <div style={{ marginTop: '0.1rem' }}>
                  <span style={styles.badge}>Ready to Export</span>
                </div>
              </div>
            </div>

            <div style={styles.progressSection}>
              <div style={styles.progressRow}>
                <span>Workflow Progress</span>
                <span style={styles.progressValue}>100%</span>
              </div>
              <div style={styles.progressBar}>
                <div style={{ ...styles.progressFill, width: '100%' }} />
              </div>
            </div>

            <ul style={styles.detailList}>
              <li style={styles.detailItem}>
                Attractions Selected (<span style={styles.detailStrong}>{trip.selectedAttractionIds?.length || 0}</span>)
              </li>
              <li style={styles.detailItem}>
                Budget Allocated (<span style={styles.detailStrong}>${trip.budget || 0}</span>)
              </li>
              <li style={styles.detailItem}>
                Accommodation:{' '}
                <span style={styles.detailStrong}>
                  {(trip.accommodations || []).map((a) => `${a.destination}: ${a.name}`).join(' · ') || 
                   trip.accommodation || '—'}
                </span>
              </li>
              <li style={styles.detailItem}>
                Saved References (<span style={styles.detailStrong}>{trip.savedReferences?.length || 0}</span>)
              </li>
            </ul>
          </div>
        </div>
      </div>

      <div style={styles.bottomTab}>
        <button style={{ ...styles.bottomTabItem, ...styles.bottomTabActive }}>
          <span style={styles.bottomTabIcon}>◆</span>
          Export
        </button>
        <button style={styles.bottomTabItem}>
          <span style={styles.bottomTabIcon}>◇</span>
          Map
        </button>
        <button style={styles.bottomTabItem}>
          <span style={styles.bottomTabIcon}>◈</span>
          Itinerary
        </button>
        <button style={styles.bottomTabItem}>
          <span style={styles.bottomTabIcon}>○</span>
          Profile
        </button>
      </div>
    </div>
  );
}