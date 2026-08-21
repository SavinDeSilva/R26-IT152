"""Convert COLLEGE_SETUP_GUIDE.md to a printable PDF using ReportLab."""
from __future__ import annotations

import re
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
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

REPO_ROOT = Path(__file__).resolve().parents[3]  # tour-ceylon/
DEFAULT_MD = REPO_ROOT / "COLLEGE_SETUP_GUIDE.md"
DEFAULT_PDF = REPO_ROOT / "COLLEGE_SETUP_GUIDE.pdf"

TEAL = colors.HexColor("#0A4A52")
TEAL_MID = colors.HexColor("#12707A")
INK = colors.HexColor("#1A2332")
MUTED = colors.HexColor("#5A6570")
LINE = colors.HexColor("#D0DCE0")
CODE_BG = colors.HexColor("#F2F6F7")
ROW_ALT = colors.HexColor("#F5FAFA")


def escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def inline_md(text: str) -> str:
    """Convert light markdown inline syntax to ReportLab rich text."""
    text = escape(text)
    text = re.sub(r"`([^`]+)`", r'<font face="Courier" size="9" color="#0A4A52">\1</font>', text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", text)
    text = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        r'<link href="\2" color="#12707A"><u>\1</u></link>',
        text,
    )
    return text


def build_styles():
    base = getSampleStyleSheet()
    styles = {
        "title": ParagraphStyle(
            "DocTitle",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=24,
            textColor=TEAL,
            alignment=TA_CENTER,
            spaceAfter=8,
        ),
        "subtitle": ParagraphStyle(
            "DocSubtitle",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=MUTED,
            alignment=TA_CENTER,
            spaceAfter=16,
        ),
        "h1": ParagraphStyle(
            "H1",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=18,
            textColor=TEAL,
            spaceBefore=16,
            spaceAfter=8,
        ),
        "h2": ParagraphStyle(
            "H2",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=15,
            textColor=TEAL_MID,
            spaceBefore=12,
            spaceAfter=6,
        ),
        "h3": ParagraphStyle(
            "H3",
            parent=base["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=INK,
            spaceBefore=10,
            spaceAfter=4,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=INK,
            spaceAfter=6,
            alignment=TA_LEFT,
        ),
        "li": ParagraphStyle(
            "LI",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=13,
            textColor=INK,
            leftIndent=0,
        ),
        "code": ParagraphStyle(
            "Code",
            parent=base["Code"],
            fontName="Courier",
            fontSize=8,
            leading=11,
            textColor=INK,
            backColor=CODE_BG,
            leftIndent=4,
            rightIndent=4,
            spaceBefore=4,
            spaceAfter=8,
        ),
        "th": ParagraphStyle(
            "TH",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8.5,
            leading=11,
            textColor=colors.white,
        ),
        "td": ParagraphStyle(
            "TD",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=11,
            textColor=INK,
        ),
        "footer": ParagraphStyle(
            "Footer",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=8,
            textColor=MUTED,
            alignment=TA_CENTER,
        ),
    }
    return styles


def parse_table(rows: list[str], styles) -> Table:
    data = []
    for i, row in enumerate(rows):
        cells = [c.strip() for c in row.strip("|").split("|")]
        style = styles["th"] if i == 0 else styles["td"]
        data.append([Paragraph(inline_md(c), style) for c in cells])

    # Drop markdown separator row like |---|---|
    if len(data) > 1:
        raw_second = [c.strip() for c in rows[1].strip("|").split("|")]
        if all(re.fullmatch(r":?-+:?", c or "") for c in raw_second):
            data.pop(1)

    col_count = max(len(r) for r in data) if data else 1
    usable = 170 * mm
    col_w = usable / col_count
    table = Table(data, colWidths=[col_w] * col_count, hAlign="LEFT", repeatRows=1)
    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), TEAL),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.4, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    for r in range(1, len(data)):
        if r % 2 == 0:
            style_cmds.append(("BACKGROUND", (0, r), (-1, r), ROW_ALT))
    table.setStyle(TableStyle(style_cmds))
    return table


def md_to_story(md_text: str, styles):
    story = []
    lines = md_text.replace("\r\n", "\n").split("\n")
    i = 0
    first_h1 = True
    list_buf: list[str] = []
    table_buf: list[str] = []

    def flush_list():
        nonlocal list_buf
        if not list_buf:
            return
        items = []
        for item in list_buf:
            items.append(ListItem(Paragraph(inline_md(item), styles["li"]), leftIndent=12, value="•"))
        story.append(
            ListFlowable(
                items,
                bulletType="bullet",
                start="•",
                leftIndent=16,
                bulletFontName="Helvetica",
                bulletFontSize=10,
                spaceBefore=2,
                spaceAfter=8,
            )
        )
        list_buf = []

    def flush_table():
        nonlocal table_buf
        if not table_buf:
            return
        story.append(Spacer(1, 4))
        story.append(parse_table(table_buf, styles))
        story.append(Spacer(1, 8))
        table_buf = []

    while i < len(lines):
        line = lines[i]

        # fenced code
        if line.strip().startswith("```"):
            flush_list()
            flush_table()
            i += 1
            code_lines = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1  # closing fence
            code = "\n".join(code_lines).rstrip() or " "
            # Preformatted doesn't like some chars; keep plain
            block = Preformatted(code, styles["code"], maxLineLength=95)
            story.append(KeepTogether([
                Spacer(1, 2),
                Table([[block]], colWidths=[170 * mm], style=TableStyle([
                    ("BACKGROUND", (0, 0), (-1, -1), CODE_BG),
                    ("BOX", (0, 0), (-1, -1), 0.5, LINE),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ])),
                Spacer(1, 6),
            ]))
            continue

        # table rows
        if line.strip().startswith("|") and "|" in line.strip()[1:]:
            flush_list()
            table_buf.append(line)
            i += 1
            continue
        else:
            flush_table()

        # blank
        if not line.strip():
            flush_list()
            i += 1
            continue

        # hr
        if re.fullmatch(r"-{3,}", line.strip()):
            flush_list()
            story.append(HRFlowable(width="100%", thickness=0.8, color=LINE, spaceBefore=6, spaceAfter=10))
            i += 1
            continue

        # headings
        m = re.match(r"^(#{1,3})\s+(.*)$", line)
        if m:
            flush_list()
            level = len(m.group(1))
            text = m.group(2).strip()
            if level == 1 and first_h1:
                story.append(Paragraph(inline_md(text), styles["title"]))
                story.append(Paragraph("Tourist SOS — College installation &amp; run guide", styles["subtitle"]))
                first_h1 = False
            elif level == 1:
                story.append(Paragraph(inline_md(text), styles["h1"]))
            elif level == 2:
                story.append(Paragraph(inline_md(text), styles["h2"]))
            else:
                story.append(Paragraph(inline_md(text), styles["h3"]))
            i += 1
            continue

        # blockquote
        if line.startswith(">"):
            flush_list()
            story.append(Paragraph(inline_md(line.lstrip("> ").strip()), styles["body"]))
            i += 1
            continue

        # unordered list
        m = re.match(r"^[-*]\s+(.*)$", line)
        if m:
            list_buf.append(m.group(1))
            i += 1
            continue

        # ordered / checkbox list as bullets
        m = re.match(r"^(\d+\.|- \[[ xX]\])\s+(.*)$", line)
        if m:
            list_buf.append(m.group(2))
            i += 1
            continue

        flush_list()
        story.append(Paragraph(inline_md(line.strip()), styles["body"]))
        i += 1

    flush_list()
    flush_table()
    return story


def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.5)
    canvas.line(18 * mm, 14 * mm, A4[0] - 18 * mm, 14 * mm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(18 * mm, 8 * mm, "Tourist SOS App — College Setup Guide")
    canvas.drawRightString(A4[0] - 18 * mm, 8 * mm, f"Page {doc.page}")
    canvas.restoreState()


def convert(md_path: Path, pdf_path: Path):
    styles = build_styles()
    md_text = md_path.read_text(encoding="utf-8")
    story = md_to_story(md_text, styles)
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=18 * mm,
        title="Tourist SOS App — College Setup Guide",
        author="Tourist SOS Project",
    )
    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    print(f"Wrote {pdf_path}")


if __name__ == "__main__":
    md = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_MD
    pdf = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_PDF
    convert(md, pdf)
