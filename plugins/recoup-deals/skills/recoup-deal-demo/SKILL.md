---
name: recoup-deal-demo
description: Run /recoup-deal-start end-to-end on the bundled synthetic catalog so a first-time user can see an executive dashboard within ~60 seconds. Use whenever the user types `/recoup-deal-demo`, says "show me the demo", "run the catalog demo", "let me see what this plugin produces", or asks for a sample / dry-run catalog deal against bundled data.
allowed-tools: [Bash, Read, Write, Edit, Glob, Grep, AskUserQuestion, Task]
---

# Deal Demo

Use this skill on first install to confirm the plugin works end-to-end
on a known-good data room before pointing it at the customer's real
files.

## What it does

1. Creates `deals/demo-catalog/` and copies
   `fixtures/demo-data-room/source/` into
   `deals/demo-catalog/source/` verbatim.
2. Seeds `deals/demo-catalog/assumptions.yaml` with:
   - `deal.deal_id: demo-catalog`
   - `deal.deal_name: "Mari Vega Catalog (demo)"`
   - `deal.workflow_type: buy-side`
   - `deal.valuation_date: 2025-01-01`
   - `materiality.concentration_threshold_percent: 25` (lower than the
     default 40 so the demo's ~35% top-1 concentration trips the
     threshold and the auto-emitted finding shows up).
3. Runs the full `/recoup-deal-start` flow against the demo workspace:
   kickoff → ingest → analysis → modeling → agent-authored dashboard →
   IC memo.
4. Ends with the same landing card as `/recoup-deal-start`, pointed at
   `deals/demo-catalog/DASHBOARD.html`.

## Steps the agent must execute

```bash
# 1. Scaffold the demo workspace from the bundled template + seed source.
mkdir -p deals/demo-catalog
cp -r templates/deal-workspace/. deals/demo-catalog/
cp -r fixtures/demo-data-room/source deals/demo-catalog/source

# 2. Move findings template into place (the template ships under
#    templates/deal-workspace/findings.json but the workspace expects
#    findings/findings.json).
mkdir -p deals/demo-catalog/findings
mv deals/demo-catalog/findings.json deals/demo-catalog/findings/findings.json
mv deals/demo-catalog/missing-files.md deals/demo-catalog/findings/missing-files.md

# 3. Seed assumptions.yaml. Overwrite the template values with demo-specific values.
cat > deals/demo-catalog/assumptions.yaml <<'YAML'
deal:
  deal_id: demo-catalog
  deal_name: Mari Vega Catalog (demo)
  workflow_type: buy-side
  buyer_or_client: Demo Buyer LLC
  valuation_date: "2025-01-01"
  currency: USD

scope:
  rights_included:
    - publishing
    - masters
    - neighboring
  territories: []
  excluded_assets: []
  preliminary_or_full: preliminary

valuation:
  discount_rate: 0.10
  publishing_multiple_low: 7
  publishing_multiple_high: 10
  master_multiple_low: 4
  master_multiple_high: 6
  terminal_growth_or_decay: -0.10

normalization:
  sync_treatment: exclude_one_time
  pro_bonus_treatment: separate_and_haircut
  reserve_treatment: review_required
  recoupment_treatment: model_when_available
  fx_source: none

materiality:
  revenue_threshold: 5000
  concentration_threshold_percent: 25
  unsupported_income_threshold_percent: 5

notes:
  - "Demo run via /recoup-deal-demo. Numbers are synthetic. Not a real opportunity."
YAML
```

After scaffolding, run the `recoup-deal-start` skill end-to-end exactly
as that skill specifies. The demo data is
deliberately shaped to produce these AHA moments without intervention:

- **Ingest coverage line**: roughly "5 of 8 statement files contributed
  financial data; 2 require manual review" (rights documents are .txt
  placeholders that the manifest correctly tags `manual_review`).
- **Concentration finding**: top-1 (Bright Lights) ≈ 35% of revenue,
  trips the 25% threshold, auto-emits `CONC-AUTO-001` finding.
- **Bright Lights ASCAP bonus row**: the agent's royalty audit should
  flag the $1,500 audio-feature premium as non-recurring.
- **Bright Lights split-sheet conflict**: the rights review should
  surface that the seller's composition list (Atlas Songs admins
  Jordan Key's 25%) contradicts the actual split sheet (Jordan Key
  self-published).
- **Slow Lightning sample**: composition-list note flags an uncleared
  6-second interpolation; rights review should surface it.
- **Long Way Home missing split sheet**: rights review should add to
  the missing-files tracker.

## Final landing card

End with `/recoup-deal-start`'s landing card, pointed at the demo
workspace:

```text
✅ Demo run complete.

This was a synthetic catalog. Numbers are not real.

Headline:
  Normalized NPS run-rate $X.
  Normalized NLS run-rate $Y.
  Preliminary value bracket: $LOW – $HIGH.
  N material blockers · K high-severity items.

Open this first:
  deals/demo-catalog/DASHBOARD.html

When you're ready for your real catalog:
  /recoup-deal-start
```
