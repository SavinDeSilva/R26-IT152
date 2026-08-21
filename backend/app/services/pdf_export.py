"""PDF export for closed incident reports (ReportLab — no system libs required)."""

from __future__ import annotations

import io
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def build_incident_pdf(incident) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleCustom",
        parent=styles["Heading1"],
        fontSize=16,
        spaceAfter=8,
    )
    body = []
    body.append(Paragraph(f"Incident Report #{incident.id}", title_style))
    body.append(
        Paragraph(
            f"Generated {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
            styles["Normal"],
        )
    )
    body.append(Spacer(1, 10))

    tourist = incident.tourist
    station = incident.station

    from app.sos_models import Incident as IncidentModel

    type_label = IncidentModel.TYPE_LABELS.get(
        getattr(incident, "incident_type", None) or "general", "General"
    )
    summary_rows = [
        ["Status", incident.status],
        ["Type", type_label],
        ["Tourist", tourist.name if tourist else "—"],
        ["Nationality", tourist.nationality if tourist else "—"],
        ["Phone", tourist.get_phone() if tourist else "—"],
        ["Passport/NIC", tourist.get_passport_or_nic() if tourist else "—"],
        ["Station", station.display_name if station else "—"],
        ["Initial GPS", f"{incident.initial_lat:.6f}, {incident.initial_lng:.6f}"],
        [
            "Distance to station",
            f"{incident.distance_to_station_km:.2f} km"
            if incident.distance_to_station_km is not None
            else "—",
        ],
    ]
    table = Table(summary_rows, colWidths=[55 * mm, 115 * mm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f0f4f8")),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    body.append(table)
    body.append(Spacer(1, 14))
    body.append(Paragraph("Timestamp trail", styles["Heading2"]))

    trail = [
        ["Event", "UTC time"],
        ["Triggered", _fmt(incident.triggered_at)],
        ["Acknowledged", _fmt(incident.acknowledged_at)],
        ["Dispatched", _fmt(incident.dispatched_at)],
        ["Closed", _fmt(incident.closed_at)],
        ["Contact notified", _fmt(incident.contact_notified_at)],
        ["Hotel notified", _fmt(incident.hotel_notified_at)],
    ]
    trail_table = Table(trail, colWidths=[55 * mm, 115 * mm])
    trail_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a5f")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    body.append(trail_table)
    body.append(Spacer(1, 14))

    pings = list(incident.location_pings.order_by().limit(200))
    body.append(Paragraph(f"Location pings ({len(pings)})", styles["Heading2"]))
    if pings:
        ping_rows = [["#", "Lat", "Lng", "Accuracy", "Recorded at"]]
        for i, p in enumerate(pings, 1):
            ping_rows.append(
                [
                    str(i),
                    f"{p.latitude:.6f}",
                    f"{p.longitude:.6f}",
                    f"{p.accuracy:.0f}m" if p.accuracy is not None else "—",
                    _fmt(p.recorded_at),
                ]
            )
        ping_table = Table(ping_rows, colWidths=[12 * mm, 35 * mm, 35 * mm, 25 * mm, 55 * mm])
        ping_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a5f")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ]
            )
        )
        body.append(ping_table)
    else:
        body.append(Paragraph("No location pings recorded.", styles["Normal"]))

    if incident.notes_summary:
        body.append(Spacer(1, 12))
        body.append(Paragraph("AI summary", styles["Heading2"]))
        body.append(Paragraph(incident.notes_summary, styles["Normal"]))

    doc.build(body)
    return buffer.getvalue()


def _fmt(dt) -> str:
    if not dt:
        return "—"
    return dt.strftime("%Y-%m-%d %H:%M:%S")
