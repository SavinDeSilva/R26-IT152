"""
SOS Component — Demonstration PDF
Screen-by-screen script (simple English) + file connections + panel Q&A.

Run:
  cd backend
  .\\.venv\\Scripts\\activate
  python ..\\docs\\generate_sos_demo_pdf.py

Output:
  docs/pdfs/SOS_Component_Demonstration.pdf
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

OUT = Path(__file__).resolve().parent / "pdfs" / "SOS_Component_Demonstration.pdf"
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
    canvas.drawString(MARGIN, PAGE[1] - 0.85 * cm, "Tour Ceylon — SOS Demo Script + File Map")
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
    return [
        p(title, st["h2"]),
        p(f"<b>Say this:</b> <i>{say}</i>", st["body"]),
        p(f"<b>Do this:</b> {do}", st["body"]),
        table(["Layer", "Files"], files, st, [w * 0.22, w * 0.78]),
        Spacer(1, 3),
        p(f"<b>How connected:</b> {connect}", st["note"]),
        Spacer(1, 6),
    ]


def build():
    st = styles()
    w = PAGE[0] - 2 * MARGIN
    story = []

    # COVER
    story += [
        Spacer(1, 1.3 * cm),
        p("Tour Ceylon", st["sub"]),
        p("SOS Component Demonstration", st["cover"]),
        p("Tourist PWA + Police Dashboard · Screen script · File map · Q&amp;A", st["sub"]),
        Spacer(1, 0.35 * cm),
        table(
            ["Field", "Value"],
            [
                ["Project ID", "R26-IT-152"],
                ["Student", "De Silva D.S.K. (IT22108654)"],
                ["Component", "SOS System (Tourist + Police)"],
                ["Date", "13 August 2026"],
                ["Tourist app", "http://localhost:5175"],
                ["Police app", "http://localhost:5176"],
                ["API", "http://127.0.0.1:5002/api"],
            ],
            st, [w * 0.28, w * 0.72],
        ),
        Spacer(1, 0.35 * cm),
        callout(
            "How to use this PDF while presenting",
            "Demo has two apps: Tourist SOS (:5175) and Police Dashboard (:5176). "
            "For each screen: read “Say this”, click “Do this”, and use Files / How connected "
            "if they ask which file or how it works.",
            st,
        ),
        PageBreak(),
    ]

    # BIG PICTURE
    story += [
        p("1. Big picture (30 seconds)", st["h1"]),
        p(
            "SOS helps a tourist get help fast. One tap sends an emergency alert with GPS location "
            "to the nearest police station. The police dashboard lets that station acknowledge, "
            "dispatch, chat, close the case, and download a PDF report. "
            "Travel login can open SOS without registering again.",
            st["body"],
        ),
        p(
            "<b>Demo path:</b> Tourist login → trigger SOS → workflow + chat → "
            "Police login → acknowledge → dispatch → close → PDF",
            st["body"],
        ),
        p(
            "<b>Code path:</b> React page → api/client.js → Flask route → routing/notify/pdf services → PostgreSQL",
            st["body"],
        ),
        Spacer(1, 4),
        callout(
            "One sentence if they ask “what did you build?”",
            "I built a Tourist SOS PWA and a Police Dashboard: one-tap alert with GPS, "
            "Haversine nearest-station routing, station workflow, chat, hospital dial, "
            "and PDF reports — with Travel login bridge.",
            st,
        ),
        Spacer(1, 8),
        p("2. Tech (short answers)", st["h1"]),
        table(
            ["They ask", "You say"],
            [
                ["Tourist frontend?", "React + Vite PWA — frontend/tourist — port 5175"],
                ["Police frontend?", "React + Vite + Leaflet — frontend/police — port 5176"],
                ["Backend?", "Same Flask API as Travel — backend/run.py — port 5002"],
                ["Database?", "PostgreSQL — tourists, incidents, stations, chat, etc."],
                ["Login?", "JWT — touristToken / policeToken in localStorage"],
                ["Routing method?", "Haversine distance — nearest dispatchable station (not ML)"],
                ["Sensitive data?", "Fernet encryption for phone, passport/NIC, emergency contact"],
                ["Map?", "Leaflet on police IncidentDetail"],
                ["PDF?", "ReportLab for closed incident reports"],
                ["Notifications?", "Console stub by default; Twilio/SendGrid optional"],
            ],
            st, [w * 0.28, w * 0.72],
        ),
        PageBreak(),
    ]

    # HOW FILES CONNECT
    story += [
        p("3. How files connect (whole SOS system)", st["h1"]),
        bullets([
            "<b>Tourist page / Police page</b> — what the user sees",
            "<b>api/client.js</b> — sends request + JWT",
            "<b>Flask route</b> — tourists.py / incidents.py / hospitals.py / auth.py",
            "<b>Service</b> — Haversine routing, notify, PDF export",
            "<b>Model / DB</b> — sos_models + PostgreSQL tables",
        ], st),
        Spacer(1, 4),
        table(
            ["Folder", "Job in one line"],
            [
                ["frontend/tourist/", "Tourist SOS PWA (alert, chat, profile)"],
                ["frontend/tourist/src/pages/", "Login, Home, History, Profile, Enter"],
                ["frontend/tourist/src/components/", "SOSButton, workflow, chat, hospital"],
                ["frontend/tourist/src/hooks/", "useGeolocation — one GPS read"],
                ["frontend/police/", "Police dashboard + map + stats"],
                ["frontend/police/src/pages/", "Login, Dashboard, IncidentDetail"],
                ["frontend/police/src/components/", "Map, chat, charts, cards"],
                ["backend/app/routes/", "incidents, tourists, hospitals, auth"],
                ["backend/app/services/", "routing.py, notify.py, pdf_export.py"],
                ["backend/app/sos_models.py", "SOS database tables"],
                ["backend/seed_sos_data.py", "Seed stations, officers, demo tourists"],
            ],
            st, [w * 0.42, w * 0.58],
        ),
        PageBreak(),
    ]

    # TOURIST SCREENS
    story += [
        p("4. Tourist app — screen-by-screen", st["h1"]),
        p(
            "Start: backend python run.py · tourist npm run dev · open :5175 · "
            "seed: python seed_sos_data.py · demo tourist emma@example.com / tourist123",
            st["note"],
        ),
    ]

    story += screen_block(
        "Screen A — Login / Register / Enter (Travel bridge)",
        "Tourists can register here, or come from the Travel app. Enter / bridge-travel "
        "exchanges a Travel JWT for a tourist SOS session, so they do not register twice.",
        "Login as emma@example.com / tourist123 OR open SOS from Travel and show handoff.",
        [
            ["Frontend", "Login.jsx · Register.jsx · Enter.jsx · api/client.js · sessionHandoff.js · travelBridge.js"],
            ["Backend", "routes/tourists.py (register, login, bridge-travel, me) · sos_models tourists"],
            ["Saved", "tourists table · localStorage touristToken + touristId"],
        ],
        "Login/Enter → POST /api/tourists/login or /bridge-travel → tourists.py → JWT → save touristToken → go Home.",
        st, w,
    )

    story += screen_block(
        "Screen B — Home + SOS button  ★ main tourist feature",
        "This is the main tourist screen. The big SOS control lets them choose a type — "
        "general, medical, assault, theft, accident, or harassment. One tap takes GPS once "
        "(not live tracking), creates an incident, and sends it to the nearest police station.",
        "Allow location. Tap SOS type (e.g. medical). Wait for sent overlay showing station name.",
        [
            ["Frontend", "App.jsx (triggerSOS) · Home.jsx · SOSButton.jsx · SOSSentOverlay.jsx · useGeolocation.js"],
            ["Backend", "routes/incidents.py · services/routing.py · notify.py · sos_models incidents + location_pings"],
            ["Saved", "incidents row + one location_ping · activeIncidentId in localStorage"],
        ],
        "SOSButton → App.triggerSOS → getCurrent() GPS → POST /api/incidents → incidents.py → "
        "Haversine nearest station → save incident → notify emergency contact/hotel → overlay shows station.",
        st, w,
    )

    story += [PageBreak()]

    story += screen_block(
        "Screen C — Incident workflow (status tracker)",
        "After sending SOS, the tourist sees the status change: Open → Acknowledged → Dispatched → Closed. "
        "The page polls the server every few seconds. There is no WebSocket — simple HTTP polling.",
        "Keep Home open. After police acknowledge (next screens), show status updating here.",
        [
            ["Frontend", "IncidentWorkflow.jsx · Home.jsx polling"],
            ["Backend", "GET /api/incidents/&lt;id&gt;/status · incidents.py"],
            ["Saved", "incident status + timestamps (acknowledged_at, dispatched_at, closed_at)"],
        ],
        "IncidentWorkflow polls status API → incidents.py returns current status → UI steps light up.",
        st, w,
    )

    story += screen_block(
        "Screen D — Incident chat (tourist side)",
        "Tourist and the assigned police station can chat — text, and also image or voice. "
        "Messages belong to that incident only.",
        "Send a short text message from tourist. Later show the same chat on police side.",
        [
            ["Frontend", "IncidentChat.jsx (tourist) · api/client.js"],
            ["Backend", "GET/POST /api/incidents/&lt;id&gt;/messages · chat / incidents routes · chat_messages table"],
            ["Saved", "chat_messages rows for that incident"],
        ],
        "IncidentChat → messages API with tourist JWT → server stores chat_messages → police app polls same endpoint.",
        st, w,
    )

    story += screen_block(
        "Screen E — Call nearest hospital",
        "If it is a medical case, the tourist can find the nearest hospital. "
        "Same Haversine idea as police routing. The app gives a dial number — hospital is not auto-dispatched.",
        "Tap Call nearest hospital. Show hospital name + distance. Optional: show tel: link.",
        [
            ["Frontend", "CallNearestHospital.jsx · useGeolocation.js"],
            ["Backend", "routes/hospitals.py · GET /api/hospitals/nearest?lat=&amp;lng= · hospitals table"],
            ["Saved", "Read-only lookup — no new incident field required"],
        ],
        "CallNearestHospital gets GPS → GET /hospitals/nearest → hospitals.py Haversine → returns dial_number.",
        st, w,
    )

    story += [PageBreak()]

    story += screen_block(
        "Screen F — History + Profile",
        "History shows past and active incidents. Profile holds tourist details like hotel and "
        "emergency contact. Sensitive fields are encrypted in the database with Fernet.",
        "Open History briefly. Open Profile and point to emergency contact / hotel fields.",
        [
            ["Frontend", "History.jsx · Profile.jsx · TouristNav.jsx"],
            ["Backend", "GET /tourists/me/incidents · GET/PATCH profile via tourists.py · emergency_contacts"],
            ["Saved", "tourists + emergency_contacts (encrypted phone/email)"],
        ],
        "Profile/History pages → tourists.py with tourist JWT → read/update sos_models → encrypted PII at rest.",
        st, w,
    )

    # POLICE SCREENS
    story += [
        p("5. Police app — screen-by-screen", st["h1"]),
        p(
            "Open http://localhost:5176 · demo officer st001 / Police001! "
            "(from seed station_credentials.csv)",
            st["note"],
        ),
    ]

    story += screen_block(
        "Screen G — Police login",
        "Officers log in with station credentials. The JWT is station-scoped — "
        "they only see incidents for their own station, not every station in Sri Lanka.",
        "Login as st001 / Police001!. Land on Dashboard.",
        [
            ["Frontend", "police Login.jsx · api/client.js"],
            ["Backend", "POST /api/auth/login · officers table"],
            ["Saved", "localStorage policeToken · officer station_id in JWT claims"],
        ],
        "Login → /api/auth/login → officer JWT with station_id → Dashboard loads only that station’s queue.",
        st, w,
    )

    story += screen_block(
        "Screen H — Dashboard queue + stats  ★ main police feature",
        "This is the station queue. New SOS cases for this station appear here. "
        "Officers can see type, status, and response timing. Charts show volume and response times. "
        "Audio alert can play for new open cases.",
        "Show the open incident from the tourist demo. Point at IncidentCard and StatsCharts.",
        [
            ["Frontend", "Dashboard.jsx · IncidentCard.jsx · StatsCharts.jsx · ResponseClock.jsx"],
            ["Backend", "GET /api/incidents · GET /api/incidents/stats · incidents.py"],
            ["Saved", "Reads incidents filtered by officer station_id"],
        ],
        "Dashboard polls GET /incidents with police JWT → incidents.py filters by station → cards + stats charts.",
        st, w,
    )

    story += [PageBreak()]

    story += screen_block(
        "Screen I — Incident detail + map + workflow buttons",
        "Opening a case shows tourist details (decrypted for officers), GPS on a Leaflet map, "
        "distance to station, and buttons: Acknowledge → Dispatch → Close. "
        "Status updates are what the tourist workflow tracker is waiting for.",
        "Open the incident. Click Acknowledge, then Dispatch. Show map pin. Later Close.",
        [
            ["Frontend", "IncidentDetail.jsx · LiveMap.jsx · IncidentChat.jsx (police)"],
            ["Backend", "PATCH .../acknowledge · .../dispatch · .../close · incidents.py"],
            ["Saved", "incident status + acknowledged_at / dispatched_at / closed_at"],
        ],
        "Buttons → PATCH status routes → update incident row → tourist polling sees new status · map uses initial_lat/lng.",
        st, w,
    )

    story += screen_block(
        "Screen J — Police chat + PDF report",
        "Police can reply in the same incident chat. After Close, they can download a PDF report "
        "with tourist info, GPS, timestamps, and notes — useful for records.",
        "Reply in chat. Close incident. Download report PDF.",
        [
            ["Frontend", "IncidentChat.jsx · IncidentDetail PDF button"],
            ["Backend", "messages APIs · GET /api/incidents/&lt;id&gt;/report.pdf · services/pdf_export.py"],
            ["Saved", "chat_messages · PDF generated from closed incident only"],
        ],
        "Close → status closed → report.pdf → pdf_export.build_incident_pdf(incident) → download.",
        st, w,
    )

    story += [PageBreak()]

    # FILE MAPS
    story += [
        p("6. Full file map", st["h1"]),
        p("6.1 Tourist frontend (frontend/tourist/src/)", st["h2"]),
        table(
            ["File", "What it does"],
            [
                ["main.jsx / App.jsx", "App shell; SOS trigger; auth gate; overlay"],
                ["api/client.js", "Tourist API + session helpers"],
                ["api/sessionHandoff.js / travelBridge.js", "Travel → SOS login bridge"],
                ["hooks/useGeolocation.js", "One-shot browser GPS"],
                ["pages/Login.jsx / Register.jsx / Enter.jsx", "Auth + handoff entry"],
                ["pages/Home.jsx", "Main screen + active incident"],
                ["pages/History.jsx", "Past incidents"],
                ["pages/Profile.jsx", "Tourist + emergency profile"],
                ["components/SOSButton.jsx", "Six-type one-tap SOS bar"],
                ["components/SOSSentOverlay.jsx", "Sent confirmation + station"],
                ["components/IncidentWorkflow.jsx", "Open→Ack→Dispatch→Closed tracker"],
                ["components/IncidentChat.jsx", "Tourist chat UI"],
                ["components/CallNearestHospital.jsx", "Nearest hospital dial"],
                ["components/TouristNav.jsx", "Bottom / nav links"],
            ],
            st, [w * 0.46, w * 0.54],
        ),
        p("6.2 Police frontend (frontend/police/src/)", st["h2"]),
        table(
            ["File", "What it does"],
            [
                ["App.jsx", "Routes; policeToken gate"],
                ["api/client.js", "Police API + JWT"],
                ["pages/Login.jsx", "Officer login"],
                ["pages/Dashboard.jsx", "Station incident queue"],
                ["pages/IncidentDetail.jsx", "Case detail, actions, PDF"],
                ["components/IncidentCard.jsx", "Queue card"],
                ["components/LiveMap.jsx", "Leaflet map for GPS"],
                ["components/IncidentChat.jsx", "Police chat UI"],
                ["components/StatsCharts.jsx", "Volume / response charts"],
                ["components/ResponseClock.jsx", "Timing display"],
            ],
            st, [w * 0.42, w * 0.58],
        ),
        PageBreak(),
        p("6.3 Backend SOS files", st["h2"]),
        table(
            ["File", "What it does"],
            [
                ["routes/tourists.py", "Register, login, bridge-travel, me, profile"],
                ["routes/incidents.py", "Create SOS, status, workflow PATCH, stats, PDF"],
                ["routes/hospitals.py", "Nearest hospital lookup"],
                ["routes/auth.py", "Police officer login"],
                ["routes/chat.py / messages in incidents", "Incident chat send/list"],
                ["services/routing.py", "Haversine nearest station / hospital"],
                ["services/notify.py", "Emergency contact + hotel notify (stub/real)"],
                ["services/pdf_export.py", "Closed incident PDF"],
                ["sos_models.py", "tourists, contacts, stations, officers, hospitals, incidents, pings, chat"],
                ["seed_sos_data.py", "Seed Excel stations/hospitals + demo users"],
            ],
            st, [w * 0.42, w * 0.58],
        ),
        PageBreak(),
    ]

    # ROUTING + DATA
    story += [
        p("7. How nearest-station routing works (simple)", st["h1"]),
        table(
            ["Step", "Simple meaning", "Where"],
            [
                ["1. GPS", "Browser gives lat/lng once at SOS tap", "useGeolocation.js"],
                ["2. Stations", "Load dispatchable police desks with coordinates", "stations table"],
                ["3. Distance", "Haversine great-circle distance to each station", "routing.py"],
                ["4. Pick one", "Choose nearest station only (not broadcast all)", "incidents.py"],
                ["5. Save", "Store station_id + distance_km on incident", "incidents table"],
                ["6. Notify", "Alert emergency contact + hotel (console/SMS/email)", "notify.py"],
            ],
            st, [w * 0.16, w * 0.54, w * 0.30],
        ),
        Spacer(1, 6),
        callout(
            "Important for panel",
            "No machine learning and no LLM. Routing is math (Haversine). "
            "No live tracking after trigger — privacy by design. Updates use HTTP polling, not WebSockets.",
            st,
        ),
        Spacer(1, 8),
        p("8. Seed data", st["h1"]),
        table(
            ["Data", "Source", "Notes"],
            [
                ["Police stations", "Excel with coordinates", "Real reference desks"],
                ["Hospitals", "Excel with coordinates / hotlines", "Gov + private sheets"],
                ["Officer logins", "station_credentials.csv", "e.g. st001 / Police001!"],
                ["Demo tourists", "seed script", "e.g. emma@example.com / tourist123"],
            ],
            st, [w * 0.28, w * 0.36, w * 0.36],
        ),
        PageBreak(),
    ]

    # Q&A
    story += [
        p("9. Questions they may ask — short answers", st["h1"]),
        table(
            ["Question", "Simple answer"],
            [
                ["Is routing AI/ML?", "No. Haversine distance to nearest dispatchable station."],
                ["Why only one station?", "By design — nearest desk only, not spam every station."],
                ["Live GPS tracking?", "No. One location ping at trigger. Extra ping API returns 409."],
                ["How status updates?", "HTTP polling every few seconds — no WebSockets."],
                ["Who sees the case?", "Only officers of the assigned station (station-scoped JWT)."],
                ["Are phones encrypted?", "Yes — Fernet at rest for phone, passport/NIC, emergency contact."],
                ["Hospital auto-called?", "No — tourist gets nearest number and dials manually."],
                ["SMS/email real?", "Default NOTIFY_MODE=console stub; Twilio/SendGrid optional."],
                ["Travel connection?", "POST /tourists/bridge-travel exchanges Travel JWT for SOS session."],
                ["Ports?", "Tourist 5175 · Police 5176 · API 5002"],
                ["PDF when?", "Only after incident is Closed — pdf_export.py"],
                ["Chat media?", "Text, image, and voice supported on incident chat"],
                ["Incident types?", "general, medical, assault, theft, accident, harassment"],
                ["Demo accounts?", "Tourist emma@example.com / tourist123 · Police st001 / Police001!"],
                ["Same backend as Travel?", "Yes — unified Flask app; SOS tables + travel tables together."],
            ],
            st, [w * 0.30, w * 0.70],
        ),
        PageBreak(),
    ]

    # RUN + CLOSING
    story += [
        p("10. How to run before demo", st["h1"]),
        bullets([
            "Terminal 1: cd backend → .venv → python run.py",
            "Seed once: python seed_sos_data.py",
            "Terminal 2: cd frontend/tourist → npm run dev → http://localhost:5175",
            "Terminal 3: cd frontend/police → npm run dev → http://localhost:5176",
            "Or use root frontend npm scripts if configured for both apps",
            "Health: http://127.0.0.1:5002/api/health",
        ], st),
        Spacer(1, 8),
        p("11. Suggested live order (8–10 min)", st["h1"]),
        bullets([
            "Tourist login → explain JWT",
            "Trigger medical SOS → show overlay + station name + GPS used once",
            "Show workflow Open",
            "Police login → dashboard card appears",
            "Acknowledge → Dispatch → show tourist status updating",
            "Chat both sides · show map on police detail",
            "Call nearest hospital on tourist",
            "Close → download PDF report",
            "Mention Travel bridge + encryption + no ML",
        ], st),
        Spacer(1, 8),
        p("12. Closing line", st["h1"]),
        callout(
            "Say at the end",
            "So overall: the tourist app captures one GPS point and creates an incident; "
            "routing.py picks the nearest station; the police app runs Acknowledge → Dispatch → Close "
            "with chat and map; PDF export records the closed case — all through the shared Flask API and PostgreSQL.",
            st,
        ),
        Spacer(1, 10),
        p(
            "Project R26-IT-152 · De Silva D.S.K. (IT22108654) · SOS System · 13 August 2026",
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
        title="SOS Component Demonstration",
        author="De Silva D.S.K.",
    )
    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    build()
