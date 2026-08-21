import { createContext, useCallback, useContext, useMemo, useState } from 'react';

const TripContext = createContext(null);

const initialState = {
  tripId: null,
  selectedMoods: [],
  days: 7,
  attractions: [],
  selectedAttractionIds: [],
  budget: 2500,
  budgetSplit: null,
  roomType: 'double',
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

export function TripProvider({ children }) {
  const [trip, setTrip] = useState(initialState);

  const updateTrip = useCallback((patch) => {
    setTrip((prev) => ({ ...prev, ...patch }));
  }, []);

  const resetTrip = useCallback(() => {
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
