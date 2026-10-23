# Public estimate methodology

A displayed stream count is an observation. Money derived from it is a model,
never measured gross, a guaranteed minimum, owner earnings, receivables or recovered
royalties. Use this workflow for a public scenario; supplied contracts/statements
can support a separately scoped deal review or reconciliation.

## Population and measurement

Freeze the requested recordings/albums and as-of date. Preserve unresolved identities,
missing platforms, unmatched album tracks, retrieval times and the exact measurement
window. A snapshot response may include only mapped tracks: it does not prove the full
album population. Repeat track IDs must not inflate counts; ISRC collisions need review.
Composition-only or unreleased material is useful repertoire but has no supported
recording-stream estimate here. Do not force an artist ID or recording into it.

Use cumulative count differences across evidenced dates. `measured_365d` means endpoints
365 days apart. Other accepted windows are labeled `runrate_Nd`, annualized to 365 days,
and retain seasonality/release-spike uncertainty. Minimum default window is 28 days.
Negative deltas, insufficient windows and unavailable observations stay unknown.
An observed zero over a valid window is distinct from no measurement.

`estimate.py` emits `insufficient_measurement` with null monetary fields for no valid
annual measurement, `unsupported_right` for composition/publication models, or a
covered-subset scenario. `partial_subset` cannot become a catalog-wide headline.
`complete_input_subset` means the supplied input population has annual measurements;
it does not prove all recordings, income sources, contractual rights or territories.
Track counts are coverage measures, not revenue-weighted completeness scores.

## Explicit scenario inputs

The script's legacy rate/gross-up/net/multiple defaults are retained only as
**illustrative, unverified assumptions** for reproducibility. They are not current
market quotes or a verified rate card. Before relying on a scenario, supply a private
`--config` recording currency, right kind, controlled-share assumption, rates, gross-up,
net factors, multiple bands and dated sources/rationale in `assumption_sources`.
Set `assumption_status` to describe the actual evidence; changing a label is not validation.
Avoid spurious precision when presenting output. The complete config is preserved.

Official context checked 2026-10-22: [Spotify's FAQ](https://loudandclear.byspotify.com/faq/)
explains its royalty system rather than promising a fixed rate per stream.
[YouTube's earnings overview](https://support.google.com/youtube/answer/72902) describes
agreement-specific revenue sharing and distinctions between estimated and finalized
amounts. Neither source validates this script's illustrative numerical defaults.
Views, Shorts, premium, Content ID and channel earnings must not share one assumed
rate without comparable source evidence.

For each low/central/high scenario:

1. Modeled Spotify master gross = accepted annual streams × assumed master rate.
2. Add the explicit other-platform scenario as a fraction of modeled Spotify gross.
   Unsupported services remain unmeasured; gross-up is sensitivity, not observed income.
3. Modeled net interest = modeled gross × net factor × assumed controlled interest.
   The net factor already includes modeled deductions. Do not separately deduct
   distributor/artist/producer fees again. Do not infer a fee from a label's name.
4. Indicative value = modeled annual net interest × selected multiple.
   Multiples need dated scope-comparable evidence or must remain illustrative.

All-time YouTube/SoundCloud ratios are retained as context only; they cannot establish
annual income. This helper supports master-side scenarios only. Composition performance,
mechanical, sync, neighboring rights and full-work vs controlled-interest amounts need
separate scopes/rates and must never be added as though they are the same base.

## Calibration and handoff

One owner statement can calibrate only a comparable slice: match right, platform,
territory, currency, service period, paid/reported basis, ownership interest and coverage.
Preserve the prior public scenario, its inputs and prediction alongside the statement.
Do not label receipts/streams a true rate until numerator and denominator are comparable;
net/gross and timing differences can otherwise distort it. Retain residual uncertainty
for omitted services, periods, fees, returns and rights. A single statement does not
collapse the band to a point or establish all future catalog earnings.

When contracts/statements become available, export the scenario with its evidence and
unresolved assumptions. Review deal evaluates transaction economics; reconciliation
checks accounting. No recalculation here registers rights, requests payment, contacts
counterparties or claims a statement was deposited in a bank.
