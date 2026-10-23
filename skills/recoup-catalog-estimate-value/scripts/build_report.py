#!/usr/bin/env python3
"""Render a v2 public estimate with the same bounded scope as its JSON workpaper.
Usage: python3 scripts/build_report.py --estimate /private/work/estimate.json --out /private/work
"""
import argparse
import json
import re
import sys
from pathlib import Path
from xml.sax.saxutils import escape


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--estimate", required=True)
    parser.add_argument("--out", default=".")
    args = parser.parse_args()
    result = json.loads(Path(args.estimate).read_text())
    if result.get("schema_version") != "public-estimate/2":
        parser.error("Regenerate this estimate with the current helper; legacy reports lack bounded coverage")
    try:
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    except ImportError:
        sys.exit("build_report.py needs reportlab — pip3 install reportlab")
    styles = getSampleStyleSheet()
    model, config = result["model"], result["assumptions"]
    story = []
    def paragraph(value, style="BodyText"):
        story.append(Paragraph(escape(str(value)), styles[style]))
        story.append(Spacer(1, 8))
    paragraph(result["asset"] + " — Public-data scenario", "Title")
    paragraph(f"As of {result['as_of']} · {model['status']} · {model['scope']}")
    paragraph(f"Annual measurement coverage: {model['covered_tracks']}/{model['input_tracks']} supplied recordings. Population complete: {model['population_complete']}.")
    paragraph(f"Currency: {model['currency']}. Assumptions: {config['assumption_status']}. Controlled-interest assumption: {config['controlled_share']:.0%}.")
    money = lambda value: "Unknown" if value is None else f"{model['currency']} {value:,.2f}"
    rows = [["Scenario", "Modeled gross/year", "Modeled net/year", "Indicative value"]]
    for band in ("low", "central", "high"):
        rows.append([band, money(model["annual_gross"][band]), money(model["annual_nls"][band]), money(model["value"][band])])
    table = Table(rows, repeatRows=1)
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eeeeee")), ("FONTSIZE", (0, 0), (-1, -1), 9), ("BOTTOMPADDING", (0, 0), (-1, -1), 8)]))
    story.extend([table, Spacer(1, 12)])
    paragraph("Method and limitations", "Heading2")
    paragraph("Annual Spotify count × assumed master rate × (1 + other-platform scenario) × net factor × controlled-interest assumption × multiple. The net factor includes modeled deductions once.")
    for limitation in model["limitations"]:
        paragraph(limitation)
    paragraph("Unknown recording IDs: " + ", ".join(str(x) for x in model["unknown_track_ids"]))
    paragraph("Assumption sources/rationale: " + json.dumps(config.get("assumption_sources", []), ensure_ascii=False))
    paragraph("The accompanying estimate.json preserves observations, source dates, complete assumptions and measurement provenance. No public metadata establishes ownership; no output is a bank receipt.")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^A-Za-z0-9]+", "-", result["asset"]).strip("-") or "catalog"
    path = out / f"{slug}-public-estimate.pdf"
    SimpleDocTemplate(str(path), title=result["asset"] + " public estimate", author="Recoup").build(story)
    print(path)


if __name__ == "__main__":
    main()
