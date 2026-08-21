"""
Generate a full Travel Dashboard PDF guide:
registration → attractions → budget → stay → itinerary → discover → export
+ every related file/folder explained in simple English.

Run:
  cd backend
  .\\.venv\\Scripts\\activate
  python ..\\docs\\generate_travel_full_guide_pdf.py

Output:
  docs/pdfs/Travel_Full_Dashboard_Guide.pdf
"""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

OUT = Path(__file__).resolve().parent / "pdfs" / "Travel_Full_Dashboard_Guide.pdf"
PAGE = A4
MARGIN = 1.7 * cm

NAVY = colors.HexColor("#0F2744")
TEAL = colors.HexColor("#0D6E6E")
SOFT = colors.HexColor("#F4F7FA")
LINE = colors.HexColor("#D5DEE8")
MUTED = colors.HexColor("#4A5A6A")
WHITE = colors.white


def styles():
    base = getSampleStyleSheet()
    return {
        "cover": ParagraphStyle(
            "cover", parent=base["Title"], fontName="Helvetica-Bold",
            fontSize=24, leading=30, textColor=NAVY, alignment=TA_CENTER, spaceAfter=8,
        ),
        "sub": ParagraphStyle(
            "sub", parent=base["Normal"], fontName="Helvetica",
            fontSize=11, leading=15, textColor=MUTED, alignment=TA_CENTER, spaceAfter=6,
        ),
        "h1": ParagraphStyle(
            "h1", parent=base["Heading1"], fontName="Helvetica-Bold",
            fontSize=15, leading=19, textColor=NAVY, spaceBefore=12, spaceAfter=7,
        ),
        "h2": ParagraphStyle(
            "h2", parent=base["Heading2"], fontName="Helvetica-Bold",
            fontSize=12, leading=16, textColor=TEAL, spaceBefore=10, spaceAfter=5,
        ),
        "body": ParagraphStyle(
            "body", parent=base["Normal"], fontName="Helvetica",
            fontSize=9.5, leading=13, textColor=colors.HexColor("#1A2430"),
            alignment=TA_JUSTIFY, spaceAfter=5,
        ),
        "bullet": ParagraphStyle(
            "bullet", parent=base["Normal"], fontName="Helvetica",
            fontSize=9.5, leading=12.5, textColor=colors.HexColor("#1A2430"),
        ),
        "note": ParagraphStyle(
            "note", parent=base["Normal"], fontName="Helvetica-Oblique",
            fontSize=9, leading=12, textColor=MUTED, spaceBefore=3, spaceAfter=6,
        ),
        "cell": ParagraphStyle(
            "cell", parent=base["Normal"], fontName="Helvetica",
            fontSize=8, leading=10.5, textColor=colors.HexColor("#1A2430"),
        ),
        "cell_b": ParagraphStyle(
            "cell_b", parent=base["Normal"], fontName="Helvetica-Bold",
            fontSize=8, leading=10.5, textColor=NAVY,
        ),
    }


def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.5)
    canvas.line(MARGIN, PAGE[1] - 1.15 * cm, PAGE[0] - MARGIN, PAGE[1] - 1.15 * cm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(MARGIN, PAGE[1] - 0.95 * cm, "Tour Ceylon — Travel Full Guide")
    canvas.drawRightString(PAGE[0] - MARGIN, PAGE[1] - 0.95 * cm, "Registration → Export")
    canvas.line(MARGIN, 1.15 * cm, PAGE[0] - MARGIN, 1.15 * cm)
    canvas.drawCentredString(PAGE[0] / 2, 0.7 * cm, f"Page {doc.page}")
    canvas.restoreState()


def p(text, style):
    return Paragraph(str(text).replace("\n", "<br/>"), style)


def bullets(items, st):
    return ListFlowable(
        [ListItem(Paragraph(i, st["bullet"]), leftIndent=10, bulletColor=TEAL) for i in items],
        bulletType="bullet", start="•", leftIndent=8, bulletFontSize=9,
    )


def table(headers, rows, st, widths):
    data = [[Paragraph(h, st["cell_b"]) for h in headers]]
    for row in rows:
        data.append([Paragraph(str(c), st["cell"]) for c in row])
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [SOFT, WHITE]),
        ("GRID", (0, 0), (-1, -1), 0.35, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return t


def callout(title, body, st):
    inner = [Paragraph(f"<b>{title}</b>", st["cell_b"]), Spacer(1, 2), Paragraph(body, st["cell"])]
    t = Table([[inner]], colWidths=[PAGE[0] - 2 * MARGIN])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#E8F4F4")),
        ("BOX", (0, 0), (-1, -1), 1, TEAL),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    return t


def build():
    st = styles()
    w = PAGE[0] - 2 * MARGIN
    story = []

    # COVER
    story += [
        Spacer(1, 2 * cm),
        p("Tour Ceylon", st["sub"]),
        p("Travel Dashboard — Full Guide", st["cover"]),
        p("From registration to itinerary export — how every folder and file works", st["sub"]),
        Spacer(1, 0.5 * cm),
        callout(
            "What this PDF is for",
            "This guide explains the Travel planner from the very beginning (create account / login) "
            "to the end (download PDF). It shows the user steps, which files run at each step, "
            "and what each folder is for — in simple English.",
            st,
        ),
        PageBreak(),
    ]

    # 1 BIG PICTURE
    story += [
        p("1. Big picture — what Travel is", st["h1"]),
        p(
            "Travel is the trip planner website. A visitor signs up, picks places in Sri Lanka, "
            "sets a budget, chooses hotels, gets a day-by-day plan, discovers local services, "
            "and downloads a PDF. History, Profile, and SOS sit outside the main wizard.",
            st["body"],
        ),
        p("User journey (in order):", st["body"]),
        bullets([
            "Register / Login",
            "Attractions — moods + places → create trip",
            "Budget — total money + split",
            "Stay — hotel per city",
            "Itinerary — day plan + times",
            "Discover — businesses, agencies, guides",
            "Export — review + download PDF",
        ], st),
        p(
            "Tech in short: React UI (port 5180) → Flask API (port 5002) → PostgreSQL database. "
            "Login uses a JWT token. Trip data is saved in the database so History can reopen it.",
            st["body"],
        ),
        PageBreak(),
    ]

    # 2 FOLDERS
    story += [
        p("2. Main folders — what each one is for", st["h1"]),
        table(
            ["Folder", "What it is for"],
            [
                ["frontend/travel/", "The Travel website (React app users see)"],
                ["frontend/travel/src/pages/", "One screen per step (Login, Budget, …)"],
                ["frontend/travel/src/components/", "Shared UI pieces (sidebar, photo)"],
                ["frontend/travel/src/context/", "Shared memory: who is logged in + current trip"],
                ["frontend/travel/src/api/", "Code that talks to the server"],
                ["frontend/travel/src/styles/", "Global look (colors, layout)"],
                ["backend/", "The API server (Flask)"],
                ["backend/app/routes/", "URL handlers (/api/…) — one file per feature"],
                ["backend/app/models/", "One file ≈ one database table"],
                ["backend/app/services/", "Business rules (budget math, day plan, times, PDF)"],
                ["backend/app/utils/", "Small helpers (load user’s own trip)"],
                ["backend/database/", "SQL schema + migrations"],
                ["backend/scripts/travel/", "Setup scripts (create tables, seed data)"],
                ["backend/data/travel/", "Excel/CSV seed files for attractions/hotels"],
            ],
            st, [w * 0.38, w * 0.62],
        ),
        Spacer(1, 8),
        p(
            "Why so many files? Each file has one job. Pages show screens. Routes answer URLs. "
            "Models talk to tables. Services hold the rules. That makes the project easier to change.",
            st["note"],
        ),
        PageBreak(),
    ]

    # 3 FRONTEND FILES
    story += [
        p("3. Every Travel frontend file", st["h1"]),
        p("Path: <b>frontend/travel/src/</b>", st["note"]),
        table(
            ["File", "What it does"],
            [
                ["main.jsx", "Starts the app; wraps Auth + Trip providers"],
                ["App.jsx", "Defines routes; blocks pages until login"],
                ["styles/global.css", "Overall look of the Travel UI"],
                ["api/client.js", "Talks to Travel APIs; attaches JWT; auth/trip/budget helpers"],
                ["api/sosClient.js", "Links Tourist SOS account; opens SOS app"],
                ["context/AuthContext.jsx", "Login / register / logout; stores token"],
                ["context/TripContext.jsx", "Holds current trip choices in browser memory"],
                ["components/Layout.jsx", "Sidebar steps, progress, SOS / History / Profile"],
                ["components/AttractionPhoto.jsx", "Shows place photo; fallback if broken"],
                ["theme/sosProfile.js", "Styles for Profile page (match SOS look)"],
                ["pages/LoginPage.jsx", "Register + login (+ Google if set)"],
                ["pages/AttractionsPage.jsx", "Pick moods + attractions; create trip"],
                ["pages/BudgetPage.jsx", "Enter budget and category split"],
                ["pages/AccommodationPage.jsx", "Pick hotel for each city"],
                ["pages/ItineraryPage.jsx", "Generate / view day-by-day times"],
                ["pages/RecommendationsPage.jsx", "Discover + save favorites"],
                ["pages/ExportPage.jsx", "Trip summary + PDF download"],
                ["pages/HistoryPage.jsx", "Open past trips again"],
                ["pages/ProfilePage.jsx", "Visitor / emergency profile (SOS)"],
            ],
            st, [w * 0.36, w * 0.64],
        ),
        PageBreak(),
    ]

    # 4 BACKEND FILES
    story += [
        p("4. Every Travel backend file (related)", st["h1"]),
        p("4.1 Routes (URL controllers)", st["h2"]),
        table(
            ["File", "What it does"],
            [
                ["routes/auth.py", "Register, login, Google, me, link-account"],
                ["routes/attractions.py", "List attractions (optional mood filter)"],
                ["routes/trip_input.py", "Create / get / update a trip"],
                ["routes/budget.py", "Save / get budget split"],
                ["routes/accommodation.py", "List hotels for trip cities + budget"],
                ["routes/itinerary.py", "Generate, get, history, PDF"],
                ["routes/recommendations.py", "Businesses, agencies, guides"],
                ["routes/saved_references.py", "Save / list favorites"],
                ["routes/images.py", "Resolve image URLs (optional)"],
                ["routes/tourists.py", "SOS bridge / profile (used by Profile + SOS button)"],
            ],
            st, [w * 0.36, w * 0.64],
        ),
        p("4.2 Models (database tables)", st["h2"]),
        table(
            ["File → table", "What it stores"],
            [
                ["user.py → users", "Travel accounts"],
                ["attraction.py → attractions", "Places to visit (seed data)"],
                ["accommodation.py → accommodation", "Hotels (seed data)"],
                ["user_trip_input.py → user_trip_input", "The user’s trip (core row)"],
                ["budget_split.py → budget_split", "Budget amounts and %"],
                ["generated_itinerary.py → generated_itinerary", "Saved day plan JSON"],
                ["business_directory.py", "Local businesses"],
                ["travel_agency.py", "Travel agencies"],
                ["tourist_guide.py", "Tourist guides"],
                ["saved_reference.py", "User favorites on a trip"],
            ],
            st, [w * 0.42, w * 0.58],
        ),
        p("4.3 Services (rules / logic)", st["h2"]),
        table(
            ["File", "What it does"],
            [
                ["budget_service.py", "Default %, money math, per-night stay budget"],
                ["trip_plan_service.py", "Split cities/days; match hotels to cities"],
                ["ai_service.py", "Build times from moods/categories (NO OpenAI)"],
                ["pdf_service.py", "Create itinerary PDF for Export"],
                ["image_resolver.py", "Help resolve attraction images"],
            ],
            st, [w * 0.36, w * 0.64],
        ),
        p("4.4 Other backend pieces", st["h2"]),
        table(
            ["File / folder", "What it does"],
            [
                ["run.py", "Starts Flask on port 5002"],
                ["app/__init__.py", "Creates app, DB, JWT, registers routes"],
                ["app/config.py", "Database URL, secrets, defaults"],
                ["utils/trip_helpers.py", "Load only the logged-in user’s trip"],
                ["database/schema.sql", "Creates all Travel tables"],
                ["scripts/travel/apply_schema.py", "Apply schema to Postgres"],
                ["scripts/travel/seed_data.py", "Load attractions/hotels from Excel"],
            ],
            st, [w * 0.42, w * 0.58],
        ),
        PageBreak(),
    ]

    # 5 STEP BY STEP
    story += [
        p("5. Step-by-step — beginning to end", st["h1"]),
        callout(
            "How to read each step",
            "For every step: what the user does → which frontend files → which backend files → "
            "what is saved in the database.",
            st,
        ),
        Spacer(1, 6),

        p("Step 0 — Register / Login", st["h2"]),
        p(
            "User creates an account or signs in (email/password or Google). The server checks or "
            "creates a row in <b>users</b> and returns a JWT. The browser stores the token. "
            "The app may also link a Tourist SOS account for Profile / SOS.",
            st["body"],
        ),
        table(
            ["Layer", "Files"],
            [
                ["Frontend", "LoginPage.jsx, AuthContext.jsx, api/client.js, api/sosClient.js"],
                ["Backend", "routes/auth.py, models/user.py; SOS: routes/tourists.py"],
                ["Saved", "users table; localStorage access_token (+ touristToken if linked)"],
            ],
            st, [w * 0.22, w * 0.78],
        ),
        Spacer(1, 8),

        p("Step 1 — Attractions", st["h2"]),
        p(
            "User sets number of days, picks up to 3 moods, selects attractions, then confirms. "
            "Confirm creates the trip row. Progress ~25%.",
            st["body"],
        ),
        table(
            ["Layer", "Files"],
            [
                ["Frontend", "AttractionsPage.jsx, AttractionPhoto.jsx, TripContext, client.js"],
                ["Backend", "routes/attractions.py, routes/trip_input.py, trip_plan_service.py"],
                ["Saved", "user_trip_input (days, moods, finalized_attractions, status)"],
            ],
            st, [w * 0.22, w * 0.78],
        ),
        Spacer(1, 8),

        p("Step 2 — Budget", st["h2"]),
        p(
            "User enters total budget and splits food / stay / shopping / transport. "
            "A pie chart shows the split. Progress ~45%.",
            st["body"],
        ),
        table(
            ["Layer", "Files"],
            [
                ["Frontend", "BudgetPage.jsx, TripContext, budgetApi in client.js"],
                ["Backend", "routes/budget.py, services/budget_service.py"],
                ["Saved", "user_trip_input.budget + budget_split table"],
            ],
            st, [w * 0.22, w * 0.78],
        ),
        Spacer(1, 8),

        p("Step 3 — Stay (Accommodation)", st["h2"]),
        p(
            "User picks one hotel per destination, filtered by stay budget. Progress ~65%.",
            st["body"],
        ),
        table(
            ["Layer", "Files"],
            [
                ["Frontend", "AccommodationPage.jsx, accommodationApi, tripApi.update"],
                ["Backend", "routes/accommodation.py, trip_input PATCH, trip_plan_service, budget_service"],
                ["Saved", "user_trip_input.accommodations (JSON per city/day)"],
            ],
            st, [w * 0.22, w * 0.78],
        ),
        PageBreak(),

        p("Step 4 — Itinerary", st["h2"]),
        p(
            "Server builds a day-by-day plan from saved attractions + hotels. "
            "Times come from rules (moods, categories, spacing) — not OpenAI. "
            "User can pick Auto start or a fixed time and Rebuild. Progress ~80%.",
            st["body"],
        ),
        table(
            ["Layer", "Files"],
            [
                ["Frontend", "ItineraryPage.jsx, itineraryApi in client.js"],
                ["Backend", "routes/itinerary.py, trip_plan_service.py, ai_service.py"],
                ["Saved", "generated_itinerary.itinerary JSON"],
            ],
            st, [w * 0.22, w * 0.78],
        ),
        p(
            "Itinerary file chain: ItineraryPage → client.js → itinerary.py → "
            "trip_plan_service (split days) + ai_service (times) → generated_itinerary table.",
            st["note"],
        ),

        p("Step 5 — Discover (Recommendations)", st["h2"]),
        p(
            "User browses businesses, agencies, and guides near trip cities and can save favorites. "
            "Progress ~90%.",
            st["body"],
        ),
        table(
            ["Layer", "Files"],
            [
                ["Frontend", "RecommendationsPage.jsx, recommendationsApi, savedRefsApi"],
                ["Backend", "routes/recommendations.py, routes/saved_references.py + models"],
                ["Saved", "saved_references rows on the trip"],
            ],
            st, [w * 0.22, w * 0.78],
        ),
        Spacer(1, 8),

        p("Step 6 — Export", st["h2"]),
        p(
            "User reviews the trip summary and downloads a PDF. Nothing new is invented — "
            "PDF is built from the saved trip + itinerary. Progress 100%.",
            st["body"],
        ),
        table(
            ["Layer", "Files"],
            [
                ["Frontend", "ExportPage.jsx, itineraryApi.pdfUrl + Bearer token fetch"],
                ["Backend", "GET /itinerary/&lt;trip_id&gt;/pdf → pdf_service.py"],
                ["Saved", "No new row — streams PDF from existing data"],
            ],
            st, [w * 0.22, w * 0.78],
        ),
        PageBreak(),
    ]

    # SIDE PATHS
    story += [
        p("6. Side paths — History, Profile, SOS", st["h1"]),
        p("History", st["h2"]),
        p(
            "Lists past itineraries. Opening one reloads trip + budget + itinerary into TripContext "
            "and goes to the Itinerary page.",
            st["body"],
        ),
        p("<b>Files:</b> HistoryPage.jsx · itinerary history / trip / budget GET APIs", st["note"]),
        p("Profile", st["h2"]),
        p(
            "Edits visitor details (passport, hotel, emergency contact) shared with Tourist SOS. "
            "Uses the SOS bridge — not the travel users table for those fields.",
            st["body"],
        ),
        p("<b>Files:</b> ProfilePage.jsx, sosClient.js, sosProfile.js · routes/tourists.py", st["note"]),
        p("SOS button (top bar)", st["h2"]),
        p(
            "Opens the Tourist SOS app with the current Travel login (bridge-travel). "
            "Does not open the Police dashboard.",
            st["body"],
        ),
        p("<b>Files:</b> Layout.jsx, sosClient.js · POST /api/tourists/bridge-travel", st["note"]),
        PageBreak(),
    ]

    # HOW DATA MOVES
    story += [
        p("7. How data moves (simple)", st["h1"]),
        p(
            "Browser (Travel UI) → JWT in localStorage → Axios /api/... → Flask route → "
            "service (rules) → SQLAlchemy model → PostgreSQL table.",
            st["body"],
        ),
        table(
            ["Where", "What it holds"],
            [
                ["localStorage", "Login token (access_token) + optional SOS token"],
                ["TripContext", "Current wizard choices in memory (lost on full refresh)"],
                ["PostgreSQL", "Real saved trip — History can reload it"],
            ],
            st, [w * 0.28, w * 0.72],
        ),
        Spacer(1, 8),
        p("8. Tech stack — why each piece", st["h1"]),
        table(
            ["Tech", "Why"],
            [
                ["React + Vite", "Fast interactive screens (port 5180)"],
                ["React Router", "Each step has its own URL"],
                ["Axios", "Call Flask APIs with the login token"],
                ["Recharts", "Budget pie chart"],
                ["Flask", "Python API server (port 5002)"],
                ["JWT", "Secure login token after sign-in"],
                ["SQLAlchemy", "Python objects ↔ database tables"],
                ["PostgreSQL", "Stores users, trips, budgets, itineraries"],
                ["ReportLab / PDF service", "Export itinerary as PDF"],
            ],
            st, [w * 0.32, w * 0.68],
        ),
        PageBreak(),
    ]

    # HOW TO RUN
    story += [
        p("9. How to run (short)", st["h1"]),
        bullets([
            "Terminal 1: cd backend → activate .venv → python run.py",
            "Terminal 2: cd frontend → npm run dev (or npm run dev:travel)",
            "Open Travel at http://localhost:5180",
            "First-time DB: apply_schema.py + seed_data.py (see README)",
        ], st),
        Spacer(1, 10),
        callout(
            "One sentence to remember",
            "Registration creates a user → each wizard step saves more on the trip → "
            "itinerary builds times from database rules → export turns that saved plan into a PDF. "
            "Every screen has a page file; every API has a route file; every table has a model file.",
            st,
        ),
        Spacer(1, 12),
        p(
            "Source: Tour Ceylon codebase — frontend/travel + backend travel models/routes/services.",
            st["note"],
        ),
    ]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUT), pagesize=PAGE,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=1.7 * cm, bottomMargin=1.7 * cm,
        title="Travel Full Dashboard Guide",
        author="Tour Ceylon",
    )
    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    build()
