"""Export the submitted Markdown reports to A4 and verify their page budgets.

Uses the desktop's optional reportlab/pypdf runtime; not a lab dependency.
"""
from pathlib import Path
import re
from xml.sax.saxutils import escape

from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output/pdf"


def inline(s):
    s = s.replace("\u2011", "-").replace("\u2013", "-").replace("\u2014", "-")
    s = escape(s)
    # Keep external references clickable; relative references belong to the
    # canonical Markdown files in the repository.
    s = re.sub(r"\[([^]]+)\]\(([^)]+)\)",
               lambda m: f'<link href="{m[2]}" color="#17615d">{m[1]}</link>'
               if m[2].startswith(("http://", "https://")) else m[1], s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    return s.replace("`", "")


def export(name, budget):
    source = ROOT / "report/team" / (name + ".md")
    styles = getSampleStyleSheet()
    for style in styles.byName.values():
        style.fontName = "Segoe"
    body = ParagraphStyle("ReportBody", fontName="Segoe", fontSize=9.2, leading=12.8,
                          spaceAfter=5, alignment=TA_LEFT)
    heading = ParagraphStyle("ReportHeading", parent=body, fontName="SegoeBold", fontSize=11,
                             leading=14, spaceBefore=9, spaceAfter=5, keepWithNext=True)
    title = ParagraphStyle("ReportTitle", parent=heading, fontSize=16, leading=21, spaceAfter=11)
    cell = ParagraphStyle("ReportCell", parent=body, fontSize=7.2, leading=10, spaceAfter=0)
    code = ParagraphStyle("ReportCode", parent=body, fontSize=8, leading=11, leftIndent=8)
    lines = source.read_text(encoding="utf-8").splitlines()
    story, i, in_code = [], 0, False
    while i < len(lines):
        line = lines[i].strip()
        if not line or line.startswith("<!--"):
            i += 1
            continue
        if line.startswith("```"):
            in_code = not in_code
            i += 1
            continue
        if in_code:
            story.append(Paragraph(inline(line), code))
        elif line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                row = [s.strip() for s in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-+:?", s) for s in row):
                    rows.append([Paragraph(inline(s), cell) for s in row])
                i += 1
            widths = [69, 42, 44, 34, 83, 52, 57, 42] if len(rows[0]) == 8 else None
            table = Table(rows, colWidths=widths, repeatRows=1, hAlign="LEFT", splitByRow=0)
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eaf0df")),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#182c2c")),
                ("GRID", (0, 0), (-1, -1), .35, colors.HexColor("#cdd7c7")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
            story.extend([table, Spacer(1, 7)])
            continue
        elif line.startswith("# "):
            story.append(Paragraph(inline(line[2:]), title))
        elif line.startswith("## "):
            story.append(Paragraph(inline(line[3:]), heading))
        else:
            story.append(Paragraph(inline(line), body))
        i += 1

    def footer(canvas, doc):
        canvas.setFont("Segoe", 8)
        canvas.setFillColor(colors.HexColor("#63766d"))
        canvas.drawString(36, 21, "Problem Solver | LogiX-VN | Lab 08")
        canvas.drawRightString(A4[0] - 36, 21, f"Trang {doc.page}")

    dest = OUT / (name + ".pdf")
    doc = SimpleDocTemplate(str(dest), pagesize=A4, leftMargin=36, rightMargin=36,
                            topMargin=32, bottomMargin=34,
                            title="Problem Solver - " + name, author="Problem Solver")
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    count = len(PdfReader(dest).pages)
    if count > budget:
        raise RuntimeError(f"{name}: {count} pages exceeds budget {budget}; shorten the Markdown report")
    print(f"{name}: {count}/{budget} A4 pages, {dest}")


def main():
    pdfmetrics.registerFont(TTFont("Segoe", "C:/Windows/Fonts/segoeui.ttf"))
    pdfmetrics.registerFont(TTFont("SegoeBold", "C:/Windows/Fonts/segoeuib.ttf"))
    pdfmetrics.registerFontFamily("Segoe", normal="Segoe", bold="SegoeBold", italic="Segoe", boldItalic="SegoeBold")
    OUT.mkdir(parents=True, exist_ok=True)
    export("group_report", 5)
    export("bonus_report", 2)


if __name__ == "__main__":
    main()
