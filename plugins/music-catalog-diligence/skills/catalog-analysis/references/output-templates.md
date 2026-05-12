# Output templates

Use these templates for catalog analysis deliverables.

## Executive valuation summary

```markdown
## Executive summary

**Preliminary value range:** $[low] - $[high]
**Base case:** $[base]
**Implied multiple:** [x] normalized NPS/NLS
**Rights analyzed:** [publishing / masters / mixed]
**Data confidence:** [high / medium / low]

The catalog generated $[reported] of reported LTM [NPS/NLS]. After normalizing
for [key adjustments], underwritable run-rate [NPS/NLS] is $[normalized].

Key value drivers:
- [Driver 1]
- [Driver 2]
- [Driver 3]

Key risks:
- [Risk 1]
- [Risk 2]
- [Risk 3]

Required diligence before final valuation:
- [Missing item 1]
- [Missing item 2]
```

## Quality-of-earnings bridge

This bridge is the canonical adjustment ladder defined in `SKILL.md`. Use every
line every time so you do not silently understate normalized run-rate by skipping
an adjustment that does apply.

```text
Reported LTM [NPS/NLS]                                       $x
  Less: one-time sync and direct-license spikes              (x)
  Less: viral, playlist, death-bump, or campaign spikes      (x)
  Less: settlement, audit recovery, accounting catch-up      (x)
  Less: non-repeat PRO bonus or premium income               (x)
  Plus/minus: current run-rate trend adjustment               x
  Plus/minus: admin, collection, reserve, recoupment,
              or contract adjustment                          x
  Plus/minus: undercollection or missing-registration
              adjustment                                      x
  Less: unsupported rights haircut                           (x)
Normalized run-rate [NPS/NLS]                                $x
```

Every adjustment needs a source, formula, or note. If an adjustment is judgment,
label it as judgment.

## Revenue mix table

| Source | LTM amount | % of total | 3-year trend | Normalization treatment |
| --- | ---: | ---: | --- | --- |
| Spotify | `$` | `%` | Growing/flat/declining | Include/haircut |
| PRO performance | `$` | `%` | Growing/flat/declining | Decompose |
| Sync | `$` | `%` | Lumpy | Exclude/smooth |
| YouTube Content ID | `$` | `%` | Growing/flat/declining | Include/haircut |

## Concentration table

| Dimension | Top exposure | % of net income | Valuation implication |
| --- | --- | ---: | --- |
| Song | `[title]` | `%` | [discount/caveat] |
| Artist | `[artist]` | `%` | [discount/caveat] |
| Platform | `[platform]` | `%` | [platform risk] |
| Territory | `[territory]` | `%` | [territory risk] |
| Rights type | `[publishing/master]` | `%` | [segmentation note] |

## Scenario table

Scenarios bundle several assumption shifts into a single narrative case
(downside / base / upside). They answer "what is the catalog worth if our whole
story is right or wrong?"

| Case | Normalized run-rate | Growth/decay | Multiple/DCF note | Value |
| --- | ---: | ---: | --- | ---: |
| Downside | `$` | `%` | [assumption] | `$` |
| Base | `$` | `%` | [assumption] | `$` |
| Upside | `$` | `%` | [assumption] | `$` |

## Sensitivity table

Sensitivities isolate a single assumption and walk it across a range. They
answer "how much does value move when this one input moves?" Include at least
one sensitivity over the multiple (for market-multiple valuations) or the
discount rate (for DCF), and one over normalized run-rate.

| Input | Range | Resulting value | Notes |
| --- | --- | ---: | --- |
| Multiple | `[low]x` / `[base]x` / `[high]x` | `$` / `$` / `$` | Holds normalized run-rate at base. |
| Discount rate | `[low]%` / `[base]%` / `[high]%` | `$` / `$` / `$` | DCF only. Holds growth/decay at base. |
| Normalized run-rate | `-[Δ]%` / base / `+[Δ]%` | `$` / `$` / `$` | Holds multiple/discount rate at base. |
| Decay rate | `[base]%` / `[stress]%` | `$` / `$` | If catalog has clear decay curve. |

Pair the sensitivity table with the scenario table in the deliverable. Scenarios
without sensitivities hide which assumption is doing the work.

## Risk register

| Risk | Severity | Evidence | Valuation treatment | Follow-up |
| --- | --- | --- | --- | --- |
| Missing split sheets | High | 17 songs unsupported | Holdback/haircut | Request signed splits |
| PRO bonus spike | Medium | One quarter drove 40% of NPS | Normalize | Get statement detail |
| Recoupment cliff | High | Artist accounts near recoupment | Model NLS step-down | Request recoupment schedule |

## Stop conditions

Use a "cannot value yet" response when:

- No reliable royalty history exists.
- Rights type is unclear.
- Reported income cannot be tied to assets.
- Meaningful income lacks ownership support.
- Gross revenue cannot be converted to NPS/NLS.
- Recoupment, reserves, or participant shares are missing for a master catalog.
- The user asks for final valuation but only provides screenshots or summaries.

When stopping, list the minimum files needed and offer a preliminary diagnostic
only if useful.
