# Red flags

Use this reference to classify diligence issues by severity and valuation
impact. Red flags do not always kill a deal. They force a decision: cure,
haircut, escrow, holdback, or walk away.

## Severity levels

| Severity | Meaning | Usual treatment |
| --- | --- | --- |
| Critical | Blocks transferability, cash-flow support, or final valuation. | Stop, cure, or exclude affected assets. |
| High | Material value or liability risk. | Haircut, escrow, holdback, or counsel review. |
| Medium | Important uncertainty that affects confidence. | Model sensitivity or require follow-up. |
| Low | Cleanup issue with limited value impact. | Track in post-close or seller-prep list. |

## Severity calibration

Anchor severity in measurable factors before assigning a tier. Pick the
worst-applicable factor; bump severity one tier when two or more factors
land in the same column. `revenue_threshold` refers to
`materiality.revenue_threshold` in `assumptions.yaml`.

| Factor | Low | Medium | High | Critical |
| --- | --- | --- | --- | --- |
| Cumulative $ at risk vs `revenue_threshold` | <1× | 1×–10× | 10×–100× | >100× |
| Duration of mispayment or exposure | <1 yr | 1–5 yr | 5–15 yr | >15 yr or ongoing |
| % of catalog revenue affected | <1% | 1–10% | 10–25% | >25% |
| Title transferability impact | none | partial / curable | one asset blocked | catalog-wide block |
| Number of affected income-generating assets | 1 | 2–5 | 6–20 | >20 |

Optionally record the rationale on the finding itself:

```json
{
  "severity": "high",
  "severity_factors": {
    "dollars_at_risk_vs_threshold": "10x-100x",
    "duration_years": 14,
    "pct_revenue_affected": "5-10",
    "transferability_impact": "one_asset",
    "affected_asset_count": 1,
    "calibration_note": "Duration alone places this in High."
  }
}
```

### Worked examples

- `SPLIT-02` — 14 years of mechanical mispayment on `Don't Stop Now`
  (Vega vs. Doré split sheet 75/25 vs. registrations 70/30). Duration is
  5–15 years, so duration alone is **High**. Dollar impact and asset count
  are Medium. Final severity: **High**.
- `SAMP-01` — uncleared 6-second sample on the catalog's top-earning song,
  open demand letter from 2019. Duration is ongoing, transferability impact
  is "one asset blocked," and the asset is the largest revenue contributor
  (asset-level revenue concentration High). Three High factors → bump to
  **Critical** if E&O exclusion confirms the exposure is uninsurable.
- `RR-02` — single zero-byte MLC monthly statement. Duration is one month,
  dollars at risk are <1×, transferability impact is none. Final severity:
  **Low**.

When the factors disagree, the worst factor wins unless the finding is
explicitly bounded (e.g., "limited to one already-excluded asset").

## Rights and ownership

Critical or high red flags:

- Income-generating works with no signed split sheet or agreement.
- Contract says seller controls less share than the catalog schedule claims.
- Missing assignment in a chain of title.
- Territory rights are narrower than modeled revenue.
- Reversion or termination rights are near-term or unmodeled.
- Sample, interpolation, or featured artist approval is missing.
- UCC, lien, estate, divorce, or dispute documents show encumbrances.
- Sync licensing is modeled as one-stop when approvals are fragmented.

## Metadata and registrations

High-value red flags:

- ISRCs and ISWCs are missing or not linked.
- Same ISRC appears on multiple conflicting titles.
- Same title has multiple writer splits across sources.
- Publisher or writer IPI/CAE values are missing for material works.
- PRO or MLC registrations do not match claimed splits.
- Income appears for works not present in the catalog schedule.
- Known streaming geography does not match collection territories.

## Royalty statement quality

High-value red flags:

- Gross income is presented as NPS or NLS.
- Period paid is confused with period earned.
- FX assumptions are missing or inconsistent.
- Statement lines cannot be traced to source files.
- Duplicate statement imports inflate revenue.
- Large unmatched royalty lines are excluded from analysis.
- Reserve releases or retroactive payments inflate LTM.

## PRO and performance income

High-value red flags:

- One quarter drives a large share of performance income.
- Bonus or premium columns drive a large share of PRO income.
- Cue sheets are missing for TV, film, or OTT income.
- Radio income is concentrated in one song, station, or promotion cycle.
- Foreign society adjustments appear as recurring income.
- Streaming usage grows while PRO income declines.
- Short-duration or background uses are modeled like feature uses.

## Master catalog economics

High-value red flags:

- Artist accounts are near recoupment and future royalties are unmodeled.
- Producer points or featured artist participations are missing.
- Cross-collateralization is assumed but unsupported.
- Reserves are high or about to unwind.
- Distribution fee changes are not reflected in NLS.
- Re-recording/version risk affects the main earning recordings.

## Valuation and concentration

High-value red flags:

- One song drives more than 40% of net income.
- One platform drives more than 50% of net income.
- Track count is used as diversification despite income concentration.
- Sync-heavy income is valued like recurring streaming or performance income.
- Viral or release-campaign spikes are treated as steady state.
- Decay assumptions are copied from comps without catalog-specific evidence.
- Active-management upside is included in base case without proof.

## Output rule

Every red flag should become a structured finding:

```json
{
  "finding_id": "RF-001",
  "severity": "high",
  "category": "rights",
  "affected_assets": ["catalog_asset_id"],
  "evidence": ["source/path.pdf#page=4"],
  "issue": "Income-generating work has no split sheet.",
  "valuation_treatment": "Exclude from base case or apply holdback until cured.",
  "follow_up": "Request signed split sheet and publishing agreement."
}
```
