"""Turn Google Image Search links / place names into direct image URLs."""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.parse
import urllib.request
from functools import lru_cache

DIRECT_IMAGE_RE = re.compile(r"\.(jpe?g|png|webp|gif)(\?|$)", re.I)
GOOGLE_HOSTS = ("google.com", "google.lk")
USER_AGENT = "TourCeylon/1.0 (education project; contact: local-dev)"


def is_direct_image_url(url: str) -> bool:
    return bool(DIRECT_IMAGE_RE.search(url.split("#")[0]))


def extract_google_search_query(url: str) -> str | None:
    try:
        parsed = urllib.parse.urlparse(url.strip())
    except Exception:
        return None
    if not any(host in (parsed.netloc or "") for host in GOOGLE_HOSTS):
        return None
    if "/search" not in parsed.path:
        return None
    query = urllib.parse.parse_qs(parsed.query).get("q", [None])[0]
    return urllib.parse.unquote(query) if query else None


def _query_variants(query: str) -> list[str]:
    variants: list[str] = []
    current = query.strip()
    if not current:
        return variants
    variants.append(current)
    if " or " in current.lower():
        variants.extend(p.strip() for p in re.split(r"\s+or\s+", current, flags=re.I) if p.strip())
    for suffix in (" Sri Lanka", " Sri Lanka accommodation", " National Park", " Beach"):
        if current.lower().endswith(suffix.lower()):
            stripped = current[: -len(suffix)].strip()
            if stripped:
                variants.append(stripped)
    # Drop leading filler words like "Whale Watching in Mirissa" -> also try "Mirissa"
    parts = re.split(r"\s+in\s+", current, flags=re.I)
    if len(parts) > 1 and parts[-1].strip():
        variants.append(parts[-1].strip())
    if "Sri Lanka" not in current:
        variants.append(f"{current} Sri Lanka")
    deduped: list[str] = []
    seen: set[str] = set()
    for item in variants:
        key = item.lower()
        if key not in seen:
            seen.add(key)
            deduped.append(item)
    return deduped


def _fetch_json(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode())


@lru_cache(maxsize=1024)
def _wikipedia_thumb(search_query: str) -> str | None:
    params = urllib.parse.urlencode(
        {
            "action": "opensearch",
            "search": search_query,
            "limit": 1,
            "namespace": 0,
            "format": "json",
        }
    )
    try:
        data = _fetch_json(f"https://en.wikipedia.org/w/api.php?{params}")
    except Exception:
        return None
    titles = data[1] if isinstance(data, list) and len(data) > 1 else []
    if not titles:
        return None
    slug = urllib.parse.quote(titles[0].replace(" ", "_"), safe="")
    try:
        summary = _fetch_json(f"https://en.wikipedia.org/api/rest_v1/page/summary/{slug}")
    except Exception:
        return None
    thumb = summary.get("thumbnail") or {}
    return thumb.get("source")


@lru_cache(maxsize=1024)
def _wikimedia_thumb(search_query: str) -> str | None:
    params = urllib.parse.urlencode(
        {
            "action": "query",
            "generator": "search",
            "gsrsearch": search_query,
            "gsrnamespace": "6",
            "gsrlimit": "1",
            "prop": "imageinfo",
            "iiprop": "url",
            "iiurlwidth": "800",
            "format": "json",
        }
    )
    try:
        data = _fetch_json(f"https://commons.wikimedia.org/w/api.php?{params}")
    except Exception:
        return None
    pages = data.get("query", {}).get("pages", {})
    for page in pages.values():
        info = page.get("imageinfo") or []
        if info:
            return info[0].get("thumburl") or info[0].get("url")
    return None


@lru_cache(maxsize=1024)
def _openverse_thumb(search_query: str) -> str | None:
    params = urllib.parse.urlencode(
        {
            "q": search_query,
            "page_size": 1,
            "mature": "false",
        }
    )
    try:
        data = _fetch_json(f"https://api.openverse.org/v1/images/?{params}")
    except Exception:
        return None
    results = data.get("results") or []
    if not results:
        return None
    item = results[0]
    # Prefer the original CDN file URL for reliable <img> display
    return item.get("url") or item.get("thumbnail")


def resolve_image_url(raw: str | None, fallback_query: str | None = None) -> str | None:
    queries: list[str] = []
    if raw is not None:
        url = str(raw).strip()
        if url and url.lower() not in ("nan", "none", "#value!"):
            if is_direct_image_url(url):
                return url
            google_q = extract_google_search_query(url)
            if google_q:
                queries.extend(_query_variants(google_q))
            elif url.startswith("http") and not extract_google_search_query(url):
                # Non-google http(s) page URL — not usable as img src
                pass

    if fallback_query:
        queries.extend(_query_variants(str(fallback_query).strip()))

    seen: set[str] = set()
    for query in queries:
        key = query.lower()
        if not query or key in seen:
            continue
        seen.add(key)
        for fetcher in (_wikipedia_thumb, _openverse_thumb, _wikimedia_thumb):
            result = fetcher(query)
            if result and str(result).startswith("http"):
                return result
    return None


def display_image_url(raw: str | None, fallback_query: str | None = None) -> str | None:
    return resolve_image_url(raw, fallback_query)
