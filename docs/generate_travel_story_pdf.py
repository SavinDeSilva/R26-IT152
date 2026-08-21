"""
Travel Dashboard PDF — story style:
First user registers → these files work like this (logic) → then login → then each step.

Run from backend:
  .\\.venv\\Scripts\\python.exe ..\\docs\\generate_travel_story_pdf.py

Output:
  docs/pdfs/Travel_Dashboard_Story_Guide.pdf
"""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
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

OUT = Path(__file__).resolve().parent / "pdfs" / "Travel_Dashboard_Story_Guide.pdf"
PAGE = A4
M = 1.7 * cm

NAVY = colors.HexColor("#0F2744")
TEAL = colors.HexColor("#0D6E6E")
SOFT = colors.HexColor("#F4F7FA")
LINE = colors.HexColor("#D5DEE8")
MUTED = colors.HexColor("#4A5A6A")
WHITE = colors.white


def S():
    b = getSampleStyleSheet()
    return {
        "cover": ParagraphStyle("c", parent=b["Title"], fontName="Helvetica-Bold", fontSize=22, leading=28, textColor=NAVY, alignment=TA_CENTER, spaceAfter=8),
        "sub": ParagraphStyle("s", parent=b["Normal"], fontName="Helvetica", fontSize=11, leading=15, textColor=MUTED, alignment=TA_CENTER, spaceAfter=6),
        "h1": ParagraphStyle("h1", parent=b["Heading1"], fontName="Helvetica-Bold", fontSize=14, leading=18, textColor=NAVY, spaceBefore=10, spaceAfter=6),
        "h2": ParagraphStyle("h2", parent=b["Heading2"], fontName="Helvetica-Bold", fontSize=11.5, leading=15, textColor=TEAL, spaceBefore=9, spaceAfter=4),
        "body": ParagraphStyle("body", parent=b["Normal"], fontName="Helvetica", fontSize=9.5, leading=13, textColor=colors.HexColor("#1A2430"), alignment=TA_JUSTIFY, spaceAfter=5),
        "bullet": ParagraphStyle("bu", parent=b["Normal"], fontName="Helvetica", fontSize=9.2, leading=12.2, textColor=colors.HexColor("#1A2430")),
        "file": ParagraphStyle("file", parent=b["Normal"], fontName="Helvetica-Bold", fontSize=9.5, leading=12, textColor=NAVY, spaceBefore=6, spaceAfter=2),
        "logic": ParagraphStyle("logic", parent=b["Normal"], fontName="Helvetica", fontSize=9, leading=12, textColor=colors.HexColor("#1A2430"), leftIndent=8, spaceAfter=4),
        "note": ParagraphStyle("n", parent=b["Normal"], fontName="Helvetica-Oblique", fontSize=8.5, leading=11, textColor=MUTED, spaceAfter=6),
        "cell": ParagraphStyle("cell", parent=b["Normal"], fontName="Helvetica", fontSize=8, leading=10.5, textColor=colors.HexColor("#1A2430")),
        "cell_b": ParagraphStyle("cellb", parent=b["Normal"], fontName="Helvetica-Bold", fontSize=8, leading=10.5, textColor=NAVY),
    }


def hf(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.5)
    canvas.line(M, PAGE[1] - 1.1 * cm, PAGE[0] - M, PAGE[1] - 1.1 * cm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(M, PAGE[1] - 0.9 * cm, "Tour Ceylon — Travel story guide")
    canvas.drawRightString(PAGE[0] - M, PAGE[1] - 0.9 * cm, "Register → Export (file-by-file logic)")
    canvas.line(M, 1.1 * cm, PAGE[0] - M, 1.1 * cm)
    canvas.drawCentredString(PAGE[0] / 2, 0.65 * cm, f"Page {doc.page}")
    canvas.restoreState()


def P(t, s):
    return Paragraph(str(t).replace("\n", "<br/>"), s)


def bullets(items, st):
    return ListFlowable(
        [ListItem(Paragraph(i, st["bullet"]), leftIndent=8, bulletColor=TEAL) for i in items],
        bulletType="bullet", start="•", leftIndent=6, bulletFontSize=9,
    )


def file_block(st, name, what, logic_lines):
    """One file explained: what it is + how its logic works."""
    bits = [P(f"FILE: {name}", st["file"]), P(what, st["body"])]
    bits.append(P("<b>How the logic works:</b>", st["logic"]))
    bits.append(bullets(logic_lines, st))
    return bits


def callout(st, title, body):
    inner = [Paragraph(f"<b>{title}</b>", st["cell_b"]), Spacer(1, 2), Paragraph(body, st["cell"])]
    t = Table([[inner]], colWidths=[PAGE[0] - 2 * M])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#E8F4F4")),
        ("BOX", (0, 0), (-1, -1), 1, TEAL),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def build():
    st = S()
    w = PAGE[0] - 2 * M
    story = []

    story += [
        Spacer(1, 1.8 * cm),
        P("Tour Ceylon", st["sub"]),
        P("Travel Dashboard — Story Guide", st["cover"]),
        P("Follow the user from register to export. At each step, see which files run and how their logic works.", st["sub"]),
        Spacer(1, 0.4 * cm),
        callout(st, "How to read this PDF",
                "We follow one user journey. First they register — we explain those files. "
                "Then they log in — next files. Then Attractions, Budget, Stay, Itinerary, Discover, Export. "
                "Each FILE block = what the file is + how its logic works in plain English."),
        PageBreak(),
    ]

    # BOOT
    story += [
        P("0. Before anything — app starts", st["h1"]),
        P("When you open Travel in the browser, these files wake up first.", st["body"]),
        *file_block(st, "frontend/travel/src/main.jsx",
            "Starts React. Puts AuthProvider and TripProvider around the whole app.",
            [
                "Creates the React root and renders App inside BrowserRouter.",
                "AuthProvider = shared login state for every page.",
                "TripProvider = shared trip wizard memory for every page.",
            ]),
        *file_block(st, "frontend/travel/src/App.jsx",
            "Map of all pages. Decides public login vs protected wizard pages.",
            [
                "Route /login shows LoginPage (no token needed).",
                "ProtectedRoute checks AuthContext: if not logged in → send to /login.",
                "If logged in, Layout wraps Attractions → Budget → Stay → Itinerary → Discover → Export.",
                "Also routes /history and /profile.",
            ]),
        *file_block(st, "frontend/travel/src/context/AuthContext.jsx",
            "Remembers who is logged in. Talks to auth API. Saves JWT.",
            [
                "On load: reads access_token from localStorage.",
                "If token expired or /auth/me fails → logout (clear storage).",
                "register() / login() / loginWithGoogle() call API, then persistAuth().",
                "persistAuth stores access_token + user JSON in localStorage.",
                "Also tries to link a Tourist SOS session (sosClient) so Profile/SOS work later.",
            ]),
        *file_block(st, "frontend/travel/src/context/TripContext.jsx",
            "Holds the current trip while the user walks the wizard (in browser memory).",
            [
                "Stores tripId, moods, days, attractions, budget, hotels, itinerary, etc.",
                "updateTrip() merges new fields after each step.",
                "Not written to localStorage — refresh can clear it; History can reload from DB.",
            ]),
        *file_block(st, "frontend/travel/src/api/client.js",
            "Axios helper. Every Travel API call goes through here.",
            [
                "Adds Authorization: Bearer &lt;token&gt; on each request.",
                "If server returns 401 → clears token (user must log in again).",
                "Exports authApi, attractionsApi, tripApi, budgetApi, accommodationApi, itineraryApi, etc.",
            ]),
        *file_block(st, "frontend/travel/src/components/Layout.jsx",
            "Shell around wizard pages: sidebar steps, progress, SOS / History / Profile / logout.",
            [
                "Shows which step you are on.",
                "SOS button uses sosClient to open Tourist SOS with the Travel login.",
                "Logout clears AuthContext.",
            ]),
        PageBreak(),
    ]

    # REGISTER
    story += [
        P("1. First — user registers", st["h1"]),
        P("User opens /login, switches to Register, types email + password, clicks create account.", st["body"]),
        *file_block(st, "pages/LoginPage.jsx (register mode)",
            "The form the user fills. Can also show Google button if configured.",
            [
                "mode state = 'login' or 'register'.",
                "On submit register: calls AuthContext.register(email, password).",
                "Shows error text if API fails (email taken, short password, …).",
                "On success, user is authenticated → App.jsx sends them into the wizard.",
            ]),
        *file_block(st, "context/AuthContext.jsx → register()",
            "Frontend register function.",
            [
                "Calls authApi.register({ email, password }).",
                "On success: persistAuth(data) → save JWT + user.",
                "setToken / setUser so React knows we are logged in.",
                "Tries syncSosSession so SOS profile can be linked later.",
            ]),
        *file_block(st, "api/client.js → authApi.register",
            "Sends POST /api/auth/register to Flask.",
            [
                "Body: email + password.",
                "Expects back: access_token + user object.",
            ]),
        *file_block(st, "backend/app/routes/auth.py → register()",
            "Server logic for creating a Travel account.",
            [
                "Reads email + password from JSON.",
                "Rejects empty fields or password shorter than 6 characters.",
                "Checks users table: if email already exists → 409 error.",
                "Creates User(email), hashes password with set_password(), saves to DB.",
                "Returns JWT via _issue_token(user) with role travel_user.",
            ]),
        *file_block(st, "backend/app/models/user.py (class User)",
            "Database model for table users.",
            [
                "Stores email, password hash, name, Google fields if used.",
                "set_password() hashes the password (not stored as plain text).",
                "check_password() used later at login.",
                "to_dict() returns safe user info (no password) to the frontend.",
            ]),
        P("<b>Result after register:</b> new row in users + JWT in browser → user can enter Attractions.", st["note"]),
        PageBreak(),
    ]

    # LOGIN
    story += [
        P("2. Next — user logs in (returning user)", st["h1"]),
        P("Same LoginPage, but mode = login. User enters email + password (or Google).", st["body"]),
        *file_block(st, "pages/LoginPage.jsx (login mode)",
            "Login form.",
            [
                "Calls AuthContext.login(email, password) or Google callback.",
                "On success → protected routes unlock.",
            ]),
        *file_block(st, "context/AuthContext.jsx → login()",
            "Frontend login function.",
            [
                "Calls authApi.login({ email, password }).",
                "Saves token like register.",
                "Links SOS session if possible.",
            ]),
        *file_block(st, "backend/app/routes/auth.py → login()",
            "Server checks credentials.",
            [
                "If body has username → police officer path (not Travel).",
                "Travel path: find User by email.",
                "If Google-only account → tell user to use Google Sign-In.",
                "check_password(password); if wrong → 401.",
                "If ok → return JWT + user dict.",
            ]),
        *file_block(st, "App.jsx → ProtectedRoute",
            "After login, every wizard page is guarded.",
            [
                "ready must be true (token checked).",
                "isAuthenticated must be true, else Navigate to /login.",
                "Children (Layout + page) only render when logged in.",
            ]),
        P("<b>Result after login:</b> same as register — JWT ready, wizard opens at /attractions.", st["note"]),
        PageBreak(),
    ]

    # ATTRACTIONS
    story += [
        P("3. Then — user picks attractions", st["h1"]),
        P("User sets days, picks moods (max 3), selects places, clicks confirm. This CREATES the trip.", st["body"]),
        *file_block(st, "pages/AttractionsPage.jsx",
            "Attractions screen — first wizard step.",
            [
                "Loads all attractions with attractionsApi.list().",
                "User toggles moods (MOOD_OPTIONS must match backend mood names).",
                "Filters list by mood / category / search text.",
                "User selects places (limit linked to number of days / destinations).",
                "On confirm: builds selected_moods + finalized_attraction ids.",
                "Calls tripApi.create(...) → server creates user_trip_input.",
                "Saves tripId into TripContext, then navigates to /budget.",
            ]),
        *file_block(st, "components/AttractionPhoto.jsx",
            "Shows each place’s image.",
            [
                "If image URL fails, shows a gradient fallback so the card still looks fine.",
            ]),
        *file_block(st, "api/client.js → attractionsApi + tripApi.create",
            "HTTP calls for this step.",
            [
                "GET /api/attractions — catalog from DB.",
                "POST /api/trip-input — create the trip with days, moods, attraction ids.",
            ]),
        *file_block(st, "backend/app/routes/attractions.py",
            "Returns attraction catalog.",
            [
                "Optional moods query filter.",
                "Reads Attraction model rows from Postgres.",
            ]),
        *file_block(st, "backend/app/routes/trip_input.py → create_trip_input()",
            "Creates the trip row for this user.",
            [
                "Requires JWT (get_current_user_id).",
                "Validates days &gt; 0 and 1–3 moods.",
                "Loads Attraction rows for selected ids; merges moods from places + UI.",
                "Saves UserTripInput: days, selected_moods, finalized_attractions, status in_progress.",
                "Returns trip dict including trip_id (UUID).",
            ]),
        *file_block(st, "backend/app/models/attraction.py + user_trip_input.py",
            "Tables used here.",
            [
                "attractions = seed catalog (name, destination, mood_tag, category, details).",
                "user_trip_input = this user’s trip (the core row later steps update).",
            ]),
        *file_block(st, "backend/app/utils/trip_helpers.py",
            "Security helper used from now on.",
            [
                "get_user_trip(trip_id) only returns the trip if it belongs to the JWT user.",
                "Stops one user from editing another user’s trip.",
            ]),
        P("<b>Result:</b> trip exists in DB + tripId in TripContext. Next: Budget.", st["note"]),
        PageBreak(),
    ]

    # BUDGET
    story += [
        P("4. Then — user sets budget", st["h1"]),
        P("User enters total money and splits % across food / stay / shopping / transport.", st["body"]),
        *file_block(st, "pages/BudgetPage.jsx",
            "Budget screen.",
            [
                "Needs trip.tripId from TripContext (from Attractions confirm).",
                "User edits total + optional manual %; pie chart (Recharts) updates.",
                "On confirm: budgetApi.split(tripId, total, percents).",
                "Updates TripContext budget fields → navigate to /accommodation.",
            ]),
        *file_block(st, "backend/app/routes/budget.py",
            "Saves the budget split for the trip.",
            [
                "Checks trip ownership via get_user_trip.",
                "Calls budget_service to validate % and compute money amounts.",
                "Writes budget_split row; updates user_trip_input.budget.",
            ]),
        *file_block(st, "backend/app/services/budget_service.py",
            "Money rules.",
            [
                "Default percentages if user did not customize.",
                "Validates splits add up correctly.",
                "Computes per-night stay budget used later to filter hotels.",
            ]),
        *file_block(st, "backend/app/models/budget_split.py",
            "Table budget_split — stores amounts and % for this trip.",
            [
                "Linked to user_trip_input by trip_id.",
            ]),
        P("<b>Result:</b> budget saved. Stay page can filter hotels by stay money.", st["note"]),
        PageBreak(),
    ]

    # STAY
    story += [
        P("5. Then — user picks hotels (Stay)", st["h1"]),
        P("For each city in the trip, user picks one hotel that fits the stay budget.", st["body"]),
        *file_block(st, "pages/AccommodationPage.jsx",
            "Stay screen.",
            [
                "Calls accommodationApi.list(tripId) → hotels grouped by destination.",
                "User picks one hotel per city.",
                "On continue: tripApi.update with accommodations_by_destination.",
                "Clears old itinerary in context (must rebuild times later).",
                "Navigates to /itinerary.",
            ]),
        *file_block(st, "backend/app/routes/accommodation.py",
            "Lists hotels for this trip.",
            [
                "Uses trip_plan_service for destinations from selected attractions.",
                "Uses budget_service for per-night LKR limit.",
                "hotels_for_destination() only returns hotels that match city + budget.",
            ]),
        *file_block(st, "backend/app/routes/trip_input.py → PATCH",
            "Saves hotel choices on the trip.",
            [
                "validate_accommodation_picks() checks every city has a matching hotel.",
                "expand_destination_picks() makes per-day hotel rows.",
                "Saves JSON on user_trip_input.accommodations.",
            ]),
        *file_block(st, "backend/app/services/trip_plan_service.py (hotel parts)",
            "Matching logic for hotels ↔ cities.",
            [
                "trip_destinations() = unique cities from selected places.",
                "hotel_matches_destination() searches hotel address/area for city words.",
                "validate_accommodation_picks() returns error messages if pick is wrong.",
            ]),
        *file_block(st, "backend/app/models/accommodation.py",
            "Table accommodation — seeded hotel catalog (name, price, area, …).",
            [
                "Read-only catalog for matching; user’s picks are stored on the trip row.",
            ]),
        P("<b>Result:</b> hotels saved per day/city. Itinerary can now be generated.", st["note"]),
        PageBreak(),
    ]

    # ITINERARY
    story += [
        P("6. Then — itinerary is generated", st["h1"]),
        P(
            "User opens Itinerary. App loads an existing plan or asks the server to generate one. "
            "User can pick Auto start (by mood) or a fixed time and Rebuild. "
            "No OpenAI — rules + database only.",
            st["body"],
        ),
        *file_block(st, "pages/ItineraryPage.jsx",
            "Itinerary screen.",
            [
                "If no tripId or no hotels → shows message to go back.",
                "Tries GET existing itinerary; if 404 → POST generate.",
                "dayStart dropdown: '' = Auto by mood; or fixed like 08:30 AM.",
                "Rebuild calls generate again with chosen dayStart.",
                "Renders each day: hotel + timed activities from the JSON.",
                "Buttons go to Discover or Export.",
            ]),
        *file_block(st, "api/client.js → itineraryApi",
            "Calls generate / get / history / pdf URL.",
            [
                "POST /itinerary/generate with trip_id + optional day_start.",
                "GET /itinerary/&lt;trip_id&gt; for saved plan.",
            ]),
        *file_block(st, "backend/app/routes/itinerary.py → generate()",
            "Controller: check trip → build → save.",
            [
                "Requires attractions, hotels, budget already on the trip.",
                "Deletes old generated_itinerary rows for this trip (clean rebuild).",
                "Calls generate_itinerary(trip, day_start=...).",
                "Saves JSON into GeneratedItinerary; returns it to the UI.",
            ]),
        *file_block(st, "backend/app/services/trip_plan_service.py (day split)",
            "Separates places across days BEFORE times are made.",
            [
                "get_day_plan(): one lead city/place per day; every city gets a day.",
                "Extra days filled by cycling selected places.",
                "attractions_grouped_by_day(): all places in a city go on that city’s day(s).",
                "hotel_for_day(): hotel name for that day number.",
            ]),
        *file_block(st, "backend/app/services/ai_service.py",
            "Builds clock times + final day JSON (still no OpenAI).",
            [
                "Day start: user pick OR average of selected moods (Spiritual early, Relaxed late).",
                "First activity bias: real categories Wild/Heritage/… or name words like temple/beach.",
                "Spacing: 1 stop = start only; 2 ≈ 3h; 3 ≈ 2.5h; more ≈ 2h; lunch push 12–1; not after ~8 PM.",
                "Fills each activity with title, mood, category, description from DB.",
                "Returns dict with source: database.",
            ]),
        *file_block(st, "backend/app/models/generated_itinerary.py",
            "Table that stores the finished plan JSON.",
            [
                "to_dict() sends id, trip_id, itinerary, created_at to the frontend.",
            ]),
        P("<b>Result:</b> day-by-day schedule saved. Next: Discover, then Export.", st["note"]),
        PageBreak(),
    ]

    # DISCOVER
    story += [
        P("7. Then — user discovers recommendations", st["h1"]),
        P("User browses businesses, agencies, guides near trip cities and can bookmark favorites.", st["body"]),
        *file_block(st, "pages/RecommendationsPage.jsx",
            "Discover screen.",
            [
                "Loads lists via recommendationsApi (businesses, agencies, guides).",
                "User can save favorites via savedRefsApi.",
                "Continue → /export.",
            ]),
        *file_block(st, "backend/app/routes/recommendations.py",
            "Returns directory lists filtered near trip destinations.",
            [
                "Reads business_directory, travel_agencies, tourist_guides tables.",
            ]),
        *file_block(st, "backend/app/routes/saved_references.py + models",
            "Saves bookmarks on the trip.",
            [
                "saved_references table: trip_id + ref_type + ref_id.",
            ]),
        P("<b>Result:</b> optional favorites saved. Export can still work without them.", st["note"]),
        PageBreak(),
    ]

    # EXPORT
    story += [
        P("8. Finally — user exports PDF", st["h1"]),
        P("User reviews the summary and downloads the itinerary PDF.", st["body"]),
        *file_block(st, "pages/ExportPage.jsx",
            "Export screen.",
            [
                "Reads trip + itinerary from TripContext (already generated).",
                "Shows summary of days, places, stays.",
                "Download: fetch itineraryApi.pdfUrl(tripId) with Bearer token.",
                "Browser saves the PDF file.",
            ]),
        *file_block(st, "backend/app/routes/itinerary.py → export_pdf()",
            "PDF download endpoint.",
            [
                "Loads trip + latest GeneratedItinerary for that user.",
                "Calls pdf_service.render_itinerary_pdf(trip, itinerary_json).",
                "Sends PDF bytes as a file download.",
            ]),
        *file_block(st, "backend/app/services/pdf_service.py",
            "Turns the saved itinerary JSON into a PDF document.",
            [
                "Uses trip title, route, day activities, hotels, descriptions.",
                "Does not invent new places — only formats what was already generated.",
            ]),
        P("<b>Result:</b> user has a PDF of their plan. Wizard complete.", st["note"]),
        PageBreak(),
    ]

    # SIDE + FOLDERS
    story += [
        P("9. Side paths (same product)", st["h1"]),
        P("History", st["h2"]),
        P(
            "HistoryPage.jsx calls itinerary history API → user opens a past trip → "
            "tripApi.get + itinerary get + budget get refill TripContext → jump to Itinerary page.",
            st["body"],
        ),
        P("Profile + SOS", st["h2"]),
        P(
            "ProfilePage.jsx + sosClient.js bridge Travel JWT to a tourist session "
            "(routes/tourists.py). Layout SOS button opens Tourist SOS app with that session. "
            "Police dashboard is separate — not opened from here.",
            st["body"],
        ),
        PageBreak(),
        P("10. Folder map (remember)", st["h1"]),
        bullets([
            "frontend/travel/src/pages — screens the user sees",
            "frontend/travel/src/context — login + trip memory",
            "frontend/travel/src/api — browser → server calls",
            "frontend/travel/src/components — Layout shell + photo helper",
            "backend/app/routes — URL logic for each step",
            "backend/app/models — database tables",
            "backend/app/services — budget math, day split, times, PDF",
            "backend/app/utils/trip_helpers.py — only load your own trip",
            "backend/database + scripts/travel — create tables + seed data",
        ], st),
        Spacer(1, 10),
        callout(st, "Story in one line",
                "Register/Login creates a JWT user → Attractions creates the trip → "
                "Budget and Stay add money + hotels → Itinerary splits days and makes times "
                "from rules → Discover adds optional favorites → Export prints the saved plan as PDF. "
                "Each step: Page file → client.js API → route file → service/model → database."),
    ]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUT), pagesize=PAGE, leftMargin=M, rightMargin=M,
        topMargin=1.65 * cm, bottomMargin=1.65 * cm,
        title="Travel Dashboard Story Guide", author="Tour Ceylon",
    )
    doc.build(story, onFirstPage=hf, onLaterPages=hf)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    build()
