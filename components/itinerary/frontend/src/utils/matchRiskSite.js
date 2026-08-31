const GENERIC_TOKENS = new Set([
  'park', 'national', 'beach', 'temple', 'rock', 'fort', 'city', 'museum',
  'waterfall', 'falls', 'ella', 'forest', 'reserve', 'botanical', 'garden',
  'gardens', 'lagoon', 'island', 'south', 'north', 'east', 'west', 'sri',
  'lanka', 'ancient', 'sacred', 'blow', 'hole', 'spot', 'surf', 'point',
  'the', 'and', 'of',
]);

const SITE_ALIASES = [
  [/sigiriya/i, 'Sigiriya Rock Fortress'],
  [/pidurangala/i, 'Pidurangala Rock'],
  [/nine\s*arch/i, 'Nine Arch Bridge'],
  [/lipton/i, "Lipton's Seat"],
  [/\b(tooth|dalada maligawa|sri dalada)\b/i, 'Temple of the Tooth Kandy'],
  [/arugam/i, 'Arugam Bay'],
  [/minneriya/i, 'Minneriya National Park'],
  [/ritigala/i, 'Ritigala Forest Monastery'],
  [/ambuluwawa/i, 'Ambuluwawa Tower'],
  [/knuckles/i, 'Knuckles Mountain Range'],
  [/peradeniya/i, 'Peradeniya Botanical Gardens'],
  [/lotus\s*tower/i, 'Colombo Lotus Tower'],
  [/polonnaruwa/i, 'Polonnaruwa Ancient City'],
  [/anuradhapura/i, 'Anuradhapura Sacred City'],
  [/nuwara\s*eliya/i, 'Nuwara Eliya'],
  [/trincomalee|trinco\b/i, 'Trincomalee'],
  [/adams?\s*peak|sri\s*pada|sripada/i, 'Adams Peak Sri Pada'],
];

function normalize(value) {
  return String(value || '')
    .toLowerCase()
    .replace(/&/g, ' and ')
    .replace(/[^a-z0-9]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

function distinctiveTokens(value) {
  return normalize(value).split(' ').filter((token) => token.length > 2 && !GENERIC_TOKENS.has(token));
}

function scoreName(attractionName, siteName) {
  const attraction = normalize(attractionName);
  const site = normalize(siteName);
  if (!attraction || !site) return 0;
  if (attraction === site) return 100;
  if (attraction.includes(site) || site.includes(attraction)) {
    if (Math.min(attraction.length, site.length) >= 6) return 82;
  }

  const attractionTokens = distinctiveTokens(attractionName);
  const siteTokens = distinctiveTokens(siteName);
  if (!attractionTokens.length || !siteTokens.length) return 0;

  const attractionSet = new Set(attractionTokens);
  const siteSet = new Set(siteTokens);
  const overlap = siteTokens.filter((token) => attractionSet.has(token));
  if (!overlap.length) return 0;

  const siteCovered = siteTokens.every((token) => attractionSet.has(token));
  const attractionCovered = attractionTokens.every((token) => siteSet.has(token));
  if (siteCovered || attractionCovered) return 88;
  return (overlap.length / Math.max(attractionSet.size, siteSet.size)) * 70;
}

function siteByName(sites, name) {
  const key = normalize(name);
  return sites.find((site) => normalize(site.site_name) === key) || null;
}

export function matchAttractionToSite(attraction, sites) {
  if (!attraction || !sites?.length) return null;
  const name = attraction.attraction_name || '';

  for (const [pattern, siteName] of SITE_ALIASES) {
    if (pattern.test(name)) {
      const aliased = siteByName(sites, siteName);
      if (aliased) return aliased;
    }
  }

  let best = null;
  let bestScore = 0;
  for (const site of sites) {
    const score = scoreName(name, site.site_name);
    if (score > bestScore) {
      bestScore = score;
      best = site;
    }
  }
  return bestScore >= 70 ? best : null;
}

export function buildAttractionSiteMap(attractions, sites) {
  const map = new Map();
  for (const attraction of attractions || []) {
    const site = matchAttractionToSite(attraction, sites);
    if (site) map.set(Number(attraction.id), site.site_id);
  }
  return map;
}

export function mapCheckRowsToAttractions(attractions, siteMap, rows) {
  const bySite = new Map((rows || []).map((row) => [Number(row.site_id), row]));
  const next = {};
  for (const item of attractions || []) {
    const siteId = siteMap.get(Number(item.id));
    const row = siteId != null ? bySite.get(Number(siteId)) : null;
    if (row) next[Number(item.id)] = row;
  }
  return next;
}
