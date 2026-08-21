"""
Generate two panel-ready component documentation PDFs:
  1. SOS_Component_Documentation.pdf  (Tourist + Police)
  2. Travel_Component_Documentation.pdf

Run:
  cd backend
  .\\.venv\\Scripts\\activate
  python ..\\docs\\generate_component_panel_pdfs.py

Output:
  docs/pdfs/SOS_Component_Documentation.pdf
  docs/pdfs/Travel_Component_Documentation.pdf
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
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

TEAL = colors.HexColor("#0A4A52")
INK = colors.HexColor("#1A2332")
MUTED = colors.HexColor("#5A6570")
CODE_BG = colors.HexColor("#F2F6F7")
LINE = colors.HexColor("#D0DCE0")
ROW_ALT = colors.HexColor("#F5FAFA")
GREEN = colors.HexColor("#166534")
AMBER = colors.HexColor("#92400E")
RED = colors.HexColor("#991B1B")


def styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "T", parent=base["Title"], fontSize=20, textColor=TEAL,
            alignment=TA_CENTER, spaceAfter=4,
        ),
        "sub": ParagraphStyle(
            "S", parent=base["Normal"], fontSize=10, textColor=MUTED,
            alignment=TA_CENTER, spaceAfter=12,
        ),
        "h1": ParagraphStyle(
            "H1", parent=base["Heading1"], fontSize=13, textColor=TEAL,
            spaceBefore=12, spaceAfter=6,
        ),
        "h2": ParagraphStyle(
            "H2", parent=base["Heading2"], fontSize=11, textColor=INK,
            spaceBefore=8, spaceAfter=4,
        ),
        "body": ParagraphStyle(
            "B", parent=base["Normal"], fontSize=9.5, textColor=INK,
            leading=13, spaceAfter=4, alignment=TA_JUSTIFY,
        ),
        "meta": ParagraphStyle(
            "M", parent=base["Normal"], fontSize=9, textColor=MUTED,
            leading=12, spaceAfter=3,
        ),
        "code": ParagraphStyle(
            "C", parent=base["Code"], fontName="Courier", fontSize=7.5,
            leading=10, textColor=INK, backColor=CODE_BG,
            leftIndent=2, rightIndent=2, spaceBefore=2, spaceAfter=6,
        ),
        "bullet": ParagraphStyle(
            "Li", parent=base["Normal"], fontSize=9.5, textColor=INK, leading=12,
        ),
    }


def jdump(obj) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False)


def code(text: str, s):
    return Preformatted(text.strip("\n"), s["code"])


def bullets(story, s, items: list[str]):
    story.append(ListFlowable(
        [ListItem(Paragraph(item, s["bullet"]), leftIndent=12) for item in items],
        bulletType="bullet", start="•", leftIndent=16, spaceAfter=6,
    ))


def table(story, s, headers: list[str], rows: list[list[str]], col_widths=None):
    data = [[Paragraph(f"<b>{h}</b>", s["body"]) for h in headers]]
    for row in rows:
        data.append([Paragraph(str(c), s["body"]) for c in row])
    if not col_widths:
        usable = 170 * mm
        col_widths = [usable / len(headers)] * len(headers)
    t = Table(data, colWidths=col_widths, repeatRows=1)
    cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), TEAL),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.4, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            cmds.append(("BACKGROUND", (0, i), (-1, i), ROW_ALT))
    t.setStyle(TableStyle(cmds))
    story.append(t)
    story.append(Spacer(1, 3 * mm))


def endpoint_block(story, s, method, path, auth, desc, req=None, resp=None):
    block = [
        Paragraph(f"<b>{method}</b>  {path}", s["h2"]),
        Paragraph(desc, s["body"]),
        Paragraph(f"<b>Auth:</b> {auth}", s["meta"]),
    ]
    if req is not None:
        block.append(Paragraph("<b>Sample request</b>", s["meta"]))
        block.append(code(jdump(req) if not isinstance(req, str) else req, s))
    if resp is not None:
        block.append(Paragraph("<b>Sample response</b>", s["meta"]))
        block.append(code(jdump(resp) if not isinstance(resp, str) else resp, s))
    block.append(Spacer(1, 2 * mm))
    story.append(KeepTogether(block))


def page_footer(canvas, doc, label: str):
    canvas.saveState()
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.5)
    canvas.line(18 * mm, 14 * mm, A4[0] - 18 * mm, 14 * mm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(18 * mm, 8 * mm, label)
    canvas.drawRightString(A4[0] - 18 * mm, 8 * mm, f"Page {doc.page}")
    canvas.restoreState()


def probe_health():
    try:
        with urllib.request.urlopen("http://127.0.0.1:5002/api/health", timeout=2) as resp:
            return True, json.loads(resp.read().decode())
    except Exception:
        return False, None


def build_sos_pdf(live: bool, health: dict | None):
    s = styles()
    story = []
    today = datetime.now().strftime("%d %B %Y")

    story.append(Paragraph("Tour Ceylon — SOS Component", s["title"]))
    story.append(Paragraph(
        f"Tourist PWA + Police Dashboard — Panel Documentation<br/>Generated {today}",
        s["sub"],
    ))
    story.append(HRFlowable(width="100%", thickness=1, color=LINE, spaceAfter=8))

    # 1. PROBLEM & OBJECTIVE
    story.append(Paragraph("1. Problem &amp; Objective", s["h1"]))
    story.append(Paragraph("<b>Problem solved for the tourist</b>", s["h2"]))
    bullets(story, s, [
        "Foreign tourists in Sri Lanka often lack a fast, trusted channel to reach police during "
        "medical emergencies, theft, assault, accidents, or harassment.",
        "They may not know the nearest police desk, emergency numbers, or how to share their "
        "location accurately under stress.",
        "Emergency contacts and hotel staff are often not notified automatically when help is needed.",
    ])
    story.append(Paragraph("<b>Core objective (original proposal scope)</b>", s["h2"]))
    bullets(story, s, [
        "Build a Tourist SOS Progressive Web App (PWA) that lets registered tourists trigger "
        "one-tap emergency alerts with GPS location.",
        "Route each incident to the <b>single nearest dispatchable police station</b> using "
        "real station coordinates — not broadcast to all stations.",
        "Provide a Police Dashboard where officers at the assigned station acknowledge, dispatch, "
        "close incidents, chat with the tourist, and export PDF reports.",
        "Integrate with the main Travel app so one Tour Ceylon login can open SOS without "
        "re-registering.",
    ])

    # 2. TECH STACK
    story.append(PageBreak())
    story.append(Paragraph("2. Tech Stack", s["h1"]))
    table(story, s, ["Layer", "Technology", "Details"], [
        ["Backend", "Flask 3.0.3", "Unified monolith with Travel; entry: backend/run.py"],
        ["Backend port", "5002", "http://127.0.0.1:5002/api"],
        ["Tourist frontend", "React 18 + Vite 5 PWA", "frontend/tourist — port 5175"],
        ["Police frontend", "React 18 + Vite + Leaflet", "frontend/police — port 5176"],
        ["Database", "PostgreSQL (travel_app)", "SOS tables via SQLAlchemy db.create_all()"],
        ["Auth", "Flask-JWT-Extended", "Roles: tourist, officer, travel_user"],
        ["Encryption", "Fernet (cryptography)", "Phone, passport/NIC, emergency contact at rest"],
        ["PDF export", "ReportLab", "Closed incident reports for police"],
        ["Notifications", "Console stub + optional Twilio/SendGrid", "NOTIFY_MODE=console by default"],
    ], [35 * mm, 45 * mm, 90 * mm])

    story.append(Paragraph("<b>What the database stores (SOS)</b>", s["h2"]))
    bullets(story, s, [
        "<b>tourists</b> — profile, encrypted PII, trip dates, hotel, last known location",
        "<b>emergency_contacts</b> — one contact per tourist (encrypted phone/email)",
        "<b>stations</b> — police desks with coordinates and dispatchable flag",
        "<b>officers</b> — station-scoped login credentials",
        "<b>hospitals</b> — government + private hospitals with coordinates or hotline-only",
        "<b>incidents</b> — type, status workflow, one-shot GPS, distance to station",
        "<b>location_pings</b> — single ping recorded at SOS trigger (no live tracking)",
        "<b>chat_messages</b> — text, image, voice between tourist and assigned station",
    ])

    # 3. METHODOLOGY
    story.append(Paragraph("3. Methodology (Routing — not ML/AI)", s["h1"]))
    story.append(Paragraph(
        "The SOS component does <b>not</b> use machine learning, Random Forest, or LLMs. "
        "Emergency routing is deterministic:",
        s["body"],
    ))
    bullets(story, s, [
        "<b>Algorithm:</b> Haversine great-circle distance (WGS84) between tourist coordinates "
        "and all dispatchable police stations.",
        "<b>Why this approach:</b> Transparent, explainable, fast, and appropriate for "
        "nearest-station dispatch without training data or model drift.",
        "<b>Inputs:</b> Tourist latitude/longitude from browser geolocation (one-shot "
        "getCurrentPosition); police station lat/lng from seeded Excel dataset.",
        "<b>Output:</b> Single nearest dispatchable station + distance_km stored on the incident.",
        "<b>Hospital lookup:</b> Same Haversine logic on hospital table for 'Call nearest hospital'.",
    ])
    story.append(Paragraph(
        "<b>Performance metrics:</b> No ML accuracy metrics apply. Routing correctness is verified "
        "by comparing Haversine distance to known station coordinates in manual/demo tests. "
        "Response-time analytics (acknowledge/dispatch/close timestamps) are exposed via "
        "GET /api/incidents/stats for the police dashboard charts.",
        s["body"],
    ))

    # 4. API DOCUMENTATION
    story.append(PageBreak())
    story.append(Paragraph("4. API Documentation", s["h1"]))
    story.append(Paragraph("Base URL: <b>http://127.0.0.1:5002/api</b>", s["body"]))

    story.append(Paragraph("4.1 Tourist endpoints (/api/tourists)", s["h2"]))
    table(story, s, ["Method", "Path", "Auth", "Purpose"], [
        ["POST", "/api/tourists/register", "None", "Register tourist with profile + emergency contact"],
        ["POST", "/api/tourists/login", "None", "Email/password → tourist JWT"],
        ["POST", "/api/tourists/bridge-travel", "None", "Exchange Travel JWT for SOS session"],
        ["GET", "/api/tourists/me", "Tourist JWT", "Current profile"],
        ["GET", "/api/tourists/me/incidents", "Tourist JWT", "Active + history incidents"],
    ], [18 * mm, 52 * mm, 28 * mm, 72 * mm])

    story.append(Paragraph("4.2 Incident endpoints (/api/incidents)", s["h2"]))
    table(story, s, ["Method", "Path", "Auth", "Purpose"], [
        ["POST", "/api/incidents", "Tourist JWT", "Trigger SOS — routes to nearest station"],
        ["GET", "/api/incidents/<id>/status", "Tourist JWT", "Poll workflow status"],
        ["GET", "/api/incidents/<id>/messages", "Tourist/officer", "Poll incident chat"],
        ["POST", "/api/incidents/<id>/messages", "Tourist/officer", "Send chat message"],
        ["GET", "/api/incidents", "Officer JWT", "Station-scoped incident queue"],
        ["PATCH", "/api/incidents/<id>/acknowledge", "Officer JWT", "Open → Acknowledged"],
        ["PATCH", "/api/incidents/<id>/dispatch", "Officer JWT", "Acknowledged → Dispatched"],
        ["PATCH", "/api/incidents/<id>/close", "Officer JWT", "→ Closed"],
        ["GET", "/api/incidents/stats", "Officer JWT", "Analytics for dashboard charts"],
        ["GET", "/api/incidents/<id>/report.pdf", "Officer JWT", "PDF export (closed only)"],
    ], [18 * mm, 58 * mm, 28 * mm, 66 * mm])

    story.append(Paragraph("4.3 Other SOS endpoints", s["h2"]))
    table(story, s, ["Method", "Path", "Auth", "Purpose"], [
        ["GET", "/api/hospitals/nearest?lat=&lng=", "None", "Nearest hospital + dial number"],
        ["POST", "/api/auth/login", "None", "Police: username+password → officer JWT"],
        ["GET", "/api/health", "None", "Liveness check"],
    ], [18 * mm, 58 * mm, 28 * mm, 66 * mm])

    story.append(Paragraph("4.4 Sample request/response (key endpoints)", s["h2"]))
    endpoint_block(story, s, "GET", "/api/health", "None",
                   "Unified backend liveness.",
                   resp=health or {"status": "ok", "app": "tour-ceylon-unified"})

    endpoint_block(story, s, "POST", "/api/tourists/login", "None",
                   "Tourist login. Demo: emma@example.com / tourist123 (after seed_sos_data.py).",
                   req={"email": "emma@example.com", "password": "tourist123"},
                   resp={"access_token": "<jwt>", "tourist": {"id": 1, "name": "Emma Wilson", "email": "emma@example.com"}})

    endpoint_block(story, s, "POST", "/api/incidents", "Bearer tourist JWT",
                   "Trigger SOS. Requires lat/lng from browser geolocation.",
                   req={"type": "medical", "latitude": 6.9271, "longitude": 79.8612},
                   resp={
                       "incident": {
                           "id": 42,
                           "tourist_id": 1,
                           "station_id": 3,
                           "incident_type": "medical",
                           "status": "open",
                           "initial_lat": 6.9271,
                           "initial_lng": 79.8612,
                           "distance_to_station_km": 1.234,
                           "tracking_active": False,
                           "station": {"desk": "Colombo Fort", "telephone": "0112422222"},
                       }
                   })

    endpoint_block(story, s, "GET", "/api/incidents/42/status", "Bearer tourist JWT",
                   "Tourist polls workflow every ~5 seconds.",
                   resp={
                       "incident": {
                           "id": 42,
                           "status": "acknowledged",
                           "acknowledged_at": "2026-08-12T06:30:00Z",
                           "station": {"desk": "Colombo Fort"},
                       }
                   })

    endpoint_block(story, s, "POST", "/api/auth/login", "None",
                   "Police officer login. Demo: st001 / Police001! (from station_credentials.csv).",
                   req={"username": "st001", "password": "Police001!"},
                   resp={"access_token": "<jwt>", "officer": {"id": 1, "name": "Officer", "station_id": 1}})

    endpoint_block(story, s, "GET", "/api/hospitals/nearest?lat=6.9271&lng=79.8612", "None",
                   "Returns nearest hospital for tel: link in tourist UI.",
                   resp={
                       "hospital": {
                           "name": "National Hospital of Sri Lanka",
                           "district": "Colombo",
                           "local_number": "0112691111",
                           "distance_km": 0.87,
                           "dial_number": "0112691111",
                       }
                   })

    if live:
        story.append(Paragraph(
            f"<font color='#{GREEN.hexval()[2:]}'><b>Live backend verified</b></font> at PDF generation time.",
            s["body"],
        ))
    else:
        story.append(Paragraph(
            "<font color='#92400E'><b>Note:</b></font> Sample JSON above matches API contract from "
            "source code and seed data. Re-run with backend on :5002 for live-captured responses.",
            s["meta"],
        ))

    # 5. DATASET
    story.append(PageBreak())
    story.append(Paragraph("5. Dataset", s["h1"]))
    table(story, s, ["Source file", "Type", "Records", "Notes"], [
        ["Sri_Lanka_Government_Hospitals_with_Coordinates.xlsx", "Real reference", "Gov + private sheets", "District, name, phone, lat/lng"],
        ["Sri_Lanka_Police_Emergency_with_Coordinates.xlsx", "Real reference", "Police desks", "Range, division, desk, phone, lat/lng"],
        ["station_credentials.csv", "Generated at seed", "1 per station", "Demo officer logins"],
        ["Demo tourists/incidents", "Simulated", "3 tourists + sample incidents", "Colombo-area coords for demo"],
    ], [55 * mm, 28 * mm, 28 * mm, 59 * mm])
    story.append(Paragraph(
        "<b>Honest disclosure:</b> Hospital and police coordinate data are real reference datasets "
        "seeded from Excel. Demo tourist accounts and closed incidents are <b>simulated</b> for "
        "presentation and manual testing. SMS/email notifications are stubbed (console log) unless "
        "Twilio/SendGrid credentials are configured.",
        s["body"],
    ))

    # 6. KEY FEATURES
    story.append(Paragraph("6. Key Features", s["h1"]))
    story.append(Paragraph("<b>Tourist PWA (port 5175)</b>", s["h2"]))
    bullets(story, s, [
        "Six-type SOS bar: general, medical, assault, theft, accident, harassment",
        "One-shot GPS capture — no continuous tracking (privacy by design)",
        "Real-time workflow tracker: Open → Acknowledged → Dispatched → Closed",
        "Incident chat with police (text, image, voice attachments)",
        "Call nearest hospital via Haversine lookup + tel: link",
        "PWA installable on mobile; Travel app handoff via JWT bridge",
    ])
    story.append(Paragraph("<b>Police Dashboard (port 5176)</b>", s["h2"]))
    bullets(story, s, [
        "Station-scoped login — officers only see their station's incidents",
        "Live incident queue with audio alert on new open cases",
        "Workflow buttons: Acknowledge → Dispatch → Close",
        "Leaflet map with tourist location; decrypted PII for officers",
        "Analytics charts (Recharts): volume by day, response times, type breakdown",
        "PDF export for closed incidents",
    ])
    story.append(Paragraph(
        "<b>Screenshots:</b> Capture from running apps at localhost:5175 (tourist) and "
        "localhost:5176 (police). Existing user guides: docs/pdfs/Tourist_SOS_Dashboard_Guide.pdf "
        "and docs/pdfs/Police_Dashboard_Guide.pdf.",
        s["meta"],
    ))

    # 7. LIMITATIONS
    story.append(Paragraph("7. Known Limitations", s["h1"]))
    bullets(story, s, [
        "No continuous GPS tracking — POST /api/incidents/:id/ping returns 409 by design",
        "Notifications are console stubs by default (NOTIFY_MODE=console)",
        "No WebSockets — all updates via HTTP polling (4–8 second intervals)",
        "Hospitals are not auto-dispatched; tourist must dial manually",
        "Only the nearest station receives the incident (by design, not a bug)",
        "Police stations without coordinates cannot be used for routing",
        "SOS schema must be seeded separately via python seed_sos_data.py",
        "No automated unit/integration test suite for SOS",
        "Demo police passwords are predictable (development only)",
    ])

    # 8. TESTING
    story.append(Paragraph("8. Testing Evidence", s["h1"]))
    bullets(story, s, [
        "<b>Manual demo flow:</b> seed_sos_data.py creates demo tourists (emma@example.com) and "
        "police credentials (st001 / Police001!). Full flow: login → trigger SOS → police "
        "acknowledge/dispatch/close → PDF export.",
        "<b>Health check:</b> GET /api/health returns {\"status\":\"ok\"}.",
        "<b>Routing validation:</b> distance_to_station_km computed and stored on each incident; "
        "visible in police incident detail.",
        "<b>Security fixes verified manually:</b> Fernet encryption on sensitive fields; "
        "station-scoped JWT prevents cross-station incident access.",
        "<b>Bug fixed during development:</b> Continuous tracking disabled after privacy review — "
        "replaced with one-shot location ping at trigger time.",
        "<b>Gap:</b> No pytest/jest automated tests. Recommend adding API integration tests for "
        "incident lifecycle and routing edge cases.",
    ])

    out = OUT_DIR / "SOS_Component_Documentation.pdf"
    doc = SimpleDocTemplate(
        str(out), pagesize=A4,
        leftMargin=18 * mm, rightMargin=18 * mm,
        topMargin=16 * mm, bottomMargin=18 * mm,
        title="Tour Ceylon SOS Component Documentation",
    )
    label = "Tour Ceylon — SOS Component (Tourist + Police)"
    doc.build(story, onFirstPage=lambda c, d: page_footer(c, d, label),
              onLaterPages=lambda c, d: page_footer(c, d, label))
    print(f"Wrote {out}")
    return out


def build_travel_pdf(live: bool, health: dict | None):
    s = styles()
    story = []
    today = datetime.now().strftime("%d %B %Y")

    story.append(Paragraph("Tour Ceylon — Travel Component", s["title"]))
    story.append(Paragraph(
        f"Itinerary Planner &amp; Discovery — Panel Documentation<br/>Generated {today}",
        s["sub"],
    ))
    story.append(HRFlowable(width="100%", thickness=1, color=LINE, spaceAfter=8))

    # 1. PROBLEM & OBJECTIVE
    story.append(Paragraph("1. Problem &amp; Objective", s["h1"]))
    story.append(Paragraph("<b>Problem solved for the tourist</b>", s["h2"]))
    bullets(story, s, [
        "Planning a Sri Lanka trip involves scattered information: attractions, hotels, budgets, "
        "local businesses, travel agencies, and licensed guides across many sources.",
        "Tourists struggle to align mood/preferences, number of days, destinations, and budget "
        "into a coherent day-by-day plan.",
        "There is no single tool that turns selections into a timed itinerary and exportable PDF.",
    ])
    story.append(Paragraph("<b>Core objective (original proposal scope)</b>", s["h2"]))
    bullets(story, s, [
        "Build a multi-step trip wizard: Attractions → Budget → Stay → Itinerary → Discover → Export.",
        "Use curated Sri Lankan tourism datasets (attractions, hotels, businesses, agencies, guides).",
        "Generate a rule-based day-by-day timed itinerary from user selections (not generic templates).",
        "Provide budget splitting, hotel matching per destination, and PDF export.",
        "Bridge to the SOS component from the same Tour Ceylon account.",
    ])

    # 2. TECH STACK
    story.append(PageBreak())
    story.append(Paragraph("2. Tech Stack", s["h1"]))
    table(story, s, ["Layer", "Technology", "Details"], [
        ["Backend", "Flask 3.0.3", "Unified monolith; backend/run.py"],
        ["Backend port", "5002", "http://127.0.0.1:5002/api"],
        ["Frontend", "React 18 + Vite 5", "frontend/travel — port 5180"],
        ["Database", "PostgreSQL (travel_app)", "Schema: backend/database/schema.sql"],
        ["ORM", "SQLAlchemy 2.0", "Models in backend/app/models/"],
        ["Auth", "Flask-JWT-Extended", "Email/password + optional Google OAuth"],
        ["Data seeding", "Pandas + openpyxl", "Excel/CSV → Postgres"],
        ["PDF export", "ReportLab", "Itinerary PDF download"],
        ["Charts", "Recharts", "Budget pie chart in UI"],
    ], [35 * mm, 45 * mm, 90 * mm])

    story.append(Paragraph("<b>What the database stores (Travel)</b>", s["h2"]))
    bullets(story, s, [
        "<b>accommodation</b> — 944 hotels with price range, location, images",
        "<b>attractions</b> — 130 attractions with mood_tag, category, destination, images",
        "<b>business_directory</b> — 126 local businesses",
        "<b>travel_agencies</b> — 417 licensed agencies",
        "<b>tourist_guides</b> — 2,906 guides (from srilanka.travel registry CSV)",
        "<b>users</b> — travel accounts (email, password_hash, google_id)",
        "<b>user_trip_input</b> — trip UUID, days, moods, attraction IDs, budget, hotels",
        "<b>budget_split</b> — food/accommodation/shopping/transport amounts",
        "<b>generated_itinerary</b> — JSON itinerary per generation",
        "<b>saved_references</b> — saved businesses/agencies/guides per trip",
    ])

    # 3. METHODOLOGY
    story.append(Paragraph("3. Methodology (Rule-Based — not ML/Random Forest)", s["h1"]))
    story.append(Paragraph(
        "<b>Important for panel:</b> Despite the module name ai_service.py, this component does "
        "<b>not</b> use Random Forest, scikit-learn, neural networks, or OpenAI. "
        "OPENAI_API_KEY can remain empty.",
        s["body"],
    ))

    story.append(Paragraph("<b>3.1 Itinerary generation algorithm</b>", s["h2"]))
    table(story, s, ["Step", "Logic", "Source file"], [
        ["Day allocation", "One day per unique destination first; leftover days cycle attractions", "trip_plan_service.py"],
        ["Start time", "User override OR mood average from MOOD_START_HOURS lookup", "ai_service.py"],
        ["Category bias", "Wild/Heritage earlier; beach/spa later via CATEGORY_START_HOURS", "ai_service.py"],
        ["Name hints", "Keywords in attraction name (temple, beach, safari) adjust start", "ai_service.py"],
        ["Activity spacing", "2–3 hr gaps; skip lunch slot 12–1 PM; cap ~8 PM", "ai_service.py"],
        ["Output tag", '"source": "database" in JSON', "ai_service.py"],
    ], [35 * mm, 85 * mm, 50 * mm])

    story.append(Paragraph("<b>3.2 Recommendation / filtering (not ML ranking)</b>", s["h2"]))
    bullets(story, s, [
        "<b>Attractions:</b> SQL WHERE mood_tag IN (selected moods) — no scoring model.",
        "<b>Hotels:</b> Price filter within accommodation budget + string token match on "
        "local authority/address (hotels_for_destination).",
        "<b>Businesses/agencies:</b> SQL ILIKE filter on trip destinations with nearby-area fallback map.",
        "<b>Tourist guides:</b> SQL filters on name, registration_no, guide_type, language + pagination.",
        "<b>Budget:</b> Fixed percentage split (default 25/35/15/25) — pure arithmetic.",
    ])

    story.append(Paragraph("<b>3.3 Features/inputs and data origin</b>", s["h2"]))
    table(story, s, ["Input", "Source", "Real or simulated"], [
        ["Attraction catalog", "attractions.xlsx", "Real reference data"],
        ["Hotel catalog", "accomadation.xlsx", "Real reference data"],
        ["Business/agency lists", "business_directory.xlsx, travel_agencies.xlsx", "Real reference data"],
        ["Tourist guides", "tourist_guides.csv (srilanka.travel)", "Real scraped registry; junk rows filtered"],
        ["User trip selections", "Runtime user input", "Dynamic — created per session"],
        ["Mood start hours", "MOOD_START_HOURS dict in code", "Assumed/heuristic tuning"],
        ["LKR/USD conversion", "LKR_TO_USD_RATE=300 in config", "Assumed fixed rate"],
    ], [45 * mm, 55 * mm, 70 * mm])

    story.append(Paragraph("<b>3.4 Training, metrics, and evaluation</b>", s["h2"]))
    story.append(Paragraph(
        "There is <b>no model training</b>, train/test split, or hyperparameter tuning. "
        "The system is fully deterministic.",
        s["body"],
    ))
    bullets(story, s, [
        "<b>Itinerary quality:</b> Evaluated manually — times are heuristic, not validated against "
        "opening hours or traffic data.",
        "<b>Hotel matching accuracy:</b> String-based location match; no geo-distance metric. "
        "Ambiguous location names logged to location_normalization_review.json at seed time "
        "(fuzzy threshold 0.88 using difflib.SequenceMatcher).",
        "<b>Seed verification:</b> verify_seed.py checks row counts (944/130/126/417/2906).",
        "<b>API smoke test:</b> test_api_flow.py runs 12-step end-to-end flow including PDF export.",
        "<b>No ML accuracy/precision/recall</b> — not applicable to this implementation.",
    ])

    # 4. API DOCUMENTATION
    story.append(PageBreak())
    story.append(Paragraph("4. API Documentation", s["h1"]))
    story.append(Paragraph("Base URL: <b>http://127.0.0.1:5002/api</b>", s["body"]))
    story.append(Paragraph("Auth header for protected routes: <b>Authorization: Bearer &lt;jwt&gt;</b>", s["body"]))

    table(story, s, ["Method", "Path", "Auth", "Purpose"], [
        ["GET", "/api/health", "None", "Liveness"],
        ["POST", "/api/auth/register", "None", "Create account"],
        ["POST", "/api/auth/login", "None", "Login → JWT"],
        ["GET", "/api/attractions?moods=...", "None", "Filter attractions by mood"],
        ["POST", "/api/trip-input", "JWT", "Create trip (days, moods, attraction IDs)"],
        ["PATCH", "/api/trip-input/<trip_id>", "JWT", "Update hotels, budget, status"],
        ["POST", "/api/budget/split", "JWT", "Split budget into categories"],
        ["GET", "/api/accommodation?trip_id=", "JWT", "Hotels per destination within budget"],
        ["POST", "/api/itinerary/generate", "JWT", "Generate timed itinerary"],
        ["GET", "/api/itinerary/<trip_id>", "JWT", "Get latest itinerary"],
        ["GET", "/api/itinerary/<trip_id>/pdf", "JWT", "Download PDF"],
        ["GET", "/api/business-directory?trip_id=", "JWT", "Businesses for destinations"],
        ["GET", "/api/travel-agencies?trip_id=", "JWT", "Agencies for destinations"],
        ["GET", "/api/tourist-guides", "JWT", "Search licensed guides"],
        ["POST", "/api/saved-references", "JWT", "Save business/agency/guide to trip"],
    ], [18 * mm, 55 * mm, 18 * mm, 79 * mm])

    story.append(Paragraph("4.1 Sample request/response (key endpoints)", s["h2"]))
    endpoint_block(story, s, "GET", "/api/health", "None", "Liveness.",
                   resp=health or {"status": "ok", "app": "tour-ceylon-unified"})

    endpoint_block(story, s, "POST", "/api/auth/login", "None", "Travel user login.",
                   req={"email": "visitor@example.com", "password": "secret123"},
                   resp={"access_token": "<jwt>", "user": {"id": 1, "email": "visitor@example.com"}})

    endpoint_block(story, s, "GET", "/api/attractions?moods=Adventure,Spiritual", "None",
                   "Public attraction browse. Returns filtered list + available moods.",
                   resp={
                       "attractions": [
                           {"id": 12, "attraction_name": "Adam's Peak", "mood_tag": "Spiritual",
                            "normalized_destination": "Nallathanniya",
                            "image": "/api/media/attractions/012-adams-peak.jpeg"}
                       ],
                       "count": 18,
                       "available_moods": ["Adventure", "Spiritual", "Culture"],
                       "filtered_moods": ["Adventure", "Spiritual"],
                   })

    endpoint_block(story, s, "POST", "/api/trip-input", "Bearer JWT",
                   "Create trip. Attraction IDs are integers (not objects).",
                   req={"days": 3, "selected_moods": ["Adventure", "Spiritual"],
                        "finalized_attractions": [12, 45, 67]},
                   resp={"trip": {"trip_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                                  "days": 3, "status": "draft"}})

    endpoint_block(story, s, "POST", "/api/budget/split", "Bearer JWT",
                   "Default split: food 25%, accommodation 35%, shopping 15%, transport 25%.",
                   req={"trip_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                        "budget": 2500, "customize": False},
                   resp={"split": {"food": 625, "accommodation": 875, "shopping": 375,
                                   "transport": 625, "food_pct": 25, "accommodation_pct": 35}})

    endpoint_block(story, s, "POST", "/api/itinerary/generate", "Bearer JWT",
                   "Builds day-by-day timed plan from saved trip data.",
                   req={"trip_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890", "day_start": "09:00"},
                   resp={
                       "itinerary": {
                           "itinerary": {
                               "title": "3-Day Sri Lanka Adventure",
                               "source": "database",
                               "days": [
                                   {"day": 1, "destination": "Nallathanniya",
                                    "items": [{"time": "06:30", "name": "Adam's Peak", "category": "Spiritual"}]}
                               ],
                           }
                       }
                   })

    endpoint_block(story, s, "GET", "/api/business-directory?trip_id=<uuid>", "Bearer JWT",
                   "Businesses filtered by trip destinations.",
                   resp={"businesses": [{"id": 5, "name": "Example Cafe", "location": "Kandy"}],
                           "count": 12})

    if live:
        story.append(Paragraph(
            f"<font color='#{GREEN.hexval()[2:]}'><b>Live backend verified</b></font> at PDF generation time.",
            s["body"],
        ))
    else:
        story.append(Paragraph(
            "<font color='#92400E'><b>Note:</b></font> Samples match API contract. Run "
            "backend/scripts/travel/test_api_flow.py with server on :5002 for live JSON.",
            s["meta"],
        ))

    # 5. DATASET
    story.append(PageBreak())
    story.append(Paragraph("5. Dataset", s["h1"]))
    table(story, s, ["File", "Table", "Expected rows", "Provenance"], [
        ["accomadation.xlsx", "accommodation", "944", "Real hotel catalog"],
        ["attractions.xlsx", "attractions", "130", "Real attraction catalog + embedded images"],
        ["business_directory.xlsx", "business_directory", "126", "Real local businesses"],
        ["travel_agencies.xlsx", "travel_agencies", "417", "Real licensed agencies"],
        ["tourist_guides.csv", "tourist_guides", "2906", "Scraped from srilanka.travel registry"],
    ], [42 * mm, 38 * mm, 28 * mm, 62 * mm])
    story.append(Paragraph(
        "<b>Honest disclosure:</b> Reference catalogs are real tourism data seeded from Excel/CSV. "
        "Mood-to-start-time mappings, budget default percentages, and LKR/USD rate are "
        "<b>assumed/heuristic</b> values in code — not learned from data. User trips and "
        "generated itineraries are created dynamically at runtime.",
        s["body"],
    ))

    # 6. KEY FEATURES
    story.append(Paragraph("6. Key Features", s["h1"]))
    bullets(story, s, [
        "<b>Mood-based attraction browse</b> — 10 moods; multi-select filter (1–3 moods per trip)",
        "<b>6-step wizard</b> — Attractions → Budget → Stay → Itinerary → Discover → Export",
        "<b>Trip constraint engine</b> — unique destinations cannot exceed trip days",
        "<b>Budget pie chart</b> — default or custom percentage split with Recharts",
        "<b>Per-destination hotel picker</b> — filtered by accommodation budget (LKR→USD conversion)",
        "<b>Rule-based timed itinerary</b> — mood/category-aware start times and activity spacing",
        "<b>Discover tab</b> — businesses, travel agencies, licensed tourist guides + save to trip",
        "<b>PDF export</b> — downloadable itinerary via GET /api/itinerary/<trip_id>/pdf",
        "<b>Trip history</b> — past plans via /api/itinerary/history",
        "<b>SOS bridge</b> — open Tourist SOS PWA from Travel sidebar with shared login",
        "<b>Google Sign-In</b> — optional when GOOGLE_CLIENT_ID is configured",
    ])
    story.append(Paragraph(
        "<b>Screenshots:</b> Capture from http://localhost:5180 during wizard flow. "
        "Existing guide: docs/pdfs/Travel_Dashboard_Guide.pdf.",
        s["meta"],
    ))

    # 7. LIMITATIONS
    story.append(Paragraph("7. Known Limitations", s["h1"]))
    bullets(story, s, [
        "No ML/Random Forest — recommendations are SQL filters + heuristics, not learned rankings",
        "No GPS/route optimization — attractions lack lat/lng; route text is City A → City B only",
        "Itinerary times are heuristic — not tied to opening hours, traffic, or travel duration",
        "Same day_start applied across all days (no per-day override in current UI)",
        "Hotel matching is string-based, not geographic distance",
        "OpenAI package in requirements.txt is unused — ai_service is rule-based only",
        "App requires manual Postgres setup + seed scripts; no Docker Compose",
        "WeasyPrint optional/disabled on Windows — PDF uses ReportLab fallback",
        "Tourist guide CSV required junk-row filtering at seed time",
        "No automated unit test suite — only 12-step smoke script",
    ])

    # 8. TESTING
    story.append(Paragraph("8. Testing Evidence", s["h1"]))
    story.append(Paragraph("<b>Automated smoke test (12 steps)</b>", s["h2"]))
    story.append(Paragraph(
        "Script: backend/scripts/travel/test_api_flow.py — run with backend on localhost:5002.",
        s["body"],
    ))
    bullets(story, s, [
        "1. GET /api/health → status ok",
        "2. Auth login/register → JWT",
        "3. GET /api/attractions?moods=Adventure,Spiritual → non-empty list",
        "4. POST /api/trip-input → trip_id",
        "5. POST /api/budget/split → split amounts",
        "6. GET /api/accommodation → hotels per destination",
        "7. PATCH /api/trip-input → hotel picks saved",
        "8. POST /api/itinerary/generate → timed itinerary JSON",
        "9. GET /api/business-directory → count > 0",
        "10. GET /api/travel-agencies → count > 0",
        "11. POST /api/saved-references → saved ref",
        "12. GET /api/itinerary/<trip_id>/pdf → valid %PDF header",
    ])
    story.append(Paragraph("<b>Seed verification</b>", s["h2"]))
    story.append(Paragraph(
        "backend/scripts/travel/verify_seed.py confirms row counts: "
        "944 accommodation, 130 attractions, 126 businesses, 417 agencies, 2906 guides.",
        s["body"],
    ))
    story.append(Paragraph("<b>Bugs found and fixed during development</b>", s["h2"]))
    bullets(story, s, [
        "Location name normalization — fuzzy matching + alias map to handle messy authority names in Excel",
        "JWT required on recommendation endpoints — corrected from earlier doc stating optional auth",
        "Trip input validation — unique_locations must not exceed days (400 error if violated)",
        "Attraction image paths — resolved via /api/media/attractions/ for broken external URLs",
    ])

    out = OUT_DIR / "Travel_Component_Documentation.pdf"
    doc = SimpleDocTemplate(
        str(out), pagesize=A4,
        leftMargin=18 * mm, rightMargin=18 * mm,
        topMargin=16 * mm, bottomMargin=18 * mm,
        title="Tour Ceylon Travel Component Documentation",
    )
    label = "Tour Ceylon — Travel Component"
    doc.build(story, onFirstPage=lambda c, d: page_footer(c, d, label),
              onLaterPages=lambda c, d: page_footer(c, d, label))
    print(f"Wrote {out}")
    return out


def main():
    live, health = probe_health()
    if live:
        print("Backend live — embedding real health response.")
    else:
        print("Backend not running — using documented sample responses.")
    build_sos_pdf(live, health)
    build_travel_pdf(live, health)
    print(f"\nDone. PDFs in {OUT_DIR}")


if __name__ == "__main__":
    main()
