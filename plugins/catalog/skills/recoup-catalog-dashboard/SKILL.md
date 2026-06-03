---
name: recoup-catalog-dashboard
description: Use when building, refreshing, or improving the customer-facing executive dashboard (DASHBOARD.html) for a music catalog deal. Trigger on "build the dashboard", "render the dashboard", "create the executive dashboard", "refresh DASHBOARD.html", or any phase of /recoup-catalog-deal that produces the customer's read-the-deal artifact.
argument-hint: [deal-id]
allowed-tools: [Bash, Read, Write, Edit, Glob, Grep]
---

# Catalog Dashboard

The dashboard is the deal's WOW moment. It is the single artifact the
customer opens when they want to know what you found and what to do
next. Treat it as the deliverable.

## Output contract

- **Single file**: `deals/{deal-id}/DASHBOARD.html`
- **Self-contained**: external resources only from the CDN allowlist
  (Chart.js, D3, Plotly, Tailwind via cdn.jsdelivr.net /
  cdnjs.cloudflare.com / unpkg.com). No other `<script src>`. No
  `<iframe>`. No `<object>`. No `<embed>`.
- **Verified by `scripts/validate-dashboard.py`** before the run can
  finish. The validator runs after you write the file. Read its output
  and fix issues before claiming completion.

You have full creative freedom on layout, chart types, interaction
patterns, narrative flow, and depth. Use that freedom to tell the
catalog's specific story. Different deals deserve different shapes.

## What the dashboard MUST contain

These markers must be present somewhere on the page. The validator
checks for them via text search. Beyond these requirements, the
structure is yours.

1. **Status indicator** — `ready`, `review_needed`, or `blocked`,
   matching the open findings tally.
2. **KPI section** — at least normalized NPS or NLS. Top-1
   concentration when it's material. Open finding counts.
3. **Findings/blockers section** — every open critical or high finding
   visible somewhere on the page (collapsed sections are fine; hidden
   tabs are fine; absent is not).
4. **Evidence trail** — every material claim either matches a value in
   a workpaper JSON file (within 5% rounding tolerance) or carries a
   `data-evidence`, `data-source`, or `data-derived` attribute. See
   "Trust contract" below.
5. **"What you can do next"** — recommendations section pointing at
   what would tighten the bracket. Read
   `workpapers/recommendations.json` if it exists; that's a starting
   point you can restructure freely or override when the deal's story
   calls for different framing.

## What the dashboard SHOULD contain (when the data exists)

- Value bracket — downside / base / upside from
  `workpapers/valuation-summary.json#scenarios`.
- NPS bridge — from `workpapers/nps-bridge.json`.
- NLS bridge — from `workpapers/nls-bridge.json`.
- Provider mix — aggregated from `normalized/royalty-ledger.csv`.
- Top-N catalog assets — from `workpapers/concentration-analysis.json`
  or aggregated from the ledger.
- Quarterly or monthly trend — aggregated from the ledger.
- Open seller requests — from `findings/missing-files.md`.

If a workpaper does not exist, render a placeholder that says so, or
leave the section out and explain in the narrative.

## What you CAN add (encouraged when the deal asks for it)

- Tabs to organize a complex story (e.g., publishing tab, masters tab,
  neighboring rights tab).
- Scenario sliders or toggles (e.g., toggle Bright Lights decay curves;
  flip recoupment branches).
- Side-by-side comparisons (reported vs normalized; pre-recoupment vs
  post-recoupment).
- Decay sweeps with multiple curves on one chart.
- Per-finding sensitivity tables ranked by valuation swing.
- Recoupment NPV branch trees.
- Foreign-society coverage matrices.
- Embedded narrative paragraphs that tell the catalog's story.
- Drill-down accordions for the curious analyst.
- A "data sources" footer linking each section to its workpaper file.
- Anything else the deal's specific shape calls for.

## Trust contract — non-negotiable

The dashboard goes to a customer. They might forward it to an IC, a
lender, or counsel. Every number on the page has to be defensible.

### Three ways a `$`-figure on the page is considered trustworthy

1. **Matches a workpaper value within 5%.** The validator builds a
   "truth set" from the source files (royalty-ledger sums, valuation-
   summary scenarios, bridge amounts and running totals, concentration
   top-10, etc.). If a `$`-claim on the page is within 5% of any
   value in the truth set, it's accepted automatically.

2. **Lives inside an element with `data-evidence="EV-NNN"`** that
   resolves to a real entry in `evidence-ledger.json`. Use this for
   numbers that came directly from a source file (e.g., a contract,
   a single ledger row).

   ```html
   <div class="kpi" data-evidence="EV-007">
     <label>Atlas admin overlay</label>
     <div class="v">$7,254</div>
   </div>
   ```

3. **Lives inside an element with `data-derived="<reason>"`.** Use
   this when the dashboard derives a value from primary numbers (a
   sum, a difference, a probability-weighted NPV) that is NOT in any
   workpaper. The reason text becomes part of the audit trail.

   ```html
   <p data-derived="weighted by 30/25/25/20 branch probabilities">
     Weighted NLS NPV is <strong>$113,930</strong>.
   </p>
   ```

You may also mark whole sections with `data-source="workpapers/path.json"`
if every claim inside ties back to that file.

### What the validator will reject

- A `$`-figure on the page that does not match the truth set AND has
  no `data-evidence` / `data-source` / `data-derived` ancestor.
- An external `<script src>` not in the CDN allowlist.
- `<iframe>`, `<object>`, `<embed>` tags.
- `eval(`, `Function(`, `document.write(` in inline JS.
- Files smaller than 5 KB (likely empty/broken) or larger than 5 MB
  (likely accidentally embedded a CSV in the HTML).
- Files that don't parse as HTML.
- A page missing any of the five required markers above.

If the validator returns errors, **read them**, fix the dashboard,
and rebuild. Do not claim the run is complete until the validator
passes.

## Source files to read

| Path | What's in it |
| --- | --- |
| `deals/{deal-id}/assumptions.yaml` | `deal.deal_name`, workflow type, valuation_date, currency, materiality thresholds. |
| `deals/{deal-id}/normalized/royalty-ledger.csv` | Every normalized statement line. Aggregate freely. |
| `deals/{deal-id}/findings/findings.json` | Every structured finding with severity and status. |
| `deals/{deal-id}/findings/missing-files.md` | Open requests for the seller. |
| `deals/{deal-id}/evidence-ledger.json` | Evidence entries to cite via `data-evidence`. |
| `deals/{deal-id}/workpapers/valuation-summary.json` | Normalized NPS/NLS, scenario brackets. |
| `deals/{deal-id}/workpapers/nps-bridge.json` | Reported→normalized NPS waterfall. |
| `deals/{deal-id}/workpapers/nls-bridge.json` | Reported→normalized NLS waterfall. |
| `deals/{deal-id}/workpapers/concentration-analysis.json` | Top-N asset, provider, territory shares. |
| `deals/{deal-id}/workpapers/ingest-coverage.json` | "X of Y files contributed financial data" line. |
| `deals/{deal-id}/workpapers/recommendations.json` | Optional structured starting point for the recommendations section. |

Any other JSON under `workpapers/` (recoupment NPV, decay scenarios,
sensitivity tables, custom analyses) is fair game. Read them if they
help tell the story; ignore them if they don't.

## Quality bar

The dashboard is a customer deliverable, not a debug dump. Apply a
designer's eye:

- **Hierarchy.** The first thing the customer sees should be the
  headline — value bracket, status, top blocker. Detail comes after.
- **Restraint.** Neutral palette (slate, dark amber for warnings, no
  saturated brand colors). Lots of whitespace. One purposeful chart
  per question, not five charts that all show the same thing.
- **Typography.** System sans-serif stack. No more than two type
  weights. Numbers in a tabular figure feature when alignment matters.
- **Accessibility.** Semantic HTML (`<section>`, `<header>`,
  `<nav>`). `aria-label` on charts. Color contrast ≥ 4.5:1 for body
  text. Don't rely on color alone to convey severity — pair with
  shape, label, or icon.
- **Responsiveness.** Works on a 1280px laptop and on a 600px phone.
  Tables scroll horizontally rather than overflowing.
- **Self-explanatory.** A reader who has never seen the catalog should
  understand the headline within 10 seconds of opening the page.

## Workflow

1. Read the source files above. Assemble the catalog's story in your
   head before you write HTML — what's the headline? What's the
   tension? What does the user need to do next?
2. Write `deals/{deal-id}/DASHBOARD.html` as a single self-contained
   page. Use Chart.js, D3, or whatever fits.
3. Run `python3 scripts/validate-dashboard.py deals/{deal-id}`.
4. If the validator returns errors, fix and re-run. Do not skip.
5. The Stop hook will block the agent from finishing if `DASHBOARD.html`
   does not exist or the validator does not pass.

## What this skill replaces

The plugin previously rendered the dashboard via a deterministic
Python script with a fixed schema. That script no longer exists. The
agent owns the dashboard. The script that remains
(`validate-dashboard.py`) only checks the agent's output for
truthfulness and safety — it never renders.

This is the agent's deliverable. Make it worth opening.
