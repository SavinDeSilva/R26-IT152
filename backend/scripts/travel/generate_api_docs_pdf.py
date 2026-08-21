"""Generate Tour Ceylon backend API documentation PDF."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch, mm
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

OUT = Path(__file__).resolve().parents[2] / "Tour_Ceylon_Backend_API_Docs.pdf"  # backend/


def styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "DocTitle",
            parent=base["Title"],
            fontSize=20,
            textColor=colors.HexColor("#1E6E6F"),
            spaceAfter=6,
            alignment=TA_CENTER,
        ),
        "subtitle": ParagraphStyle(
            "DocSub",
            parent=base["Normal"],
            fontSize=10,
            textColor=colors.HexColor("#4a8586"),
            alignment=TA_CENTER,
            spaceAfter=18,
        ),
        "h1": ParagraphStyle(
            "H1",
            parent=base["Heading1"],
            fontSize=14,
            textColor=colors.HexColor("#1E6E6F"),
            spaceBefore=14,
            spaceAfter=8,
        ),
        "h2": ParagraphStyle(
            "H2",
            parent=base["Heading2"],
            fontSize=11,
            textColor=colors.HexColor("#1E6E6F"),
            spaceBefore=12,
            spaceAfter=4,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["Normal"],
            fontSize=9,
            leading=12,
            spaceAfter=4,
        ),
        "meta": ParagraphStyle(
            "Meta",
            parent=base["Normal"],
            fontSize=8.5,
            textColor=colors.HexColor("#4a8586"),
            spaceAfter=4,
        ),
        "code": ParagraphStyle(
            "Code",
            parent=base["Code"],
            fontName="Courier",
            fontSize=7.5,
            leading=10,
            backColor=colors.HexColor("#f4fbfb"),
            borderPadding=6,
            spaceBefore=4,
            spaceAfter=8,
            leftIndent=4,
            rightIndent=4,
        ),
        "label": ParagraphStyle(
            "Label",
            parent=base["Normal"],
            fontSize=8,
            textColor=colors.HexColor("#1E6E6F"),
            fontName="Helvetica-Bold",
            spaceBefore=4,
            spaceAfter=2,
        ),
    }


def hr():
    return HRFlowable(width="100%", thickness=0.6, color=colors.HexColor("#b6e6e9"), spaceBefore=4, spaceAfter=8)


def code_block(text, s):
    return Preformatted(text.strip("\n"), s["code"])


def endpoint(story, s, method, path, auth, request=None, response=None, notes=None):
    block = []
    block.append(Paragraph(f"<b>{method}</b>  {path}", s["h2"]))
    block.append(Paragraph(f"Auth: {auth}", s["meta"]))
    if notes:
        block.append(Paragraph(notes, s["body"]))
    if request:
        block.append(Paragraph("Sample request", s["label"]))
        block.append(code_block(request, s))
    if response:
        block.append(Paragraph("Sample response", s["label"]))
        block.append(code_block(response, s))
    block.append(hr())
    story.append(KeepTogether(block))


def build():
    s = styles()
    doc = SimpleDocTemplate(
        str(OUT),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title="Tour Ceylon Backend API Documentation",
        author="Tour Ceylon / Visily Travel App",
    )
    story = []

    story.append(Paragraph("Tour Ceylon — Backend API Documentation", s["title"]))
    story.append(
        Paragraph(
            "Answers for: Base URL · Live endpoints · Sample request/response · Auth/headers · Current status",
            s["subtitle"],
        )
    )
    story.append(hr())

    # 1
    story.append(Paragraph("1. Base URL / port", s["h1"]))
    data = [
        [Paragraph("<b>Item</b>", s["body"]), Paragraph("<b>Value</b>", s["body"])],
        [Paragraph("Backend host", s["body"]), Paragraph("http://localhost:5002", s["body"])],
        [Paragraph("API prefix", s["body"]), Paragraph("/api", s["body"])],
        [Paragraph("Full API base URL", s["body"]), Paragraph("http://localhost:5002/api", s["body"])],
        [
            Paragraph("Frontend proxy", s["body"]),
            Paragraph("Vite (:5173) proxies /api → http://localhost:5002", s["body"]),
        ],
        [Paragraph("Default port", s["body"]), Paragraph("5000 (env PORT override supported)", s["body"])],
    ]
    t = Table(data, colWidths=[2.2 * inch, 4.5 * inch])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eef8f8")),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#b6e6e9")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(t)
    story.append(Spacer(1, 6))
    story.append(Paragraph("Start the server:", s["label"]))
    story.append(
        code_block(
            """cd backend
.venv\\Scripts\\activate
python run.py""",
            s,
        )
    )

    # 2
    story.append(Paragraph("2. Live endpoints (method + path)", s["h1"]))
    rows = [
        [Paragraph("<b>Method</b>", s["body"]), Paragraph("<b>Path</b>", s["body"]), Paragraph("<b>Auth</b>", s["body"])],
        ["GET", "/api/health", "Public"],
        ["POST", "/api/auth/register", "Public"],
        ["POST", "/api/auth/login", "Public"],
        ["GET", "/api/attractions", "Public"],
        ["GET", "/api/images/resolve", "Public"],
        ["GET", "/api/media/attractions/<filename>", "Public"],
        ["POST", "/api/trip-input", "JWT"],
        ["GET", "/api/trip-input/<trip_id>", "JWT"],
        ["PATCH", "/api/trip-input/<trip_id>", "JWT"],
        ["POST", "/api/budget/split", "JWT"],
        ["GET", "/api/budget/split/<trip_id>", "JWT"],
        ["GET", "/api/accommodation", "JWT"],
        ["POST", "/api/itinerary/generate", "JWT"],
        ["GET", "/api/itinerary/<trip_id>", "JWT"],
        ["GET", "/api/itinerary/<trip_id>/pdf", "JWT"],
        ["GET", "/api/business-directory", "JWT"],
        ["GET", "/api/travel-agencies", "JWT"],
        ["POST", "/api/saved-references", "JWT"],
        ["GET", "/api/saved-references", "JWT"],
    ]
    table_data = []
    for i, row in enumerate(rows):
        if i == 0:
            table_data.append(row)
        else:
            table_data.append(
                [
                    Paragraph(row[0], s["body"]),
                    Paragraph(row[1], s["body"]),
                    Paragraph(row[2], s["body"]),
                ]
            )
    et = Table(table_data, colWidths=[0.9 * inch, 4.0 * inch, 1.6 * inch])
    et.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E6E6F")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#cfe8e9")),
                ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7fcfc")]),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    story.append(et)

    # 4 first briefly then 3 with samples - user asked 1-5 in order, so keep 3 then 4
    story.append(Paragraph("3. Sample request / response JSON for each endpoint", s["h1"]))
    story.append(
        Paragraph(
            "All JSON endpoints use Content-Type: application/json unless noted. "
            "Protected routes also require the Authorization header described in section 4.",
            s["body"],
        )
    )

    endpoint(
        story,
        s,
        "GET",
        "/api/health",
        "Public",
        response='{ "status": "ok" }',
    )

    endpoint(
        story,
        s,
        "POST",
        "/api/auth/register",
        "Public",
        request='{\n  "email": "test@example.com",\n  "password": "secret123"\n}',
        response='{\n  "access_token": "eyJ...",\n  "user": {\n    "id": 1,\n    "email": "test@example.com",\n    "created_at": "2026-07-24T08:00:00"\n  }\n}',
        notes="Errors: 400 missing/short password · 409 email already registered · 201 on success",
    )

    endpoint(
        story,
        s,
        "POST",
        "/api/auth/login",
        "Public",
        request='{\n  "email": "test@example.com",\n  "password": "secret123"\n}',
        response='{\n  "access_token": "eyJ...",\n  "user": {\n    "id": 1,\n    "email": "test@example.com",\n    "created_at": "..."\n  }\n}',
        notes="Error: 401 invalid credentials",
    )

    endpoint(
        story,
        s,
        "GET",
        "/api/attractions",
        "Public",
        request="Query params:\n  moods=Adventure,Spiritual   (optional, comma-separated)",
        response='{\n  "attractions": [\n    {\n      "id": 12,\n      "attraction_name": "Sigiriya",\n      "category": "Historical",\n      "destination": "Dambulla",\n      "normalized_destination": "Dambulla",\n      "details": "...",\n      "mood_tag": "Adventure",\n      "image": "/api/media/attractions/sigiriya.jpg"\n    }\n  ],\n  "count": 1,\n  "available_moods": ["Adventure", "Authentic"],\n  "filtered_moods": ["Adventure", "Spiritual"]\n}',
    )

    endpoint(
        story,
        s,
        "POST",
        "/api/trip-input",
        "JWT required",
        request='{\n  "days": 3,\n  "selected_moods": ["Adventure", "Peaceful"],\n  "finalized_attractions": [12, 45, 78]\n}',
        response='{\n  "trip": {\n    "trip_id": "a1b2c3d4-....",\n    "user_id": 1,\n    "selected_moods": ["Adventure", "Peaceful"],\n    "days": 3,\n    "finalized_attractions": [12, 45, 78],\n    "budget": null,\n    "accommodations": [],\n    "status": "in_progress"\n  },\n  "day_plan": [\n    {\n      "day": 1,\n      "destination": "Dambulla",\n      "attraction_id": 12,\n      "attraction_name": "Sigiriya"\n    }\n  ],\n  "rules": {\n    "min_locations": 1,\n    "max_locations": 3,\n    "location_count": 2,\n    "max_hotels": 2\n  }\n}',
        notes="Rule: unique destinations must be between 1 and days. Response status 201.",
    )

    endpoint(
        story,
        s,
        "GET",
        "/api/trip-input/<trip_id>",
        "JWT required",
        response="Same shape as create: { trip, day_plan, rules }\n404 if trip not found / not owned by user.",
    )

    endpoint(
        story,
        s,
        "PATCH",
        "/api/trip-input/<trip_id>",
        "JWT required",
        request='{\n  "accommodations_by_destination": {\n    "Dambulla": 101,\n    "Galle": 205\n  },\n  "budget": 2500,\n  "status": "in_progress"\n}',
        response='{\n  "trip": { "...": "..." },\n  "accommodations": [\n    {\n      "destination": "Dambulla",\n      "id": 101,\n      "name": "Hotel Example"\n    }\n  ]\n}',
        notes='Also accepts accommodations: [{ "destination": "Dambulla", "accommodation_id": 101 }]',
    )

    endpoint(
        story,
        s,
        "POST",
        "/api/budget/split",
        "JWT required",
        request='{\n  "trip_id": "a1b2c3d4-....",\n  "budget": 2500,\n  "customize": true,\n  "food_pct": 25,\n  "accommodation_pct": 35,\n  "shopping_pct": 15,\n  "transport_pct": 25\n}',
        response='{\n  "trip_id": "a1b2c3d4-....",\n  "budget": 2500,\n  "daily_estimate": 833.33,\n  "split": {\n    "food": 625,\n    "accommodation": 875,\n    "shopping": 375,\n    "transport": 625,\n    "food_pct": 25,\n    "accommodation_pct": 35,\n    "shopping_pct": 15,\n    "transport_pct": 25\n  }\n}',
        notes="If customize=false, default percentages are used (25/35/15/25). Custom percentages must sum to 100.",
    )

    endpoint(
        story,
        s,
        "GET",
        "/api/budget/split/<trip_id>",
        "JWT required",
        response='{\n  "budget": 2500,\n  "split": {\n    "food": 625,\n    "accommodation": 875,\n    "shopping": 375,\n    "transport": 625\n  }\n}',
    )

    endpoint(
        story,
        s,
        "GET",
        "/api/accommodation",
        "JWT required",
        request="Query params:\n  trip_id=<uuid>   (required)\nRequires budget split first.",
        response='{\n  "day_plan": [{ "day": 1, "destination": "Dambulla" }],\n  "stops_by_destination": [\n    {\n      "destination": "Dambulla",\n      "days": [1, 2],\n      "attractions": [{ "attraction_id": 12, "attraction_name": "Sigiriya" }],\n      "hotels": [{\n        "id": 101,\n        "name": "Hotel Example",\n        "price_range": "15000-25000",\n        "price_min": 15000,\n        "price_max": 25000\n      }],\n      "hotel_count": 1\n    }\n  ],\n  "count": 1,\n  "rules": { "required_hotels": 2, "max_hotels": 2 },\n  "filters": {\n    "per_night_usd": 291.67,\n    "per_night_lkr": 87500,\n    "destinations": ["Dambulla", "Galle"]\n  }\n}',
    )

    endpoint(
        story,
        s,
        "POST",
        "/api/itinerary/generate",
        "JWT required",
        request='{\n  "trip_id": "a1b2c3d4-...."\n}',
        response='{\n  "itinerary": {\n    "id": 1,\n    "trip_id": "a1b2c3d4-....",\n    "created_at": "...",\n    "itinerary": {\n      "title": "3-Day Sri Lanka Trip",\n      "summary": "Visiting: Sigiriya. Stays: Hotel Example.",\n      "route": "Dambulla → Galle",\n      "highlights": ["Sigiriya"],\n      "days": [{\n        "day": 1,\n        "title": "Dambulla",\n        "location": "Dambulla",\n        "accommodation": "Hotel Example",\n        "activities": [{\n          "time": "09:00 AM",\n          "title": "Sigiriya",\n          "mood_tag": "Adventure",\n          "attraction_id": 12\n        }]\n      }],\n      "source": "database"\n    }\n  }\n}',
        notes="Needs attractions + hotels for each destination + budget. Response status 201.",
    )

    endpoint(
        story,
        s,
        "GET",
        "/api/itinerary/<trip_id>",
        "JWT required",
        response="Same itinerary object as generate response.\n404 if not generated yet.",
    )

    endpoint(
        story,
        s,
        "GET",
        "/api/itinerary/<trip_id>/pdf",
        "JWT required",
        response="Returns application/pdf file download (not JSON).\nFilename example: itinerary-a1b2c3d4.pdf",
    )

    endpoint(
        story,
        s,
        "GET",
        "/api/business-directory",
        "JWT required",
        request="Query params:\n  trip_id=<uuid>   (optional — filters by trip destinations)",
        response='{\n  "businesses": [{\n    "id": 5,\n    "business_name": "Spice Shop",\n    "local_authority": "Galle",\n    "district": "Galle",\n    "telephone": "..."\n  }],\n  "count": 1,\n  "destinations": ["Galle"],\n  "remaining_budget": 1625.0\n}',
    )

    endpoint(
        story,
        s,
        "GET",
        "/api/travel-agencies",
        "JWT required",
        request="Query params:\n  trip_id=<uuid>   (optional)",
        response='{\n  "agencies": [{\n    "id": 3,\n    "name": "Ceylon Tours",\n    "local_authority": "Colombo",\n    "telephone": "...",\n    "email": "..."\n  }],\n  "count": 1,\n  "destinations": ["Colombo"]\n}',
    )

    endpoint(
        story,
        s,
        "POST",
        "/api/saved-references",
        "JWT required",
        request='{\n  "trip_id": "a1b2c3d4-....",\n  "ref_type": "business_directory",\n  "ref_id": 5\n}',
        response='{\n  "saved_reference": {\n    "id": 1,\n    "trip_id": "a1b2c3d4-....",\n    "user_id": 1,\n    "ref_type": "business_directory",\n    "ref_id": 5,\n    "created_at": "..."\n  }\n}',
        notes='ref_type must be "business_directory" or "travel_agency".',
    )

    endpoint(
        story,
        s,
        "GET",
        "/api/saved-references",
        "JWT required",
        request="Query params:\n  trip_id=<uuid>   (required)",
        response='{\n  "saved_references": [{\n    "id": 1,\n    "ref_type": "business_directory",\n    "ref_id": 5\n  }],\n  "count": 1\n}',
    )

    endpoint(
        story,
        s,
        "GET",
        "/api/images/resolve",
        "Public",
        request="Query params:\n  url=<image-or-page-url>  and/or  q=<search text>",
        response='{ "url": "https://...", "resolved": true }',
    )

    endpoint(
        story,
        s,
        "GET",
        "/api/media/attractions/<filename>",
        "Public",
        response="Serves a static image file (not JSON).",
    )

    # 4
    story.append(Paragraph("4. Auth / headers required", s["h1"]))
    story.append(
        Paragraph(
            "<b>Public endpoints</b> — no Authorization header.",
            s["body"],
        )
    )
    story.append(
        Paragraph(
            "<b>Protected endpoints</b> — send JWT after login/register:",
            s["body"],
        )
    )
    story.append(
        code_block(
            """Authorization: Bearer <access_token>
Content-Type: application/json""",
            s,
        )
    )
    story.append(
        Paragraph(
            "Token lifetime: <b>24 hours</b> (Flask-JWT-Extended). "
            "CORS is enabled for /api/* origins. "
            "Frontend stores the token in localStorage as access_token and attaches it via Axios interceptor.",
            s["body"],
        )
    )
    story.append(Spacer(1, 4))
    story.append(Paragraph("Typical curl example:", s["label"]))
    story.append(
        code_block(
            """curl -X POST http://localhost:5002/api/trip-input ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Bearer eyJ..." ^
  -d "{\\"days\\":3,\\"selected_moods\\":[\\"Adventure\\"],\\"finalized_attractions\\":[12]}" """,
            s,
        )
    )

    # 5
    story.append(Paragraph("5. Current status", s["h1"]))
    story.append(
        Paragraph(
            "<b>Status as of documentation generation: NOT RUNNING.</b>",
            s["body"],
        )
    )
    story.append(
        Paragraph(
            "The backend API is implemented and ready to test, but no Flask process was running "
            "in the open project terminals when this PDF was created. Start PostgreSQL, ensure "
            "schema/seed are applied, then run python run.py in the backend folder.",
            s["body"],
        )
    )
    story.append(Paragraph("Health check after start:", s["label"]))
    story.append(
        code_block(
            """curl http://localhost:5002/api/health
# Expect: {"status":"ok"}""",
            s,
        )
    )
    story.append(Spacer(1, 8))
    story.append(hr())
    story.append(
        Paragraph(
            "Project: Visily Travel App (Tour Ceylon / CeylonPath Planner) · Stack: Flask + PostgreSQL + JWT",
            s["meta"],
        )
    )

    doc.build(story)
    return OUT


if __name__ == "__main__":
    path = build()
    print(f"Wrote: {path}")
