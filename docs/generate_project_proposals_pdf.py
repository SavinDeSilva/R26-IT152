"""
Generate two formal project proposal PDFs for Tour Ceylon:

  1. SOS_Emergency_Response_System_Proposal.pdf
  2. Travel_Itinerary_Planning_System_Proposal.pdf

Run:
  cd backend
  .\\.venv\\Scripts\\activate
  python ..\\docs\\generate_project_proposals_pdf.py

Output:
  docs/pdfs/SOS_Emergency_Response_System_Proposal.pdf
  docs/pdfs/Travel_Itinerary_Planning_System_Proposal.pdf
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
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

OUT_DIR = Path(__file__).resolve().parent / "pdfs"
OUT_DIR.mkdir(parents=True, exist_ok=True)

TEAL = colors.HexColor("#0A4A52")
NAVY = colors.HexColor("#0F2744")
INK = colors.HexColor("#1A2332")
MUTED = colors.HexColor("#5A6570")
LINE = colors.HexColor("#D0DCE0")
ROW_ALT = colors.HexColor("#F5FAFA")
ACCENT = colors.HexColor("#0D6E6E")

PROJECT_ID = "R26-IT-152"
STUDENT_SOS = "D.S.K. De Silva"
STUDENT_SOS_ID = "IT22108654"
STUDENT_ITINERARY = "Wanniarachchi P.M.R."
STUDENT_ITINERARY_ID = ""
INSTITUTION = "Informatics Institute of Technology (IIT)"
DEGREE = "BSc (Hons) Information Technology — Software Engineering"
PROJECT_TITLE = "Tour Ceylon — Unified Tourism Platform for Sri Lanka"


def styles():
    base = getSampleStyleSheet()
    return {
        "cover_title": ParagraphStyle(
            "CT", parent=base["Title"], fontSize=22, textColor=TEAL,
            alignment=TA_CENTER, spaceAfter=8, fontName="Helvetica-Bold", leading=28,
        ),
        "cover_sub": ParagraphStyle(
            "CS", parent=base["Normal"], fontSize=11, textColor=MUTED,
            alignment=TA_CENTER, spaceAfter=4, leading=15,
        ),
        "doc_type": ParagraphStyle(
            "DT", parent=base["Normal"], fontSize=14, textColor=NAVY,
            alignment=TA_CENTER, spaceBefore=12, spaceAfter=6,
            fontName="Helvetica-Bold",
        ),
        "meta": ParagraphStyle(
            "M", parent=base["Normal"], fontSize=10, textColor=INK,
            alignment=TA_LEFT, spaceAfter=3, leading=14,
        ),
        "h1": ParagraphStyle(
            "H1", parent=base["Heading1"], fontSize=13, textColor=TEAL,
            spaceBefore=12, spaceAfter=6, fontName="Helvetica-Bold",
        ),
        "h2": ParagraphStyle(
            "H2", parent=base["Heading2"], fontSize=11, textColor=INK,
            spaceBefore=8, spaceAfter=4, fontName="Helvetica-Bold",
        ),
        "body": ParagraphStyle(
            "B", parent=base["Normal"], fontSize=10, textColor=INK,
            leading=14, spaceAfter=5, alignment=TA_JUSTIFY,
        ),
        "bullet": ParagraphStyle(
            "Li", parent=base["Normal"], fontSize=10, textColor=INK, leading=13,
        ),
        "footer_note": ParagraphStyle(
            "FN", parent=base["Normal"], fontSize=9, textColor=MUTED,
            alignment=TA_CENTER, spaceBefore=8,
        ),
    }


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


def cover_page(story, s, proposal_title: str, component: str, today: str, student: str, student_id: str):
    story.append(Spacer(1, 25 * mm))
    story.append(Paragraph(PROJECT_TITLE, s["cover_sub"]))
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph("Project Proposal", s["doc_type"]))
    story.append(Paragraph(proposal_title, s["cover_title"]))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph(component, s["cover_sub"]))
    story.append(Spacer(1, 18 * mm))
    table(story, s, ["Field", "Details"], [
        ["Project ID", PROJECT_ID],
        ["Student Name", student],
        ["Student ID", student_id or "—"],
        ["Institution", INSTITUTION],
        ["Programme", DEGREE],
        ["Submission Date", today],
        ["Document Type", "Project Proposal"],
    ], [45 * mm, 125 * mm])
    story.append(PageBreak())


def build_sos_proposal(today: str):
    s = styles()
    story = []
    title = "SOS Emergency Response System"
    label = f"{PROJECT_ID} — SOS Emergency Response System Proposal"

    cover_page(
        story, s, title, "Component 1: Tourist SOS PWA + Police Dashboard", today,
        STUDENT_SOS, STUDENT_SOS_ID,
    )

    # 1. Executive Summary
    story.append(Paragraph("1. Executive Summary", s["h1"]))
    story.append(Paragraph(
        "This proposal describes the design and implementation of an SOS Emergency Response System "
        "as part of the Tour Ceylon unified tourism platform. The system addresses a critical gap "
        "for international visitors in Sri Lanka: the lack of a fast, trusted, location-aware "
        "channel to reach police assistance during emergencies.",
        s["body"],
    ))
    story.append(Paragraph(
        "The solution comprises two web applications — a Tourist Progressive Web App (PWA) for "
        "one-tap emergency alerts and a Police Dashboard for station officers to acknowledge, "
        "dispatch, communicate with, and close incidents. Both applications share a unified "
        "Flask backend and PostgreSQL database with the Travel itinerary component.",
        s["body"],
    ))

    # 2. Background
    story.append(Paragraph("2. Background &amp; Motivation", s["h1"]))
    bullets(story, s, [
        "Sri Lanka welcomed over 1.5 million tourists annually pre-pandemic, with numbers recovering "
        "strongly. Visitors often lack knowledge of local emergency numbers, nearest police desks, "
        "or how to communicate location under stress.",
        "Existing emergency channels (119 hotline) do not automatically share GPS coordinates or "
        "route incidents to the geographically nearest dispatchable police station.",
        "Tour operators and hotels are not automatically notified when a registered tourist triggers "
        "an emergency, delaying family or staff awareness.",
        "The Tour Ceylon platform already serves tourists for trip planning; extending it with an "
        "integrated SOS module creates a single account experience from planning through safety.",
    ])

    # 3. Problem Statement
    story.append(Paragraph("3. Problem Statement", s["h1"]))
    story.append(Paragraph(
        "Foreign tourists in Sri Lanka face difficulty obtaining timely police assistance during "
        "medical emergencies, theft, assault, accidents, or harassment. They may not know which "
        "police station covers their location, cannot easily share accurate GPS coordinates by "
        "phone, and have no digital workflow to track whether help has been acknowledged or "
        "dispatched. Police stations lack a dedicated digital queue for tourist SOS incidents "
        "with location, tourist profile, and communication tools in one place.",
        s["body"],
    ))

    # 4. Objectives
    story.append(Paragraph("4. Project Objectives", s["h1"]))
    table(story, s, ["#", "Objective", "Success Indicator"], [
        ["O1", "Enable one-tap SOS alerts with GPS from a mobile-friendly PWA",
         "Tourist triggers incident in &lt;3 taps with lat/lng captured"],
        ["O2", "Route each incident to the single nearest dispatchable police station",
         "Haversine distance computed; station_id stored on incident"],
        ["O3", "Provide police workflow: Acknowledge → Dispatch → Close",
         "Status timestamps recorded; tourist UI reflects updates"],
        ["O4", "Support incident chat between tourist and assigned station",
         "Text, image, and voice messages stored per incident"],
        ["O5", "Integrate with Travel app login (no duplicate registration)",
         "JWT bridge-travel endpoint exchanges Travel token for SOS session"],
        ["O6", "Export closed incident PDF reports for police records",
         "ReportLab PDF downloadable after Close status"],
        ["O7", "Protect sensitive tourist PII with encryption at rest",
         "Fernet encryption on phone, passport/NIC, emergency contact"],
    ], [10 * mm, 78 * mm, 82 * mm])

    story.append(PageBreak())

    # 5. Proposed Solution
    story.append(Paragraph("5. Proposed Solution", s["h1"]))
    story.append(Paragraph(
        "The SOS system is split into three tiers: Tourist PWA, Police Dashboard, and Shared Backend.",
        s["body"],
    ))
    story.append(Paragraph("5.1 Tourist PWA (port 5175)", s["h2"]))
    bullets(story, s, [
        "Six-type SOS bar: general, medical, assault, theft, accident, harassment",
        "One-shot browser geolocation at trigger — no continuous tracking (privacy by design)",
        "Real-time workflow tracker: Open → Acknowledged → Dispatched → Closed",
        "Incident chat with assigned police station",
        "Call nearest hospital via Haversine lookup + tel: dial link",
        "Installable PWA for mobile; Travel app handoff via JWT bridge",
    ])
    story.append(Paragraph("5.2 Police Dashboard (port 5176)", s["h2"]))
    bullets(story, s, [
        "Station-scoped officer login — each station sees only its own incidents",
        "Live incident queue with audio alert on new open cases",
        "Leaflet map showing tourist GPS pin and distance to station",
        "Workflow buttons: Acknowledge, Dispatch, Close",
        "Analytics charts: incident volume, response times, type breakdown",
        "PDF export for closed incidents",
    ])
    story.append(Paragraph("5.3 Shared Backend (port 5002)", s["h2"]))
    bullets(story, s, [
        "Unified Flask monolith shared with Travel component",
        "REST API with JWT authentication (tourist role vs officer role)",
        "Haversine routing service for nearest station and nearest hospital",
        "Notification service (console stub; Twilio/SendGrid optional)",
        "PostgreSQL persistence for tourists, incidents, stations, chat, hospitals",
    ])

    # 6. Methodology
    story.append(Paragraph("6. Methodology", s["h1"]))
    story.append(Paragraph(
        "Emergency routing uses deterministic Haversine great-circle distance — not machine learning. "
        "This approach is transparent, explainable, fast, and appropriate for nearest-station dispatch.",
        s["body"],
    ))
    table(story, s, ["Phase", "Activity", "Deliverable"], [
        ["1. Requirements", "Stakeholder analysis, user stories for tourist and officer flows",
         "Requirements document + wireframes"],
        ["2. Data collection", "Import police station and hospital coordinates from Excel datasets",
         "Seeded PostgreSQL tables"],
        ["3. Backend API", "Flask routes, JWT auth, routing, notify, PDF export",
         "REST API on port 5002"],
        ["4. Tourist PWA", "React + Vite PWA with SOS trigger, chat, workflow",
         "frontend/tourist on port 5175"],
        ["5. Police Dashboard", "React + Leaflet map, queue, stats, workflow",
         "frontend/police on port 5176"],
        ["6. Integration", "Travel JWT bridge, shared database, end-to-end demo",
         "Unified Tour Ceylon platform"],
        ["7. Testing", "Manual demo flow, routing validation, security review",
         "Demo script + panel documentation"],
    ], [28 * mm, 82 * mm, 60 * mm])

    # 7. Technology Stack
    story.append(Paragraph("7. Technology Stack", s["h1"]))
    table(story, s, ["Layer", "Technology", "Purpose"], [
        ["Backend", "Flask 3.0.3", "Unified REST API"],
        ["Tourist UI", "React 18 + Vite 5 PWA", "Mobile-friendly SOS app"],
        ["Police UI", "React 18 + Vite + Leaflet", "Station dashboard with map"],
        ["Database", "PostgreSQL (travel_app)", "Incidents, tourists, stations, chat"],
        ["Auth", "Flask-JWT-Extended", "Role-based tokens (tourist, officer)"],
        ["Encryption", "Fernet (cryptography)", "PII at rest"],
        ["PDF", "ReportLab", "Closed incident reports"],
        ["Charts", "Recharts", "Police analytics dashboard"],
        ["Routing", "Haversine (Python math)", "Nearest station/hospital"],
    ], [35 * mm, 45 * mm, 90 * mm])

    story.append(PageBreak())

    # 8. Data Requirements
    story.append(Paragraph("8. Data Requirements", s["h1"]))
    table(story, s, ["Dataset", "Source", "Records", "Usage"], [
        ["Police stations", "Sri_Lanka_Police_Emergency_with_Coordinates.xlsx",
         "Real desks", "Routing targets"],
        ["Hospitals", "Sri_Lanka_Government_Hospitals_with_Coordinates.xlsx",
         "Gov + private", "Nearest hospital lookup"],
        ["Officer credentials", "station_credentials.csv (generated)", "1 per station",
         "Police login"],
        ["Demo tourists", "seed_sos_data.py", "Simulated", "Presentation/testing"],
    ], [38 * mm, 62 * mm, 28 * mm, 42 * mm])

    # 9. Scope
    story.append(Paragraph("9. Scope", s["h1"]))
    story.append(Paragraph("<b>In scope</b>", s["h2"]))
    bullets(story, s, [
        "Tourist registration, login, and Travel JWT bridge",
        "Six-type SOS trigger with one-shot GPS",
        "Nearest-station routing and incident creation",
        "Police acknowledge/dispatch/close workflow",
        "Incident chat (text, image, voice)",
        "Nearest hospital dial lookup",
        "Police analytics and PDF export",
        "Fernet encryption of sensitive fields",
    ])
    story.append(Paragraph("<b>Out of scope (future work)</b>", s["h2"]))
    bullets(story, s, [
        "Continuous live GPS tracking after SOS trigger",
        "Automatic hospital dispatch or ambulance routing",
        "WebSocket real-time updates (polling used instead)",
        "Integration with national 119 emergency switchboard",
        "Multi-language tourist interface",
        "Automated unit/integration test suite",
    ])

    # 10. Expected Outcomes
    story.append(Paragraph("10. Expected Outcomes &amp; Impact", s["h1"]))
    bullets(story, s, [
        "Tourists gain a trusted digital SOS channel integrated with their trip planning account.",
        "Police stations receive structured incident queues with GPS, tourist profile, and chat.",
        "Response workflow is auditable via timestamps and exportable PDF reports.",
        "Privacy is preserved through one-shot location capture and encrypted PII.",
        "The system demonstrates practical use of geospatial routing without ML complexity.",
        "Platform readiness for future SMS/email notification via Twilio/SendGrid configuration.",
    ])

    # 11. Timeline
    story.append(Paragraph("11. Proposed Timeline", s["h1"]))
    table(story, s, ["Week", "Milestone"], [
        ["1–2", "Requirements, data import, database schema design"],
        ["3–4", "Backend API: auth, incidents, routing, hospitals"],
        ["5–6", "Tourist PWA: SOS trigger, workflow, chat, hospital dial"],
        ["7–8", "Police Dashboard: queue, map, workflow, stats, PDF"],
        ["9", "Travel JWT bridge integration"],
        ["10", "Testing, documentation, panel preparation"],
    ], [25 * mm, 145 * mm])

    # 12. Conclusion
    story.append(Paragraph("12. Conclusion", s["h1"]))
    story.append(Paragraph(
        "The SOS Emergency Response System provides a practical, privacy-conscious solution for "
        "tourist safety in Sri Lanka. By combining a one-tap mobile PWA, deterministic nearest-station "
        "routing, and a station-scoped police dashboard, the system closes a real gap in digital "
        "tourism infrastructure. As Component 1 of Tour Ceylon, it integrates seamlessly with the "
        "Travel itinerary planner, offering tourists a unified platform from trip planning through "
        "emergency assistance.",
        s["body"],
    ))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        f"{PROJECT_ID} · {STUDENT_SOS} ({STUDENT_SOS_ID}) · {INSTITUTION}",
        s["footer_note"],
    ))

    out = OUT_DIR / "SOS_Emergency_Response_System_Proposal.pdf"
    doc = SimpleDocTemplate(
        str(out), pagesize=A4,
        leftMargin=18 * mm, rightMargin=18 * mm,
        topMargin=16 * mm, bottomMargin=18 * mm,
        title="SOS Emergency Response System Proposal",
    )
    doc.build(story, onFirstPage=lambda c, d: page_footer(c, d, label),
              onLaterPages=lambda c, d: page_footer(c, d, label))
    print(f"Wrote {out}")
    return out


def build_travel_proposal(today: str):
    s = styles()
    story = []
    title = "Travel Itinerary Planning System"
    label = f"{PROJECT_ID} — Travel Itinerary Planning System Proposal"

    cover_page(
        story, s, title, "Component 2: Trip Wizard, AI Itinerary Generator &amp; Export", today,
        STUDENT_ITINERARY, STUDENT_ITINERARY_ID,
    )

    # 1. Executive Summary
    story.append(Paragraph("1. Executive Summary", s["h1"]))
    story.append(Paragraph(
        "This proposal describes the Travel Itinerary Planning System — the second major component "
        "of Tour Ceylon. The system helps international and local visitors plan Sri Lankan holidays "
        "through a guided multi-step wizard that turns mood preferences, attraction selections, "
        "budget constraints, and hotel choices into a personalised day-by-day timed itinerary "
        "with PDF export.",
        s["body"],
    ))
    story.append(Paragraph(
        "Unlike generic travel blogs or static templates, Tour Ceylon uses curated Sri Lankan tourism "
        "datasets (937 hotels, 350 attractions, 417 travel agencies, 2,906 licensed guides, and "
        "126 local businesses) combined with a transparent rule-based itinerary engine. The Travel "
        "component shares authentication and backend infrastructure with the SOS Emergency Response "
        "System, enabling a single login across planning and safety features.",
        s["body"],
    ))

    # 2. Background
    story.append(Paragraph("2. Background &amp; Motivation", s["h1"]))
    bullets(story, s, [
        "Planning a Sri Lanka trip involves scattered information across websites, guidebooks, "
        "and social media — attractions, hotels, budgets, local services, and licensed guides "
        "are rarely in one place.",
        "Tourists struggle to align mood preferences, number of days, multiple destinations, "
        "and budget into a coherent day-by-day schedule.",
        "Existing tools offer generic templates rather than personalised plans built from "
        "real Sri Lankan catalog data and user selections.",
        "There is no integrated path from trip planning to emergency assistance — Tour Ceylon "
        "addresses both through a unified platform.",
    ])

    # 3. Problem Statement
    story.append(Paragraph("3. Problem Statement", s["h1"]))
    story.append(Paragraph(
        "Tourists visiting Sri Lanka lack a single digital tool that combines mood-based attraction "
        "discovery, budget-aware hotel matching, rule-based day-by-day itinerary generation, "
        "local business and guide recommendations, and exportable trip documents. Manual planning "
        "is time-consuming, error-prone (e.g. scheduling more destinations than available days), "
        "and does not leverage structured tourism datasets already maintained by authorities and "
        "industry bodies.",
        s["body"],
    ))

    # 4. Objectives
    story.append(Paragraph("4. Project Objectives", s["h1"]))
    table(story, s, ["#", "Objective", "Success Indicator"], [
        ["O1", "Provide mood-based attraction browsing and selection",
         "350 attractions filterable by 10 mood tags"],
        ["O2", "Guide users through budget splitting and hotel selection",
         "Budget pie chart + per-destination hotel picker within budget"],
        ["O3", "Generate personalised day-by-day timed itineraries",
         "Rule-based engine produces JSON with activities and clock times"],
        ["O4", "Recommend local businesses, agencies, and licensed guides",
         "SQL-filtered lists by trip destinations; save to trip"],
        ["O5", "Export complete trip plan as downloadable PDF",
         "ReportLab PDF with schedule, budget, stays, saved references"],
        ["O6", "Persist trip history for returning users",
         "JWT-authenticated trips stored in PostgreSQL"],
        ["O7", "Bridge to SOS component from same account",
         "Sidebar link opens Tourist SOS PWA with JWT handoff"],
    ], [10 * mm, 78 * mm, 82 * mm])

    story.append(PageBreak())

    # 5. Proposed Solution
    story.append(Paragraph("5. Proposed Solution", s["h1"]))
    story.append(Paragraph(
        "The Travel system follows a six-step wizard architecture backed by a rule-based itinerary "
        "engine and curated PostgreSQL datasets.",
        s["body"],
    ))
    story.append(Paragraph("5.1 Six-step trip wizard", s["h2"]))
    table(story, s, ["Step", "Page", "User action", "Data saved"], [
        ["1", "Attractions", "Pick moods, select places, set days",
         "user_trip_input: moods, attraction IDs, days"],
        ["2", "Budget", "Enter total budget; view/customise split",
         "budget_split: food/stay/shopping/transport"],
        ["3", "Accommodation", "Pick room type + hotel per city",
         "user_trip_input: hotels, room_type"],
        ["4", "Itinerary", "Set start time; click Generate",
         "generated_itinerary: timed JSON plan"],
        ["5", "Discover", "Browse/save shops, agencies, guides",
         "saved_references per trip"],
        ["6", "Export", "Download PDF",
         "PDF from itinerary + budget + references"],
    ], [12 * mm, 28 * mm, 55 * mm, 75 * mm])

    story.append(Paragraph("5.2 Itinerary generation pipeline", s["h2"]))
    bullets(story, s, [
        "<b>trip_plan_service.py</b> — splits days across cities in consecutive blocks; assigns "
        "attractions and hotels to each day (no city bouncing).",
        "<b>ai_service.py</b> — adds clock times using mood lookup tables, category/name hints, "
        "and fixed activity gaps (2–3 hours; skip lunch slot). Despite the filename, this is "
        "rule-based — not OpenAI or machine learning.",
        "<b>generated_itinerary table</b> — persists JSON plan; replaced on each regeneration.",
        "<b>pdf_service.py</b> — renders schedule, trip budget, selected stays, and saved references.",
    ])

    story.append(Paragraph("5.3 Room type pricing model", s["h2"]))
    story.append(Paragraph(
        "Hotels store nightly price ranges (min A, max B). Room type selection applies a transparent "
        "formula: Single = A, Double = (A+B)/2, Family = B. Display uses approximate formatting "
        "(e.g. ~15,000 LKR / night).",
        s["body"],
    ))

    # 6. Methodology
    story.append(Paragraph("6. Methodology", s["h1"]))
    story.append(Paragraph(
        "The itinerary engine is fully deterministic — no model training, no Random Forest, "
        "no neural networks. Quality is evaluated through manual review and a 12-step automated "
        "API smoke test.",
        s["body"],
    ))
    table(story, s, ["Phase", "Activity", "Deliverable"], [
        ["1. Data seeding", "Import Excel/CSV tourism datasets into PostgreSQL",
         "937 hotels, 350 attractions, guides, agencies, businesses"],
        ["2. Auth &amp; trip API", "Register/login, trip-input, budget split endpoints",
         "JWT-secured trip CRUD"],
        ["3. Accommodation", "Hotel filtering by destination + budget + room type",
         "Accommodation page with Single/Double/Family selector"],
        ["4. Itinerary engine", "Day allocation, time scheduling, JSON output",
         "trip_plan_service + ai_service"],
        ["5. Discover &amp; export", "Business/agency/guide APIs, saved references, PDF",
         "Discover page + Export page"],
        ["6. Frontend wizard", "React 6-step UI with Recharts budget chart",
         "frontend/travel on port 5180"],
        ["7. Testing", "verify_seed.py + test_api_flow.py (12 steps incl. PDF)",
         "Seed counts + smoke test pass"],
    ], [28 * mm, 82 * mm, 60 * mm])

    # 7. Technology Stack
    story.append(Paragraph("7. Technology Stack", s["h1"]))
    table(story, s, ["Layer", "Technology", "Purpose"], [
        ["Backend", "Flask 3.0.3", "Unified REST API (shared with SOS)"],
        ["Frontend", "React 18 + Vite 5", "Six-step trip wizard"],
        ["Database", "PostgreSQL (travel_app)", "Catalogs + user trips + itineraries"],
        ["ORM", "SQLAlchemy 2.0", "Data models"],
        ["Auth", "Flask-JWT-Extended + optional Google OAuth", "User accounts"],
        ["Data import", "Pandas + openpyxl", "Excel/CSV seeding"],
        ["PDF", "ReportLab", "Itinerary PDF export"],
        ["Charts", "Recharts", "Budget pie chart"],
        ["Itinerary logic", "Python rule engine", "Day/time scheduling (not ML)"],
    ], [35 * mm, 45 * mm, 90 * mm])

    story.append(PageBreak())

    # 8. Data Requirements
    story.append(Paragraph("8. Data Requirements", s["h1"]))
    table(story, s, ["Dataset", "File", "Rows", "Provenance"], [
        ["Hotels", "accomadation.xlsx", "937", "Real hotel catalog"],
        ["Attractions", "attractions.xlsx", "350", "Real catalog + images"],
        ["Businesses", "business_directory.xlsx", "126", "Local shops &amp; services"],
        ["Travel agencies", "travel_agencies.xlsx", "417", "Licensed agencies"],
        ["Tourist guides", "tourist_guides.csv", "2,906", "srilanka.travel registry"],
        ["User trips", "Runtime input", "Dynamic", "Created per authenticated session"],
        ["Heuristic tuning", "MOOD_START_HOURS in code", "N/A", "Assumed start-time mappings"],
    ], [35 * mm, 45 * mm, 22 * mm, 68 * mm])

    # 9. Scope
    story.append(Paragraph("9. Scope", s["h1"]))
    story.append(Paragraph("<b>In scope</b>", s["h2"]))
    bullets(story, s, [
        "User registration, login, optional Google Sign-In",
        "Mood-based attraction browse and multi-select (1–3 moods)",
        "Trip constraint: unique destinations cannot exceed trip days",
        "Budget splitting (default 25/35/15/25 or custom percentages)",
        "Per-destination hotel selection with room type pricing",
        "Rule-based timed itinerary generation and regeneration",
        "Discover tab: businesses, agencies, licensed guides + save to trip",
        "PDF export with budget, stays, schedule, saved references",
        "Trip history and SOS bridge link",
    ])
    story.append(Paragraph("<b>Out of scope (future work)</b>", s["h2"]))
    bullets(story, s, [
        "GPS/route optimisation between attractions (no lat/lng on attractions)",
        "Opening hours and traffic-aware scheduling",
        "ML-based recommendation ranking (current: SQL filters + heuristics)",
        "Real-time hotel availability and booking",
        "Multi-currency live exchange rates (fixed LKR/USD rate used)",
        "Per-day start time override in UI",
        "Docker Compose deployment packaging",
    ])

    # 10. Key Features
    story.append(Paragraph("10. Key Features", s["h1"]))
    table(story, s, ["Feature", "Description"], [
        ["Mood-based discovery", "10 moods; filter 350 attractions by user preference"],
        ["Smart day allocation", "Consecutive city blocks — no back-and-forth routing"],
        ["Budget visualisation", "Interactive pie chart with customisable category split"],
        ["Room type pricing", "Single/Double/Family mapped to hotel price range formula"],
        ["Timed activities", "Mood/category-aware start times with lunch gap"],
        ["Local recommendations", "Businesses, agencies, guides filtered by destinations"],
        ["PDF export", "Professional trip document with all saved selections"],
        ["Unified login", "Same account opens SOS PWA via JWT bridge"],
    ], [45 * mm, 125 * mm])

    # 11. Expected Outcomes
    story.append(Paragraph("11. Expected Outcomes &amp; Impact", s["h1"]))
    bullets(story, s, [
        "Tourists receive personalised Sri Lankan itineraries built from real catalog data.",
        "Planning time reduced from hours of research to a guided 10-minute wizard.",
        "Budget transparency through visual splitting and hotel filtering within stay budget.",
        "Local economy support via discovery of businesses, agencies, and licensed guides.",
        "Exportable PDF serves as a shareable trip document for travel companions or agents.",
        "Foundation for future enhancements (GPS routing, ML recommendations, live booking).",
    ])

    # 12. Timeline
    story.append(Paragraph("12. Proposed Timeline", s["h1"]))
    table(story, s, ["Week", "Milestone"], [
        ["1–2", "Database schema, data seeding, attraction/hotel import"],
        ["3–4", "Auth, trip-input API, budget split, accommodation filtering"],
        ["5–6", "Itinerary engine: day allocation + time scheduling"],
        ["7–8", "React wizard UI: all six steps + Recharts budget chart"],
        ["9", "Discover tab, saved references, PDF export"],
        ["10", "Room type pricing, SOS bridge, testing, documentation"],
    ], [25 * mm, 145 * mm])

    # 13. Conclusion
    story.append(Paragraph("13. Conclusion", s["h1"]))
    story.append(Paragraph(
        "The Travel Itinerary Planning System transforms scattered Sri Lankan tourism information "
        "into a coherent, personalised trip plan through a transparent rule-based engine and "
        "curated datasets. Combined with the SOS Emergency Response System under the Tour Ceylon "
        "umbrella, it offers tourists an end-to-end digital companion — from dreaming and planning "
        "to staying safe on the ground.",
        s["body"],
    ))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        f"{PROJECT_ID} · {STUDENT_ITINERARY} · {INSTITUTION}",
        s["footer_note"],
    ))

    out = OUT_DIR / "Travel_Itinerary_Planning_System_Proposal.pdf"
    doc = SimpleDocTemplate(
        str(out), pagesize=A4,
        leftMargin=18 * mm, rightMargin=18 * mm,
        topMargin=16 * mm, bottomMargin=18 * mm,
        title="Travel Itinerary Planning System Proposal",
    )
    doc.build(story, onFirstPage=lambda c, d: page_footer(c, d, label),
              onLaterPages=lambda c, d: page_footer(c, d, label))
    print(f"Wrote {out}")
    return out


def main():
    today = datetime.now().strftime("%d %B %Y")
    build_sos_proposal(today)
    build_travel_proposal(today)
    print(f"\nDone. Download from:\n  {OUT_DIR}")


if __name__ == "__main__":
    main()
