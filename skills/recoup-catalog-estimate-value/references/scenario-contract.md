# Catalog scenario domain handoff (App2211)

Version `public-estimate-spotify-rate/1` exposes one already-supported sensitivity:
change the assumed Spotify master rate. It calls `estimate.py:model_tracks` unchanged;
there is no new valuation method, commercial threshold, fee deduction or rate default.
The fixed baseline supplies every assumption explicitly and remains illustrative.

Read `references/scenario-method.json` for the method/source pin and consumer rules,
`references/scenario-request.schema.json` for input shape, and
`fixtures/scenario-vectors.json` for exact synthetic inputs/expected outcomes.
`python3 scripts/scenario.py --input request.json` writes a JSON result to stdout.
The reusable Python function is `run_scenario(request)`; it reads only its own calculation source at import/evaluation to detect drift,
and makes no network calls.

## Bounded scope and reset

Only same-cohort master recordings with the same explicit currency and exact 365-day
Spotify measurement window enter this dev scenario. Every record carries the same
basis, original source reference and capture date. Measured counts are safe nonnegative
integers; unknown counts are null with `ttm_source: "none"`. Cumulative counts,
run-rate annualizations, compositions, Luminate measures, browser events and cash
cannot be substituted. Missing evidence is not zero. No source descriptor or Context
collection contract is introduced here.

The only control is `spotify_rate`, in currency per Spotify stream. Null resets to the
original rate. Other assumptions stay fixed: gross-up is hypothetical other-platform
income, net factors already include modeled deductions, controlled share is an
assumption and multiples are illustrative. No input rates or commercial defaults are
recommended by these fixtures. New assumptions require a new explicit baseline.

Output retains unchanged observations and their hash, both complete assumption sets,
method/version/source hash, units, coverage and both baseline/scenario results. The
original partial/unknown coverage status survives; no extrapolation to unseen tracks
or currencies occurs. Preserve coverage notes including source age/collection-lag and
low-count limitations in UI and exports. A capture timestamp is provenance, not proof
of current freshness or a receiving-account observation.

## Reconciliation example

Synthetic 1,000 annual streams at hypothetical USD0.004, gross-up0.25, net factor0.8,
controlled share0.5 and multiple10 yield modeled annual gross5, net2 and value20.
Changing only the rate to0.008 yields10,4,40. The second unknown recording remains
unknown: coverage is1/2 and status is partial_subset in both results. Reset returns
5,2,20. No claimed artist payout, ownership, guaranteed value or realized cash follows.

## Consumer boundary

This is an owning-domain reference helper and machine-readable contract, not a shipped
browser control. The App must not reimplement these formulas ad hoc. Root/UI must select
and review a browser-compatible local execution adapter against these vectors and the
pinned source before shared integration. That adapter must preserve all refusal checks,
coverage, full assumptions and reset, run without model/network calls, and refuse
incompatible periods/currencies/cohorts. A Python server round-trip would not establish
the requested in-browser behavior. Existing daily/cumulative explorer fixtures require
separate compatible synthetic annual observations; do not relabel them as measured365d.

Current method uses binary64 estimate arithmetic, not statement-accounting Decimal.
No intermediate rounding; conformance uses relative tolerance1e-12 and absolute1e-9.
Financial output is hypothetical. This contract does not cover authenticated ingestion,
Context persistence/descriptors, statement diligence or production activation.
