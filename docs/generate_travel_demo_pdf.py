"""
Travel Component — Demonstration PDF
Screen-by-screen script (simple English) + file connections + panel Q&A.

Run:
  cd backend
  .\\.venv\\Scripts\\activate
  python ..\\docs\\generate_travel_demo_pdf.py

Output:
  docs/pdfs/Travel_Component_Demonstration.pdf
"""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
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

OUT = Path(__file__).resolve().parent / "pdfs" / "Travel_Component_Demonstration.pdf"
PAGE = A4
MARGIN = 1.55 * cm

NAVY = colors.HexColor("#0F2744")
TEAL = colors.HexColor("#0D6E6E")
SOFT = colors.HexColor("#F4F7FA")
LINE = colors.HexColor("#D5DEE8")
MUTED = colors.HexColor("#4A5A6A")
WHITE = colors.white
INK = colors.HexColor("#1A2430")
BOX = colors.HexColor("#E8F4F4")


def styles():
    base = getSampleStyleSheet()
    return {
        "cover": ParagraphStyle(
            "cover", parent=base["Title"], fontName="Helvetica-Bold",
            fontSize=20, leading=25, textColor=NAVY, alignment=TA_CENTER, spaceAfter=8,
        ),
        "sub": ParagraphStyle(
            "sub", parent=base["Normal"], fontName="Helvetica",
            fontSize=10.5, leading=14, textColor=MUTED, alignment=TA_CENTER, spaceAfter=4,
        ),
        "h1": ParagraphStyle(
            "h1", parent=base["Heading1"], fontName="Helvetica-Bold",
            fontSize=13.5, leading=17, textColor=NAVY, spaceBefore=8, spaceAfter=5,
        ),
        "h2": ParagraphStyle(
            "h2", parent=base["Heading2"], fontName="Helvetica-Bold",
            fontSize=11, leading=14, textColor=TEAL, spaceBefore=7, spaceAfter=3,
        ),
        "body": ParagraphStyle(
            "body", parent=base["Normal"], fontName="Helvetica",
            fontSize=9.5, leading=13, textColor=INK, alignment=TA_LEFT, spaceAfter=4,
        ),
        "say": ParagraphStyle(
            "say", parent=base["Normal"], fontName="Helvetica-Oblique",
            fontSize=9.5, leading=12.5, textColor=INK, spaceAfter=4,
        ),
        "bullet": ParagraphStyle(
            "bullet", parent=base["Normal"], fontName="Helvetica",
            fontSize=9.5, leading=12.5, textColor=INK,
        ),
        "cell": ParagraphStyle(
            "cell", parent=base["Normal"], fontName="Helvetica",
            fontSize=8, leading=10.5, textColor=INK,
        ),
        "cell_b": ParagraphStyle(
            "cell_b", parent=base["Normal"], fontName="Helvetica-Bold",
            fontSize=8, leading=10.5, textColor=NAVY,
        ),
        "note": ParagraphStyle(
            "note", parent=base["Normal"], fontName="Helvetica-Oblique",
            fontSize=8.5, leading=11, textColor=MUTED, spaceBefore=2, spaceAfter=4,
        ),
    }


def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.5)
    canvas.line(MARGIN, PAGE[1] - 1.05 * cm, PAGE[0] - MARGIN, PAGE[1] - 1.05 * cm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(MARGIN, PAGE[1] - 0.85 * cm, "Tour Ceylon — Travel Demo Script + File Map")
    canvas.drawRightString(PAGE[0] - MARGIN, PAGE[1] - 0.85 * cm, "13 August 2026")
    canvas.line(MARGIN, 1.05 * cm, PAGE[0] - MARGIN, 1.05 * cm)
    canvas.drawCentredString(PAGE[0] / 2, 0.6 * cm, f"Page {doc.page}")
    canvas.restoreState()


def p(text, style):
    return Paragraph(str(text), style)


def bullets(items, st):
    return ListFlowable(
        [ListItem(Paragraph(i, st["bullet"]), leftIndent=8, bulletColor=TEAL) for i in items],
        bulletType="bullet", start="•", leftIndent=6, bulletFontSize=9,
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
    inner = [
        Paragraph(f"<b>{title}</b>", st["cell_b"]),
        Spacer(1, 2),
        Paragraph(body, st["cell"]),
    ]
    t = Table([[inner]], colWidths=[PAGE[0] - 2 * MARGIN])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BOX),
        ("BOX", (0, 0), (-1, -1), 1, TEAL),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def screen_block(title, say, do, files, connect, st, w):
    block = [
        p(title, st["h2"]),
        p(f"<b>Say this:</b> <i>{say}</i>", st["body"]),
        p(f"<b>Do this:</b> {do}", st["body"]),
        table(
            ["Layer", "Files"],
            files,
            st, [w * 0.22, w * 0.78],
        ),
        Spacer(1, 3),
        p(f"<b>How connected:</b> {connect}", st["note"]),
        Spacer(1, 6),
    ]
    return block


def build():
    st = styles()
    w = PAGE[0] - 2 * MARGIN
    story = []

    # COVER
    story += [
        Spacer(1, 1.4 * cm),
        p("Tour Ceylon", st["sub"]),
        p("Travel Component Demonstration", st["cover"]),
        p("Screen script · File connections · Panel answers", st["sub"]),
        Spacer(1, 0.4 * cm),
        table(
            ["Field", "Value"],
            [
                ["Project ID", "R26-IT-152"],
                ["Student", "Warniarachchi P.M.R. (IT22225092)"],
                ["Component", "AI Itinerary Generator (Travel)"],
                ["Date", "13 August 2026"],
                ["Travel URL", "http://localhost:5180"],
                ["API URL", "http://127.0.0.1:5002/api"],
            ],
            st, [w * 0.28, w * 0.72],
        ),
        Spacer(1, 0.4 * cm),
        callout(
            "How to use this PDF while presenting",
            "For each screen: read the “Say this” line in simple English, click what “Do this” says, "
            "and if they ask “which file?”, use the Files + How connected lines.",
            st,
        ),
        PageBreak(),
    ]

    # BIG PICTURE
    story += [
        p("1. Big picture (30 seconds)", st["h1"]),
        p(
            "Travel is the trip planner. A tourist logs in, picks places, sets money, chooses hotels, "
            "gets a day-by-day plan with times, finds local help, and downloads a PDF. "
            "History opens old trips. SOS opens from the same login.",
            st["body"],
        ),
        p("<b>Path on screen:</b> Login → Attractions → Budget → Stay → Itinerary → Discover → Export", st["body"]),
        p(
            "<b>Path in code:</b> React page → api/client.js → Flask route → service → PostgreSQL table",
            st["body"],
        ),
        Spacer(1, 4),
        callout(
            "One sentence if they ask “what did you build?”",
            "I built a React + Flask trip wizard that turns moods, attractions, budget, and hotels "
            "into a rule-based timed itinerary, discovers local services, and exports a PDF.",
            st,
        ),
        Spacer(1, 8),
        p("2. Tech (short answers)", st["h1"]),
        table(
            ["They ask", "You say"],
            [
                ["Frontend?", "React 18 + Vite — folder frontend/travel — port 5180"],
                ["Backend?", "Flask API — backend/run.py — port 5002"],
                ["Database?", "PostgreSQL — tables for users, trips, hotels, itineraries"],
                ["Login?", "JWT token saved in browser localStorage"],
                ["PDF?", "ReportLab in pdf_service.py"],
                ["AI / ML?", "No OpenAI / no Random Forest. Times from rules in ai_service.py"],
                ["Charts?", "Recharts pie chart on Budget page"],
            ],
            st, [w * 0.22, w * 0.78],
        ),
        PageBreak(),
    ]

    # HOW FILES CONNECT
    story += [
        p("3. How files connect (whole system)", st["h1"]),
        p("Simple chain for every click:", st["body"]),
        bullets([
            "<b>Page</b> (what user sees) — e.g. ItineraryPage.jsx",
            "<b>Context</b> — AuthContext (login) + TripContext (current trip choices)",
            "<b>API client</b> — api/client.js sends request + JWT",
            "<b>Route</b> — e.g. routes/itinerary.py receives URL",
            "<b>Service</b> — rules (trip_plan_service / ai_service / budget_service / pdf_service)",
            "<b>Model / DB</b> — SQLAlchemy model ↔ PostgreSQL table",
        ], st),
        Spacer(1, 4),
        table(
            ["Folder", "Job in one line"],
            [
                ["frontend/travel/src/pages/", "Each wizard screen"],
                ["frontend/travel/src/context/", "Shared login + trip memory"],
                ["frontend/travel/src/api/", "Talks to Flask"],
                ["frontend/travel/src/components/", "Sidebar Layout, photos"],
                ["backend/app/routes/", "API URLs"],
                ["backend/app/services/", "Business rules"],
                ["backend/app/models/", "Database tables"],
                ["backend/data/travel/", "Excel/CSV seed data"],
            ],
            st, [w * 0.42, w * 0.58],
        ),
        PageBreak(),
    ]

    # SCREEN BY SCREEN
    story += [
        p("4. Screen-by-screen demo script", st["h1"]),
        p("Start both servers first: backend python run.py · frontend npm run dev · open :5180", st["note"]),
    ]

    story += screen_block(
        "Screen A — Login",
        "This is the login screen. Users create an account or sign in. The server checks the "
        "users table and gives a JWT token. The browser keeps that token for later API calls.",
        "Register or login with a demo account. Show the app moves to Attractions.",
        [
            ["Frontend", "LoginPage.jsx · AuthContext.jsx · api/client.js"],
            ["Backend", "routes/auth.py · models/user.py"],
            ["Saved", "users table · localStorage access_token"],
        ],
        "LoginPage → AuthContext.login() → client.js POST /api/auth/login → auth.py → users table → JWT back to browser.",
        st, w,
    )

    story += screen_block(
        "Screen B — Attractions (step 1)",
        "Here the tourist sets trip days, picks moods like Adventure or Spiritual, and selects "
        "attractions. Moods filter the list from the database. When they confirm, we create the trip record.",
        "Set days (e.g. 3). Pick 1–3 moods. Select a few places. Click confirm / continue.",
        [
            ["Frontend", "AttractionsPage.jsx · AttractionPhoto.jsx · TripContext · client.js"],
            ["Backend", "routes/attractions.py · routes/trip_input.py · models/attraction.py · user_trip_input.py"],
            ["Saved", "user_trip_input (days, moods, attraction IDs)"],
        ],
        "AttractionsPage loads GET /attractions?moods=… → attractions.py filters SQL by mood_tag. "
        "Confirm → POST /trip-input → trip_input.py saves user_trip_input.",
        st, w,
    )

    story += [
        PageBreak(),
    ]

    story += screen_block(
        "Screen C — Budget (step 2)",
        "Now we set money. The user enters a total budget. The system splits it into food, stay, "
        "shopping, and transport. Default is about 25% / 35% / 15% / 25%. The pie chart shows that split.",
        "Enter a total (e.g. 150000). Show the pie chart. Save / continue.",
        [
            ["Frontend", "BudgetPage.jsx · Recharts · TripContext · budgetApi in client.js"],
            ["Backend", "routes/budget.py · services/budget_service.py · models/budget_split.py"],
            ["Saved", "user_trip_input.budget + budget_split row"],
        ],
        "BudgetPage → POST /budget/split → budget.py → budget_service.py does the math → budget_split table.",
        st, w,
    )

    story += screen_block(
        "Screen D — Stay / Accommodation (step 3)",
        "For each city in the trip, the tourist picks a hotel. Hotels are filtered by the stay "
        "budget and matched to the destination name from our hotel catalog.",
        "Pick one hotel per destination. Continue.",
        [
            ["Frontend", "AccommodationPage.jsx · accommodationApi · tripApi.update"],
            ["Backend", "routes/accommodation.py · trip_plan_service.py · budget_service.py · models/accommodation.py"],
            ["Saved", "user_trip_input.accommodations JSON"],
        ],
        "AccommodationPage → GET /accommodation?trip_id= → accommodation.py uses trip destinations + "
        "stay budget → hotels listed → PATCH trip-input saves chosen hotels.",
        st, w,
    )

    story += [
        PageBreak(),
    ]

    story += screen_block(
        "Screen E — Itinerary (step 4)  ★ main feature",
        "This is the main part. The system builds a day-by-day plan with start times. "
        "It is rule-based: first split days by destination, then set times using moods and "
        "categories — for example heritage earlier, beach later. We skip lunch time and finish around 8 PM. "
        "Important: this is NOT ChatGPT and NOT machine learning.",
        "Click Generate (or Rebuild). Scroll days. Point at times and destinations.",
        [
            ["Frontend", "ItineraryPage.jsx · itineraryApi in client.js"],
            ["Backend", "routes/itinerary.py · trip_plan_service.py · ai_service.py · models/generated_itinerary.py"],
            ["Saved", "generated_itinerary.itinerary JSON"],
        ],
        "ItineraryPage → POST /itinerary/generate → itinerary.py → trip_plan_service splits days → "
        "ai_service adds times → save JSON in generated_itinerary → page shows result.",
        st, w,
    )

    story += screen_block(
        "Screen F — Discover / Recommendations (step 5)",
        "After the plan, tourists can find local businesses, travel agencies, and licensed guides "
        "near their trip cities, and save favorites to the trip.",
        "Open Businesses / Agencies / Guides. Save one item.",
        [
            ["Frontend", "RecommendationsPage.jsx · recommendationsApi · savedRefsApi"],
            ["Backend", "routes/recommendations.py · routes/saved_references.py · business/agency/guide models"],
            ["Saved", "saved_references table"],
        ],
        "Page calls GET with trip_id → recommendations.py filters by destination (SQL ILIKE) → "
        "user saves → POST saved-references.",
        st, w,
    )

    story += [
        PageBreak(),
    ]

    story += screen_block(
        "Screen G — Export (step 6)",
        "Last step. We show a summary of the trip and download a PDF made from the saved itinerary. "
        "Nothing new is invented here — it prints what we already generated.",
        "Click download PDF. Open the PDF briefly for the panel.",
        [
            ["Frontend", "ExportPage.jsx · itineraryApi.pdfUrl + token fetch"],
            ["Backend", "routes/itinerary.py (PDF route) · services/pdf_service.py"],
            ["Saved", "No new row — PDF built from existing trip + itinerary"],
        ],
        "ExportPage → GET /itinerary/&lt;trip_id&gt;/pdf with JWT → itinerary.py → pdf_service.py → PDF bytes.",
        st, w,
    )

    story += screen_block(
        "Screen H — History (side path)",
        "History lists past trips. Opening one puts the old trip back into memory so we can view "
        "or export again. This proves data is saved in the database, not only in the browser.",
        "Open History. Click a past trip. Show it loads on Itinerary.",
        [
            ["Frontend", "HistoryPage.jsx · TripContext reload"],
            ["Backend", "itinerary history + trip-input GET + budget GET"],
            ["Saved", "Reads existing user_trip_input + generated_itinerary"],
        ],
        "HistoryPage loads past rows → user picks one → frontend refills TripContext from API → go to Itinerary.",
        st, w,
    )

    story += screen_block(
        "Screen I — Profile + SOS button",
        "Profile holds visitor details used with SOS, like hotel and emergency contact. "
        "The SOS button opens the Tourist SOS app using the same Travel login — no need to register again.",
        "Optional: open Profile, then click SOS in the top bar.",
        [
            ["Frontend", "ProfilePage.jsx · Layout.jsx · api/sosClient.js · theme/sosProfile.js"],
            ["Backend", "routes/tourists.py (bridge-travel + profile)"],
            ["Saved", "Tourist SOS profile / session token"],
        ],
        "SOS click → sosClient.js POST /api/tourists/bridge-travel with Travel JWT → SOS session → open tourist app.",
        st, w,
    )

    story += [PageBreak()]

    # FILE MAP TABLES
    story += [
        p("5. Full file map (if they ask “show me the files”)", st["h1"]),
        p("5.1 Frontend files", st["h2"]),
        table(
            ["File", "What it does"],
            [
                ["main.jsx", "Starts app; wraps Auth + Trip providers"],
                ["App.jsx", "Routes; blocks pages until login"],
                ["api/client.js", "All Travel API calls + JWT header"],
                ["api/sosClient.js", "Bridge / open Tourist SOS"],
                ["context/AuthContext.jsx", "Login state + token"],
                ["context/TripContext.jsx", "Current trip wizard state"],
                ["components/Layout.jsx", "Sidebar steps, progress, SOS / History / Profile"],
                ["components/AttractionPhoto.jsx", "Place photos"],
                ["components/AttractionDetailModal.jsx", "Attraction details popup"],
                ["pages/LoginPage.jsx", "Register + login"],
                ["pages/AttractionsPage.jsx", "Days, moods, places"],
                ["pages/BudgetPage.jsx", "Money + pie chart"],
                ["pages/AccommodationPage.jsx", "Hotels"],
                ["pages/ItineraryPage.jsx", "Day plan"],
                ["pages/RecommendationsPage.jsx", "Discover + save"],
                ["pages/ExportPage.jsx", "PDF download"],
                ["pages/HistoryPage.jsx", "Past trips"],
                ["pages/ProfilePage.jsx", "Visitor / emergency profile"],
            ],
            st, [w * 0.42, w * 0.58],
        ),
        PageBreak(),
        p("5.2 Backend routes", st["h2"]),
        table(
            ["File", "What it does"],
            [
                ["routes/auth.py", "Register / login / me"],
                ["routes/attractions.py", "List attractions by mood"],
                ["routes/trip_input.py", "Create / update trip"],
                ["routes/budget.py", "Budget split save/get"],
                ["routes/accommodation.py", "Hotels for trip cities"],
                ["routes/itinerary.py", "Generate / get / history / PDF"],
                ["routes/recommendations.py", "Businesses, agencies, guides"],
                ["routes/saved_references.py", "Saved favorites"],
                ["routes/tourists.py", "SOS bridge + profile"],
            ],
            st, [w * 0.40, w * 0.60],
        ),
        p("5.3 Backend services + models", st["h2"]),
        table(
            ["File", "What it does"],
            [
                ["services/budget_service.py", "Budget % and money math"],
                ["services/trip_plan_service.py", "Split days; match hotels to cities"],
                ["services/ai_service.py", "Activity times from rules (no OpenAI)"],
                ["services/pdf_service.py", "Build itinerary PDF"],
                ["models/user.py", "Travel accounts"],
                ["models/attraction.py", "130 attractions"],
                ["models/accommodation.py", "944 hotels"],
                ["models/user_trip_input.py", "Trip core row"],
                ["models/budget_split.py", "Budget categories"],
                ["models/generated_itinerary.py", "Saved day plan JSON"],
                ["models/business_directory.py / travel_agency.py / tourist_guide.py", "Discover catalogs"],
                ["models/saved_reference.py", "Favorites on a trip"],
            ],
            st, [w * 0.48, w * 0.52],
        ),
        PageBreak(),
    ]

    # ITINERARY RULES + DATA
    story += [
        p("6. How itinerary timing works (simple)", st["h1"]),
        table(
            ["Step", "Simple meaning", "File"],
            [
                ["Day split", "One day per city first; extra days reuse places", "trip_plan_service.py"],
                ["Start time", "From selected moods (or user picks a time)", "ai_service.py"],
                ["Category bias", "Wild / heritage earlier; beach / spa later", "ai_service.py"],
                ["Name hints", "Words like temple / beach / safari adjust time", "ai_service.py"],
                ["Spacing", "About 2–3 hours between activities; skip 12–1 lunch", "ai_service.py"],
                ["End of day", "Stop around 8 PM", "ai_service.py"],
            ],
            st, [w * 0.20, w * 0.52, w * 0.28],
        ),
        Spacer(1, 6),
        p("7. Data counts (seeded)", st["h1"]),
        table(
            ["Data", "Count", "Where from"],
            [
                ["Attractions", "130", "attractions.xlsx"],
                ["Hotels", "944", "accomadation.xlsx"],
                ["Businesses", "126", "business_directory.xlsx"],
                ["Agencies", "417", "travel_agencies.xlsx"],
                ["Guides", "2,906", "tourist_guides.csv"],
            ],
            st, [w * 0.28, w * 0.18, w * 0.54],
        ),
        PageBreak(),
    ]

    # PANEL Q&A
    story += [
        p("8. Questions they may ask — short answers", st["h1"]),
        table(
            ["Question", "Simple answer"],
            [
                ["Is this AI / ML?", "No ML model. Rule-based planner. File ai_service.py only sets times from rules."],
                ["Why name ai_service?", "Legacy name. Logic is lookups + heuristics, not OpenAI."],
                ["How hotels match?", "Stay budget filter + destination name/address token match."],
                ["How attractions filter?", "SQL WHERE mood_tag IN selected moods."],
                ["Where is trip saved?", "PostgreSQL user_trip_input + generated_itinerary."],
                ["What if I refresh?", "TripContext memory clears, but saved trip reloads from History / DB."],
                ["How PDF is made?", "pdf_service.py reads saved itinerary and builds PDF with ReportLab."],
                ["How SOS connects?", "bridge-travel exchanges Travel JWT for SOS tourist session."],
                ["Frontend port?", "5180"],
                ["Backend port?", "5002"],
                ["Auth method?", "Flask-JWT-Extended; Bearer token on protected APIs."],
                ["Any training data / accuracy?", "No model training. Quality checked manually + API smoke tests."],
                ["Budget split default?", "About 25% food, 35% stay, 15% shopping, 25% transport."],
                ["Can user change times?", "Yes — Auto start or fixed time, then Rebuild on Itinerary page."],
                ["Discover data real?", "Yes — seeded from Excel/CSV catalogs (agencies, guides registry)."],
            ],
            st, [w * 0.30, w * 0.70],
        ),
        PageBreak(),
    ]

    # RUN + CLOSING
    story += [
        p("9. How to run before demo", st["h1"]),
        bullets([
            "Terminal 1: cd backend → activate .venv → python run.py",
            "Terminal 2: cd frontend → npm run dev (or npm run dev:travel)",
            "Open http://localhost:5180",
            "If empty data: run apply_schema.py then seed_data.py under backend/scripts/travel/",
            "Health check: open http://127.0.0.1:5002/api/health",
        ], st),
        Spacer(1, 8),
        p("10. Closing line", st["h1"]),
        callout(
            "Say at the end",
            "So overall: each screen is a React page, each action goes through client.js to a Flask "
            "route, services apply the rules, and PostgreSQL keeps the trip — then Export turns that "
            "saved plan into a PDF.",
            st,
        ),
        Spacer(1, 10),
        p(
            "Project R26-IT-152 · Warniarachchi P.M.R. (IT22225092) · AI Itinerary Generator · 13 August 2026",
            st["note"],
        ),
    ]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUT),
        pagesize=PAGE,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=1.55 * cm,
        bottomMargin=1.55 * cm,
        title="Travel Component Demonstration",
        author="Warniarachchi P.M.R.",
    )
    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    build()
