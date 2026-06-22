#!/usr/bin/env python3
"""Render a clean one-page catalog-valuation PDF for a sales lead.

Reads a lead JSON (see fixtures/example-lead.json for the shape) and writes a
branded one-pager: artist, estimated catalog value + range, key stats, the
value model in plain English, and next steps. Hand this to the lead with the
first outreach email.

This script ships alongside the skill in scripts/. Run it from the skill dir:

  python3 scripts/render_valuation_pdf.py --lead fixtures/example-lead.json --out ./out

Requires reportlab:  pip install reportlab --break-system-packages
"""
import argparse, json, os, sys


def money(n):
    try:
        return "${:,.0f}".format(float(n))
    except (TypeError, ValueError):
        return str(n or "—")


def millions(n):
    try:
        return "{:.1f}M".format(float(n) / 1_000_000)
    except (TypeError, ValueError):
        return "—"


def thousands(n):
    try:
        return "{:,.0f}".format(float(n))
    except (TypeError, ValueError):
        return "—"


def build(lead, out_dir):
    try:
        from reportlab.lib.pagesizes import LETTER
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        )
    except ImportError:
        sys.exit("reportlab not installed. Run: pip install reportlab --break-system-packages")

    artist = lead.get("artist") or "Unknown Artist"
    central = lead.get("est_catalog_value")
    low = lead.get("value_low")
    high = lead.get("value_high")

    os.makedirs(out_dir, exist_ok=True)
    safe = "".join(c if c.isalnum() else "-" for c in artist).strip("-") or "artist"
    path = os.path.join(out_dir, f"{safe}-valuation.pdf")

    styles = getSampleStyleSheet()
    navy = colors.HexColor("#0b1f3a")
    h1 = ParagraphStyle("h1", parent=styles["Title"], textColor=navy, fontSize=24, spaceAfter=2)
    sub = ParagraphStyle("sub", parent=styles["Normal"], textColor=colors.grey, fontSize=11, spaceAfter=14)
    body = ParagraphStyle("body", parent=styles["Normal"], fontSize=10.5, leading=15, spaceAfter=8)
    cellbw = ParagraphStyle("cellbw", parent=styles["Normal"], textColor=colors.white, fontSize=10, leading=13)
    big = ParagraphStyle("big", parent=styles["Normal"], textColor=colors.white, fontSize=22, leading=24)

    doc = SimpleDocTemplate(path, pagesize=LETTER, topMargin=0.7 * inch,
                            bottomMargin=0.7 * inch, leftMargin=0.8 * inch, rightMargin=0.8 * inch)
    story = []
    story.append(Paragraph(f"{artist} — Catalog Valuation", h1))
    story.append(Paragraph("Recoup · estimated from public streaming data", sub))

    # Headline value band
    band = Table([[Paragraph("Estimated catalog value", cellbw)],
                  [Paragraph(money(central), big)],
                  [Paragraph(f"Range {money(low)} – {money(high)}" if low and high else "", cellbw)]],
                 colWidths=[6.9 * inch])
    band.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), navy),
        ("LEFTPADDING", (0, 0), (-1, -1), 16), ("RIGHTPADDING", (0, 0), (-1, -1), 16),
        ("TOPPADDING", (0, 0), (-1, 0), 10), ("BOTTOMPADDING", (0, -1), (-1, -1), 12),
    ]))
    story.append(band)
    story.append(Spacer(1, 16))

    # Key stats
    stats = Table([
        ["Lifetime streams", millions(lead.get("lifetime_streams"))],
        ["Followers", thousands(lead.get("follower_count"))],
        ["Relationship", lead.get("relationship") or "—"],
        ["Valued", lead.get("valued_at") or "—"],
    ], colWidths=[2.3 * inch, 4.6 * inch])
    stats.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 10.5),
        ("TEXTCOLOR", (0, 0), (0, -1), navy),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("LINEBELOW", (0, 0), (-1, -2), 0.4, colors.HexColor("#dddddd")),
        ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(stats)
    story.append(Spacer(1, 16))

    story.append(Paragraph("How this is calculated", body))
    story.append(Paragraph(
        "Value is modeled as <b>sustainable annual Net Label Share (NLS) × a market "
        "multiple</b> (typically 8–12×). NLS is what the owner keeps after artist royalties, "
        "distribution fees, and reserves — not headline streaming revenue. This is a "
        "directional, public-data estimate of the master/recording side; publishing is "
        "separate and additive.", body))

    story.append(Spacer(1, 6))
    story.append(Paragraph("How Recoup grows this number", body))
    story.append(Paragraph(
        "• <b>Recover</b> uncollected royalties (neighboring rights, unmatched mechanicals, "
        "YouTube Content ID).<br/>"
        "• <b>Grow</b> monthly streams via playlist-gap analysis and audience expansion.<br/>"
        "• <b>Document</b> a clean, buyer-ready baseline so the catalog re-rates to a higher "
        "multiple — and watch the value climb month over month.", body))

    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "<i>Prepared by Recoup. Estimate only — not financial advice or an offer.</i>",
        ParagraphStyle("foot", parent=styles["Normal"], fontSize=8.5, textColor=colors.grey)))

    doc.build(story)
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lead", required=True, help="path to lead JSON")
    ap.add_argument("--out", default="./out", help="output directory")
    args = ap.parse_args()
    with open(args.lead) as f:
        lead = json.load(f)
    path = build(lead, args.out)
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
