"""PDF export — WeasyPrint when available, ReportLab fallback on Windows."""

from __future__ import annotations

import base64
import sys
from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape

from flask import current_app, render_template_string

from components.itinerary.backend.models.accommodation import Accommodation
from components.itinerary.backend.models.business_directory import BusinessDirectory
from components.itinerary.backend.models.saved_reference import SavedReference
from components.itinerary.backend.models.tourist_guide import TouristGuide
from components.itinerary.backend.models.travel_agency import TravelAgency
from components.itinerary.backend.models.user_trip_input import UserTripInput
from components.itinerary.backend.services.budget_service import accommodation_budget_per_night
from components.itinerary.backend.services.room_type_service import (
    enrich_accommodation,
    format_lkr_near,
    format_usd_near,
    normalize_room_type,
    room_type_label,
)

# ---------------------------------------------------------------------------
# Shared colours / typography
# ---------------------------------------------------------------------------
GREEN = "#1a7f4b"
INK = "#1a2332"
MUTED = "#5a6570"
LINE = "#d0dce0"
PANEL = "#f7faf9"

BRAND_NAME = "Tour Ceylon"
CONTACT_PHONE = "+94 11 243 7059"
CONTACT_MOBILE = "+94 77 123 4567"
CONTACT_EMAIL = "hello@tourceylon.lk"
CONTACT_ADDRESS = "Colombo, Sri Lanka"
CONTACT_HOURS = "09:00 AM — 05:00 PM"
LOGO_PATH = Path(__file__).resolve().parents[2] / "frontend" / "public" / "tour-ceylon-logo.png"


def _logo_file() -> Path | None:
    return LOGO_PATH if LOGO_PATH.is_file() else None


def _logo_data_uri() -> str:
    path = _logo_file()
    if not path:
        return ""
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def _contact_block() -> str:
    return (
        f"{CONTACT_PHONE} · {CONTACT_MOBILE}<br/>"
        f"{CONTACT_EMAIL} · {CONTACT_ADDRESS}<br/>"
        f"{CONTACT_HOURS}"
    )


PDF_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body { font-family: Helvetica, Arial, sans-serif; color: #1a2332; margin: 32px 40px; font-size: 10.5pt; line-height: 1.5; }
    .letterhead { display: flex; align-items: center; gap: 16px; margin-bottom: 18px; padding-bottom: 10px; border-bottom: 2px solid #1a7f4b; }
    .letterhead img { width: 64px; height: 64px; object-fit: contain; }
    .letterhead-name { font-size: 15pt; font-weight: 700; color: #1a7f4b; margin: 0 0 4px; }
    .letterhead-contact { color: #5a6570; font-size: 9pt; line-height: 1.45; }
    .cover-title { color: #1a7f4b; font-size: 20pt; font-weight: 700; margin: 8px 0 2px; letter-spacing: 0.04em; }
    .cover-sub { color: #1a7f4b; font-size: 13pt; font-weight: 700; margin: 0 0 18px; }
    h2 { color: #1a7f4b; font-size: 12pt; margin: 22px 0 8px; letter-spacing: 0.04em; text-transform: uppercase; }
    h3 { color: #1a7f4b; font-size: 11pt; margin: 16px 0 6px; }
    p { margin: 0 0 8px; }
    .note { color: #5a6570; font-size: 9pt; font-style: italic; margin-bottom: 16px; }
    .overnight { font-weight: 600; margin: 4px 0 14px; }
    .farewell { font-style: italic; margin: 18px 0; }
    .panel { background: #f7faf9; border: 1px solid #d0dce0; padding: 10px 14px; margin-bottom: 12px; }
    .row { display: flex; justify-content: space-between; padding: 4px 0; border-bottom: 1px solid #e8eeec; }
    .row:last-child { border-bottom: none; }
    .label { color: #5a6570; }
    .value { font-weight: 600; }
    .saved-item { margin: 0 0 10px; padding-bottom: 8px; border-bottom: 1px dashed #e0e6e4; }
    .saved-name { font-weight: 600; }
    .saved-meta { color: #5a6570; font-size: 9.5pt; margin-top: 2px; }
    ul { margin: 4px 0 10px 18px; padding: 0; }
    li { margin-bottom: 3px; }
  </style>
</head>
<body>
  <div class="letterhead">
    {% if logo_src %}<img src="{{ logo_src }}" alt="Tour Ceylon">{% endif %}
    <div>
      <p class="letterhead-name">{{ brand_name }}</p>
      <div class="letterhead-contact">{{ contact_html|safe }}</div>
    </div>
  </div>
  <div class="cover-title">{{ booklet.cover_title }}</div>
  <div class="cover-sub">{{ booklet.cover_subtitle }}</div>

  {% if booklet.program_summary %}
  <h2>Program Summary</h2>
  {% for line in booklet.program_summary %}<p>{{ line }}</p>{% endfor %}
  {% endif %}

  {% if booklet.program_days %}
  <h2>Program in Details</h2>
  {% for day in booklet.program_days %}
  <h3>{{ day.heading }}</h3>
  {% if day.narratives %}
  {% for para in day.narratives %}<p>{{ para }}</p>{% endfor %}
  {% endif %}
  {% if day.suggestions %}<p class="note">{{ day.suggestions }}</p>{% endif %}
  {% if day.overnight %}<p class="overnight">{{ day.overnight }}</p>{% endif %}
  {% endfor %}
  {% endif %}

  {% if booklet.quote_rows %}
  <h2>Price</h2>
  <div class="panel">
    {% for row in booklet.quote_rows %}
    <div class="row"><span class="label">{{ row.label }}</span><span class="value">{{ row.value }}</span></div>
    {% endfor %}
  </div>
  {% endif %}

  {% if booklet.hotels %}
  <h2>Accommodation</h2>
  {% for stay in booklet.hotels %}
  <div class="saved-item">
    <div class="saved-name">{{ stay.name }}</div>
    <div class="saved-meta">{{ stay.destination }}{% if stay.price_range %} · {{ stay.price_range }}{% endif %}</div>
    {% if stay.address %}<div class="saved-meta">{{ stay.address }}</div>{% endif %}
    {% if stay.tel %}<div class="saved-meta">Tel: {{ stay.tel }}</div>{% endif %}
    {% if stay.mobile %}<div class="saved-meta">Mobile: {{ stay.mobile }}</div>{% endif %}
    {% if stay.email %}<div class="saved-meta">{{ stay.email }}</div>{% endif %}
    {% if stay.web %}<div class="saved-meta">{{ stay.web }}</div>{% endif %}
  </div>
  {% endfor %}
  {% endif %}

  {% if booklet.include_visits %}
  <h2>Selected Visits</h2>
  <ul>{% for item in booklet.include_visits %}<li>{{ item }}</li>{% endfor %}</ul>
  {% endif %}

  {% if saved_businesses %}
  <h2>Local Shops &amp; Services</h2>
  {% for b in saved_businesses %}
  <div class="saved-item">
    <div class="saved-name">{{ b.name }}</div>
    {% if b.meta %}<div class="saved-meta">{{ b.meta }}</div>{% endif %}
    {% if b.address %}<div class="saved-meta">{{ b.address }}</div>{% endif %}
    {% if b.contact %}<div class="saved-meta">{{ b.contact }}</div>{% endif %}
  </div>
  {% endfor %}
  {% endif %}

  {% if saved_agencies %}
  <h2>Travel Agencies</h2>
  {% for a in saved_agencies %}
  <div class="saved-item">
    <div class="saved-name">{{ a.name }}</div>
    {% if a.meta %}<div class="saved-meta">{{ a.meta }}</div>{% endif %}
    {% if a.contact %}<div class="saved-meta">{{ a.contact }}</div>{% endif %}
  </div>
  {% endfor %}
  {% endif %}

  {% if saved_guides %}
  <h2>Tour Guides</h2>
  {% for g in saved_guides %}
  <div class="saved-item">
    <div class="saved-name">{{ g.name }}</div>
    {% if g.meta %}<div class="saved-meta">{{ g.meta }}</div>{% endif %}
    {% if g.registration %}<div class="saved-meta">{{ g.registration }}</div>{% endif %}
    {% if g.address %}<div class="saved-meta">{{ g.address }}</div>{% endif %}
    {% if g.contact %}<div class="saved-meta">{{ g.contact }}</div>{% endif %}
  </div>
  {% endfor %}
  {% endif %}
</body>
</html>
"""


def _contact_line(*parts: str | None) -> str:
    return " · ".join(p.strip() for p in parts if p and str(p).strip())


def _xml(text: str | None) -> str:
    """Escape text for ReportLab Paragraph markup."""
    return escape(str(text or ""))


def _meal_basis(room_type: str | None) -> tuple[str, str]:
    """Return (phrase, short) e.g. ('half board', 'HB')."""
    suffix = normalize_room_type(room_type).rsplit("_", 1)[-1]
    mapping = {
        "bb": ("bed and breakfast", "BB"),
        "hb": ("half board", "HB"),
        "fb": ("full board", "FB"),
    }
    return mapping.get(suffix, mapping["hb"])


def _nights_count(days: int | None) -> int:
    return max(int(days or 1) - 1, 0)


def _unique_join(parts: list[str], sep: str = " – ") -> str:
    out: list[str] = []
    for part in parts:
        clean = (part or "").strip()
        if not clean:
            continue
        if not out or out[-1].lower() != clean.lower():
            out.append(clean)
    return sep.join(out)


def _day_location(day: dict) -> str:
    return (day.get("location") or day.get("title") or "Sri Lanka").strip()


def _day_route(days: list[dict], index: int) -> str:
    loc = _day_location(days[index])
    prev = _day_location(days[index - 1]) if index > 0 else ""
    if prev and prev.lower() != loc.lower():
        return _unique_join([prev, loc])
    return loc


def _day_heading(days: list[dict], index: int) -> str:
    day_num = days[index].get("day") or (index + 1)
    return f"Day {int(day_num):02d} – {_day_route(days, index)}"


def _room_type_for_hotel(trip: UserTripInput, hotel_name: str | None) -> str:
    for entry in trip.accommodations or []:
        if hotel_name and entry.get("name") == hotel_name and entry.get("room_type"):
            return normalize_room_type(entry.get("room_type"))
    return normalize_room_type(trip.room_type)


def _overnight_line(trip: UserTripInput, day: dict) -> str:
    hotel = (day.get("accommodation") or "").strip()
    if not hotel:
        return ""
    phrase, _ = _meal_basis(_room_type_for_hotel(trip, hotel))
    return f"Overnight at {hotel}, on {phrase} basis."


def _day_activity_lines(day: dict) -> list[str]:
    """One PDF paragraph per stop so times never run into the previous description."""
    lines: list[str] = []
    for act in day.get("activities") or []:
        title = (act.get("title") or "").strip()
        desc = (act.get("description") or "").strip()
        time = (act.get("time") or "").strip()
        slot = (act.get("time_slot") or "").strip()
        prefix = ""
        if time and slot:
            prefix = f"{time} ({slot}) — "
        elif time:
            prefix = f"{time} — "
        if title and desc:
            lines.append(f"{prefix}{title}. {desc}")
        elif title:
            lines.append(f"{prefix}{title}")
        elif desc:
            lines.append(f"{prefix}{desc}")
    return lines


def _day_suggestions_line(day: dict) -> str:
    titles = [
        (item.get("title") or "").strip()
        for item in (day.get("suggestions") or [])
        if (item.get("title") or "").strip()
    ]
    if not titles:
        return ""
    return "Suggested nearby: " + "; ".join(titles) + "."


def _build_booklet(trip: UserTripInput, itinerary: dict, budget: dict | None) -> dict:
    days = list(itinerary.get("days") or [])
    nights = _nights_count(trip.days)
    meal_phrase, meal_short = _meal_basis(trip.room_type)
    program_summary = [_day_heading(days, i) for i in range(len(days))]
    program_days = [
        {
            "heading": _day_heading(days, i),
            "narratives": _day_activity_lines(day),
            "suggestions": _day_suggestions_line(day),
            "overnight": _overnight_line(trip, day),
        }
        for i, day in enumerate(days)
    ]

    visits = []
    for day in days:
        for act in day.get("activities") or []:
            title = (act.get("title") or "").strip()
            if title:
                visits.append(title)
    if not visits:
        visits = [h for h in (itinerary.get("highlights") or []) if h]

    quote_rows = []
    if budget:
        quote_rows = [
            {"label": "Total budget", "value": budget["total_usd"]},
            {"label": "Duration", "value": f"{budget['days']} days / {nights} nights"},
            {"label": "Meal basis", "value": f"{meal_phrase.title()} ({meal_short})"},
            {"label": "Room type", "value": budget["room_type_label"]},
        ]
        for row in budget.get("split_rows") or []:
            quote_rows.append({"label": row["label"], "value": row["amount"]})

    return {
        "cover_title": "EXPLORE SRI LANKA",
        "cover_subtitle": f"{trip.days} DAYS  {nights} NIGHTS",
        "program_summary": program_summary,
        "program_days": program_days,
        "quote_rows": quote_rows,
        "hotels": (budget or {}).get("hotel_stays") or [],
        "include_visits": list(dict.fromkeys(visits)),
    }


def _lkr_rate() -> float:
    try:
        return float(current_app.config.get("LKR_TO_USD_RATE", 300))
    except RuntimeError:
        return 300.0


def _build_budget_pdf_context(trip: UserTripInput) -> dict | None:
    if trip.budget is None and not trip.budget_split:
        return None

    room_type = normalize_room_type(trip.room_type)
    total_usd = float(trip.budget or 0)
    per_night_usd = None
    if trip.budget_split:
        per_night_usd = accommodation_budget_per_night(
            float(trip.budget_split.accommodation), trip.days
        )

    split_rows = []
    if trip.budget_split:
        split_rows = [
            {"label": "Food", "amount": format_usd_near(float(trip.budget_split.food))},
            {"label": "Accommodation", "amount": format_usd_near(float(trip.budget_split.accommodation))},
            {"label": "Shopping", "amount": format_usd_near(float(trip.budget_split.shopping))},
            {"label": "Transport", "amount": format_usd_near(float(trip.budget_split.transport))},
        ]
        guide_amount = float(getattr(trip.budget_split, "guide", 0) or 0)
        include_guide = bool(getattr(trip.budget_split, "include_guide", False))
        if include_guide or guide_amount > 0:
            split_rows.append({"label": "Tour guide", "amount": format_usd_near(guide_amount)})

    per_night_lkr = None
    if per_night_usd is not None:
        per_night_lkr = format_lkr_near(per_night_usd * _lkr_rate())

    hotel_stays: list[dict] = []
    seen_dest: set[str] = set()
    for entry in trip.accommodations or []:
        dest = entry.get("destination")
        if not dest or dest in seen_dest:
            continue
        seen_dest.add(dest)
        hotel_id = entry.get("accommodation_id")
        hotel = Accommodation.query.get(hotel_id) if hotel_id else None
        if not hotel and entry.get("name"):
            hotel = Accommodation.query.filter_by(name=entry["name"]).first()
        if not hotel:
            hotel_stays.append(
                {
                    "destination": dest,
                    "name": entry.get("name") or "Selected hotel",
                    "price_range": "Price on request",
                }
            )
            continue
        stay_type = normalize_room_type(entry.get("room_type") or room_type)
        enriched = enrich_accommodation(hotel, stay_type)
        hotel_stays.append(
            {
                "destination": dest,
                "name": enriched["name"],
                "price_range": enriched["price_range_display"],
                "address": enriched.get("address"),
                "tel": enriched.get("tel"),
                "mobile": enriched.get("mobile"),
                "email": enriched.get("email"),
                "web": enriched.get("web"),
                "registration_no": enriched.get("registration_no"),
            }
        )

    return {
        "total_usd": format_usd_near(total_usd) if total_usd else "—",
        "days": trip.days,
        "split_rows": split_rows,
        "room_type_label": room_type_label(room_type),
        "pricing_note": "Stay rates step from each hotel range A–B: Single BB = A through Triple FB = B (BB/HB/FB).",
        "per_night_usd": format_usd_near(per_night_usd) if per_night_usd is not None else "—",
        "per_night_lkr": per_night_lkr or "—",
        "hotel_stays": hotel_stays,
    }


def _append_quote_table(story, styles, rows: list[dict]):
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from reportlab.platypus import Paragraph, Spacer, Table, TableStyle

    if not rows:
        return
    table_data = [
        [Paragraph(f"<b>{_xml(row['label'])}</b>", styles["cell"]), Paragraph(_xml(row["value"]), styles["cell"])]
        for row in rows
    ]
    table = Table(table_data, colWidths=[52 * mm, 118 * mm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(PANEL)),
                ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor(LINE)),
                ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor(LINE)),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 8))


def _append_hotels(story, styles, stays: list[dict]):
    from reportlab.platypus import Paragraph, Spacer

    if not stays:
        return
    story.append(Paragraph("ACCOMMODATION", styles["h2"]))
    for stay in stays:
        extras = []
        for label, key in (
            ("", "address"),
            ("Tel", "tel"),
            ("Mobile", "mobile"),
            ("", "email"),
            ("", "web"),
        ):
            value = (stay.get(key) or "").strip()
            if not value:
                continue
            extras.append(f"{label}: {value}" if label else value)
        extra_html = "".join(f"<br/><font color='{MUTED}'>{_xml(line)}</font>" for line in extras)
        dest = stay.get("destination") or ""
        price = stay.get("price_range") or ""
        meta = " · ".join(p for p in (dest, price) if p)
        story.append(
            Paragraph(
                f"<b>{_xml(stay['name'])}</b><br/>"
                f"<font color='{MUTED}'>{_xml(meta)}</font>"
                f"{extra_html}",
                styles["body"],
            )
        )
        story.append(Spacer(1, 6))


def _append_bullets(story, styles, title: str, items: list[str], intro: str | None = None):
    from reportlab.platypus import Paragraph, Spacer

    if not items:
        return
    story.append(Paragraph(_xml(title), styles["h2"]))
    if intro:
        story.append(Paragraph(_xml(intro), styles["body"]))
        story.append(Spacer(1, 4))
    for item in items:
        story.append(Paragraph(f"• {_xml(item)}", styles["body"]))
        story.append(Spacer(1, 2))
    story.append(Spacer(1, 6))


def _append_list_section(story, styles, title: str, items: list[dict], line_builder):
    from reportlab.platypus import Paragraph, Spacer

    if not items:
        return
    story.append(Paragraph(title, styles["h2"]))
    for item in items:
        story.append(Paragraph(line_builder(item), styles["body"]))
        story.append(Spacer(1, 6))


def _load_saved_for_pdf(
    trip: UserTripInput,
) -> tuple[list[dict], list[dict], list[dict]]:
    refs = SavedReference.query.filter_by(trip_id=trip.trip_id).all()
    businesses: list[dict] = []
    agencies: list[dict] = []
    guides: list[dict] = []

    for ref in refs:
        ref_type = ref.ref_type.value if hasattr(ref.ref_type, "value") else ref.ref_type
        if ref_type == "business_directory":
            biz = BusinessDirectory.query.get(ref.ref_id)
            if not biz:
                continue
            biz_data = biz.to_dict()
            businesses.append(
                {
                    "name": biz_data["business_name"],
                    "meta": _contact_line(biz_data.get("local_authority"), biz_data.get("district")),
                    "address": (biz_data.get("address") or "").strip(),
                    "contact": _contact_line(
                        f"Tel: {biz_data['telephone']}" if biz_data.get("telephone") else None,
                        f"Email: {biz_data['email']}" if biz_data.get("email") else None,
                    ),
                }
            )
        elif ref_type == "travel_agency":
            agency = TravelAgency.query.get(ref.ref_id)
            if not agency:
                continue
            agencies.append(
                {
                    "name": agency.name,
                    "meta": (agency.local_authority or "").strip(),
                    "contact": _contact_line(agency.telephone, agency.email),
                }
            )
        elif ref_type == "tourist_guide":
            guide = TouristGuide.query.get(ref.ref_id)
            if not guide:
                continue
            registration = "Reg: " + (guide.registration_no or "—")
            if guide.languages:
                registration += f" · {guide.languages}"
            guides.append(
                {
                    "name": guide.name,
                    "meta": (guide.guide_type or "").strip(),
                    "registration": registration,
                    "address": (guide.address or "").strip(),
                    "contact": _contact_line(guide.tel, guide.email),
                }
            )

    return businesses, agencies, guides


def _reportlab_styles():
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet

    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "PdfTitle",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=18,
            textColor=colors.HexColor(GREEN),
            spaceAfter=2,
        ),
        "coverSub": ParagraphStyle(
            "PdfCoverSub",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            textColor=colors.HexColor(GREEN),
            spaceAfter=12,
        ),
        "h2": ParagraphStyle(
            "PdfH2",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=11.5,
            textColor=colors.HexColor(GREEN),
            spaceBefore=14,
            spaceAfter=8,
        ),
        "h3": ParagraphStyle(
            "PdfH3",
            parent=base["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=11,
            textColor=colors.HexColor(GREEN),
            spaceBefore=8,
            spaceAfter=4,
        ),
        "body": ParagraphStyle(
            "PdfBody",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=colors.HexColor(INK),
            alignment=TA_LEFT,
        ),
        "muted": ParagraphStyle(
            "PdfMuted",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=colors.HexColor(MUTED),
        ),
        "note": ParagraphStyle(
            "PdfNote",
            parent=base["BodyText"],
            fontName="Helvetica-Oblique",
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor(MUTED),
        ),
        "cell": ParagraphStyle(
            "PdfCell",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=12,
            textColor=colors.HexColor(INK),
        ),
    }


def _saved_line(item: dict) -> str:
    lines = [f"<b>{_xml(item['name'])}</b>"]
    for key in ("meta", "registration", "address", "contact"):
        if item.get(key):
            lines.append(f"<font color='{MUTED}'>{_xml(item[key])}</font>")
    return "<br/>".join(lines)


def _render_with_weasyprint(trip: UserTripInput, itinerary: dict) -> bytes:
    from weasyprint import HTML

    saved_businesses, saved_agencies, saved_guides = _load_saved_for_pdf(trip)
    budget = _build_budget_pdf_context(trip)
    booklet = _build_booklet(trip, itinerary, budget)
    html = render_template_string(
        PDF_TEMPLATE,
        logo_src=_logo_data_uri(),
        brand_name=BRAND_NAME,
        contact_html=_contact_block(),
        booklet=booklet,
        saved_businesses=saved_businesses,
        saved_agencies=saved_agencies,
        saved_guides=saved_guides,
    )
    return HTML(string=html).write_pdf()


def _render_with_reportlab(trip: UserTripInput, itinerary: dict) -> bytes:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.platypus import HRFlowable, Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=18 * mm,
        title="Tour Ceylon Itinerary",
    )
    styles = _reportlab_styles()
    story = []

    brand = Paragraph(
        f"<b>{_xml(BRAND_NAME)}</b><br/>"
        f"<font color='{MUTED}'>{_xml(CONTACT_PHONE)} · {_xml(CONTACT_MOBILE)}</font><br/>"
        f"<font color='{MUTED}'>{_xml(CONTACT_EMAIL)} · {_xml(CONTACT_ADDRESS)}</font><br/>"
        f"<font color='{MUTED}'>{_xml(CONTACT_HOURS)}</font>",
        styles["body"],
    )
    logo_path = _logo_file()
    if logo_path:
        letterhead = Table(
            [[Image(str(logo_path), width=24 * mm, height=20.4 * mm), brand]],
            colWidths=[28 * mm, 142 * mm],
        )
        letterhead.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ]
            )
        )
        story.append(letterhead)
    else:
        story.append(brand)
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.4, color=colors.HexColor(GREEN), spaceBefore=0, spaceAfter=10))

    budget = _build_budget_pdf_context(trip)
    booklet = _build_booklet(trip, itinerary, budget)
    saved_businesses, saved_agencies, saved_guides = _load_saved_for_pdf(trip)

    story.append(Paragraph(_xml(booklet["cover_title"]), styles["title"]))
    story.append(Paragraph(_xml(booklet["cover_subtitle"]), styles["coverSub"]))

    if booklet["program_summary"]:
        story.append(Paragraph("PROGRAM SUMMARY", styles["h2"]))
        for line in booklet["program_summary"]:
            story.append(Paragraph(_xml(line), styles["body"]))

    if booklet["program_days"]:
        story.append(Paragraph("PROGRAM IN DETAILS", styles["h2"]))
        for day in booklet["program_days"]:
            story.append(Paragraph(_xml(day["heading"]), styles["h3"]))
            for para in day.get("narratives") or []:
                story.append(Paragraph(_xml(para), styles["body"]))
                story.append(Spacer(1, 5))
            if day.get("suggestions"):
                story.append(Paragraph(_xml(day["suggestions"]), styles["note"]))
            if day.get("overnight"):
                story.append(Spacer(1, 3))
                story.append(Paragraph(f"<b>{_xml(day['overnight'])}</b>", styles["body"]))
            story.append(Spacer(1, 8))

    if booklet["quote_rows"]:
        story.append(Paragraph("PRICE", styles["h2"]))
        _append_quote_table(story, styles, booklet["quote_rows"])

    _append_hotels(story, styles, booklet["hotels"])
    _append_bullets(story, styles, "SELECTED VISITS", booklet["include_visits"])

    _append_list_section(story, styles, "Local Shops &amp; Services", saved_businesses, _saved_line)
    _append_list_section(story, styles, "Travel Agencies", saved_agencies, _saved_line)
    _append_list_section(story, styles, "Tour Guides", saved_guides, _saved_line)

    def _footer(canvas, doc_obj):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor(LINE))
        canvas.line(18 * mm, 14 * mm, A4[0] - 18 * mm, 14 * mm)
        footer_logo = _logo_file()
        text_x = 18 * mm
        if footer_logo:
            canvas.drawImage(
                str(footer_logo),
                18 * mm,
                5.2 * mm,
                width=7 * mm,
                height=7 * mm,
                preserveAspectRatio=True,
                mask="auto",
            )
            text_x = 27 * mm
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor(MUTED))
        canvas.drawString(text_x, 8 * mm, f"{BRAND_NAME}  ·  {CONTACT_PHONE}  ·  {CONTACT_EMAIL}")
        canvas.drawRightString(A4[0] - 18 * mm, 8 * mm, f"Page {doc_obj.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    return buffer.getvalue()


def render_itinerary_pdf(trip: UserTripInput, itinerary: dict) -> bytes:
    """Generate PDF bytes. ReportLab on Windows; WeasyPrint elsewhere when available."""
    if sys.platform == "win32":
        return _render_with_reportlab(trip, itinerary)
    try:
        return _render_with_weasyprint(trip, itinerary)
    except Exception:
        return _render_with_reportlab(trip, itinerary)
