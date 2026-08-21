"""
Generate Itinerary Generator — Demonstration Guide PDF.

For panel / viva: explains login → wizard → how itinerary is built (file by file).

Run:
  cd backend
  .\\.venv\\Scripts\\activate
  python ..\\docs\\generate_itinerary_demo_guide_pdf.py

Output:
  docs/pdfs/Itinerary_Generator_Demo_Guide.pdf
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
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

OUT = Path(__file__).resolve().parent / "pdfs" / "Itinerary_Generator_Demo_Guide.pdf"
OUT.parent.mkdir(parents=True, exist_ok=True)

TEAL = colors.HexColor("#0A4A52")
INK = colors.HexColor("#1A2332")
MUTED = colors.HexColor("#5A6570")
LINE = colors.HexColor("#D0DCE0")
PANEL = colors.HexColor("#F7FAFA")
GREEN = colors.HexColor("#1a7f4b")


def S():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "T", parent=base["Title"], fontSize=22, textColor=TEAL,
            alignment=TA_CENTER, spaceAfter=6, fontName="Helvetica-Bold",
        ),
        "sub": ParagraphStyle(
            "Sub", parent=base["Normal"], fontSize=10, textColor=MUTED,
            alignment=TA_CENTER, spaceAfter=14,
        ),
        "h1": ParagraphStyle(
            "H1", parent=base["Heading1"], fontSize=14, textColor=TEAL,
            spaceBefore=14, spaceAfter=8, fontName="Helvetica-Bold",
        ),
        "h2": ParagraphStyle(
            "H2", parent=base["Heading2"], fontSize=11, textColor=INK,
            spaceBefore=10, spaceAfter=5, fontName="Helvetica-Bold",
        ),
        "body": ParagraphStyle(
            "B", parent=base["Normal"], fontSize=10, textColor=INK,
            leading=14, spaceAfter=5, alignment=TA_JUSTIFY,
        ),
        "bullet": ParagraphStyle(
            "Li", parent=base["Normal"], fontSize=10, textColor=INK, leading=13,
        ),
        "code": ParagraphStyle(
            "C", parent=base["Code"], fontName="Courier", fontSize=8,
            leading=11, textColor=INK, backColor=colors.HexColor("#F2F6F7"),
            leftIndent=4, spaceBefore=4, spaceAfter=8,
        ),
        "demo": ParagraphStyle(
            "D", parent=base["Normal"], fontSize=10, textColor=INK,
            leading=14, leftIndent=12, spaceAfter=4, fontName="Helvetica-Oblique",
        ),
        "cell": ParagraphStyle("Cell", fontSize=9, leading=12, textColor=INK),
        "cell_b": ParagraphStyle("CellB", fontSize=9, leading=12, textColor=INK, fontName="Helvetica-Bold"),
    }


def bullets(story, sty, items: list[str]):
    story.append(ListFlowable(
        [ListItem(Paragraph(i, sty["bullet"]), leftIndent=10) for i in items],
        bulletType="bullet", start="•", leftIndent=14, spaceAfter=8,
    ))


def table(story, sty, headers, rows, widths=None):
    data = [[Paragraph(f"<b>{h}</b>", sty["cell_b"]) for h in headers]]
    for row in rows:
        data.append([Paragraph(str(c), sty["cell"]) for c in row])
    if not widths:
        widths = [170 * mm / len(headers)] * len(headers)
    t = Table(data, colWidths=widths, repeatRows=1)
    cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), TEAL),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.4, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            cmds.append(("BACKGROUND", (0, i), (-1, i), PANEL))
    t.setStyle(TableStyle(cmds))
    story.append(t)
    story.append(Spacer(1, 6))


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(LINE)
    canvas.line(18 * mm, 14 * mm, A4[0] - 18 * mm, 14 * mm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(18 * mm, 8 * mm, "Tour Ceylon — Itinerary Generator Demo Guide")
    canvas.drawRightString(A4[0] - 18 * mm, 8 * mm, f"Page {doc.page}")
    canvas.restoreState()


def build():
    sty = S()
    story = []
    today = datetime.now().strftime("%d %B %Y")

    story.append(Paragraph("Tour Ceylon — Itinerary Generator", sty["title"]))
    story.append(Paragraph(
        f"Demonstration &amp; Explanation Guide<br/>From user login to day-by-day plan · {today}",
        sty["sub"],
    ))
    story.append(HRFlowable(width="100%", thickness=1, color=LINE, spaceAfter=10))

    # --- 1. Overview ---
    story.append(Paragraph("1. What you are demonstrating", sty["h1"]))
    story.append(Paragraph(
        "The <b>Travel Itinerary Generator</b> is part of Tour Ceylon. A tourist logs in, "
        "picks attractions and budget, chooses hotels, then clicks Generate to receive a "
        "<b>day-by-day timed schedule</b>. The engine is <b>rule-based</b> (not ChatGPT, not Random Forest). "
        "It reads real data from PostgreSQL and applies fixed logic for day splitting and clock times.",
        sty["body"],
    ))
    table(story, sty, ["Item", "Value"], [
        ["Travel app URL", "http://localhost:5180"],
        ["Backend API", "http://127.0.0.1:5002/api"],
        ["Database", "PostgreSQL — travel_app"],
        ["Demo flow", "Login → Attractions → Budget → Stay → Itinerary → Export PDF"],
    ], [45 * mm, 125 * mm])

    # --- 2. Login ---
    story.append(Paragraph("2. User login (before the wizard)", sty["h1"]))
    story.append(Paragraph(
        "Every trip is tied to a logged-in user. Without login, the app redirects to the login page.",
        sty["body"],
    ))
    table(story, sty, ["File", "Role"], [
        ["frontend/travel/src/pages/LoginPage.jsx", "Login / register form (email + password, optional Google)"],
        ["frontend/travel/src/context/AuthContext.jsx", "Stores JWT token in localStorage (access_token)"],
        ["frontend/travel/src/App.jsx", "ProtectedRoute — blocks wizard until authenticated"],
        ["backend/app/routes/auth.py", "POST /api/auth/login and /api/auth/register"],
        ["backend/app/models/user.py", "users table — email, password_hash"],
    ], [55 * mm, 115 * mm])

    story.append(Paragraph("Login flow (simple):", sty["h2"]))
    bullets(story, sty, [
        "User enters email + password on LoginPage.",
        "Browser calls POST /api/auth/login → auth.py checks users table.",
        "Server returns JWT access_token (valid ~7 days).",
        "Token saved in localStorage; all later API calls send Authorization: Bearer &lt;token&gt;.",
        "App redirects to /attractions — wizard step 1.",
    ])

    story.append(Preformatted(
        "POST /api/auth/login\n"
        '{ "email": "visitor@example.com", "password": "secret123" }\n'
        '→ { "access_token": "<jwt>", "user": { "id": 1, "email": "..." } }',
        sty["code"],
    ))

    story.append(PageBreak())

    # --- 3. Wizard ---
    story.append(Paragraph("3. Trip wizard (data collected before itinerary)", sty["h1"]))
    story.append(Paragraph(
        "The itinerary cannot run until steps 1–3 are complete. Each step saves data to "
        "<b>user_trip_input</b> and related tables.",
        sty["body"],
    ))
    table(story, sty, ["Step", "Page", "API", "What is saved"], [
        ["1", "AttractionsPage.jsx", "POST /api/trip-input", "days, moods, attraction IDs"],
        ["2", "BudgetPage.jsx", "POST /api/budget/split", "total budget + food/stay/shopping/transport split"],
        ["3", "AccommodationPage.jsx", "PATCH /api/trip-input", "hotel per destination + room type (Single/Double/Family)"],
        ["4", "ItineraryPage.jsx", "POST /api/itinerary/generate", "← GENERATES the plan"],
        ["5", "RecommendationsPage.jsx", "GET /api/business-directory etc.", "optional saved shops/agencies/guides"],
        ["6", "ExportPage.jsx", "GET /api/itinerary/&lt;id&gt;/pdf", "download PDF"],
    ], [12 * mm, 38 * mm, 48 * mm, 72 * mm])

    story.append(Paragraph("Backend files for steps 1–3:", sty["h2"]))
    bullets(story, sty, [
        "routes/trip_input.py — create/update trip",
        "routes/budget.py + services/budget_service.py — split budget percentages",
        "routes/accommodation.py + trip_plan_service.py — list hotels within budget",
        "models/user_trip_input.py — main trip row (days, attractions, hotels, room_type)",
        "models/budget_split.py — budget categories",
        "Data seeded from Excel: attractions.xlsx (130 places), accomadation.xlsx (944 hotels)",
    ])

    # --- 4. Itinerary generation ---
    story.append(PageBreak())
    story.append(Paragraph("4. How the itinerary is generated (core component)", sty["h1"]))
    story.append(Paragraph(
        "When the user opens Itinerary and clicks <b>Generate</b>, this chain runs:",
        sty["body"],
    ))
    story.append(Preformatted(
        "ItineraryPage.jsx\n"
        "    ↓ itineraryApi.generate() in client.js\n"
        "    ↓ POST /api/itinerary/generate\n"
        "routes/itinerary.py  (validate trip, delete old plan)\n"
        "    ↓ generate_itinerary(trip)\n"
        "services/ai_service.py  (build JSON — rules, NOT OpenAI)\n"
        "    ↳ uses trip_plan_service.py (days, cities, hotels)\n"
        "models/generated_itinerary.py  (save JSON to DB)\n"
        "    ↓ response back to browser\n"
        "ItineraryPage shows Day 1, Day 2, … with times",
        sty["code"],
    ))

    story.append(Paragraph("4.1 routes/itinerary.py — API controller", sty["h2"]))
    bullets(story, sty, [
        "Checks: attractions selected, hotels selected, budget split exists.",
        "Loads trip with get_user_trip() — user can only access own trips.",
        "Deletes previous generated_itinerary rows for this trip.",
        "Calls ai_service.generate_itinerary(trip, day_start).",
        "Saves result; returns JSON to frontend.",
    ])

    story.append(Paragraph("4.2 trip_plan_service.py — geography &amp; days", sty["h2"]))
    bullets(story, sty, [
        "ordered_attractions() — load picked places from DB in user order.",
        "get_day_plan() — split trip days across cities in <b>consecutive blocks</b> (no bouncing back). "
        "Example: 7 days, 3 cities → ~2 + 2 + 3 days.",
        "attractions_grouped_by_day() — assign each attraction to the correct day number.",
        "hotel_for_day() — which hotel name applies to each day.",
        "Does NOT assign clock times — only structure.",
    ])

    story.append(Paragraph("4.3 ai_service.py — times &amp; final JSON", sty["h2"]))
    bullets(story, sty, [
        "Despite the name, this does NOT use OpenAI or machine learning.",
        "Start time: user picks (e.g. 07:30 AM) OR Auto averages mood lookup table (MOOD_START_HOURS).",
        "First activity may shift by category (Wild/Heritage early, beach later) or name hints.",
        "_build_day_times() — spaces activities 2–3 hours apart, skips lunch hour, caps ~8 PM.",
        "Extra days in same city with no more places → 'Explore {city}' leisure block.",
        "Output: title, route, highlights, days[] with activities[{time, title, description}].",
        "Tagged source: 'database' in JSON.",
    ])

    story.append(Paragraph("4.4 generated_itinerary.py — storage", sty["h2"]))
    bullets(story, sty, [
        "Table: generated_itinerary — columns trip_id, itinerary (JSONB), created_at.",
        "Itinerary page loads this on revisit; Export page uses it for PDF.",
        "pdf_service.py reads same JSON + budget + saved references for download.",
    ])

    story.append(PageBreak())

    # --- 5. Example ---
    story.append(Paragraph("5. Worked example (what to say in demo)", sty["h1"]))
    story.append(Paragraph(
        "Suppose user picks 7 days, 3 destinations (Colombo, Batticaloa, Hambantota), "
        "one attraction per city, Double room, budget $700.",
        sty["body"],
    ))
    table(story, sty, ["Stage", "Result"], [
        ["get_day_plan()", "Days 1–2 Colombo, 3–4 Batticaloa, 5–7 Hambantota"],
        ["attractions_grouped_by_day()", "Attidiya on day 1, Thoppigala on day 3, Bird Center on day 5"],
        ["hotel_for_day()", "Zest Metropole (Colombo days), Amethyst (Batticaloa), Wild Culture (Hambantota)"],
        ["_parse_day_start()", "Adventure mood → ~7:30 AM start if Auto selected"],
        ["_build_day_times()", "7:30 AM activity, gaps for lunch, no late evening slots"],
        ["Saved JSON", "7-Day Sri Lanka Trip + day cards shown on screen"],
    ], [50 * mm, 120 * mm])

    story.append(Paragraph("Sample generate request:", sty["h2"]))
    story.append(Preformatted(
        "POST /api/itinerary/generate\n"
        "Authorization: Bearer <jwt>\n"
        '{\n'
        '  "trip_id": "cdb41679-....",\n'
        '  "day_start": "07:30 AM"\n'
        '}\n'
        "→ 201 Created with full itinerary JSON",
        sty["code"],
    ))

    # --- 6. Demo script ---
    story.append(Paragraph("6. Step-by-step demonstration script", sty["h1"]))
    story.append(Paragraph("Read this aloud while clicking through the app:", sty["body"]))

    demo_steps = [
        ("Open http://localhost:5180", "Show Travel app landing on login or attractions."),
        ("Login", "Explain JWT — server verifies email, token used for all trip APIs."),
        ("Attractions", "Pick moods, select places, set trip days. POST /api/trip-input creates trip_id."),
        ("Budget", "Enter total budget; show pie split. POST /api/budget/split."),
        ("Stay", "Select room type Single/Double/Family — price uses A, (A+B)/2, or B from hotel range. Pick one hotel per city."),
        ("Itinerary", "Click Generate. Explain: server validates, trip_plan_service splits days, ai_service adds times. Show day cards."),
        ("Change start time", "Regenerate — same places, different times. Old plan replaced in DB."),
        ("Discover (optional)", "Save shops/agencies/guides — appear in export PDF."),
        ("Export", "Download PDF — budget table, stays, schedule, saved references."),
    ]
    for i, (action, say) in enumerate(demo_steps, 1):
        story.append(Paragraph(f"<b>Step {i} — {action}</b>", sty["h2"]))
        story.append(Paragraph(say, sty["demo"]))

    story.append(PageBreak())

    # --- 7. Panel Q&A ---
    story.append(Paragraph("7. Likely panel questions &amp; short answers", sty["h1"]))
    qa = [
        ("Is this AI / machine learning?", "No. Rule-based engine with lookup tables. OPENAI_API_KEY can stay empty."),
        ("Random Forest?", "Not used anywhere in itinerary generation."),
        ("Where does attraction data come from?", "Real Excel seed: attractions.xlsx → PostgreSQL."),
        ("How are days assigned to cities?", "Consecutive blocks; days split evenly across destinations, extra days at later stops."),
        ("How are times chosen?", "Mood average or user override; category/name hints; fixed gaps between activities."),
        ("Why can't I generate without hotels?", "itinerary.py requires hotels + budget — design choice for complete plans."),
        ("Is GPS / routing used?", "No. Route text is city names only; no lat/lng on attractions."),
        ("How is plan persisted?", "JSON in generated_itinerary table; PDF reads same data."),
    ]
    table(story, sty, ["Question", "Answer"], qa, [55 * mm, 115 * mm])

    story.append(Spacer(1, 10))
    story.append(Paragraph("8. Key file checklist (print for reference)", sty["h1"]))
    table(story, sty, ["File path", "One-line job"], [
        ["frontend/travel/src/pages/LoginPage.jsx", "User authentication UI"],
        ["frontend/travel/src/context/TripContext.jsx", "Wizard state in browser"],
        ["frontend/travel/src/pages/ItineraryPage.jsx", "Generate button + display plan"],
        ["frontend/travel/src/api/client.js", "HTTP calls to backend"],
        ["backend/app/routes/auth.py", "Login/register → JWT"],
        ["backend/app/routes/trip_input.py", "Create trip, save hotels"],
        ["backend/app/routes/budget.py", "Budget split"],
        ["backend/app/routes/accommodation.py", "Hotel list filtered by budget + room type"],
        ["backend/app/routes/itinerary.py", "Generate / get / PDF endpoints"],
        ["backend/app/services/trip_plan_service.py", "Days ↔ cities ↔ attractions ↔ hotels"],
        ["backend/app/services/ai_service.py", "Clock times + final itinerary JSON"],
        ["backend/app/services/pdf_service.py", "Export PDF (ReportLab)"],
        ["backend/app/models/generated_itinerary.py", "Saved plan storage"],
    ], [78 * mm, 92 * mm])

    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=0.5, color=LINE))
    story.append(Paragraph(
        "Tour Ceylon · Travel component · Backend port 5002 · Frontend port 5180",
        sty["sub"],
    ))

    doc = SimpleDocTemplate(
        str(OUT), pagesize=A4,
        leftMargin=18 * mm, rightMargin=18 * mm,
        topMargin=16 * mm, bottomMargin=18 * mm,
        title="Itinerary Generator Demo Guide",
    )
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    build()
