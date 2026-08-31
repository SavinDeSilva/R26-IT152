import { createContext, useCallback, useContext, useMemo, useState } from 'react';

const TripContext = createContext(null);
const STORAGE_KEY = 'tc_trip_draft';

const initialState = {
  tripId: null,
  selectedMoods: [],
  days: 7,
  attractions: [],
  selectedAttractionIds: [],
  budget: 2500,
  budgetSplit: null,
  roomType: 'double_hb',
  accommodation: null,
  accommodations: [],
  accommodationOptions: [],
  itinerary: null,
  preferredDayStart: '',
  savedReferences: [],
  pendingSavedReferences: [],
  remainingBudget: null,
  landmarkSearch: '',
};

const PERSIST_KEYS = [
  'tripId',
  'selectedMoods',
  'days',
  'selectedAttractionIds',
  'budget',
  'budgetSplit',
  'roomType',
  'accommodation',
  'accommodations',
  'preferredDayStart',
];

function loadPersistedTrip() {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    if (!raw) return initialState;
    const parsed = JSON.parse(raw);
    const next = { ...initialState };
    PERSIST_KEYS.forEach((key) => {
      if (parsed[key] !== undefined) next[key] = parsed[key];
    });
    return next;
  } catch {
    return initialState;
  }
}

function persistTrip(trip) {
  try {
    const slim = {};
    PERSIST_KEYS.forEach((key) => {
      slim[key] = trip[key];
    });
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(slim));
  } catch {
    /* private mode / quota */
  }
}

export function TripProvider({ children }) {
  const [trip, setTrip] = useState(loadPersistedTrip);

  const updateTrip = useCallback((patch) => {
    setTrip((prev) => {
      const next = { ...prev, ...patch };
      persistTrip(next);
      return next;
    });
  }, []);

  const resetTrip = useCallback(() => {
    try {
      sessionStorage.removeItem(STORAGE_KEY);
    } catch {
      /* ignore */
    }
    setTrip(initialState);
  }, []);

  const value = useMemo(
    () => ({ trip, updateTrip, resetTrip }),
    [trip, updateTrip, resetTrip]
  );
  return <TripContext.Provider value={value}>{children}</TripContext.Provider>;
}

export function useTrip() {
  return useContext(TripContext);
}
