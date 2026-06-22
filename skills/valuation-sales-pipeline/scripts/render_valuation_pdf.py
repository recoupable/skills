#!/usr/bin/env python3
"""Render a clean catalog-valuation PDF for a sales lead.

Reads a lead JSON (see fixtures/example-lead.json for the shape) and writes:

  Page 1 — the headline the lead already saw: estimated value + range, key stats,
           and the per-release breakdown with album art ("what we measured").
  Page 2 — an honest reading of THAT data (concentration, dormant tail, range
           caveats) — grounded in page 1, no unverified claims.

Lead data can be assembled directly from the public Recoup APIs with
scripts/fetch_catalog.py (album art + streams), so no DOM scraping is needed.

Run it from the skill dir:
  python3 scripts/render_valuation_pdf.py --lead fixtures/example-lead.json --out ./out

Requires reportlab:  pip install reportlab --break-system-packages
"""
import argparse, json, os, sys, urllib.request
from io import BytesIO


def money(n):
    try:
        return "${:,.0f}".format(float(n))
    except (TypeError, ValueError):
        return str(n or "—")


def hstreams(n):
    try:
        n = float(n)
    except (TypeError, ValueError):
        return "—"
    if n >= 1_000_000:
        return "{:.1f}M".format(n / 1_000_000)
    if n >= 1_000:
        return "{:.0f}K".format(n / 1_000)
    return "{:.0f}".format(n)


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
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, CondPageBreak,
            KeepTogether,
        )
    except ImportError:
        sys.exit("reportlab not installed. Run: pip install reportlab --break-system-packages")

    def cover(url, pt=34):
        """Download an album-art URL into a small reportlab Image (or '' on failure)."""
        if not url:
            return ""
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as r:
                img = Image(BytesIO(r.read()))
            img.drawWidth = pt
            img.drawHeight = pt
            return img
        except Exception:
            return ""

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
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], textColor=navy, fontSize=16, spaceAfter=8)
    sub = ParagraphStyle("sub", parent=styles["Normal"], textColor=colors.grey, fontSize=11, spaceAfter=14)
    body = ParagraphStyle("body", parent=styles["Normal"], fontSize=10.5, leading=15, spaceAfter=8)
    small = ParagraphStyle("small", parent=styles["Normal"], fontSize=9, leading=11)
    cellbw = ParagraphStyle("cellbw", parent=styles["Normal"], textColor=colors.white, fontSize=10, leading=13)
    big = ParagraphStyle("big", parent=styles["Normal"], textColor=colors.white, fontSize=22, leading=24)

    doc = SimpleDocTemplate(path, pagesize=LETTER, topMargin=0.7 * inch,
                            bottomMargin=0.7 * inch, leftMargin=0.8 * inch, rightMargin=0.8 * inch)
    story = []
    story.append(Paragraph(f"{artist} — Catalog Valuation", h1))
    story.append(Paragraph("Recoup · measured live from public streaming data", sub))

    # Admin reference (owner email + account ids) — for easy lookup by admins
    acct = lead.get("account") or {}
    ref = []
    if acct.get("owner_email"):
        ref.append("owner " + acct["owner_email"])
    if acct.get("owner_account_id"):
        ref.append("account " + acct["owner_account_id"])
    if ref:
        story.append(Paragraph("Admin reference — " + "  ·  ".join(ref),
                               ParagraphStyle("admin", parent=styles["Normal"], fontSize=8,
                                              textColor=colors.grey, spaceAfter=10)))

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

    # Key stats (only rows that are present)
    rows = [["Lifetime streams", hstreams(lead.get("lifetime_streams"))],
            ["Followers", thousands(lead.get("follower_count"))]]
    if lead.get("tracks_measured") is not None:
        rows.append(["Tracks measured", thousands(lead.get("tracks_measured"))])
    if lead.get("releases_measured") is not None:
        rows.append(["Releases measured", thousands(lead.get("releases_measured"))])
    rows += [["Relationship", lead.get("relationship") or "—"],
             ["Valued", lead.get("valued_at") or "—"]]
    stats = Table(rows, colWidths=[2.3 * inch, 4.6 * inch])
    stats.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 10.5),
        ("TEXTCOLOR", (0, 0), (0, -1), navy),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("LINEBELOW", (0, 0), (-1, -2), 0.4, colors.HexColor("#dddddd")),
        ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(stats)
    story.append(Spacer(1, 16))

    # Per-release breakdown ("what we measured") with album art.
    # Include the Value column only if any release carries a dollar value.
    releases = lead.get("releases") or []
    has_value = any(r.get("value") is not None for r in releases)
    if releases:
        story.append(Paragraph("What we measured", body))
        cols = ["", "Release", "Year", "Tracks"] + (["Value"] if has_value else []) + ["Streams"]
        head = [Paragraph(t, cellbw) for t in cols]
        data = [head]
        shown = releases[:7]
        for r in shown:
            row = [cover(r.get("image"), 30), (r.get("name") or "—")[:34],
                   str(r.get("year") or "—"),
                   str(r.get("tracks") if r.get("tracks") is not None else "—")]
            if has_value:
                row.append(money(r.get("value")) if r.get("value") is not None else "—")
            row.append(hstreams(r.get("streams")))
            data.append(row)
        total_rel = lead.get("releases_measured") or len(releases)
        if total_rel > len(shown):
            data.append(["", f"+ {total_rel - len(shown)} more releases (long tail)"] + [""] * (len(cols) - 2))
        widths = [0.55 * inch, 2.45 * inch, 0.6 * inch, 0.7 * inch] + ([1.0 * inch] if has_value else []) + [0.9 * inch]
        tbl = Table(data, colWidths=widths)
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), navy),
            ("FONTSIZE", (0, 1), (-1, -1), 9.5),
            ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LINEBELOW", (0, 1), (-1, -2), 0.3, colors.HexColor("#eeeeee")),
            ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(tbl)
        story.append(Spacer(1, 6))
        story.append(Paragraph(
            "Top releases by streams; full catalog in the appendix. Measured live from public "
            "Spotify play counts.",
            ParagraphStyle("note", parent=styles["Normal"], fontSize=8.5, textColor=colors.grey)))

    # Artist channels — verified socials table (last block on page 1)
    socials = lead.get("socials")
    if isinstance(socials, list) and socials:
        shead = [Paragraph(t, cellbw) for t in ("Platform", "Handle", "Followers", "Bio")]
        sdata = [shead]
        for s in socials:
            handle = s.get("handle") or s.get("platform") or "—"
            url = s.get("url")
            hcell = Paragraph(
                f'<a href="{url}" color="#0b1f3a"><u>{handle}</u></a>' if url else handle, small)
            sdata.append([s.get("platform") or "—", hcell, thousands(s.get("followers")),
                          Paragraph(s.get("bio") or "—", small)])
        stbl = Table(sdata, colWidths=[1.1 * inch, 1.65 * inch, 0.85 * inch, 3.0 * inch])
        stbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), navy),
            ("FONTSIZE", (0, 1), (-1, -1), 9),
            ("ALIGN", (2, 1), (2, -1), "RIGHT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LINEBELOW", (0, 1), (-1, -2), 0.3, colors.HexColor("#eeeeee")),
            ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        # KeepTogether so the heading + table never split across a page boundary.
        story.append(Spacer(1, 12))
        story.append(KeepTogether([Paragraph("Artist channels", body), Spacer(1, 4), stbl]))

    # ---- Page 2: an honest reading of THIS catalog's data ----
    # CondPageBreak (not a hard PageBreak) avoids a blank page when page 1 is already full.
    story.append(CondPageBreak(6.5 * inch))
    story.append(Paragraph("Reading your result", h2))
    story.append(Paragraph(
        f"Everything on the previous page is measured live from public play counts — the same "
        f"figures you saw when you ran {artist}. A few honest reads from that data:", body))

    # Concentration — by value if present, else by streams.
    try:
        if releases:
            key = "value" if has_value else "streams"
            top = max(releases, key=lambda r: float(r.get(key) or 0))
            tv = float(top.get(key) or 0)
            if has_value and central:
                denom = float(central)
            elif not has_value and lead.get("lifetime_streams"):
                denom = float(lead.get("lifetime_streams"))
            else:
                denom = sum(float(r.get(key) or 0) for r in releases)
            pct = round(100 * tv / denom) if denom else 0
            unit = "estimated value" if has_value else "streams"
            if pct >= 40:
                story.append(Paragraph(
                    f"<b>It rests on one release.</b> ~{pct}% of the catalog's {unit} comes from "
                    f"“{top.get('name')}.” That makes the value real but concentrated — a catalog "
                    f"spread across more songs is steadier to own and tends to be valued higher.", body))
    except (TypeError, ValueError):
        pass

    # Analyst-supplied verified observations (case-specific, e.g. collab splits, audience gap)
    for note in (lead.get("reading_notes") or []):
        story.append(Paragraph(note, body))

    # Dormant tail
    dormant = lead.get("dormant_releases")
    rm = lead.get("releases_measured")
    if dormant and rm:
        story.append(Paragraph(
            f"<b>{dormant} of {rm} releases show little or no measurable public streaming.</b> "
            f"Some may be genuinely dormant; others may simply not be surfacing the way they should. "
            f"Either way, it's worth knowing which is which.", body))

    # Range honesty
    if low and high:
        story.append(Paragraph(
            f"<b>The band is wide ({money(low)}–{money(high)}) on purpose.</b> It's modeled from "
            f"public streaming alone and is master-side only — publishing isn't included. A real "
            f"royalty statement would narrow it considerably.", body))

    # Sincere close
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        f"We built this to be accurate to what's public, not to flatter — which is why we'd rather "
        f"show you the concentration and the gaps than hide them. If it matches what you already know "
        f"about {artist}, the honest next step is to read it against your actual statements; that's "
        f"where the range tightens and where anything uncollected would show up. Happy to do that "
        f"read with you whenever it's useful.", body))

    # Roster CTA — natural next step: extend the same baseline to the rest of the roster
    roster = lead.get("roster") or {}
    rartists = roster.get("artists") or []
    if rartists:
        label = (roster.get("label") or "").strip()
        cta_block = [Paragraph(f"Extend the analysis — the {label} roster".strip(), h2)]
        if roster.get("note"):
            cta_block.append(Paragraph(roster["note"], body))
        rdata = [[Paragraph(t, cellbw) for t in ("Artist", "Spotify followers")]]
        for a in rartists:
            rdata.append([a.get("name", "—"), thousands(a.get("followers"))])
        if roster.get("more_count"):
            rdata.append([Paragraph(f"<i>+ {roster['more_count']} more on the roster</i>", small), ""])
        rtbl = Table(rdata, colWidths=[3.4 * inch, 1.6 * inch])
        rtbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), navy),
            ("FONTSIZE", (0, 1), (-1, -1), 9.5),
            ("ALIGN", (1, 1), (1, -1), "RIGHT"),
            ("LINEBELOW", (0, 1), (-1, -2), 0.3, colors.HexColor("#eeeeee")),
            ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        cta_block += [Spacer(1, 6), rtbl]
        if roster.get("cta"):
            cta_block += [Spacer(1, 6), Paragraph("<b>" + roster["cta"] + "</b>", body)]
        story.append(Spacer(1, 14))
        story.append(KeepTogether(cta_block))

    story.append(Spacer(1, 10))
    story.append(Paragraph("How this is calculated", body))
    story.append(Paragraph(
        "Value is modeled as <b>sustainable annual Net Label Share (NLS) × a 10–16× market "
        "multiple</b>. NLS is what the owner keeps after artist royalties, distribution fees, and "
        "reserves — not headline streaming revenue. Annual run-rate is taken from the catalog's "
        "lifetime average; other platforms are approximated as a labeled share of Spotify. "
        "Directional estimate from public data, not an appraisal.", body))

    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "<i>Prepared by Recoup. Estimate only — not financial advice or an offer.</i>",
        ParagraphStyle("foot", parent=styles["Normal"], fontSize=8.5, textColor=colors.grey)))

    # ---- Appendix: the full catalog measured (matches the live tool's full list) ----
    if releases:
        story.append(PageBreak())
        total_rel = lead.get("releases_measured") or len(releases)
        story.append(Paragraph("Appendix — full catalog measured", h2))
        story.append(Paragraph(
            f"All {total_rel} releases measured live from public Spotify play counts. Streams are "
            f"platform-displayed counts; per-release value is modeled at the catalog level (see page 2). "
            f"Page 1 shows the top releases by streams; the complete set is below.", body))
        ahead = [Paragraph(t, cellbw) for t in ("#", "", "Release", "Year", "Tracks", "Streams")]
        adata = [ahead]
        for i, r in enumerate(releases, 1):
            adata.append([str(i), cover(r.get("image"), 22), (r.get("name") or "—")[:46],
                          str(r.get("year") or "—"),
                          str(r.get("tracks") if r.get("tracks") is not None else "—"),
                          hstreams(r.get("streams"))])
        atbl = Table(adata, colWidths=[0.3 * inch, 0.4 * inch, 3.25 * inch, 0.6 * inch, 0.7 * inch, 1.05 * inch], repeatRows=1)
        atbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), navy),
            ("FONTSIZE", (0, 1), (-1, -1), 9),
            ("ALIGN", (0, 0), (0, -1), "RIGHT"),
            ("ALIGN", (3, 0), (-1, -1), "RIGHT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LINEBELOW", (0, 1), (-1, -2), 0.25, colors.HexColor("#eeeeee")),
            ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(atbl)

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
