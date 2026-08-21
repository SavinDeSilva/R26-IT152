"""PDF export — WeasyPrint when available, ReportLab fallback on Windows."""

from __future__ import annotations

import sys
from io import BytesIO
from xml.sax.saxutils import escape

from flask import current_app, render_template_string

from app.models.accommodation import Accommodation
from app.models.business_directory import BusinessDirectory
from app.models.saved_reference import SavedReference
from app.models.tourist_guide import TouristGuide
from app.models.travel_agency import TravelAgency
from app.models.user_trip_input import UserTripInput
from app.services.budget_service import accommodation_budget_per_night
from app.services.room_type_service import (
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

PDF_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body { font-family: Helvetica, Arial, sans-serif; color: #1a2332; margin: 36px 42px; font-size: 11pt; line-height: 1.45; }
    h1 { color: #1a7f4b; font-size: 22pt; margin: 0 0 6px; border-bottom: 2px solid #1a7f4b; padding-bottom: 8px; }
    h2 { color: #1a7f4b; font-size: 13pt; margin: 22px 0 10px; letter-spacing: 0.02em; }
    h3 { color: #1a2332; font-size: 11.5pt; margin: 0 0 6px; }
    .panel { background: #f7faf9; border: 1px solid #d0dce0; border-radius: 8px; padding: 14px 16px; margin-bottom: 14px; }
    .row { display: flex; justify-content: space-between; padding: 4px 0; border-bottom: 1px solid #e8eeec; }
    .row:last-child { border-bottom: none; }
    .label { color: #5a6570; }
    .value { font-weight: 600; color: #1a2332; }
    .saved-item { margin: 0 0 10px 0; padding-bottom: 8px; border-bottom: 1px dashed #e0e6e4; }
    .saved-name { font-weight: 600; color: #1a2332; }
    .saved-meta { color: #5a6570; font-size: 10pt; margin-top: 2px; }
    .day { page-break-inside: avoid; margin-bottom: 14px; padding: 14px 16px; border: 1px solid #d0dce0; border-radius: 8px; background: #fff; }
    .day-meta { color: #5a6570; font-size: 10pt; margin-bottom: 8px; }
    .activity { margin: 8px 0 0 14px; padding-left: 10px; border-left: 3px solid #1a7f4b; }
    .activity-time { font-weight: 700; color: #1a7f4b; }
    .activity-meta { color: #5a6570; font-size: 9.5pt; }
    ul { margin: 6px 0 0 18px; padding: 0; }
    li { margin-bottom: 4px; }
    .note { color: #5a6570; font-size: 9.5pt; font-style: italic; }
  </style>
</head>
<body>
  <h1>{{ title }}</h1>

  {% if budget %}
  <h2>Trip Budget</h2>
  <div class="panel">
    <div class="row"><span class="label">Total budget</span><span class="value">{{ budget.total_usd }}</span></div>
    <div class="row"><span class="label">Trip length</span><span class="value">{{ budget.days }} days</span></div>
    {% if budget.split_rows %}
    {% for row in budget.split_rows %}
    <div class="row"><span class="label">{{ row.label }}</span><span class="value">{{ row.amount }}</span></div>
    {% endfor %}
    {% endif %}
    <div class="row"><span class="label">Room type</span><span class="value">{{ budget.room_type_label }}</span></div>
    <div class="row"><span class="label">Stay budget / night</span><span class="value">{{ budget.per_night_usd }} ({{ budget.per_night_lkr }})</span></div>
    <p class="note">{{ budget.pricing_note }}</p>
  </div>
  {% if budget.hotel_stays %}
  <h2>Selected Stays</h2>
  {% for stay in budget.hotel_stays %}
  <div class="saved-item">
    <div class="saved-name">{{ stay.name }}</div>
    <div class="saved-meta">{{ stay.destination }} · {{ stay.price_range }}</div>
  </div>
  {% endfor %}
  {% endif %}
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

  {% if highlights %}
  <h2>Trip Highlights</h2>
  <ul>{% for h in highlights %}<li>{{ h }}</li>{% endfor %}</ul>
  {% endif %}

  <h2>Day-by-Day Schedule</h2>
  {% for day in day_list %}
  <div class="day">
    <h3>Day {{ day.day }} — {{ day.title }}</h3>
    <div class="day-meta">{{ day.location }} · Stay: {{ day.accommodation }}</div>
    {% for act in day.activities %}
    <div class="activity">
      <span class="activity-time">{{ act.time }}</span> — {{ act.title }}
      {% if act.meta %}<span class="activity-meta"> · {{ act.meta }}</span>{% endif %}
      {% if act.description %}<br>{{ act.description }}{% endif %}
    </div>
    {% endfor %}
  </div>
  {% endfor %}

  {% if tips %}
  <h2>Travel Tips</h2>
  <ul>{% for t in tips %}<li>{{ t }}</li>{% endfor %}</ul>
  {% endif %}
</body>
</html>
"""


def _contact_line(*parts: str | None) -> str:
    return " · ".join(p.strip() for p in parts if p and str(p).strip())


def _xml(text: str | None) -> str:
    """Escape text for ReportLab Paragraph markup."""
    return escape(str(text or ""))


def _activity_meta(act: dict) -> str:
    parts = []
    if act.get("mood_tag"):
        parts.append(f"Mood: {act['mood_tag']}")
    if act.get("category"):
        parts.append(str(act["category"]))
    return " · ".join(parts)


def _prepare_day_list(itinerary: dict) -> list[dict]:
    days = []
    for day in itinerary.get("days") or []:
        activities = []
        for act in day.get("activities") or []:
            activities.append({**act, "meta": _activity_meta(act)})
        days.append({**day, "activities": activities})
    return days


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
        enriched = enrich_accommodation(hotel, room_type)
        hotel_stays.append(
            {
                "destination": dest,
                "name": enriched["name"],
                "price_range": enriched["price_range_display"],
            }
        )

    return {
        "total_usd": format_usd_near(total_usd) if total_usd else "—",
        "days": trip.days,
        "split_rows": split_rows,
        "room_type_label": room_type_label(room_type),
        "pricing_note": "Hotel rates are approximate. Single ≈ A, Double ≈ (A+B)/2, Family ≈ B from each hotel range.",
        "per_night_usd": format_usd_near(per_night_usd) if per_night_usd is not None else "—",
        "per_night_lkr": per_night_lkr or "—",
        "hotel_stays": hotel_stays,
    }


def _append_budget_section_reportlab(story, styles, budget: dict | None):
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from reportlab.platypus import Paragraph, Spacer, Table, TableStyle

    if not budget:
        return

    story.append(Paragraph("Trip Budget", styles["h2"]))
    rows = [
        ["Total budget", budget["total_usd"]],
        ["Trip length", f"{budget['days']} days"],
    ]
    for row in budget.get("split_rows") or []:
        rows.append([row["label"], row["amount"]])
    rows.extend(
        [
            ["Room type", budget["room_type_label"]],
            ["Stay budget / night", f"{budget['per_night_usd']} ({budget['per_night_lkr']})"],
        ]
    )

    table_data = [[Paragraph(f"<b>{a}</b>", styles["cell"]), Paragraph(b, styles["cell"])] for a, b in rows]
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
    story.append(Spacer(1, 4))
    story.append(Paragraph(budget.get("pricing_note", ""), styles["note"]))
    story.append(Spacer(1, 8))

    stays = budget.get("hotel_stays") or []
    if stays:
        story.append(Paragraph("Selected Stays", styles["h2"]))
        for stay in stays:
            story.append(
                Paragraph(
                    f"<b>{_xml(stay['name'])}</b><br/>"
                    f"<font color='{MUTED}'>{_xml(stay['destination'])} · {_xml(stay['price_range'])}</font>",
                    styles["body"],
                )
            )
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
            businesses.append(
                {
                    "name": biz.business_name,
                    "meta": _contact_line(biz.local_authority, biz.district),
                    "address": (biz.address or "").strip(),
                    "contact": _contact_line(biz.telephone, biz.email),
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
            fontSize=20,
            textColor=colors.HexColor(GREEN),
            spaceAfter=10,
        ),
        "h2": ParagraphStyle(
            "PdfH2",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            textColor=colors.HexColor(GREEN),
            spaceBefore=14,
            spaceAfter=8,
        ),
        "h3": ParagraphStyle(
            "PdfH3",
            parent=base["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=11,
            textColor=colors.HexColor(INK),
            spaceBefore=4,
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
    html = render_template_string(
        PDF_TEMPLATE,
        title=itinerary.get("title", "Sri Lanka Itinerary"),
        budget=budget,
        saved_businesses=saved_businesses,
        saved_agencies=saved_agencies,
        saved_guides=saved_guides,
        highlights=itinerary.get("highlights", []),
        day_list=_prepare_day_list(itinerary),
        tips=itinerary.get("tips", []),
    )
    return HTML(string=html).write_pdf()


def _render_with_reportlab(trip: UserTripInput, itinerary: dict) -> bytes:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title="Tour Ceylon Itinerary",
    )
    styles = _reportlab_styles()
    story = []

    story.append(Paragraph(_xml(itinerary.get("title", "Sri Lanka Itinerary")), styles["title"]))
    story.append(Spacer(1, 6))

    budget = _build_budget_pdf_context(trip)
    _append_budget_section_reportlab(story, styles, budget)

    saved_businesses, saved_agencies, saved_guides = _load_saved_for_pdf(trip)
    _append_list_section(story, styles, "Local Shops &amp; Services", saved_businesses, _saved_line)
    _append_list_section(story, styles, "Travel Agencies", saved_agencies, _saved_line)
    _append_list_section(story, styles, "Tour Guides", saved_guides, _saved_line)

    highlights = itinerary.get("highlights") or []
    if highlights:
        story.append(Paragraph("Trip Highlights", styles["h2"]))
        for item in highlights:
            story.append(Paragraph(f"• {_xml(item)}", styles["body"]))
        story.append(Spacer(1, 6))

    story.append(Paragraph("Day-by-Day Schedule", styles["h2"]))
    for day in _prepare_day_list(itinerary):
        day_num = day.get("day")
        location = day.get("location") or day.get("title") or ""
        title = location
        if isinstance(title, str) and title.lower().startswith(f"day {day_num}".lower()):
            title = title.split(" — ", 1)[-1] if " — " in title else location

        story.append(Paragraph(f"Day {day_num} — {_xml(title)}", styles["h3"]))
        story.append(
            Paragraph(
                f"<font color='{MUTED}'>{_xml(day.get('location', ''))} · "
                f"Stay: {_xml(day.get('accommodation', ''))}</font>",
                styles["muted"],
            )
        )
        story.append(Spacer(1, 4))

        for act in day.get("activities") or []:
            meta = act.get("meta") or ""
            meta_html = f" <font color='{MUTED}'>({_xml(meta)})</font>" if meta else ""
            desc = act.get("description") or ""
            desc_html = f"<br/>{_xml(desc)}" if desc else ""
            story.append(
                Paragraph(
                    f"<font color='{GREEN}'><b>{_xml(act.get('time', ''))}</b></font> — "
                    f"{_xml(act.get('title', ''))}{meta_html}{desc_html}",
                    styles["body"],
                )
            )
            story.append(Spacer(1, 4))

        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor(LINE), spaceBefore=6, spaceAfter=10))

    tips = itinerary.get("tips") or []
    if tips:
        story.append(Paragraph("Travel Tips", styles["h2"]))
        for tip in tips:
            story.append(Paragraph(f"• {_xml(tip)}", styles["body"]))

    def _footer(canvas, doc_obj):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor(LINE))
        canvas.line(18 * mm, 14 * mm, A4[0] - 18 * mm, 14 * mm)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor(MUTED))
        canvas.drawString(18 * mm, 8 * mm, "Tour Ceylon — Travel Itinerary")
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
