---
name: recoup-catalog-report
description: Use when the user wants to turn a deal's dashboard, memos, and workpapers into a single shareable, emailable PDF report. Trigger on "build the PDF report", "export the report", "make a PDF I can email", "share this deal", "PDF version of the dashboard", "buyer-ready PDF", "IC-ready PDF", "financing pack PDF", or any request to package a catalog deal for distribution.
argument-hint: [deal-id] [--package ic-memo|seller-cleanup|financing-pack|post-close-admin]
allowed-tools: [Bash, Read, Write, Edit, Glob, Grep]
---

# Catalog Report (PDF)

The dashboard is the agent's interactive deliverable. The report is the
**file the customer attaches to an email.** Same trust contract, same
story — different medium and a different consumption pattern. A reader
who opens this PDF on their phone in a noisy boardroom should grasp the
headline in 10 seconds and have the receipts on the next page.

## When this skill runs

- After `/recoup-catalog-deal` finishes, when the user wants to
  share the deal externally.
- When the user explicitly asks for a PDF version of the dashboard, IC
  memo, seller cleanup report, financing pack, or post-close plan.
- When forwarding to a counterparty who will not open a local HTML file
  (lenders, counsel, IC voters, brokers).

## Output contract

- **Default file**: `deals/{deal-id}/REPORT.pdf`
- **Variant files** (when the user asks for more than one flavor):
  `deals/{deal-id}/reports/<package-type>.pdf` — e.g.
  `reports/ic-memo.pdf`, `reports/seller-cleanup.pdf`,
  `reports/financing-pack.pdf`, `reports/post-close-admin.pdf`.
- **Self-contained.** No external links the recipient must click to
  understand the headline. No "see the dashboard" — the report stands
  alone.
- **Print-safe.** No hover-only information. No interactive controls
  that won't function on paper. No tab content that's invisible by
  default. Every section the reader needs is laid out in reading order.
- **Reasonable size.** Aim for 2–4 MB. Hard ceiling 15 MB. If you blow
  past 15 MB you're embedding raw CSVs or full-resolution charts —
  fix it.

You have full creative freedom on layout, sectioning, conversion path,
typography, and depth. Use that freedom to fit the deal's story to a
medium the recipient can scan, sign, and forward.

## What the report MUST contain

These elements must be visible on a printed page (not behind a tab, not
in an appendix that gets dropped):

1. **Cover page** — deal name, workflow type (buy-side / seller-prep /
   financing / post-close), valuation date, "Confidential — Prepared
   by Recoup" footer. Page count or version stamp.
2. **One-page executive summary** — the headline a reader gets in 10
   seconds: value bracket, normalized NPS / NLS, top blocker, status
   (`ready` / `review_needed` / `blocked`). This page comes before
   anything else.
3. **Findings & blockers** — every open critical and high-severity
   finding. Not in an appendix; readable in body type.
4. **What you can do next** — the recommendations from
   `workpapers/recommendations.json` (or restructured by the agent when
   the deal calls for it). Concrete asks; concrete impact.
5. **Evidence trail / methodology footer** — at minimum, the workpaper
   files and evidence-ledger entries that backed each material claim.
   "Sources" on the last page is fine; absent is not.
6. **Page numbers and a per-page footer** with the deal ID, the date
   the report was generated, and `Confidential`. Print without these
   and the reader has no provenance when they hand it to counsel.

## What the report SHOULD contain (when the data exists)

- Value bracket table — downside / base / upside, from
  `workpapers/valuation-summary.json`.
- NPS bridge + NLS bridge — reported → normalized waterfalls.
- Provider mix — pie or bar, aggregated from `normalized/royalty-ledger.csv`.
- Top-N concentration — usually top 10 assets by 12-month royalties.
- Quarterly or monthly trend chart — print-friendly line or column.
- Open seller requests — from `findings/missing-files.md`.
- Methodology section — assumptions used (discount rate, decay, etc.)
  from `assumptions.yaml`.

If a workpaper does not exist, render a one-line placeholder ("Data
not yet computed — see findings/missing-files.md") rather than
silently dropping the section.

## What you CAN add (encouraged when the deal asks for it)

- A short narrative paragraph per section — what changed from reported
  to normalized, why, what's the implication.
- Per-finding sensitivity columns — how much each open finding could
  swing the bracket.
- Recoupment NPV branch trees.
- Foreign-society coverage matrices.
- A "what's not in scope" section that prevents over-reading the
  report.
- A signature line / acknowledgement page at the back when the user
  asks for one.

## Trust contract — non-negotiable

The PDF goes to people outside the agent's session — IC, lender,
counsel, broker. Every claim must be defensible.

**The trust rules are identical to the dashboard's.** Re-read the
`recoup-catalog-dashboard` skill's "Trust contract" section before
authoring fresh PDF content.

In short:

1. Any `$`-figure must match a value in `workpapers/*.json` /
   `normalized/royalty-ledger.csv` within 5%, OR
2. Be wrapped in HTML with `data-evidence="EV-NNN"` (resolves to an
   `evidence-ledger.json` entry), OR
3. Be wrapped in HTML with `data-derived="<reason>"` (explains the
   math the agent did on top of primary numbers).

When the report is **converted from `DASHBOARD.html`**, the dashboard
validator has already passed and the trust contract is inherited.
**No further validation needed for the same numbers.**

When the report is **authored as a separate print-styled HTML** before
conversion, run the dashboard validator against the print HTML first:

```bash
python3 scripts/validate-dashboard.py deals/{deal-id} \
  --dashboard-path deals/{deal-id}/.report-source.html
```

If the validator doesn't support `--dashboard-path`, temporarily copy
the print HTML over `DASHBOARD.html`, validate, then move it back —
or simply embed the report content INSIDE the dashboard via a
`@media print` stylesheet so a single validated source serves both
purposes. **Never skip validation when authoring fresh dollar-figures.**

## Source files to read

The report does not invent numbers. It pulls from the same source set
the dashboard reads:

| Path | What's in it |
| --- | --- |
| `deals/{deal-id}/DASHBOARD.html` | The validated interactive artifact. Convert this when possible. |
| `deals/{deal-id}/memos/ic-memo.md` (or seller / financing / post-close memo) | The longer narrative for the report's body. |
| `deals/{deal-id}/assumptions.yaml` | Deal name, workflow type, valuation date, currency, materiality thresholds. |
| `deals/{deal-id}/workpapers/valuation-summary.json` | Normalized NPS/NLS, scenario brackets. |
| `deals/{deal-id}/workpapers/nps-bridge.json` | Reported→normalized NPS waterfall. |
| `deals/{deal-id}/workpapers/nls-bridge.json` | Reported→normalized NLS waterfall. |
| `deals/{deal-id}/workpapers/concentration-analysis.json` | Top-N asset / provider / territory shares. |
| `deals/{deal-id}/workpapers/recommendations.json` | "What you can do next." |
| `deals/{deal-id}/findings/findings.json` | Every structured finding with severity and status. |
| `deals/{deal-id}/findings/missing-files.md` | Open requests for the seller. |
| `deals/{deal-id}/evidence-ledger.json` | Evidence entries cited via `data-evidence`. |

## Quality bar — print-specific

The dashboard's quality bar applies (hierarchy, restraint, typography,
accessibility), plus these print-only rules:

- **Page breaks.** Major sections start on a new page. No widow
  headings (a section title at the bottom of a page with body on the
  next). Use `page-break-before: always` on `<section>` boundaries.
- **Margins.** ≥ 0.5" on every side. Footer reserved.
- **Color contrast.** Body text ≥ 7:1 on white (prints darker than
  screens). Test by printing one page in grayscale — severity colors
  must still distinguish.
- **No interactivity stand-ins.** Replace tabs / sliders / accordions
  with the most useful static state (usually the base scenario, all
  sections expanded).
- **Charts.** Vector when possible (Chart.js → SVG export, or
  D3/Plotly render). If a chart is bitmap, ≥ 300 DPI. Charts get a
  printed caption — "Figure 1: …" — so a forwarded screenshot can be
  cited.
- **Tabular numbers** use a tabular-figure font feature so columns
  line up.
- **Header / footer on every body page**: deal ID • date •
  Confidential • page N of M.

## How to convert HTML to PDF

You pick the conversion path. Suggested order of preference (use what
works in the user's environment without forcing an install they don't
need):

### Path A — Headless Chrome (fastest, no Python deps)

Works out of the box on any machine with Chrome / Chromium / Edge
installed. Renders Chart.js, D3, Plotly, and modern CSS perfectly.

```bash
# macOS
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu --no-pdf-header-footer \
  --print-to-pdf="deals/{deal-id}/REPORT.pdf" \
  "file://$(pwd)/deals/{deal-id}/DASHBOARD.html"

# Linux
google-chrome --headless --disable-gpu --no-pdf-header-footer \
  --print-to-pdf="deals/{deal-id}/REPORT.pdf" \
  "file://$(pwd)/deals/{deal-id}/DASHBOARD.html"
```

Drawback: Chrome's headless PDF mode doesn't fully respect every
`@page` directive. If margins / page breaks come out wrong, jump to
Path B.

### Path B — Playwright (most reliable, one-time Python install)

```bash
pip3 install playwright
python3 -m playwright install chromium
```

Then a small Python script (write it inline, optionally saving it as
`render-report.py` in this skill's `scripts/` if the user wants to reuse it):

```python
from playwright.sync_api import sync_playwright
from pathlib import Path

deal_dir = Path("deals/{deal-id}")
src = deal_dir / "DASHBOARD.html"  # or .report-source.html
out = deal_dir / "REPORT.pdf"

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(src.absolute().as_uri())
    page.emulate_media(media="print")
    page.pdf(
        path=str(out),
        format="Letter",
        margin={"top": "0.6in", "bottom": "0.6in",
                "left": "0.5in", "right": "0.5in"},
        print_background=True,
        display_header_footer=True,
        header_template="<div></div>",
        footer_template=(
            '<div style="font-size:9px;width:100%;'
            'padding:0 0.5in;color:#666;display:flex;'
            'justify-content:space-between;">'
            '<span>{deal-id} · Confidential</span>'
            '<span class="pageNumber"></span>/'
            '<span class="totalPages"></span>'
            "</div>"
        ),
    )
    browser.close()
```

### Path C — WeasyPrint (pure Python, print-typography excellent, no JS)

```bash
pip3 install weasyprint
```

WeasyPrint does NOT execute JavaScript — Chart.js / D3 / Plotly won't
render. Only use this path if the report HTML's charts are
pre-rendered as inline SVG or PNG. Beautiful CSS print support
(`@page`, running headers, footnotes).

### Path D — ReportLab / fpdf2 (from-scratch PDF, maximum control)

Use when you want a layout that doesn't map naturally to HTML — heavy
typography, complex tables, or a deck-style report. Higher effort.
Only reach for this when Paths A–C give a poor result.

## Workflow

1. **Confirm the deal workspace is ready.** Read `assumptions.yaml`
   and confirm `DASHBOARD.html` exists and was validated this session
   (or run `python3 scripts/validate-dashboard.py deals/{deal-id}`
   first). Without a validated dashboard, the report has no source of
   truth.

2. **Decide the source HTML.** Two viable choices:
   - **Convert the existing dashboard directly** when it already
     prints cleanly (no hover-only info, no tabs hiding critical
     content, page-break-friendly).
   - **Author a print-styled source HTML** when the interactive
     dashboard wouldn't print well. Save it as
     `deals/{deal-id}/.report-source.html` and validate it the same
     way the dashboard is validated. Alternatively, add a
     `@media print` stylesheet inside `DASHBOARD.html` that
     restructures the page for print, then convert the dashboard
     itself.

3. **Pick a conversion path** (A → B → C → D in order of preference).
   For Path B you may need `pip3 install playwright && python3 -m
   playwright install chromium` first — ask the user before
   installing globally if you're not sure.

4. **Convert to `deals/{deal-id}/REPORT.pdf`.** If the user requested
   multiple flavors (IC, seller, financing, post-close), write each to
   `deals/{deal-id}/reports/<package-type>.pdf` in addition to the
   default `REPORT.pdf`.

5. **Verify the output.** At minimum:
   - The file exists, opens, and is between 100 KB and 15 MB.
   - Page count is reasonable (typical IC report: 6–18 pages; seller
     cleanup: 4–10; financing pack: 8–20).
   - First page is the cover; second page is the executive summary.
   - The cover, exec summary, findings, and recommendations sections
     are visually present (eyeball or `pdftotext` extract).

   Quick text-extract sanity check (if `pdftotext` from poppler is
   installed):

   ```bash
   pdftotext -layout deals/{deal-id}/REPORT.pdf - | head -50
   ```

   Look for the deal name, "Executive Summary", and at least one
   `$`-figure that matches the dashboard.

6. **Print one line** to the user: the file path, page count, and
   approximate size. Don't recap the whole deal — that's the report's
   job.

## What this skill is NOT

- Not a replacement for the dashboard. The interactive dashboard
  remains the analyst's working artifact; the PDF is the
  external-distribution artifact.
- Not a place to introduce numbers that aren't in the workpapers. If
  the agent needs a number that isn't already in the truth set, write
  it into a workpaper file first, then cite it in the report.
- Not a Word document. The user can convert PDF→DOCX themselves if
  counsel needs it; the deliverable from this skill is PDF.

## Final landing card the agent should print

```text
✅ Report exported.

  File:        deals/{deal-id}/REPORT.pdf
  Pages:       <n>
  Size:        <X.X MB>
  Source:      deals/{deal-id}/DASHBOARD.html (validated)
  Converted:   <Chrome headless | Playwright | WeasyPrint>

Open it locally to scan, then attach to the email.
```

The dashboard taught the agent how to render a deal's story. The
report skill is the same story, formatted for someone who's reading
it on a phone with no Wi-Fi.
