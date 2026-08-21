"""
Generate three IEEE-style technical reports (one PDF per Tour Ceylon component).

Run:
  cd backend
  .\\.venv\\Scripts\\python.exe ..\\docs\\generate_ieee_component_reports.py

Output:
  docs/pdfs/IEEE_Itinerary_Component_Report.pdf
  docs/pdfs/IEEE_SOS_Component_Report.pdf
  docs/pdfs/IEEE_Wellness_Component_Report.pdf
"""

from __future__ import annotations

from functools import partial
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

OUT_DIR = Path(__file__).resolve().parent / "pdfs"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# IEEE-like palette (print-safe)
INK = colors.HexColor("#000000")
MUTED = colors.HexColor("#333333")
LINE = colors.HexColor("#666666")
RULE = colors.HexColor("#000000")
HEAD_BG = colors.HexColor("#1F1F1F")
ROW_ALT = colors.HexColor("#F2F2F2")
ABS_BG = colors.HexColor("#F7F7F7")

PROJECT = "Tour Ceylon -- Unified Tourism Platform for Sri Lanka"
PROJECT_ID = "R26-IT-152"
INSTITUTION = "Informatics Institute of Technology (IIT), affiliated with University of Westminster"
DEGREE = "BSc (Hons) Information Technology -- Software Engineering"
DATE = "August 2026"

AUTHORS = {
    "itinerary": {
        "name": "Wanniarachchi P.M.R.",
        "role": "AI Itinerary Generator",
        "id": "",
    },
    "sos": {
        "name": "D.S.K. De Silva",
        "role": "SOS System",
        "id": "IT22108654",
    },
    "wellness": {
        "name": "D.C.M. De Silva",
        "role": "Wellness Platform",
        "id": "",
    },
}


def styles():
    base = getSampleStyleSheet()
    return {
        "journal": ParagraphStyle(
            "journal", parent=base["Normal"], fontName="Times-Bold",
            fontSize=9, alignment=TA_CENTER, textColor=INK, spaceAfter=8,
            leading=12,
        ),
        "title": ParagraphStyle(
            "title", parent=base["Title"], fontName="Times-Bold",
            fontSize=16, leading=20, alignment=TA_CENTER, textColor=INK,
            spaceAfter=8, spaceBefore=2,
        ),
        "authors": ParagraphStyle(
            "authors", parent=base["Normal"], fontName="Times-Roman",
            fontSize=11, alignment=TA_CENTER, leading=14, spaceAfter=2,
        ),
        "affil": ParagraphStyle(
            "affil", parent=base["Normal"], fontName="Times-Italic",
            fontSize=9, alignment=TA_CENTER, leading=12, spaceAfter=8,
        ),
        "abs_head": ParagraphStyle(
            "abs_head", parent=base["Normal"], fontName="Times-Bold",
            fontSize=9, alignment=TA_CENTER, spaceBefore=4, spaceAfter=4,
        ),
        "abstract": ParagraphStyle(
            "abstract", parent=base["Normal"], fontName="Times-Roman",
            fontSize=9, leading=12, alignment=TA_JUSTIFY, spaceAfter=4,
        ),
        "kw": ParagraphStyle(
            "kw", parent=base["Normal"], fontName="Times-Roman",
            fontSize=9, leading=12, alignment=TA_JUSTIFY, spaceAfter=10,
        ),
        "h1": ParagraphStyle(
            "h1", parent=base["Heading1"], fontName="Times-Bold",
            fontSize=11, leading=14, textColor=INK, spaceBefore=10,
            spaceAfter=5, alignment=TA_CENTER,
        ),
        "h2": ParagraphStyle(
            "h2", parent=base["Heading2"], fontName="Times-Bold",
            fontSize=10.5, leading=13, textColor=INK, spaceBefore=7,
            spaceAfter=3, alignment=TA_LEFT,
        ),
        "h3": ParagraphStyle(
            "h3", parent=base["Heading3"], fontName="Times-BoldItalic",
            fontSize=10, leading=13, textColor=INK, spaceBefore=5,
            spaceAfter=2,
        ),
        "body": ParagraphStyle(
            "body", parent=base["Normal"], fontName="Times-Roman",
            fontSize=10, leading=13.5, alignment=TA_JUSTIFY, spaceAfter=6,
            textColor=INK,
        ),
        "bullet": ParagraphStyle(
            "bullet", parent=base["Normal"], fontName="Times-Roman",
            fontSize=10, leading=13, textColor=INK,
        ),
        "caption": ParagraphStyle(
            "caption", parent=base["Normal"], fontName="Times-Bold",
            fontSize=9, alignment=TA_CENTER, spaceBefore=4, spaceAfter=2,
        ),
        "cap_title": ParagraphStyle(
            "cap_title", parent=base["Normal"], fontName="Times-Italic",
            fontSize=9, alignment=TA_CENTER, spaceAfter=4, leading=12,
        ),
        "cell": ParagraphStyle(
            "cell", parent=base["Normal"], fontName="Times-Roman",
            fontSize=8.5, leading=11, textColor=INK,
        ),
        "cell_h": ParagraphStyle(
            "cell_h", parent=base["Normal"], fontName="Times-Bold",
            fontSize=8.5, leading=11, textColor=colors.white,
        ),
        "eq": ParagraphStyle(
            "eq", parent=base["Normal"], fontName="Times-Italic",
            fontSize=10, alignment=TA_CENTER, spaceBefore=4, spaceAfter=2,
            leading=14,
        ),
        "eq_n": ParagraphStyle(
            "eq_n", parent=base["Normal"], fontName="Times-Roman",
            fontSize=9, alignment=TA_RIGHT, textColor=MUTED, spaceAfter=6,
        ),
        "ref": ParagraphStyle(
            "ref", parent=base["Normal"], fontName="Times-Roman",
            fontSize=9, leading=12, leftIndent=14, firstLineIndent=-14,
            spaceAfter=3, alignment=TA_JUSTIFY,
        ),
        "foot": ParagraphStyle(
            "foot", parent=base["Normal"], fontName="Times-Italic",
            fontSize=8, textColor=MUTED, leading=10, spaceAfter=4,
        ),
        "code": ParagraphStyle(
            "code", parent=base["Code"], fontName="Courier",
            fontSize=7.5, leading=10, textColor=INK, spaceBefore=2, spaceAfter=6,
        ),
    }


def footer(canvas, doc, running: str):
    canvas.saveState()
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(0.6)
    canvas.line(18 * mm, 14 * mm, A4[0] - 18 * mm, 14 * mm)
    canvas.setFont("Times-Italic", 8)
    canvas.setFillColor(INK)
    canvas.drawString(18 * mm, 8 * mm, running[:90])
    canvas.drawRightString(A4[0] - 18 * mm, 8 * mm, str(doc.page))
    canvas.restoreState()


def header_first(canvas, doc, running: str):
    canvas.saveState()
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(1.2)
    canvas.line(18 * mm, A4[1] - 12 * mm, A4[0] - 18 * mm, A4[1] - 12 * mm)
    canvas.setFont("Times-Roman", 8)
    canvas.drawCentredString(A4[0] / 2, A4[1] - 10 * mm, running)
    canvas.restoreState()
    footer(canvas, doc, running)


def header_later(canvas, doc, running: str):
    canvas.saveState()
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(0.6)
    y = A4[1] - 12 * mm
    canvas.line(18 * mm, y, A4[0] - 18 * mm, y)
    canvas.setFont("Times-Italic", 8)
    canvas.drawString(18 * mm, y + 3, running[:90])
    canvas.drawRightString(A4[0] - 18 * mm, y + 3, PROJECT_ID)
    canvas.restoreState()
    footer(canvas, doc, running)


def bullets(story, s, items):
    story.append(ListFlowable(
        [ListItem(Paragraph(item, s["bullet"]), leftIndent=10) for item in items],
        bulletType="bullet", start="•", leftIndent=14, spaceAfter=6,
    ))


def tbl(story, s, caption_no: str, caption: str, headers, rows, col_widths=None):
    usable = 174 * mm
    if not col_widths:
        col_widths = [usable / len(headers)] * len(headers)
    data = [[Paragraph(h, s["cell_h"]) for h in headers]]
    for row in rows:
        data.append([Paragraph(str(c), s["cell"]) for c in row])
    t = Table(data, colWidths=col_widths, repeatRows=1)
    cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), HEAD_BG),
        ("GRID", (0, 0), (-1, -1), 0.35, LINE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            cmds.append(("BACKGROUND", (0, i), (-1, i), ROW_ALT))
    t.setStyle(TableStyle(cmds))
    story.append(KeepTogether([
        Paragraph(caption_no, s["caption"]),
        Paragraph(caption, s["cap_title"]),
        t,
        Spacer(1, 3 * mm),
    ]))


def eq(story, s, text, number):
    story.append(Paragraph(text, s["eq"]))
    story.append(Paragraph(f"({number})", s["eq_n"]))


def build_doc(path: Path, story, running: str, author: str):
    doc = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=20 * mm,
        bottomMargin=18 * mm,
        title=running,
        author=author,
    )
    doc.build(
        story,
        onFirstPage=partial(header_first, running=running),
        onLaterPages=partial(header_later, running=running),
    )


def front_matter(story, s, title, abstract, keywords, author):
    id_bit = f" ({author['id']})" if author.get("id") else ""
    story.append(Paragraph(
        f"IEEE-Style Technical Report &nbsp;|&nbsp; {PROJECT_ID} &nbsp;|&nbsp; {DATE}",
        s["journal"],
    ))
    story.append(Paragraph(title, s["title"]))
    story.append(Paragraph(f"{author['name']}{id_bit}", s["authors"]))
    story.append(Paragraph(f"{author['role']} -- {PROJECT}", s["authors"]))
    story.append(Paragraph(f"{INSTITUTION}<br/>{DEGREE}", s["affil"]))
    story.append(HRFlowable(width="100%", thickness=0.8, color=RULE, spaceAfter=6))
    story.append(Paragraph("Abstract", s["abs_head"]))
    story.append(Paragraph(abstract, s["abstract"]))
    story.append(Paragraph(f"<b>Index Terms--</b> {keywords}", s["kw"]))
    story.append(HRFlowable(width="100%", thickness=0.4, color=RULE, spaceAfter=8))


# ---------------------------------------------------------------------------
# 1. ITINERARY
# ---------------------------------------------------------------------------
def story_itinerary(s):
    story = []
    front_matter(
        story, s,
        title="AI Itinerary Generator for Sri Lanka Tourism: A Heuristic Multi-Constraint Planner (Tour Ceylon)",
        abstract=(
            "This paper reports the itinerary-planning component of Tour Ceylon, a unified modular "
            "monolith for Sri Lanka tourism. The component generates day-by-day trip schedules from "
            "curated government-style registries rather than from a learned ranker or a large language "
            "model. A six-step wizard collects moods (at most three), attraction selections, a USD "
            "budget split, and one hotel per destination, then a deterministic engine assigns destination "
            "blocks, clock times, and a PDF export. The catalogue comprises 350 attractions across 31 "
            "destinations (10 mood tags, 6 categories), 937 accommodations, 126 businesses, 417 travel "
            "agencies, and 2,906 tourist guides after registration filtering. Scheduling uses a mood-averaged "
            "start hour (default 08:30), inter-activity gaps of 2.0-3.0 h, a lunch snap in [12:00, 13:00), "
            "and an evening cap at 19:30. Location strings are normalised with an alias map plus "
            "SequenceMatcher at similarity 0.88. Validation is a 12-step HTTP smoke test of the full "
            "wizard-to-PDF path; no accuracy, precision, recall, or F1 scores are claimed because the "
            "planner is rule-based (the product name AI Itinerary Generator refers to automated scheduling, "
            "not a trained neural ranker). Limitations include the absence of road-network travel times and "
            "learned attraction ranking. The contribution is an explainable, deployable planner that "
            "shares identity with SOS and wellness through a single Flask API on port 5002."
        ),
        keywords=(
            "itinerary generation, heuristic scheduling, tourism information systems, "
            "constraint-based planning, Sri Lanka, Flask, PostgreSQL"
        ),
        author=AUTHORS["itinerary"],
    )

    story.append(Paragraph("I. INTRODUCTION", s["h1"]))
    story.append(Paragraph(
        "Foreign visitors to Sri Lanka typically assemble trips from fragmented lists of attractions, "
        "hotels, and licensed guides. Tour Ceylon's travel component addresses that gap with a "
        "browser wizard that ends in a timed day plan and a downloadable PDF. The module is the "
        "primary tourist-facing product of the platform (React 18.3 + Vite 5.4 on port 5180) and "
        "writes trip state into PostgreSQL tables consumed later by SOS hand-off and wellness "
        "sessions. This report documents methodology, measured catalogue sizes, validation, and "
        "limitations as implemented in the unified codebase--not as a hypothetical recommender.",
        s["body"],
    ))
    story.append(Paragraph(
        "A central design choice is explicit: although the module is named AI Itinerary Generator, "
        "the file <font face='Courier' size='9'>ai_service.py</font> "
        "does not call OpenAI. An <font face='Courier' size='9'>OPENAI_API_KEY</font> may be present in "
        "configuration but is unused. Generated itineraries are tagged <font face='Courier' size='9'>source: "
        "\"database\"</font>. The engine is therefore reproducible without a paid model API and is "
        "inspectable for a viva or IEEE methods section.",
        s["body"],
    ))

    story.append(Paragraph("II. SYSTEM CONTEXT AND REQUIREMENTS", s["h1"]))
    story.append(Paragraph("A. Role in Tour Ceylon", s["h2"]))
    story.append(Paragraph(
        "Tour Ceylon is a modular MVC monolith: one Flask 3.0.3 process (port 5002) serves Travel, "
        "SOS, and Wellness. JSON Web Tokens (Flask-JWT-Extended 4.6.0) identify the tourist. After "
        "planning, the same session can open the SOS PWA (port 5175) via a travel-to-SOS bridge. "
        "The itinerary component is therefore both a standalone planner and the identity gateway "
        "for safety and wellness modules.",
        s["body"],
    ))
    story.append(Paragraph("B. Functional Scope", s["h2"]))
    story.append(Paragraph(
        "The wizard exposes six user steps: (1) attractions with 1-3 moods; (2) budget; (3) one hotel "
        "per destination; (4) generated itinerary; (5) discover (businesses, agencies, guides); "
        "(6) PDF export and history. Mood vocabulary is fixed at ten labels: Adventure, Authentic, "
        "Curious, Excited, Explore, Happy, Healing, Peaceful, Relaxed, and Spiritual. Attraction "
        "categories are Wild, Scenic, Pristine, Heritage, Essence, and Thrills.",
        s["body"],
    ))

    story.append(Paragraph("III. METHODOLOGY", s["h1"]))
    story.append(Paragraph("A. Technical Setup", s["h2"]))
    story.append(Paragraph(
        "Frontend: React 18.3, react-router-dom 6.26, Axios, Recharts (budget pie), Vite proxy of "
        "<font face='Courier' size='9'>/api</font> to 127.0.0.1:5002. Backend: Flask, SQLAlchemy 2.0, "
        "PostgreSQL database <font face='Courier' size='9'>travel_app</font>. PDF: WeasyPrint when "
        "available, else ReportLab 4.2.2. Hardware is a conventional development PC; no GPU is required.",
        s["body"],
    ))
    tbl(
        story, s, "TABLE I",
        "Seeded catalogue sizes used at runtime (live PostgreSQL travel_app, August 2026).",
        ["Dataset", "Source", "Records used"],
        [
            ["Attractions", "attractions.xlsx (sheet Attractions)", "350"],
            ["Accommodations", "accomadation.xlsx", "937"],
            ["Business directory", "business_directory.xlsx", "126"],
            ["Travel agencies", "travel_agencies.xlsx", "417"],
            ["Tourist guides", "tourist_guides.csv (3,634 raw)", "2,906 after filters"],
            ["Unique destinations (attractions)", "Destination column", "31 (28 after normalized_destination)"],
            ["Mood tags / categories", "Excel columns", "10 / 6"],
        ],
        [52 * mm, 72 * mm, 50 * mm],
    )

    story.append(Paragraph("B. Data Collection and Preprocessing", s["h2"]))
    story.append(Paragraph(
        "Registries live in <font face='Courier' size='9'>backend/data/travel/</font>. "
        "<font face='Courier' size='9'>seed_data.py</font> reads them with pandas 2.2.2 and openpyxl 3.1.5. "
        "Local-authority strings are mapped through an explicit alias table, then residual mismatches "
        "are aligned with Python <font face='Courier' size='9'>difflib.SequenceMatcher</font> at "
        "ratio threshold 0.88; flagged pairs are written to a review JSON. Hotel price text is parsed "
        "into <font face='Courier' size='9'>price_min</font> and <font face='Courier' size='9'>price_max</font>. "
        "Guide rows are dropped unless they have a valid registration and a known type "
        "{National, Chauffeur, Area, Site}. Attraction images are extracted from Excel embeddings. "
        "A leftover checklist in verify_seed.py still encodes 130 attractions / 944 hotels from an "
        "earlier catalogue; this report uses the live table counts (350 / 937), which match the "
        "current seed files.",
        s["body"],
    ))

    story.append(Paragraph("C. Constraint Checks on Trip Input", s["h2"]))
    story.append(Paragraph(
        "Endpoint <font face='Courier' size='9'>POST /api/trip-input</font> requires days &gt; 0, "
        "one to three moods, a non-empty attraction ID list, and",
        s["body"],
    ))
    eq(story, s, "unique_locations(selected attractions)  &lt;=  trip_days", "1")
    story.append(Paragraph(
        "Equation (1) forbids visiting more distinct destinations than there are days. Moods stored "
        "on the trip are the union of attraction mood tags and UI moods, truncated to three.",
        s["body"],
    ))

    story.append(Paragraph("D. Destination Block Allocation", s["h2"]))
    story.append(Paragraph(
        "Attractions are grouped by destination in user selection order (no travelling-salesman "
        "reordering). Let <i>D</i> be the number of destinations and <i>N</i> the trip length. "
        "Base length is <i>N</i> // <i>D</i>; remainder <i>r</i> = <i>N</i> mod <i>D</i> is given "
        "to later destinations:",
        s["body"],
    ))
    eq(
        story, s,
        "block_i = floor(N/D) + 1[ i &gt;= D - r ]",
        "2",
    )
    story.append(Paragraph(
        "Example encoded in comments: a 7-day trip Colombo -&gt; Batticaloa -&gt; Hambantota "
        "yields days 1-2, 3-4, and 5-7. If a destination occupies several days, attractions are "
        "spread one-per-day with overflow on the last day of the block. Spare days with no remaining "
        "sights receive a synthetic activity Explore {destination}.",
        s["body"],
    ))

    story.append(Paragraph("E. Clock-Time Heuristic", s["h2"]))
    story.append(Paragraph(
        "Start hour is the mean of a mood lookup (decimal hours). Spiritual = 6.5, Adventure = 7.5, "
        "Explore = Excited = 8.0, Curious = 8.5, Happy = Authentic = 9.0, Healing = 9.5, "
        "Peaceful = 10.0, Relaxed = 10.5. Empty mood list defaults to 8.5 (08:30). The first "
        "activity may be delayed by a category/name bias, then clamped to [5.0, 14.0]. Gaps: "
        "3.0 h for two activities, 2.5 h for three, 2.0 h for four or more. If the cursor lies in "
        "[12.0, 13.0) it snaps to 13.0 (lunch). If the cursor reaches 20.0 it is capped at 19.5.",
        s["body"],
    ))

    story.append(Paragraph("F. Hotel Filter and Budget", s["h2"]))
    story.append(Paragraph(
        "Default split is 25% food, 35% accommodation, 15% shopping, 25% transport "
        "(must sum to 100%). Nightly USD budget is accommodation_amount / max(days - 1, 1), "
        "converted at 300 LKR per USD. Room rates: Single = price_min; Family = price_max; "
        "Double = (price_min + price_max) / 2. Hotels whose nightly rate exceeds the cap are "
        "dropped. Matching is ILIKE on normalised local authority, authority, and address--not "
        "Haversine (unlike SOS).",
        s["body"],
    ))

    story.append(Paragraph("G. Discover Recommendations", s["h2"]))
    story.append(Paragraph(
        "Businesses, agencies, and guides are filtered by destination substring. If empty, a "
        "hard-coded nearby-city map is tried; if still empty, a global top-100 fallback is returned. "
        "Remaining spend shown to the user is food + shopping + transport.",
        s["body"],
    ))

    story.append(Paragraph("H. Approaches Considered and Final Choice", s["h2"]))
    story.append(Paragraph(
        "No sklearn models were trained on attractions. An LLM path was prototyped in naming only "
        "(unused API key). Collaborative filtering was not implemented because the catalogue has "
        "no large rating matrix. The final heuristic planner was selected for (i) explainability "
        "in an undergraduate viva, (ii) zero inference cost, and (iii) stable outputs for PDF "
        "export. scikit-learn 1.5.1 appears in requirements.txt solely for the wellness component.",
        s["body"],
    ))

    story.append(Paragraph("IV. RESULTS", s["h1"]))
    story.append(Paragraph(
        "This component does not produce classifier accuracy. Reportable quantitative results are "
        "catalogue cardinalities (Table I), algorithm constants (Table II), and a 12-step "
        "integration test that asserts HTTP success from health check through PDF, not itinerary "
        "quality. There is no ablation of ranking models because ranking is binary mood inclusion, "
        "not a scored list (attractions are ordered alphabetically).",
        s["body"],
    ))
    tbl(
        story, s, "TABLE II",
        "Implemented constants (from ai_service.py, trip_plan_service.py, budget_service.py).",
        ["Parameter", "Value"],
        [
            ["Default day start", "08:30 (decimal 8.5)"],
            ["Mood start range", "06:30-10:30"],
            ["First-activity clamp", "[05:00, 14:00]"],
            ["Inter-activity gap (2 / 3 / 4+ stops)", "3.0 h / 2.5 h / 2.0 h"],
            ["Lunch window snap", "[12:00, 13:00) -&gt; 13:00"],
            ["Evening cap", "19:30"],
            ["Location fuzzy threshold", "0.88"],
            ["LKR per USD", "300"],
            ["Default budget split (F/A/S/T)", "25 / 35 / 15 / 25 %"],
            ["Max moods", "3"],
            ["Hotels per destination", "1"],
            ["API smoke test steps", "12"],
        ],
        [100 * mm, 74 * mm],
    )
    story.append(Paragraph(
        "Persistence: trip drafts in <font face='Courier' size='9'>user_trip_input</font> and "
        "<font face='Courier' size='9'>budget_split</font>; generated plans as JSONB in "
        "<font face='Courier' size='9'>generated_itinerary</font>. History is listed by "
        "<font face='Courier' size='9'>GET /api/itinerary/history</font>.",
        s["body"],
    ))

    story.append(Paragraph("V. DISCUSSION", s["h1"]))
    story.append(Paragraph("A. What the Component Enables", s["h2"]))
    story.append(Paragraph(
        "A completed itinerary gives the tourist a timed plan and, more importantly for the "
        "platform, a logged-in identity that SOS and wellness reuse. Heuristic times make the "
        "PDF look like a real day rather than an unordered list, which matters for demonstration "
        "and for user trust even without an ML ranker.",
        s["body"],
    ))
    story.append(Paragraph("B. Limitations", s["h2"]))
    bullets(story, s, [
        "No road-network or public-transport times; destination order is selection order, not TSP.",
        "Hotel matching is string ILIKE, so a beach hotel in a neighbouring Pradeshiya Sabha may be missed.",
        "Mood filtering is include/exclude; there is no relevance score.",
        "Activity durations and opening hours are not modelled; every attraction occupies one slot.",
        "A tight accommodation budget can return zero hotels (no relaxation strategy).",
        "Fuzzy match at 0.88 can mis-map local-authority names; review JSON exists but is manual.",
        "The 12-step test does not score whether 08:30 is a sensible start at a given site.",
    ])
    story.append(Paragraph("C. Future Work", s["h2"]))
    story.append(Paragraph(
        "With more time: OpenStreetMap driving matrices between consecutive stops; duration-aware "
        "packing; learning-to-rank from saved itineraries; automatic budget relaxation; A/B of "
        "mood-mean start versus user-chosen start. Those are explicitly out of the current release.",
        s["body"],
    ))

    story.append(Paragraph("VI. CONCLUSION", s["h1"]))
    story.append(Paragraph(
        "The Tour Ceylon itinerary component is a constraint-based planner over 350 attractions "
        "and 937 hotels, with deterministic block allocation and clock heuristics. It is suitable "
        "to describe in IEEE methods as a rule-based information system, not as a machine-learning "
        "result. Its value in the overall system is a complete, exportable trip plus a shared "
        "tourist identity for SOS and wellness.",
        s["body"],
    ))

    story.append(Paragraph("REFERENCES", s["h1"]))
    refs = [
        "[1] P. J. Pedregosa et al. are not used in this component; scikit-learn in the monorepo supports wellness only.",
        "[2] Flask documentation, Pallets Projects, version 3.0, 2024. [Online]. Available: https://flask.palletsprojects.com/",
        "[3] SQLAlchemy 2.0 documentation, 2024. [Online]. Available: https://docs.sqlalchemy.org/",
        "[4] PostgreSQL Global Development Group, PostgreSQL 16 documentation.",
        '[5] React, "React 18 documentation," Meta, 2024.',
        '[6] Vite.js, "Vite 5 documentation," 2024.',
        "[7] Python Software Foundation, difflib.SequenceMatcher, Python 3 Library Reference.",
        "[8] ReportLab Ltd., ReportLab PDF Library 4.2.2 User Guide, 2024.",
        "[9] Sri Lanka Tourism Development Authority (SLTDA) style registries as ingested Excel/CSV catalogues (attractions, accommodation, agencies, guides) in backend/data/travel/.",
        "[10] Tour Ceylon, backend/app/services/ai_service.py and trip_plan_service.py, source code, 2026.",
        "[11] Tour Ceylon, backend/scripts/travel/test_api_flow.py, 12-step HTTP integration test, 2026.",
        '[12] Fielding, R. T., "Architectural Styles and the Design of Network-based Software Architectures," Ph.D. dissertation, Univ. of California, Irvine, 2000 (REST constraints used by the /api surface).',
    ]
    for r in refs:
        story.append(Paragraph(r, s["ref"]))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph(
        "Note: Do not report classifier F1 or millisecond inference for this component; those metrics belong to the wellness report.",
        s["foot"],
    ))
    return story


# ---------------------------------------------------------------------------
# 2. SOS
# ---------------------------------------------------------------------------
def story_sos(s):
    story = []
    front_matter(
        story, s,
        title="SOS System: One-Tap Tourist Emergency Routing with Haversine Nearest-Station Assignment",
        abstract=(
            "Tourists in an unfamiliar country rarely know which police desk covers their GPS "
            "coordinate. This paper describes Tour Ceylon SOS: a progressive web app (port 5175) "
            "and a station-scoped police live desk (port 5176) on the same Flask API (port 5002). "
            "A single tap among six incident types requests a fresh high-accuracy geolocation "
            "(maximumAge 0, timeout 20 000 ms, no watchPosition) and creates an incident assigned "
            "to exactly one dispatchable station. Assignment is nearest neighbour on the WGS84 "
            "sphere with Earth radius 6371 km (Haversine). Of 73 police rows loaded from Excel, "
            "coordinate clustering at 4 decimal degrees (~11 m) yields 44 dispatchable desks; "
            "duplicate headquarters and rows without coordinates are excluded. A hospital registry "
            "of 42 facilities (40 with coordinates, 2 hotline-only) supports a separate dialer; "
            "hospitals are not auto-dispatched. Workflow is strictly forward: open, acknowledged, "
            "dispatched, closed. Chat, encrypted PII (Fernet), optional Twilio/SendGrid, and a "
            "closed-case PDF complete the loop. No machine-learning accuracy is claimed. "
            "Operational metrics (volume by day, minutes-to-acknowledge on closed cases) are "
            "exposed to officers. Limitations include great-circle versus road distance and "
            "one-shot location (continuous ping returns HTTP 409)."
        ),
        keywords=(
            "emergency response, Haversine, nearest neighbour, geolocation, PWA, "
            "incident workflow, Sri Lanka Police, Leaflet"
        ),
        author=AUTHORS["sos"],
    )

    story.append(Paragraph("I. INTRODUCTION", s["h1"]))
    story.append(Paragraph(
        "Emergency numbers and local police geography are not obvious to visitors. Tour Ceylon SOS "
        "converts a typed emergency and a GPS fix into a case at the nearest dispatchable desk, "
        "then lets that desk acknowledge, dispatch, and close the case while chatting with the "
        "tourist. The design goals encoded in source comments are: (i) do not spam all 73 loaded "
        "desks; (ii) capture location only at SOS time; (iii) encrypt passport/phone at rest; "
        "(iv) reuse Tour Ceylon login so tourists do not register twice.",
        s["body"],
    ))

    story.append(Paragraph("II. SYSTEM CONTEXT", s["h1"]))
    story.append(Paragraph(
        "The tourist client is React 18 + Vite 5 with vite-plugin-pwa 0.20.5 (Workbox NetworkFirst "
        "for API). The police client adds Leaflet 1.9.4, react-leaflet 4.2.1, and Recharts 2.12.7. "
        "Both proxy <font face='Courier' size='9'>/api</font> to Flask. SOS tables are created by "
        "SQLAlchemy in <font face='Courier' size='9'>seed_sos_data.py</font> (they are not in the "
        "travel <font face='Courier' size='9'>schema.sql</font>). PII uses cryptography 42.0.8 "
        "Fernet. Maps use OpenStreetMap tiles. Icons: lucide-react 0.454.0.",
        s["body"],
    ))
    tbl(
        story, s, "TABLE I",
        "SOS data loaded from backend/data/sos/ Excel workbooks after seed rules.",
        ["Entity", "Count", "Notes"],
        [
            ["Police rows (Excel)", "73", "One officer login per row"],
            ["Dispatchable stations", "44", "After 4-d.p. coordinate clustering"],
            ["Non-dispatchable desks", "29", "Shared HQ coords or missing lat/lng"],
            ["Government hospitals", "37", "All geocoded"],
            ["Private / hotline rows", "5", "3 geo + 2 hotline-only"],
            ["Hospitals used for geo match", "40", "is_hotline_only = false"],
            ["Incident types", "6", "general, medical, rape, theft, accident, harassment"],
            ["Workflow states", "4", "open -&gt; acknowledged -&gt; dispatched -&gt; closed"],
        ],
        [58 * mm, 32 * mm, 84 * mm],
    )

    story.append(Paragraph("III. METHODOLOGY", s["h1"]))
    story.append(Paragraph("A. Client Geolocation", s["h2"]))
    story.append(Paragraph(
        "Hook <font face='Courier' size='9'>useGeolocation.getCurrent()</font> calls "
        "navigator.geolocation.getCurrentPosition with enableHighAccuracy true, maximumAge 0 "
        "(no cached fix), and timeout 20 000 ms. Horizontal accuracy is stored on "
        "<font face='Courier' size='9'>location_pings.accuracy</font> but is not a routing weight. "
        "If permission is denied, SOS aborts; there is no last-known fallback at trigger time "
        "(last_known_lat/lng on the tourist row is updated after a successful create).",
        s["body"],
    ))

    story.append(Paragraph("B. Haversine Assignment", s["h2"]))
    story.append(Paragraph(
        "Let phi, lambda be WGS84 latitude and longitude in radians. With R = 6371 km,",
        s["body"],
    ))
    eq(
        story, s,
        "a = sin^2(dphi/2) + cos(phi1) cos(phi2) sin^2(dlambda/2),   d = 2 R arcsin(sqrt(a))",
        "1",
    )
    story.append(Paragraph(
        "Function <font face='Courier' size='9'>nearest_entity</font> scans all candidates with "
        "non-null coordinates and returns the minimum <i>d</i>. Distance is stored to three decimal "
        "places as <font face='Courier' size='9'>distance_to_station_km</font>. There is no OSRM "
        "or Google Directions hop; terrain and one-way roads are ignored. If no dispatchable "
        "station remains, the code retries all stations that have coordinates.",
        s["body"],
    ))

    story.append(Paragraph("C. Dispatchable-Desk Deduplication", s["h2"]))
    story.append(Paragraph(
        "COORD_PRECISION = 4 rounds latitude and longitude (~11 m). Rows that share a rounded "
        "pair form a cluster; all but one are marked is_dispatchable = false. The survivor prefers "
        "a row with Division set, else the lowest id. Rows missing coordinates are never dispatchable. "
        "This prevents several Colombo HQ labels at the same pin from all receiving the same SOS.",
        s["body"],
    ))

    story.append(Paragraph("D. Incident Types and Workflow", s["h2"]))
    story.append(Paragraph(
        "Types: general, medical, rape (UI label Assault; aliases rape/assault, assault), theft, "
        "accident, harassment. Unknown strings collapse to general. Status transitions are "
        "monotonic: a closed case cannot reopen; backward steps are rejected in "
        "<font face='Courier' size='9'>_transition</font>. Closing sets tracking_active false "
        "(already false by product policy). Police endpoints: PATCH acknowledge, dispatch, close. "
        "Tourist poll: GET status every 5 s. Police queue poll: 7 s with an audio cue on new open "
        "cases. Chat poll: 4 s. Police incident-detail poll: 8 s. Messages are scoped to the assigned station_id in the officer JWT.",
        s["body"],
    ))

    story.append(Paragraph("E. Hospital Dialer versus Dispatch", s["h2"]))
    story.append(Paragraph(
        "GET /api/hospitals/nearest uses the same Haversine scan over geo hospitals. The tourist UI "
        "opens a tel: link. incident.hospital_id remains null; hospital_notified_at is never set "
        "in current routes. Hotline-only rows are a fallback if no geo hospital exists.",
        s["body"],
    ))

    story.append(Paragraph("F. Privacy, Notifications, Export", s["h2"]))
    story.append(Paragraph(
        "Phone, passport/NIC, and emergency-contact fields are Fernet-encrypted. Continuous "
        "tracking was removed: POST .../ping returns 409. Notifications default to console logs "
        "(NOTIFY_MODE); Twilio SMS and SendGrid email are optional. Closed cases export via "
        "ReportLab (GET .../report.pdf). Travel-to-SOS identity uses POST /api/tourists/bridge-travel.",
        s["body"],
    ))

    story.append(Paragraph("G. Approaches Considered", s["h2"]))
    story.append(Paragraph(
        "Road-network routing would better match how a patrol car drives; it was not integrated. "
        "Broadcasting every desk would maximise recall of someone seeing the SOS but would violate "
        "the spam constraint and the station-scoped JWT model. An ML classifier of incident type "
        "from free text is unnecessary because the tourist taps a labelled button. The selected "
        "stack is deterministic geometry plus a finite-state workflow--appropriate where false "
        "dispatch to the wrong town is more serious than a few extra kilometres of great-circle error.",
        s["body"],
    ))

    story.append(Paragraph("IV. RESULTS", s["h1"]))
    story.append(Paragraph(
        "Routing is exact nearest neighbour among the 44 dispatchable coordinates; there is no "
        "confusion matrix against a jurisdictional ground-truth layer (none is in the repository). "
        "Table II lists measurable system parameters. GET /api/incidents/stats (officer JWT) returns "
        "volume_by_day, minutes_to_ack = (acknowledged_at - triggered_at)/60 for closed cases "
        "with both timestamps, counts by type, and active/closed totals. Demo seed data uses "
        "synthetic acknowledge delays of approximately 5 min (medical) and 10 min (theft); those "
        "are fixtures, not a field trial. A micro-benchmark of Haversine nearest-neighbour over 44 "
        "synthetic coordinates (1000 repeats, CPython on the development PC) took 44.4 ms total, "
        "i.e. 0.044 ms per full scan. No automated unit test of Haversine was found in-repo.",
        s["body"],
    ))
    tbl(
        story, s, "TABLE II",
        "Implemented SOS parameters and polling intervals.",
        ["Parameter", "Value"],
        [
            ["Earth radius R", "6371 km"],
            ["Coordinate cluster precision", "4 decimal degrees (~11 m)"],
            ["Geolocation timeout", "20 000 ms"],
            ["maximumAge / watchPosition", "0 / not used"],
            ["Tourist status poll", "5 s"],
            ["Chat poll", "4 s"],
            ["Police queue poll", "7 s"],
            ["Police incident-detail poll", "8 s"],
            ["Distance storage", "round(d, 3) km"],
            ["Default notify channel", "console (Twilio/SendGrid optional)"],
            ["PWA plugin", "vite-plugin-pwa 0.20.5"],
            ["Map library", "Leaflet 1.9.4"],
            ["Haversine nearest-of-44 (bench, 1000 scans)", "mean 0.044 ms / scan"],
        ],
        [90 * mm, 84 * mm],
    )
    story.append(Paragraph(
        "End-to-end path: tap type -&gt; overlay + optional vibrate -&gt; getCurrent -&gt; "
        "POST /api/incidents {tourist_id, type, lat, lng, accuracy} -&gt; assign station -&gt; "
        "one location_ping row -&gt; notify station / emergency contact / hotel if present -&gt; "
        "tourist workflow + chat -&gt; police PATCH chain -&gt; optional PDF.",
        s["body"],
    ))

    story.append(Paragraph("V. DISCUSSION", s["h1"]))
    story.append(Paragraph("A. System-Level Value", s["h2"]))
    story.append(Paragraph(
        "SOS is the safety backstop for the itinerary product: the same tourist record that booked "
        "moods and hotels can raise a typed emergency without explaining Sri Lankan police geography. "
        "Station scoping makes a live demo credible (one desk's queue, not a national flood).",
        s["body"],
    ))
    story.append(Paragraph("B. Limitations", s["h2"]))
    bullets(story, s, [
        "Great-circle distance can rank a station across a mountain or lagoon ahead of a farther-but-faster road desk.",
        "GPS accuracy is stored but unused; indoor/urban-canyon error is unmodelled.",
        "29 of 73 rows never receive SOS traffic by construction.",
        "One-shot location: the police map is not a live track (product decision, HTTP 409 on ping).",
        "Hospital is tourist-initiated dialling only.",
        "Polling (4-8 s) is not WebSocket push; officers may see new cases a few seconds late.",
        "Default notifications are logs unless SMS/email secrets are configured.",
        "No published field accuracy study versus actual Sri Lanka Police boundaries.",
    ])
    story.append(Paragraph("C. Future Work", s["h2"]))
    story.append(Paragraph(
        "OSRM driving time; polygon jurisdiction; availability/load of officers; WebSockets; "
        "offline PWA outbox; auto-notify nearest hospital on medical type; unit tests with known "
        "lat/lng fixtures and expected station_id.",
        s["body"],
    ))

    story.append(Paragraph("VI. CONCLUSION", s["h1"]))
    story.append(Paragraph(
        "Tour Ceylon SOS assigns one of six typed emergencies to 1 of 44 dispatchable stations "
        "using Haversine nearest neighbour (R = 6371 km) on a one-shot high-accuracy GPS fix. "
        "It should be reported as a geospatial routing and workflow system. Classifier F1 is not "
        "applicable. The component's importance is a privacy-aware, station-scoped emergency path "
        "bound to the same tourist identity as the itinerary planner.",
        s["body"],
    ))

    story.append(Paragraph("REFERENCES", s["h1"]))
    refs = [
        '[1] R. W. Sinnott, "Virtues of the Haversine," Sky and Telescope, vol. 68, no. 2, p. 159, 1984.',
        '[2] W3C, "Geolocation API," W3C Recommendation, 2022. [Online]. Available: https://www.w3.org/TR/geolocation/',
        '[3] Leaflet, "Leaflet 1.9.4 documentation," 2023. [Online]. Available: https://leafletjs.com/',
        "[4] OpenStreetMap contributors, tile service {s}.tile.openstreetmap.org, ODbL.",
        "[5] Pallets, Flask 3.0 documentation, 2024.",
        "[6] Flask-JWT-Extended 4.6.0 documentation.",
        '[7] Cryptography.io, "Fernet (symmetric encryption)," 2024.',
        "[8] ReportLab 4.2.2, PDF generation for closed incident reports.",
        "[9] Vite PWA (vite-plugin-pwa 0.20.5) and Workbox, Progressive Web App caching.",
        "[10] Recharts 2.12.7, police analytics charts.",
        "[11] Tour Ceylon, backend/app/services/routing.py (haversine_km, nearest_entity), 2026.",
        "[12] Tour Ceylon, backend/seed_sos_data.py, COORD_PRECISION = 4, 2026.",
        "[13] Tour Ceylon, frontend/tourist/src/hooks/useGeolocation.js, 2026.",
    ]
    for r in refs:
        story.append(Paragraph(r, s["ref"]))
    return story


# ---------------------------------------------------------------------------
# 3. WELLNESS
# ---------------------------------------------------------------------------
def story_wellness(s):
    story = []
    front_matter(
        story, s,
        title="Wellness Platform: Hybrid Dosha Classification and Weighted Centre Matching for Ayurveda and Spiritual Tourism in Sri Lanka",
        abstract=(
            "This paper presents the wellness component of Tour Ceylon: a hybrid matcher that "
            "combines a Random Forest dosha (Vikruti) classifier with a transparent linear ranker "
            "over 83 curated centres (37 Curative, 32 Wellness/Rejuvenative, 14 Spiritual/Meditation). "
            "Tourists follow one of two paths--Ayurveda (69 centres, 12 conditions) or spiritual "
            "retreat (14 centres, 6 retreat types)--and complete a six-feature quiz (age, gender, "
            "sleep, appetite, temperature sensitivity, emotional tendency). The production classifier "
            "is sklearn.ensemble.RandomForestClassifier with n_estimators = 100 and random_state = 42, "
            "trained at Flask import on 102 labelled profiles after dropping 8 Balanced (N/A) rows "
            "from a 110-row workbook (6 real Ayya's Case records and 104 expert-augmented rows). "
            "An offline six-model comparison file reports Random Forest accuracy 0.81, precision 0.832, "
            "recall 0.81, and F1-score 0.794, outperforming Decision Tree (F1 0.705), ANN (0.667), "
            "Naive Bayes (0.567), SVM (0.360), and k-NN (0.332). Centre score uses weights 0.35 "
            "condition, 0.20 dosha, 0.25 NLP quality/5, 0.20 budget. Ablation of those terms shows "
            "the full model average quality 4.484 versus 3.845 for condition-only. Timed on the "
            "development PC, predict_dosha() mean inference is 7.94 ms (n=200, p50 7.76 ms, p95 9.06 ms); "
            "joblib dump of the fitted RF is 406.97 KB. Outcome percentages "
            "in the UI are illustrative, not clinical claims. Limitations include the small real "
            "labelled set, 50/83 centres with unspecified dosha focus, and the absence of the original "
            "training notebook in the repository."
        ),
        keywords=(
            "Random Forest, Ayurveda, dosha classification, recommender systems, "
            "ablation study, scikit-learn, wellness tourism, Sri Lanka"
        ),
        author=AUTHORS["wellness"],
    )

    story.append(Paragraph("I. INTRODUCTION", s["h1"]))
    story.append(Paragraph(
        "Sri Lanka offers Ayurvedic hospitals, wellness resorts, and meditation monasteries without "
        "a single tourist-facing matcher that jointly considers presenting condition, constitution "
        "(dosha), budget, and review-derived quality. The wellness component (Vite MPA, port 5181) "
        "fills that role inside the Tour Ceylon monolith. Machine learning is used only for dosha "
        "prediction. Centre ranking is a documented weighted sum so that an examiner can recompute "
        "a score by hand. Duration and outcome-likelihood maps are expert- and literature-informed "
        "lookups and are labelled in the UI as non-clinical.",
        s["body"],
    ))

    story.append(Paragraph("II. RELATED WORK AND DATA SOURCES", s["h1"]))
    story.append(Paragraph(
        "Dosha (Vata, Pitta, Kapha) classification in software often uses questionnaires plus "
        "classical decision rules. This project replaces purely hand-coded rules with a Random "
        "Forest trained on a mixed real/augmented table, then keeps the ranker linear for "
        "auditability. Review quality is precomputed (nlp_quality on a 5-point scale) rather than "
        "inferred at request time by a transformer. Spiritual matching still runs dosha prediction "
        "even though many retreats are constitution-agnostic--an acknowledged limitation.",
        s["body"],
    ))
    tbl(
        story, s, "TABLE I",
        "Centre pool (full_candidate_pool.json) and training workbook.",
        ["Item", "Value"],
        [
            ["Centres (JSON bytes)", "83 (102,918 bytes)"],
            ["Curative / Wellness / Spiritual", "37 / 32 / 14"],
            ["Ayurveda path pool", "69 (non-spiritual)"],
            ["Dosha focus General/Unspecified", "50 of 83"],
            ["Dosha focus Vata / Pitta / Kapha / Balanced", "11 / 3 / 3 / 16"],
            ["Training workbook rows", "110"],
            ["Labelled after dropping Balanced (N/A)", "102"],
            ["Data origin REAL / AUGMENTED", "6 / 104"],
            ["Label counts before Balanced drop", "Vata 53, Pitta 33, Kapha 16, Balanced 8"],
            ["Features", "6 (Age + 5 categorical)"],
            ["sklearn version", "1.5.1"],
        ],
        [100 * mm, 74 * mm],
    )

    story.append(Paragraph("III. METHODOLOGY", s["h1"]))
    story.append(Paragraph("A. Technical Setup", s["h2"]))
    story.append(Paragraph(
        "Service: <font face='Courier' size='9'>backend/app/services/matching_engine.py</font>. "
        "Routes: <font face='Courier' size='9'>/api/recommend</font>, <font face='Courier' size='9'>/api/match</font>, "
        "admin CRUD and analytics. Persistence is dual: JSON is authoritative for matching; "
        "PostgreSQL tables wellness_centers, wellness_reviews, wellness_condition_mappings, and "
        "wellness_matching_sessions follow MVC. Admin password defaults to a shared demo secret "
        "overridable by WELLNESS_ADMIN_PASSWORD. Leaflet 1.9.4 renders maps. No GPU is used.",
        s["body"],
    ))

    story.append(Paragraph("B. Pipeline", s["h2"]))
    bullets(story, s, [
        "Path selection: Ayurveda (12 conditions) or Spiritual (6 retreat types).",
        "Quiz POST /api/recommend: condition, age, gender, sleep_pattern, appetite, cold_heat_sensitivity, emotional_tendency, budget_tier, optional companion_condition, top_n=6.",
        "Dosha: LabelEncoder on five categoricals; Age numeric; RF predict + predict_proba; confidence = 100 * max(proba), one decimal.",
        "Unknown quiz categories map silently to the first encoder class.",
        "Path filter on category == Spiritual/Meditation versus the complement.",
        "Weighted score (Section III-D); companion blend 0.65 primary + 0.35 companion.",
        "Keyword risk scan on Google-style review strings.",
        "Attach duration and illustrative outcome from DURATION_MAP / OUTCOME_MAP.",
        "Optional WellnessMatchingSession row if a tourist JWT is present.",
    ])

    story.append(Paragraph("C. Dosha Classifier", s["h2"]))
    story.append(Paragraph(
        "If tourist_profiles_training_data.xlsx is missing, a synthetic 240-row set (80 per dosha, "
        "12% label noise, RNG seed 42) is generated so the API still boots. In the submitted "
        "tree the xlsx exists, so synthetic data is not used. Production fit uses all 102 filtered "
        "rows (no hold-out at runtime). Hyperparameters in source: n_estimators=100, random_state=42. "
        "Epochs do not apply to Random Forest. The recorded comparison CSV is treated as the "
        "offline experiment (development Step 4). A stratified 80/20 split on 102 rows implies "
        "81 train / 21 test and reproduces five of six CSV rows in independent checks; the ANN "
        "CSV value 0.667 may not match a default MLPClassifier (max_iter=500 reproduced ~0.476). "
        "This paper therefore cites the CSV as the archived experiment and notes that the generating "
        "notebook is not in the repository.",
        s["body"],
    ))

    story.append(Paragraph("D. Weighted Ranker", s["h2"]))
    eq(
        story, s,
        "S = 0.35 s_cond + 0.20 s_dosha + 0.25 (q_nlp / 5) + 0.20 s_budget",
        "1",
    )
    story.append(Paragraph(
        "Condition: 1.0 on substring match in conditions_text, else 0.3. Dosha: 1.0 exact, "
        "0.6 General/Unspecified, 0.4 mismatch. Budget: 1.0 on tier substring, else 0.5. "
        "These rules are code, not a second learned model.",
        s["body"],
    ))

    story.append(Paragraph("E. Model Selection Rationale", s["h2"]))
    story.append(Paragraph(
        "Random Forest was selected because it recorded the highest accuracy (0.81) and F1 (0.794) "
        "in Table II. Decision Tree was second (F1 0.705) but more brittle. SVM and k-NN collapsed "
        "(F1 0.360 and 0.332), consistent with mixed categorical encodings and a small test fold. "
        "The ranker weights were retained because ablation (Table III) shows FULL best on average "
        "quality (4.484), budget alignment (0.767), and dosha compatibility (0.513).",
        s["body"],
    ))

    story.append(Paragraph("IV. RESULTS", s["h1"]))
    tbl(
        story, s, "TABLE II",
        "Dosha classifier comparison (verbatim: backend/data/wellness/model_comparison_results.csv).",
        ["Model", "Accuracy", "Precision", "Recall", "F1-score"],
        [
            ["Random Forest (selected)", "0.810", "0.832", "0.810", "0.794"],
            ["Decision Tree", "0.714", "0.702", "0.714", "0.705"],
            ["Neural network (ANN)", "0.667", "0.667", "0.667", "0.667"],
            ["Naive Bayes", "0.571", "0.589", "0.571", "0.567"],
            ["SVM", "0.524", "0.274", "0.524", "0.360"],
            ["k-NN", "0.381", "0.325", "0.381", "0.332"],
        ],
        [50 * mm, 31 * mm, 31 * mm, 31 * mm, 31 * mm],
    )
    tbl(
        story, s, "TABLE III",
        "Matching-weight ablation (verbatim: ablation_results.json). Dosha_n is the evaluation subset size.",
        ["Configuration", "Avg. quality", "Budget align.", "Dosha compat.", "dosha_n"],
        [
            ["FULL", "4.484", "0.767 (76.7%)", "0.513 (51.3%)", "39"],
            ["NO-DOSHA", "4.411", "0.733", "0.237", "38"],
            ["NO-NLP-QUALITY", "4.044", "0.733", "0.450", "40"],
            ["NO-BUDGET", "4.443", "0.433", "0.476", "42"],
            ["CONDITION-ONLY", "3.845", "0.417", "0.290", "31"],
        ],
        [42 * mm, 32 * mm, 36 * mm, 36 * mm, 28 * mm],
    )
    story.append(Paragraph(
        "Live analytics from get_analytics(): mean nlp_quality 4.24 / 5; 4 flagged reviews on 4 "
        "centres. Duration examples: Arthritis 18-25 days (expert 21-day case); Stress/Anxiety "
        "25-35 days; Migraine 14-30 days tourist-adapted versus a literature 90-day protocol "
        "(n=406 cited in comments). Illustrative outcome map examples: Arthritis 78%, Sciatica 80%, "
        "Skin 60%. Runtime was measured on the development workstation after a single warmup call: "
        "predict_dosha() mean 7.935 ms over 200 trials (median 7.756 ms, 95th percentile 9.055 ms, "
        "min 6.587 ms). joblib serialisation of the fitted RandomForestClassifier is 416 737 bytes "
        "(406.97 KB). Ranking 69 Ayurveda centres with match_centers() mean 1.276 ms over 100 trials "
        "(median 1.217 ms, 95th percentile 1.820 ms). These are CPU times in CPython, not GPU. "
        "A single-quiz predict_proba peak of 94.0% on one Vata example is a confidence score, not "
        "hold-out accuracy; classifier accuracy remains 0.81 from Table II.",
        s["body"],
    ))
    tbl(
        story, s, "TABLE IV",
        "Measured runtime and artefact size (development PC, scikit-learn 1.5.1, n_estimators=100).",
        ["Quantity", "Value", "Protocol"],
        [
            ["RF features / trees / train rows", "6 / 100 / 102", "matching_engine.py import fit"],
            ["predict_dosha() mean", "7.94 ms", "200 trials after 1 warmup"],
            ["predict_dosha() median / p95", "7.76 ms / 9.06 ms", "same run"],
            ["RF joblib size", "406.97 KB (416 737 B)", "joblib.dump of DOSHA_MODEL"],
            ["match_centers() mean (Ayurveda, top_n=6)", "1.28 ms", "100 trials, 69-centre pool"],
        ],
        [70 * mm, 52 * mm, 52 * mm],
    )
    tbl(
        story, s, "TABLE V",
        "Selected duration / outcome lookups (matching_engine.py). Outcome % is not a clinical claim.",
        ["Condition", "Duration range", "Illustrative %", "Source note in code"],
        [
            ["Arthritis", "18-25 days", "78", "Domain expert 21-day case; n=406 migraine study as reference class"],
            ["Sciatica", "18-25 days", "80", "1 documented full-recovery case + literature pattern"],
            ["Hypertension", "12-18 days", "68", "Ayurveda Sarana Beach Hospital market case"],
            ["Detox / weight", "10-16 days", "72", "Heritance Ayurveda 14 days / 5 kg report"],
            ["Migraine", "14-30 days (adapted)", "71", "Literature protocol n=406, 90-day course"],
            ["General wellness", "3-7 days", "85", "Subjective relaxation, high self-report"],
        ],
        [32 * mm, 38 * mm, 28 * mm, 76 * mm],
    )

    story.append(Paragraph("V. DISCUSSION", s["h1"]))
    story.append(Paragraph("A. Contribution to Tour Ceylon", s["h2"]))
    story.append(Paragraph(
        "Wellness is the only module with a trained classifier and a recorded model bake-off. "
        "It turns the platform from plan-a-route-and-call-for-help into personalised health-and-retreat "
        "discovery, using the same tourist JWT when present. Admin analytics surface Table II-III "
        "so a panel can inspect the same numbers as this report.",
        s["body"],
    ))
    story.append(Paragraph("B. Limitations", s["h2"]))
    bullets(story, s, [
        "Only 6 real Vikruti cases; 104 rows are expert-rule augmentations (70/30 dominant/overlap).",
        "Production RF is fit on all 102 rows; CSV metrics are an offline hold-out artifact.",
        "50 of 83 centres have unspecified dosha focus, so s_dosha is often 0.6 by default.",
        "Risk detection is a keyword list (unhygienic, scam, unsafe, …), not a text classifier.",
        "OOV quiz answers silently become the first LabelEncoder class.",
        "Spiritual path still predicts dosha, which may be weakly relevant.",
        "Outcome percentages must not be quoted as treatment efficacy in a medical sense.",
        "Training script/notebook not versioned; ANN CSV row may be irreproducible with default MLP.",
        "Admin authentication is a shared password, not per-user RBAC.",
    ])
    story.append(Paragraph("C. Future Work", s["h2"]))
    story.append(Paragraph(
        "Nested cross-validation on a larger real labelled set; class-weighting for Kapha (16 rows); "
        "separate spiritual ranker without dosha; transformer review NLP; logged inference latency; "
        "serialize the fitted RF to disk instead of refitting at every process start.",
        s["body"],
    ))

    story.append(Paragraph("VI. CONCLUSION", s["h1"]))
    story.append(Paragraph(
        "The wellness component is a hybrid system: Random Forest dosha classification "
        "(n_estimators=100, recorded F1 0.794) and a four-term linear centre ranker (full ablation "
        "quality 4.484 vs 3.845 condition-only) over 83 centres. These are the numbers that belong "
        "in an IEEE results section. Itinerary and SOS, by contrast, are heuristic and geospatial "
        "respectively and must not inherit these F1 scores.",
        s["body"],
    ))

    story.append(Paragraph("REFERENCES", s["h1"]))
    refs = [
        '[1] L. Breiman, "Random Forests," Machine Learning, vol. 45, pp. 5-32, 2001.',
        '[2] F. Pedregosa et al., "Scikit-learn: Machine Learning in Python," J. Mach. Learn. Res., vol. 12, pp. 2825-2830, 2011.',
        "[3] scikit-learn developers, RandomForestClassifier, DecisionTreeClassifier, MLPClassifier, GaussianNB, SVC, KNeighborsClassifier, version 1.5.1, 2024.",
        "[4] pandas 2.2.2 and openpyxl 3.1.5, training-table I/O.",
        "[5] Domain expert case set labelled Ayya's Case (6 real profiles) and expert-rule augmentation (104 rows, 70/30 dominant/overlap) in tourist_profiles_training_data.xlsx.",
        "[6] Comment citation: migraine clinical protocol literature (n=406, 90-day course)--full bibliographic details must be inserted by the authors before camera-ready submission.",
        "[7] Market cross-check notes: Ayurveda Sarana Beach Hospital (hypertension duration); Heritance Ayurveda (14-day detox, 5 kg report).",
        "[8] S. N. Goenka tradition, ten-day Vipassana course structure (used in get_session_schedule).",
        "[9] Leaflet 1.9.4, map UI for centres.",
        "[10] Tour Ceylon, backend/app/services/matching_engine.py, WEIGHTS and DOSHA_MODEL, 2026.",
        "[11] Tour Ceylon, backend/data/wellness/model_comparison_results.csv and ablation_results.json, 2026.",
        "[12] Tour Ceylon, backend/data/wellness/full_candidate_pool.json, 83-centre pool, 2026.",
    ]
    for r in refs:
        story.append(Paragraph(r, s["ref"]))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph(
        "Disclaimer: Treatment durations and outcome percentages are decision-support illustrations for a tourism information system. They are not medical advice or validated clinical endpoints.",
        s["foot"],
    ))
    return story


def main():
    s = styles()
    specs = [
        (
            OUT_DIR / "IEEE_Itinerary_Component_Report.pdf",
            story_itinerary(s),
            "IEEE-style report: AI Itinerary Generator",
            AUTHORS["itinerary"]["name"],
        ),
        (
            OUT_DIR / "IEEE_SOS_Component_Report.pdf",
            story_sos(s),
            "IEEE-style report: SOS System",
            AUTHORS["sos"]["name"],
        ),
        (
            OUT_DIR / "IEEE_Wellness_Component_Report.pdf",
            story_wellness(s),
            "IEEE-style report: Wellness Platform",
            AUTHORS["wellness"]["name"],
        ),
    ]
    for path, story, running, author in specs:
        build_doc(path, story, running, author)
        print(f"Wrote {path} ({path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
