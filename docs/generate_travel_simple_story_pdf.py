"""
Ultra-simple Travel dashboard story PDF.
Click-by-click: register → JWT → each wizard step → architecture + tech stack.

Run:
  cd backend
  .\\.venv\\Scripts\\python.exe ..\\docs\\generate_travel_simple_story_pdf.py
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

OUT = Path(__file__).resolve().parent / "pdfs" / "Travel_Dashboard_Simple_Explain.pdf"
PAGE = A4
M = 1.7 * cm

NAVY = colors.HexColor("#0F2744")
TEAL = colors.HexColor("#0D6E6E")
SOFT = colors.HexColor("#F4F7FA")
LINE = colors.HexColor("#D5DEE8")
MUTED = colors.HexColor("#4A5A6A")
WHITE = colors.white
STEP = colors.HexColor("#E8F4F4")


def S():
    b = getSampleStyleSheet()
    return {
        "cover": ParagraphStyle("c", parent=b["Title"], fontName="Helvetica-Bold", fontSize=22, leading=28, textColor=NAVY, alignment=TA_CENTER, spaceAfter=8),
        "sub": ParagraphStyle("s", parent=b["Normal"], fontName="Helvetica", fontSize=11, leading=15, textColor=MUTED, alignment=TA_CENTER, spaceAfter=6),
        "h1": ParagraphStyle("h1", parent=b["Heading1"], fontName="Helvetica-Bold", fontSize=14, leading=18, textColor=NAVY, spaceBefore=11, spaceAfter=6),
        "h2": ParagraphStyle("h2", parent=b["Heading2"], fontName="Helvetica-Bold", fontSize=11.5, leading=15, textColor=TEAL, spaceBefore=8, spaceAfter=4),
        "body": ParagraphStyle("body", parent=b["Normal"], fontName="Helvetica", fontSize=10, leading=13.5, textColor=colors.HexColor("#1A2430"), alignment=TA_JUSTIFY, spaceAfter=5),
        "path": ParagraphStyle("path", parent=b["Normal"], fontName="Helvetica", fontSize=9, leading=12.5, textColor=colors.HexColor("#1A2430"), leftIndent=4, spaceAfter=3),
        "bullet": ParagraphStyle("bu", parent=b["Normal"], fontName="Helvetica", fontSize=9.5, leading=12.5, textColor=colors.HexColor("#1A2430")),
        "note": ParagraphStyle("n", parent=b["Normal"], fontName="Helvetica-Oblique", fontSize=9, leading=12, textColor=MUTED, spaceAfter=6),
        "cell": ParagraphStyle("cell", parent=b["Normal"], fontName="Helvetica", fontSize=8.5, leading=11, textColor=colors.HexColor("#1A2430")),
        "cell_b": ParagraphStyle("cellb", parent=b["Normal"], fontName="Helvetica-Bold", fontSize=8.5, leading=11, textColor=NAVY),
    }


def hf(c, doc):
    c.saveState()
    c.setStrokeColor(LINE)
    c.setLineWidth(0.5)
    c.line(M, PAGE[1] - 1.1 * cm, PAGE[0] - M, PAGE[1] - 1.1 * cm)
    c.setFont("Helvetica", 8)
    c.setFillColor(MUTED)
    c.drawString(M, PAGE[1] - 0.9 * cm, "Tour Ceylon — Travel explained simply")
    c.drawRightString(PAGE[0] - M, PAGE[1] - 0.9 * cm, "Click → files → JWT → end")
    c.line(M, 1.1 * cm, PAGE[0] - M, 1.1 * cm)
    c.drawCentredString(PAGE[0] / 2, 0.65 * cm, f"Page {doc.page}")
    c.restoreState()


def P(t, s):
    return Paragraph(str(t).replace("\n", "<br/>"), s)


def bullets(items, st):
    return ListFlowable(
        [ListItem(Paragraph(i, st["bullet"]), leftIndent=8, bulletColor=TEAL) for i in items],
        bulletType="bullet", start="•", leftIndent=6, bulletFontSize=9,
    )


def box(st, title, lines):
    parts = [Paragraph(f"<b>{title}</b>", st["cell_b"]), Spacer(1, 3)]
    for line in lines:
        parts.append(Paragraph(f"→ {line}", st["path"]))
    t = Table([[parts]], colWidths=[PAGE[0] - 2 * M])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), STEP),
        ("BOX", (0, 0), (-1, -1), 1, TEAL),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    return t


def tbl(headers, rows, st, widths):
    data = [[Paragraph(h, st["cell_b"]) for h in headers]]
    for r in rows:
        data.append([Paragraph(str(c), st["cell"]) for c in r])
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


def build():
    st = S()
    w = PAGE[0] - 2 * M
    story = []

    story += [
        Spacer(1, 1.6 * cm),
        P("Tour Ceylon", st["sub"]),
        P("How the Travel Dashboard Works", st["cover"]),
        P("Simple English · click by click · which files run · JWT · architecture · tech stack", st["sub"]),
        Spacer(1, 0.35 * cm),
        box(st, "Read like a story", [
            "Imagine you are the tourist using the website.",
            "You click. Data moves through files. We say what each file does.",
            "At the end: architecture picture + tech stack.",
        ]),
        PageBreak(),
    ]

    # INTRO
    story += [
        P("What is Travel?", st["h1"]),
        P(
            "Travel is the trip planner. You sign up, pick places in Sri Lanka, set money, "
            "choose hotels, get a day plan, then download a PDF.",
            st["body"],
        ),
        P("Three big pieces always work together:", st["body"]),
        bullets([
            "<b>Browser (React)</b> — screens you see (port 5180)",
            "<b>Server (Flask)</b> — API that checks login and saves data (port 5002)",
            "<b>Database (PostgreSQL)</b> — stores users, trips, hotels, itineraries",
        ], st),
        P(
            "Think of it like a shop: the website is the counter, Flask is the worker in the back, "
            "Postgres is the filing cabinet.",
            st["note"],
        ),
        PageBreak(),
    ]

    # REGISTER
    story += [
        P("STEP 1 — You click Register and enter details", st["h1"]),
        P("You open http://localhost:5180/login. You switch to Register. You type email + password. You click create account.", st["body"]),
        box(st, "Path of this click (register)", [
            "LoginPage.jsx — form you typed in; calls register()",
            "AuthContext.jsx — register() function runs",
            "client.js (authApi.register) — sends POST /api/auth/register",
            "Vite proxy — forwards /api to Flask :5002",
            "routes/auth.py → register() — server checks email/password rules",
            "models/user.py — creates User; password is hashed (not plain text)",
            "PostgreSQL table users — new row saved",
            "auth.py — makes a JWT token and sends it back",
            "AuthContext — saves access_token + user in localStorage",
            "App.jsx ProtectedRoute — now you are “logged in”; go to Attractions",
        ]),
        P("What is a JWT token?", st["h2"]),
        P(
            "JWT is a small signed pass. After register/login, the server gives you this pass. "
            "The browser keeps it in localStorage as access_token. "
            "Every later request (budget, hotels, itinerary) sends: Authorization: Bearer &lt;token&gt;. "
            "The server reads the token, knows who you are, and only shows YOUR trips.",
            st["body"],
        ),
        P(
            "Also: AuthContext may link a Tourist SOS account (sosClient.js) so Profile / SOS button work later. "
            "That is optional for planning; Travel still works with only the travel JWT.",
            st["note"],
        ),
        PageBreak(),
    ]

    # LOGIN
    story += [
        P("STEP 2 — You click Login (next time)", st["h1"]),
        P("Same page, login mode. Email + password (or Google).", st["body"]),
        box(st, "Path of this click (login)", [
            "LoginPage.jsx — calls login()",
            "AuthContext.jsx — login()",
            "client.js — POST /api/auth/login { email, password }",
            "routes/auth.py → login() — finds User by email",
            "user.check_password() — compares hash",
            "If OK → new JWT returned",
            "AuthContext — saves token again in localStorage",
            "App.jsx — unlocks wizard pages",
        ]),
        P(
            "If token is old/expired when you reopen the site: AuthContext checks /api/auth/me. "
            "If bad → clears storage → back to login.",
            st["note"],
        ),
        PageBreak(),
    ]

    # ATTRACTIONS
    story += [
        P("STEP 3 — You pick moods and attractions", st["h1"]),
        P("You choose days, up to 3 moods, select places, click Confirm. This CREATES your trip.", st["body"]),
        box(st, "Path of this click (confirm attractions)", [
            "AttractionsPage.jsx — UI for moods + place cards",
            "Earlier load: attractionsApi.list → GET /api/attractions",
            "routes/attractions.py — reads attractions table → sends list",
            "AttractionPhoto.jsx — shows each photo",
            "On Confirm: tripApi.create → POST /api/trip-input",
            "client.js — adds Bearer JWT on the request",
            "trip_helpers.get_current_user_id — reads user id from JWT",
            "routes/trip_input.py → create_trip_input()",
            "Checks days, moods (1–3), attraction ids",
            "models/user_trip_input.py — new trip row saved",
            "Response includes trip_id (UUID)",
            "TripContext.jsx — stores tripId + choices in browser memory",
            "Navigate to /budget",
        ]),
        P(
            "Saved in DB now: days, selected_moods, finalized_attractions, status. "
            "This trip_id is used in every next step.",
            st["note"],
        ),
        PageBreak(),
    ]

    # BUDGET
    story += [
        P("STEP 4 — You set budget", st["h1"]),
        P("You type total money and split % for food / stay / shopping / transport. Pie chart updates. You confirm.", st["body"]),
        box(st, "Path of this click (save budget)", [
            "BudgetPage.jsx — form + Recharts pie",
            "Needs trip.tripId from TripContext",
            "budgetApi.split → POST /api/budget/split",
            "routes/budget.py — loads YOUR trip with get_user_trip (JWT + trip_id)",
            "budget_service.py — checks %; calculates money amounts; per-night stay budget",
            "models/budget_split.py — saves budget_split row",
            "Also updates user_trip_input.budget",
            "TripContext updated → go to /accommodation",
        ]),
        PageBreak(),
    ]

    # STAY
    story += [
        P("STEP 5 — You pick hotels", st["h1"]),
        P("For each city in your trip, you pick one hotel that fits the stay budget.", st["body"]),
        box(st, "Path of this click (choose hotels)", [
            "AccommodationPage.jsx — hotel cards per city",
            "First load: accommodationApi.list(tripId) → GET /api/accommodation?trip_id=…",
            "routes/accommodation.py + trip_plan_service.py",
            "Finds cities from your attractions",
            "hotels_for_destination — only hotels in that city under stay budget",
            "models/accommodation.py — hotel catalog table",
            "You pick hotels → tripApi.update → PATCH /api/trip-input/&lt;id&gt;",
            "validate_accommodation_picks — every city must have a matching hotel",
            "Saves hotels JSON on user_trip_input.accommodations",
            "TripContext updated; old itinerary cleared → go to /itinerary",
        ]),
        PageBreak(),
    ]

    # ITINERARY
    story += [
        P("STEP 6 — Itinerary is built", st["h1"]),
        P(
            "The page loads or generates a day-by-day plan. You can pick Auto (by mood) or a start time and Rebuild. "
            "Empty OPENAI_API_KEY is fine — this uses rules + your saved data only.",
            st["body"],
        ),
        box(st, "Path of this click (generate / rebuild)", [
            "ItineraryPage.jsx — shows days; start-time dropdown; Rebuild button",
            "itineraryApi.generate → POST /api/itinerary/generate { trip_id, day_start?}",
            "client.js — JWT on request",
            "routes/itinerary.py → generate()",
            "Checks: attractions + hotels + budget already exist",
            "Deletes old generated_itinerary rows for this trip",
            "trip_plan_service.py — splits cities/places across days; hotel per day",
            "ai_service.py — picks start hour (your time OR mood average)",
            "ai_service.py — category bias (Wild early, Pristine later) + spacing (3h / 2.5h / 2h)",
            "Builds JSON: days → activities with clock times + descriptions from DB",
            "models/generated_itinerary.py — saves that JSON",
            "UI shows Day 1, Day 2, … with times",
        ]),
        P(
            "Moods like Spiritual start ~6:30; Relaxed ~10:30. "
            "Example: start 8:00 + 3 places ≈ 8:00, 10:30, 1:00 PM.",
            st["note"],
        ),
        PageBreak(),
    ]

    # DISCOVER + EXPORT
    story += [
        P("STEP 7 — Discover (optional)", st["h1"]),
        P("You browse businesses, agencies, guides and can save favorites.", st["body"]),
        box(st, "Path", [
            "RecommendationsPage.jsx",
            "GET recommendations APIs → routes/recommendations.py → catalog tables",
            "Save favorite → routes/saved_references.py → saved_references table",
            "Continue → Export",
        ]),
        P("STEP 8 — Export PDF", st["h1"]),
        P("You review the summary and download the PDF.", st["body"]),
        box(st, "Path of this click (download PDF)", [
            "ExportPage.jsx — shows trip summary from TripContext",
            "Download → fetch /api/itinerary/&lt;trip_id&gt;/pdf with Bearer JWT",
            "routes/itinerary.py → export_pdf()",
            "Loads your trip + saved generated_itinerary JSON",
            "pdf_service.py — turns that JSON into a PDF file",
            "Browser downloads the PDF",
        ]),
        P("<b>Important:</b> Export does not invent a new plan. It prints what was already generated and saved.", st["note"]),
        PageBreak(),
    ]

    # SIDE
    story += [
        P("Extra buttons (same Travel app)", st["h1"]),
        P("History", st["h2"]),
        P(
            "HistoryPage lists past itineraries. You open one → APIs reload trip + budget + itinerary "
            "into TripContext → you land on Itinerary again.",
            st["body"],
        ),
        P("Profile", st["h2"]),
        P(
            "ProfilePage edits visitor / emergency details via sosClient (Tourist SOS APIs). "
            "Travel JWT is bridged to a tourist session.",
            st["body"],
        ),
        P("SOS button in Layout", st["h2"]),
        P(
            "Opens Tourist SOS app with your login (bridge-travel). "
            "It does NOT open the Police dashboard.",
            st["body"],
        ),
        PageBreak(),
    ]

    # ARCHITECTURE
    story += [
        P("Architecture (how pieces connect)", st["h1"]),
        P(
            "Browser (React Travel app :5180)\n"
            "    ↓  HTTP /api/... + JWT\n"
            "Flask API (:5002) — routes → services → models\n"
            "    ↓\n"
            "PostgreSQL (travel_app) — users, trips, budgets, hotels, itineraries\n"
            "\n"
            "Optional side: sosClient bridges to Tourist SOS app (:5175) for Profile/SOS only.",
            st["body"],
        ),
        P("MVC idea inside the backend:", st["h2"]),
        bullets([
            "<b>Model</b> — backend/app/models/ (tables)",
            "<b>View</b> — frontend/travel React pages",
            "<b>Controller</b> — backend/app/routes/ (URLs)",
            "<b>Services</b> — extra brain for rules (budget, day split, times, PDF)",
        ], st),
        P("Folder map", st["h2"]),
        tbl(
            ["Folder", "Job"],
            [
                ["frontend/travel/src/pages/", "Screens you click"],
                ["frontend/travel/src/context/", "Login memory + trip memory"],
                ["frontend/travel/src/api/", "Send requests to Flask"],
                ["frontend/travel/src/components/", "Layout shell + photo helper"],
                ["backend/app/routes/", "Handle each /api URL"],
                ["backend/app/models/", "Talk to database tables"],
                ["backend/app/services/", "Rules: money, days, times, PDF"],
                ["backend/app/utils/", "Helpers like get_user_trip"],
                ["backend/database/", "SQL schema"],
                ["backend/scripts/travel/", "Create DB + seed data"],
            ],
            st, [w * 0.42, w * 0.58],
        ),
        PageBreak(),
    ]

    # TECH STACK
    story += [
        P("Tech stack (and why)", st["h1"]),
        tbl(
            ["Tech", "Where", "Why we use it"],
            [
                ["React 18", "Frontend", "Interactive pages without full reload"],
                ["Vite", "Frontend tool", "Fast dev server on port 5180"],
                ["React Router", "Frontend", "URLs for each step (/budget, /export…)"],
                ["Axios", "Frontend", "HTTP calls; attach JWT header"],
                ["Recharts", "Frontend", "Budget pie chart"],
                ["localStorage", "Browser", "Keep JWT after refresh"],
                ["Flask", "Backend", "Python API on port 5002"],
                ["Flask-JWT-Extended", "Backend", "Create/check login tokens"],
                ["SQLAlchemy", "Backend", "Python classes ↔ DB tables"],
                ["PostgreSQL", "Database", "Permanent storage"],
                ["ReportLab / pdf_service", "Backend", "Build export PDF"],
            ],
            st, [w * 0.28, w * 0.20, w * 0.52],
        ),
        Spacer(1, 10),
        P("Whole story in one paragraph", st["h1"]),
        P(
            "You register or login → JWT is saved → you pick attractions and the server creates a trip → "
            "you save budget → you save hotels → the server splits days and makes times from moods/categories "
            "(no OpenAI) → you may save discover favorites → export downloads a PDF of that saved plan. "
            "Every click: Page → client.js → Flask route → service/model → database → JSON back to the page.",
            st["body"],
        ),
        Spacer(1, 8),
        box(st, "Remember JWT", [
            "No token → cannot open wizard pages.",
            "Token on every API call → server knows it is YOU.",
            "Token bad/expired → login again.",
        ]),
    ]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUT), pagesize=PAGE, leftMargin=M, rightMargin=M,
        topMargin=1.65 * cm, bottomMargin=1.65 * cm,
        title="Travel Dashboard Simple Explain", author="Tour Ceylon",
    )
    doc.build(story, onFirstPage=hf, onLaterPages=hf)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    build()
