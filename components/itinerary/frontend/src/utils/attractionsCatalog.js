const CACHE_KEY = 'tc_attractions_catalog_v1';

export function readAttractionsCatalogCache() {
  try {
    const raw = sessionStorage.getItem(CACHE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed?.attractions) ? parsed.attractions : [];
  } catch {
    return [];
  }
}

export function writeAttractionsCatalogCache(attractions) {
  try {
    sessionStorage.setItem(
      CACHE_KEY,
      JSON.stringify({ attractions, savedAt: Date.now() })
    );
  } catch {
    /* ignore quota errors */
  }
}

export function seedAttractionsCatalog(tripAttractions) {
  if (Array.isArray(tripAttractions) && tripAttractions.length) return tripAttractions;
  return readAttractionsCatalogCache();
}
