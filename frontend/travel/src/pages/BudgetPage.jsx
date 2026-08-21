import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';
import { budgetApi } from '../api/client';
import { useTrip } from '../context/TripContext';

const DEFAULTS = { food_pct: 25, accommodation_pct: 35, shopping_pct: 15, transport_pct: 25 };

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

const CHART_COLORS = ['#4EC6D4', '#7AC7BD', '#1E6E6F', '#F2D9B7'];

const fontBody = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif";

// Professional design system
const styles = {
  container: {
    background: colors.background,
    fontFamily: fontBody,
    color: colors.text,
    padding: '0',
    width: '100%',
    maxWidth: '1400px',
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
    minHeight: '200px',
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
    backgroundImage: 'url("https://images.unsplash.com/photo-1559827260-dc66d52bef19?w=1400&q=80")',
    backgroundSize: 'cover',
    backgroundPosition: 'center',
    opacity: 0.12,
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
    lineHeight: 1.5,
  },

  mainGrid: {
    display: 'grid',
    gap: '2rem',
    padding: '0 0 2rem',
    width: '100%',
  },

  budgetCard: {
    background: 'white',
    borderRadius: '16px',
    padding: '1.5rem',
    boxShadow: '0 2px 12px rgba(0, 0, 0, 0.03)',
    border: `1px solid ${colors.border}`,
    marginBottom: '1.5rem',
  },
  budgetLabel: {
    fontWeight: 600,
    fontSize: '0.9rem',
    color: colors.text,
    marginBottom: '0.75rem',
  },
  budgetInputGroup: {
    display: 'flex',
    gap: '0.75rem',
    alignItems: 'center',
  },
  budgetSelect: {
    padding: '0.6rem 1rem',
    borderRadius: '10px',
    border: `1px solid ${colors.border}`,
    fontSize: '0.85rem',
    background: 'white',
    fontFamily: 'inherit',
    color: colors.text,
    outline: 'none',
    transition: 'border-color 0.2s ease',
  },
  budgetInput: {
    flex: 1,
    padding: '0.6rem 1rem',
    borderRadius: '10px',
    border: `1px solid ${colors.border}`,
    fontSize: '0.85rem',
    fontFamily: 'inherit',
    outline: 'none',
    transition: 'border-color 0.2s ease',
    background: 'white',
    color: colors.text,
  },

  categoryHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '1rem',
  },
  categoryTitle: {
    fontWeight: 600,
    fontSize: '0.95rem',
    color: colors.text,
  },
  toggleLabel: {
    display: 'flex',
    gap: '0.5rem',
    alignItems: 'center',
    fontSize: '0.8rem',
    color: colors.textMuted,
    cursor: 'pointer',
  },
  toggleCheckbox: {
    width: '18px',
    height: '18px',
    borderRadius: '5px',
    border: `2px solid ${colors.border}`,
    appearance: 'none',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
  },
  toggleCheckboxChecked: {
    background: colors.primary,
    borderColor: colors.primary,
  },

  categoryItem: {
    background: 'white',
    borderRadius: '14px',
    padding: '1rem 1.2rem 0.8rem',
    marginBottom: '0.75rem',
    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.02)',
    border: `1px solid ${colors.border}`,
    transition: 'all 0.2s ease',
  },
  categoryHeaderRow: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: '0.4rem',
  },
  categoryInfo: {
    display: 'flex',
    gap: '0.75rem',
    alignItems: 'flex-start',
  },
  categoryLabel: {
    fontWeight: 600,
    fontSize: '0.9rem',
    color: colors.text,
  },
  categoryDesc: {
    fontSize: '0.75rem',
    color: colors.textMuted,
    marginTop: '0.05rem',
  },
  categoryAmounts: {
    textAlign: 'right',
    flexShrink: 0,
  },
  categoryPercent: {
    fontSize: '1rem',
    fontWeight: 600,
    color: colors.text,
  },
  categoryDollar: {
    fontSize: '0.85rem',
    fontWeight: 500,
    color: colors.primary,
  },
  categorySlider: {
    width: '100%',
    marginTop: '0.5rem',
    height: '4px',
    borderRadius: '4px',
    background: colors.border,
    outline: 'none',
    transition: 'background 0.2s ease',
  },

  error: {
    background: 'rgba(185, 28, 28, 0.04)',
    color: colors.error,
    padding: '0.7rem 1.5rem',
    borderRadius: '14px',
    marginTop: '0.75rem',
    border: '1px solid rgba(185, 28, 28, 0.06)',
    fontWeight: 500,
    fontSize: '0.8rem',
  },

  sidebar: {
    alignSelf: 'start',
    width: '100%',
  },
  sidebarCard: {
    background: colors.glass,
    borderRadius: '10px',
    padding: '1.5rem',
    border: `1px solid ${colors.border}`,
    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.02)',
  },
  sidebarTitle: {
    fontSize: '1rem',
    fontWeight: 600,
    fontFamily: fontBody,
    margin: '0 0 0.5rem 0',
    color: colors.text,
  },
  chartContainer: {
    height: '180px',
    marginTop: '0.5rem',
  },
  chartLegend: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: '0.3rem 0.75rem',
    marginTop: '0.75rem',
  },
  legendItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.4rem',
    fontSize: '0.7rem',
    color: colors.textMuted,
  },
  legendDot: {
    width: '10px',
    height: '10px',
    borderRadius: '50%',
    flexShrink: 0,
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
    height: '5px',
    background: colors.border,
    borderRadius: '8px',
    marginTop: '0.5rem',
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    background: colors.primary,
    borderRadius: '8px',
    transition: 'width 0.3s ease',
  },
  dailyEstimate: {
    marginTop: '1rem',
    padding: '0.75rem',
    background: 'rgba(78, 198, 212, 0.03)',
    borderRadius: '12px',
    textAlign: 'center',
    fontSize: '0.85rem',
    color: colors.textMuted,
    border: `1px solid ${colors.border}`,
  },
  dailyEstimateStrong: {
    fontWeight: 600,
    color: colors.primary,
    fontSize: '1rem',
  },
  sidebarButton: {
    width: '100%',
    background: colors.primary,
    border: 'none',
    borderRadius: '8px',
    padding: '0.7rem',
    color: 'white',
    fontWeight: 600,
    fontSize: '0.85rem',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    fontFamily: 'inherit',
    letterSpacing: '0.01em',
    marginTop: '1rem',
  },
  sidebarButtonDisabled: {
    opacity: 0.3,
    cursor: 'not-allowed',
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

  '@media (max-width: 1024px)': {
    mainGrid: {
      gridTemplateColumns: '1fr',
    },
    sidebar: {
      position: 'static',
    },
  },
  '@media (max-width: 768px)': {
    hero: {
      padding: '1.5rem',
      minHeight: '150px',
      margin: '0.5rem 0.8rem 1rem',
      borderRadius: '16px',
    },
    heroTitle: {
      fontSize: '1.4rem',
    },
    heroSubtitle: {
      fontSize: '0.8rem',
    },
    mainGrid: {
      padding: '0 0.8rem 1rem',
      gap: '1.5rem',
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
    sidebarCard: {
      padding: '1rem',
    },
    budgetInputGroup: {
      flexDirection: 'column',
      alignItems: 'stretch',
    },
    categoryHeaderRow: {
      flexDirection: 'column',
      gap: '0.5rem',
    },
    categoryAmounts: {
      textAlign: 'left',
      width: '100%',
    },
    chartLegend: {
      gridTemplateColumns: '1fr',
    },
  },
};

export default function BudgetPage() {
  const navigate = useNavigate();
  const { trip, updateTrip } = useTrip();
  const [budget, setBudget] = useState(trip.budget || 2500);
  const [customize, setCustomize] = useState(false);
  const [percentages, setPercentages] = useState(DEFAULTS);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  // Stay on this page when opened from the sidebar; actions still need a saved trip.

  const totalPct = Object.values(percentages).reduce((a, b) => a + Number(b), 0);
  const amounts = useMemo(() => ({
    food: (budget * percentages.food_pct) / 100,
    accommodation: (budget * percentages.accommodation_pct) / 100,
    shopping: (budget * percentages.shopping_pct) / 100,
    transport: (budget * percentages.transport_pct) / 100,
  }), [budget, percentages]);

  const chartData = [
    { name: 'Food', value: percentages.food_pct },
    { name: 'Accommodation', value: percentages.accommodation_pct },
    { name: 'Shopping', value: percentages.shopping_pct },
    { name: 'Transport', value: percentages.transport_pct },
  ];

  const setPct = (key, value) => setPercentages((p) => ({ ...p, [key]: Number(value) }));

  const confirm = async () => {
    setError('');
    if (!trip.tripId) {
      setError('Confirm attractions first to create a trip, then allocate your budget.');
      return;
    }
    if (Math.round(totalPct) !== 100) {
      setError('Percentages must sum to 100%');
      return;
    }
    setLoading(true);
    try {
      const payload = {
        trip_id: trip.tripId,
        budget,
        customize,
        ...(customize ? percentages : {}),
      };
      const { data } = await budgetApi.split(payload);
      updateTrip({ budget, budgetSplit: data.split });
      navigate('/accommodation');
    } catch (e) {
      setError(e.response?.data?.error || 'Failed to save budget');
    } finally {
      setLoading(false);
    }
  };

  const sliders = [
    { key: 'food_pct', label: 'Food & Dining', desc: 'Authentic rice & curry, street food, fine dining.' },
    { key: 'accommodation_pct', label: 'Accommodation', desc: 'Boutique villas, eco-lodges, colonial retreats.' },
    { key: 'shopping_pct', label: 'Shopping', desc: 'Spices, tea, textiles, artisan crafts.' },
    { key: 'transport_pct', label: 'Internal Travel', desc: 'Drivers, scenic trains, coastal transfers.' },
  ];

  return (
    <div className="budget-page" style={styles.container}>
      <style>{`
        @keyframes fadeRise { from { opacity:0; transform:translateY(12px);} to { opacity:1; transform:translateY(0);} }
        * { box-sizing: border-box; }
        body { margin: 0; background: ${colors.background}; }
        button { cursor: pointer; }
        button:disabled { cursor: not-allowed; }
        .card-hover:hover { transform: translateY(-3px); }
        .budget-input:focus, .budget-select:focus {
          border-color: ${colors.primary};
          box-shadow: 0 0 0 2px rgba(78, 198, 212, 0.06);
        }
        .slider-input::-webkit-slider-thumb {
          -webkit-appearance: none;
          appearance: none;
          width: 16px;
          height: 16px;
          border-radius: 50%;
          background: ${colors.primary};
          cursor: pointer;
          box-shadow: 0 2px 8px rgba(78, 198, 212, 0.15);
        }
        .slider-input::-moz-range-thumb {
          width: 16px;
          height: 16px;
          border-radius: 50%;
          background: ${colors.primary};
          cursor: pointer;
          border: none;
          box-shadow: 0 2px 8px rgba(78, 198, 212, 0.15);
        }
        @media (max-width: 1024px) {
          .budget-page .budget-grid {
            grid-template-columns: 1fr !important;
          }
          .budget-page .budget-sidebar {
            position: static !important;
          }
          .budget-page .budget-hero {
            margin-left: 0 !important;
            margin-right: 0 !important;
          }
          .budget-page .budget-grid {
            padding-left: 0 !important;
            padding-right: 0 !important;
          }
        }
        @media (max-width: 768px) {
          .budget-page .budget-hero {
            padding: 1.35rem 1.2rem !important;
            min-height: 0 !important;
            margin: 0.5rem 0 1rem !important;
            border-radius: 14px !important;
          }
          .budget-page .budget-hero h1 {
            font-size: 1.35rem !important;
          }
          .budget-page .budget-hero p {
            font-size: 0.84rem !important;
          }
          .budget-page .budget-grid {
            padding: 0 0 1rem !important;
            gap: 1.25rem !important;
          }
          .budget-page .budget-input-group {
            flex-direction: column !important;
            align-items: stretch !important;
          }
          .budget-page .budget-category-row {
            flex-direction: column !important;
            gap: 0.5rem !important;
          }
          .budget-page .budget-category-amounts {
            text-align: left !important;
            width: 100% !important;
          }
          .budget-page .budget-legend {
            grid-template-columns: 1fr !important;
          }
          .budget-page .budget-sidebar-card {
            padding: 1rem !important;
          }
          .slider-input::-webkit-slider-thumb {
            width: 20px;
            height: 20px;
          }
        }
      `}</style>

      <section className="budget-hero" style={styles.hero}>
        <div style={styles.heroBg} />
        <div style={styles.heroContent}>
          <span style={styles.heroBadge}>Financial Planning</span>
          <h1 style={styles.heroTitle}>Budget Allocation</h1>
          <p style={styles.heroSubtitle}>Distribute your travel funds across key categories for the perfect Sri Lankan adventure.</p>
        </div>
      </section>

      {!trip.tripId && (
        <div style={styles.error}>
          Confirm attractions first to create a trip, then return here to split your budget.
          <div style={{ marginTop: 12 }}>
            <button style={styles.sidebarButton} onClick={() => navigate('/attractions')}>
              Go to Attractions
            </button>
          </div>
        </div>
      )}

      <div className="budget-grid" style={styles.mainGrid}>
        <div>
          <div style={styles.budgetCard}>
            <div style={styles.budgetLabel}>Total Trip Budget</div>
            <div className="budget-input-group" style={styles.budgetInputGroup}>
              <select style={styles.budgetSelect} className="budget-select">
                <option>USD</option>
              </select>
              <input
                type="number"
                value={budget}
                onChange={(e) => setBudget(Number(e.target.value))}
                style={styles.budgetInput}
                className="budget-input"
                placeholder="Enter your budget"
              />
            </div>
          </div>

          <div style={styles.categoryHeader}>
            <div style={styles.categoryTitle}>Category Split</div>
            <label style={styles.toggleLabel}>
              <input
                type="checkbox"
                checked={customize}
                onChange={(e) => setCustomize(e.target.checked)}
                style={{
                  ...styles.toggleCheckbox,
                  ...(customize ? styles.toggleCheckboxChecked : {}),
                }}
              />
              Manual Adjustment
            </label>
          </div>

          {sliders.map((s) => {
            const key = s.key;
            const pct = percentages[key];
            const amountKey = key.replace('_pct', '');
            return (
              <div key={key} style={styles.categoryItem}>
                <div className="budget-category-row" style={styles.categoryHeaderRow}>
                  <div style={styles.categoryInfo}>
                    <div>
                      <div style={styles.categoryLabel}>{s.label}</div>
                      <div style={styles.categoryDesc}>{s.desc}</div>
                    </div>
                  </div>
                  <div className="budget-category-amounts" style={styles.categoryAmounts}>
                    <div style={styles.categoryPercent}>{pct}%</div>
                    <div style={styles.categoryDollar}>${amounts[amountKey]?.toFixed(2)}</div>
                  </div>
                </div>
                {customize && (
                  <input
                    type="range"
                    min={0}
                    max={100}
                    value={pct}
                    onChange={(e) => setPct(key, e.target.value)}
                    style={styles.categorySlider}
                    className="slider-input"
                  />
                )}
              </div>
            );
          })}

          {error && <div style={styles.error}>{error}</div>}
        </div>

        <div className="budget-sidebar" style={styles.sidebar}>
          <div className="budget-sidebar-card" style={styles.sidebarCard}>
            <h3 style={styles.sidebarTitle}>Visual Breakdown</h3>
            <div style={styles.chartContainer}>
              <ResponsiveContainer>
                <PieChart>
                  <Pie
                    data={chartData}
                    dataKey="value"
                    innerRadius={55}
                    outerRadius={80}
                    paddingAngle={2}
                  >
                    {chartData.map((_, i) => (
                      <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
                    ))}
                  </Pie>
                </PieChart>
              </ResponsiveContainer>
            </div>

            <div className="budget-legend" style={styles.chartLegend}>
              {chartData.map((item, i) => (
                <div key={item.name} style={styles.legendItem}>
                  <span style={{ ...styles.legendDot, background: CHART_COLORS[i] }} />
                  <span>{item.name}</span>
                  <span style={{ marginLeft: 'auto', fontWeight: 500 }}>{item.value}%</span>
                </div>
              ))}
            </div>

            <div style={styles.progressSection}>
              <div style={styles.progressRow}>
                <span>Allocation Balance</span>
                <span style={{ ...styles.progressValue, color: totalPct === 100 ? colors.primary : colors.error }}>
                  {totalPct}% / 100%
                </span>
              </div>
              <div style={styles.progressBar}>
                <div
                  style={{
                    ...styles.progressFill,
                    width: `${Math.min(totalPct, 100)}%`,
                    background: totalPct === 100
                      ? colors.primary
                      : colors.primary,
                    opacity: totalPct === 100 ? 1 : 0.6,
                  }}
                />
              </div>
            </div>

            <div style={styles.dailyEstimate}>
              Daily Estimate: <strong style={styles.dailyEstimateStrong}>
                ${(budget / (trip.days || 1)).toFixed(0)}
              </strong> / day
            </div>

            <button
              style={{
                ...styles.sidebarButton,
                ...(loading ? styles.sidebarButtonDisabled : {}),
              }}
              disabled={loading}
              onClick={confirm}
            >
              {loading ? 'Saving...' : 'Confirm Allocation'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}