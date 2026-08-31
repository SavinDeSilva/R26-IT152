"""Translate attraction catalog fields for the tourist UI language."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache

from app.services.translate_service import translate_free

SITE_LANGS = frozenset({"en", "si", "ta", "ru", "de", "zh", "ja", "es", "fr", "ko", "ar"})
LIST_FIELDS = ("attraction_name", "destination")
DETAIL_FIELDS = ("attraction_name", "destination", "details")


def normalize_site_lang(value: str | None) -> str:
    code = (value or "en").strip().lower().split("-")[0][:16]
    return code if code in SITE_LANGS else "en"


@lru_cache(maxsize=8192)
def _translate_en_text(text: str, target_lang: str) -> str:
    if not text or target_lang == "en":
        return text or ""
    translated = translate_free(text, "en", target_lang)
    return translated if translated and translated.strip() else text


def _translate_unique_strings(strings: set[str], target_lang: str) -> dict[str, str]:
    if not strings or target_lang == "en":
        return {s: s for s in strings}
    mapping: dict[str, str] = {}
    workers = min(12, max(1, len(strings)))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(_translate_en_text, text, target_lang): text for text in strings}
        for future in as_completed(futures):
            source = futures[future]
            try:
                mapping[source] = future.result()
            except Exception:
                mapping[source] = source
    return mapping


def _apply_field_map(data: dict, field_map: dict[str, str], fields: tuple[str, ...]) -> dict:
    out = dict(data)
    for field in fields:
        raw = (out.get(field) or "").strip()
        if raw:
            out[field] = field_map.get(raw, raw)
    return out


def localize_attraction(data: dict, lang: str, *, include_details: bool = True) -> dict:
    """Translate one attraction record."""
    target = normalize_site_lang(lang)
    if target == "en":
        return data
    fields = DETAIL_FIELDS if include_details else LIST_FIELDS
    unique = {(data.get(field) or "").strip() for field in fields}
    unique.discard("")
    field_map = _translate_unique_strings(unique, target)
    return _apply_field_map(data, field_map, fields)


def localize_attraction_list(items: list[dict], lang: str, *, include_details: bool = False) -> list[dict]:
    """Batch-translate a list — dedupe strings and run lookups in parallel."""
    target = normalize_site_lang(lang)
    if target == "en" or not items:
        return items

    fields = DETAIL_FIELDS if include_details else LIST_FIELDS
    unique: set[str] = set()
    for item in items:
        for field in fields:
            value = (item.get(field) or "").strip()
            if value:
                unique.add(value)

    field_map = _translate_unique_strings(unique, target)
    return [_apply_field_map(item, field_map, fields) for item in items]
